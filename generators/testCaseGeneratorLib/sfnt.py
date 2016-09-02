"""
SFNT data extractor.
"""

import brotli
import struct
from collections import OrderedDict
from fontTools.misc import sstruct
from fontTools.ttLib import TTFont, getSearchRange
from fontTools.ttLib.sfnt import \
    SFNTDirectoryEntry, sfntDirectoryFormat, sfntDirectorySize, sfntDirectoryEntryFormat, sfntDirectoryEntrySize, \
    ttcHeaderFormat, ttcHeaderSize
from utilities import padData, calcPaddingLength, calcHeadCheckSumAdjustmentSFNT, calcTableChecksum
from woff import packTestCollectionDirectory, packTestDirectory, packTestCollectionHeader, packTestHeader, transformTable

def getTTFont(path, **kwargs):
    return TTFont(path, recalcTimestamp=False, **kwargs)

# ---------
# Unpacking
# ---------

def getSFNTData(pathOrFile, unsortGlyfLoca=False, glyphBBox="", alt255UInt16=False):
    if isinstance(pathOrFile, TTFont):
        font = pathOrFile
    else:
        font = getTTFont(pathOrFile)
    tableChecksums = {}
    tableData = {}
    tableOrder = [i for i in sorted(font.keys()) if len(i) == 4]
    if unsortGlyfLoca:
        assert "loca" in tableOrder
        loca = tableOrder.index("loca")
        glyf = tableOrder.index("glyf")
        tableOrder.insert(glyf, tableOrder.pop(loca))
    for tag in tableOrder:
        tableChecksums[tag] = font.reader.tables[tag].checkSum
        tableData[tag] = transformTable(font, tag, glyphBBox=glyphBBox, alt255UInt16=alt255UInt16)
    totalData = "".join([tableData[tag][1] for tag in tableOrder])
    compData = brotli.compress(totalData, brotli.MODE_FONT)
    if len(compData) >= len(totalData):
        compData = totalData
    if not isinstance(pathOrFile, TTFont):
        font.close()
        del font
    return tableData, compData, tableOrder, tableChecksums

def getSFNTCollectionData(pathOrFiles, modifyNames=True, reverseNames=False, DSIG=False, duplicates=[], shared=[]):
    tables = []
    offsets = {}
    fonts = []

    for pathOrFile in pathOrFiles:
        if isinstance(pathOrFile, TTFont):
            fonts.append(pathOrFile)
        else:
            fonts.append(getTTFont(pathOrFile))
    numFonts = len(fonts)

    header = dict(
        TTCTag="ttcf",
        Version=0x00010000,
        numFonts=numFonts,
    )

    if DSIG:
        header["version"] = 0x00020000

    fontData = sstruct.pack(ttcHeaderFormat, header)
    offset = ttcHeaderSize + (numFonts * struct.calcsize(">L"))
    if DSIG:
        offset += 3 * struct.calcsize(">L")

    for font in fonts:
        fontData += struct.pack(">L", offset)
        tags = [i for i in sorted(font.keys()) if len(i) == 4]
        offset += sfntDirectorySize + (len(tags) * sfntDirectoryEntrySize)

    if DSIG:
        data = "\0" * 4
        tables.append(data)
        offset += len(data)
        fontData += struct.pack(">4s", "DSIG")
        fontData += struct.pack(">L", len(data))
        fontData += struct.pack(">L", offset)

    for i, font in enumerate(fonts):
        # Make the name table unique
        if modifyNames:
            index = i
            if reverseNames:
                index = len(fonts) - i - 1
            name = font["name"]
            for namerecord in name.names:
                nameID = namerecord.nameID
                string = namerecord.toUnicode()
                if nameID == 1:
                    namerecord.string = "%s %d" % (string, index)
                elif nameID == 4:
                    namerecord.string = string.replace("Regular", "%d Regular" % index)
                elif nameID == 6:
                    namerecord.string = string.replace("-", "%d-" % index)

        tags = [i for i in sorted(font.keys()) if len(i) == 4]

        searchRange, entrySelector, rangeShift = getSearchRange(len(tags), 16)
        offsetTable = dict(
            sfntVersion=font.sfntVersion,
            numTables=len(tags),
            searchRange=searchRange,
            entrySelector=entrySelector,
            rangeShift=rangeShift,
        )

        fontData += sstruct.pack(sfntDirectoryFormat, offsetTable)

        for tag in tags:
            data = font.getTableData(tag)
            checksum = calcTableChecksum(tag, data)
            entry = dict(
                tag=tag,
                offset=offset,
                length=len(data),
                checkSum=checksum,
            )

            if (shared and tag not in shared) or tag in duplicates or data not in tables:
                tables.append(data)
                offsets[checksum] = offset
                offset += len(data) + calcPaddingLength(len(data))
            else:
                entry["offset"] = offsets[checksum]

            fontData += sstruct.pack(sfntDirectoryEntryFormat, entry)

    for table in tables:
        fontData += padData(table)

    return fontData

def getWOFFCollectionData(pathOrFiles, MismatchGlyfLoca=False, reverseNames=False):
    from defaultData import defaultTestData

    tableChecksums = []
    tableData = []
    tableOrder = []
    collectionDirectory = []
    locaIndices = []
    fonts = []

    for pathOrFile in pathOrFiles:
        if isinstance(pathOrFile, TTFont):
            fonts.append(pathOrFile)
        else:
            fonts.append(getTTFont(pathOrFile))

    for i, font in enumerate(fonts):
        index = i
        if reverseNames:
            index = len(fonts) - i - 1

        # Make the name table unique
        name = font["name"]
        for namerecord in name.names:
            nameID = namerecord.nameID
            string = namerecord.toUnicode()
            if nameID == 1:
                namerecord.string = "%s %d" % (string, index)
            elif nameID == 4:
                namerecord.string = string.replace("Regular", "%d Regular" % index)
            elif nameID == 6:
                namerecord.string = string.replace("-", "%d-" % index)

        tags = [i for i in sorted(font.keys()) if len(i) == 4]
        if "glyf" in tags:
            glyf = tags.index("glyf")
            loca = tags.index("loca")
            tags.insert(glyf + 1, tags.pop(loca))
        tableIndices = OrderedDict()
        for tag in tags:
            data = transformTable(font, tag)
            if MismatchGlyfLoca and tag in ("glyf", "loca"):
                tableData.append([tag, data])
                tableChecksums.append([tag, font.reader.tables[tag].checkSum])
                tableOrder.append(tag)
                tableIndex = len(tableData) - 1
                tableIndices[tag] = tableIndex
                if tag == "loca":
                    locaIndices.append(tableIndex)
            else:
                if [tag, data] not in tableData:
                    tableData.append([tag, data])
                    tableChecksums.append([tag, font.reader.tables[tag].checkSum])
                    tableOrder.append(tag)
                tableIndices[tag] = tableData.index([tag, data])
        collectionDirectory.append(dict(numTables=len(tableIndices), flavor=font.sfntVersion, index=tableIndices))
        font.close()
        del font

    if MismatchGlyfLoca:
        locaIndices.reverse()
        for i, entry in enumerate(collectionDirectory):
            entry["index"]["loca"] = locaIndices[i]
    totalData = "".join([data[1][1] for data in tableData])
    compData = brotli.compress(totalData, brotli.MODE_FONT)
    if len(compData) >= len(totalData):
        compData = totalData

    directory = [dict(tag=tag, origLength=0, transformLength=0, transformFlag=0) for tag in tableOrder]

    header, directory, collectionHeader, collectionDirectory, tableData = defaultTestData(directory=directory,
            tableData=tableData, compressedData=compData, collectionDirectory=collectionDirectory)

    data = packTestHeader(header)
    data += packTestDirectory(directory, isCollection=True)
    data += packTestCollectionHeader(collectionHeader)
    data += packTestCollectionDirectory(collectionDirectory)
    data += tableData

    data = padData(data)

    return data

# -------
# Packing
# -------

def packSFNT(header, directory, tableData, flavor="cff",
    calcCheckSum=True, applyPadding=True, sortDirectory=True,
    searchRange=None, entrySelector=None, rangeShift=None):
    # update the checkSum
    if calcCheckSum:
        if flavor == "cff":
            f = "OTTO"
        else:
            f = "\000\001\000\000"
        calcHeadCheckSumAdjustmentSFNT(directory, tableData, flavor=f)
    # update the header
    cSearchRange, cEntrySelector, cRangeShift = getSearchRange(len(directory), 16)
    if searchRange is None:
        searchRange = cSearchRange
    if entrySelector is None:
        entrySelector = cEntrySelector
    if rangeShift is None:
        rangeShift = cRangeShift
    if flavor == "cff":
        header["sfntVersion"] = "OTTO"
    else:
        header["sfntVersion"] = "\000\001\000\000"
    header["searchRange"] = searchRange
    header["entrySelector"] = entrySelector
    header["rangeShift"] = rangeShift
    # version and num tables should already be set
    sfntData = sstruct.pack(sfntDirectoryFormat, header)
    # compile the directory
    sfntDirectoryEntries = {}
    entryOrder = []
    for entry in directory:
        sfntEntry = SFNTDirectoryEntry()
        sfntEntry.tag = entry["tag"]
        sfntEntry.checkSum = entry["checksum"]
        sfntEntry.offset = entry["offset"]
        sfntEntry.length = entry["length"]
        sfntDirectoryEntries[entry["tag"]] = sfntEntry
        entryOrder.append(entry["tag"])
    if sortDirectory:
        entryOrder = sorted(entryOrder)
    for tag in entryOrder:
        entry = sfntDirectoryEntries[tag]
        sfntData += entry.toString()
    # compile the data
    directory = [(entry["offset"], entry["tag"]) for entry in directory]
    for o, tag in sorted(directory):
        data = tableData[tag]
        if applyPadding:
            data = padData(data)
        sfntData += data
    # done
    return sfntData
