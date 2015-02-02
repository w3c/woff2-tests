"""
SFNT data extractor.
"""

import brotli
from fontTools.misc import sstruct
from fontTools.ttLib import TTFont, getSearchRange
from fontTools.ttLib.sfnt import \
    SFNTDirectoryEntry, sfntDirectoryFormat, sfntDirectorySize, sfntDirectoryEntryFormat, sfntDirectoryEntrySize
from utilities import padData, calcHeadCheckSumAdjustmentSFNT
from woff import transformTable

# ---------
# Unpacking
# ---------

def getSFNTData(pathOrFile):
    font = TTFont(pathOrFile)
    tableChecksums = {}
    tableData = {}
    tableOrder = [i for i in sorted(font.keys()) if len(i) == 4]
    for tag in tableOrder:
        tableChecksums[tag] = font.reader.tables[tag].checkSum
        tableData[tag] = transformTable(font, tag)
    totalData = "".join([tableData[tag][1] for tag in tableOrder])
    compData = brotli.compress(totalData, brotli.MODE_FONT, True)
    if len(compData) >= len(totalData):
        compData = totalData
    font.close()
    del font
    return tableData, compData, tableOrder, tableChecksums

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
