"""
SFNT data extractor.
"""

import brotli
from collections import OrderedDict
from fontTools.misc import sstruct
from fontTools.ttLib import TTFont, getSearchRange
from fontTools.ttLib.sfnt import \
    SFNTDirectoryEntry, sfntDirectoryFormat, sfntDirectorySize, sfntDirectoryEntryFormat, sfntDirectoryEntrySize
from utilities import padData, calcHeadCheckSumAdjustmentSFNT
from woff import transformTable

# ---------
# Unpacking
# ---------

def getSFNTData(pathOrFile, unsortGlyfLoca=False, glyphBBox="", alt255UInt16=False):
    font = TTFont(pathOrFile)
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
    font.close()
    del font
    return tableData, compData, tableOrder, tableChecksums

def getWOFFCollectionData(pathOrFiles, MismatchGlyfLoca=False):
    tableChecksums = []
    tableData = []
    tableOrder = []
    collectionDirectory = []
    locaIndices = []

    for i, pathOrFile in enumerate(pathOrFiles):
        font = TTFont(pathOrFile)

        # Make the name table unique
        name = font["name"]
        for namerecord in name.names:
            nameID = namerecord.nameID
            string = namerecord.toUnicode()
            if nameID == 1:
                namerecord.string = "%s %d" % (string, i)
            elif nameID == 4:
                namerecord.string = string.replace("Regular", "%d Regular" % i)
            elif nameID == 6:
                namerecord.string = string.replace("-", "%d-" % i)

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
    return tableData, compData, tableOrder, tableChecksums, collectionDirectory

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
