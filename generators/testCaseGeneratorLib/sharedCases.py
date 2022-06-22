"""
Test cases that can be shared between two or more suites.
"""

import brotli
import os
import zlib
import codecs
import struct
from copy import deepcopy
from fontTools.ttLib import TTFont
from fontTools.ttLib.sfnt import sfntDirectoryEntrySize
from testCaseGeneratorLib.woff import base128Size, packTestHeader, packTestDirectory, packTestMetadata, packTestPrivateData,\
    woffHeaderSize, transformTable
from testCaseGeneratorLib.defaultData import defaultTestData, defaultSFNTTestData, testDataWOFFMetadata, testDataWOFFPrivateData,\
    sfntCFFTableData, testCFFDataWOFFDirectory
from testCaseGeneratorLib.paths import sfntTTFSourcePath, sfntTTFCompositeSourcePath
from testCaseGeneratorLib.utilities import calcPaddingLength, padData, calcTableChecksum, stripMetadata
from testCaseGeneratorLib.sfnt import getSFNTData, packSFNT, getTTFont

def makeMetadataTest(metadata):
    """
    This is a convenience functon that eliminates the need to make a complete
    WOFF when only the metadata is being tested.
    """
    metadata = metadata.strip()
    # convert to tabs
    metadata = str(metadata)
    metadata = metadata.replace("    ", "\t")
    # store
    originalMetadata = metadata
    # pack
    header, directory, tableData, metadata = defaultTestData(metadata=metadata)
    data = padData(packTestHeader(header) + packTestDirectory(directory) + tableData) + packTestMetadata(metadata)
    # done
    return data, originalMetadata


# -----------
# Valid Files
# -----------

# CFF

def makeValidWOFF1():
    header, directory, tableData = defaultTestData()
    data = padData(packTestHeader(header) + packTestDirectory(directory) + tableData)
    return data

makeValidWOFF1Title = "Valid WOFF 1"
makeValidWOFF1Description = "Valid CFF flavored WOFF with no metadata and no private data"
makeValidWOFF1Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

def makeValidWOFF2():
    header, directory, tableData, metadata = defaultTestData(metadata=testDataWOFFMetadata)
    data = padData(packTestHeader(header) + packTestDirectory(directory) + tableData) + packTestMetadata(metadata)
    return data

makeValidWOFF2Title = "Valid WOFF 2"
makeValidWOFF2Description = "Valid CFF flavored WOFF with metadata"
makeValidWOFF2Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

def makeValidWOFF3():
    header, directory, tableData, privateData = defaultTestData(privateData=testDataWOFFPrivateData)
    data = padData(packTestHeader(header) + packTestDirectory(directory) + tableData) + packTestPrivateData(privateData)
    return data

makeValidWOFF3Title = "Valid WOFF 3"
makeValidWOFF3Description = "Valid CFF flavored WOFF with private data"
makeValidWOFF3Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

def makeValidWOFF4():
    header, directory, tableData, metadata, privateData = defaultTestData(metadata=testDataWOFFMetadata, privateData=testDataWOFFPrivateData)
    data = padData(packTestHeader(header) + packTestDirectory(directory) + tableData) + packTestMetadata(metadata, havePrivateData=True) + packTestPrivateData(privateData)
    return data

makeValidWOFF4Title = "Valid WOFF 4"
makeValidWOFF4Description = "Valid CFF flavored WOFF with metadata and private data"
makeValidWOFF4Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# TTF

def makeValidWOFF5():
    header, directory, tableData = defaultTestData(flavor="ttf")
    data = padData(packTestHeader(header) + packTestDirectory(directory) + tableData)
    return data

makeValidWOFF5Title = "Valid WOFF 5"
makeValidWOFF5Description = "Valid TTF flavored WOFF with no metadata and no private data"
makeValidWOFF5Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

def makeValidWOFF6():
    header, directory, tableData, metadata = defaultTestData(metadata=testDataWOFFMetadata, flavor="ttf")
    data = padData(packTestHeader(header) + packTestDirectory(directory) + tableData) + packTestMetadata(metadata)
    return data

makeValidWOFF6Title = "Valid WOFF 6"
makeValidWOFF6Description = "Valid TTF flavored WOFF with metadata"
makeValidWOFF6Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

def makeValidWOFF7():
    header, directory, tableData, privateData = defaultTestData(privateData=testDataWOFFPrivateData, flavor="ttf")
    data = padData(packTestHeader(header) + packTestDirectory(directory) + tableData) + packTestPrivateData(privateData)
    return data

makeValidWOFF7Title = "Valid WOFF 7"
makeValidWOFF7Description = "Valid TTF flavored WOFF with private data"
makeValidWOFF7Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

def makeValidWOFF8():
    header, directory, tableData, metadata, privateData = defaultTestData(metadata=testDataWOFFMetadata, privateData=testDataWOFFPrivateData, flavor="ttf")
    data = padData(packTestHeader(header) + packTestDirectory(directory) + tableData) + packTestMetadata(metadata, havePrivateData=True) + packTestPrivateData(privateData)
    return data

makeValidWOFF8Title = "Valid WOFF 8"
makeValidWOFF8Description = "Valid TTF flavored WOFF with metadata and private data"
makeValidWOFF8Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# ---------------------------------
# File Structure: Header: signature
# ---------------------------------

def makeHeaderInvalidSignature1():
    header, directory, tableData = defaultTestData()
    header["signature"] = "XXXX"
    data = padData(packTestHeader(header) + packTestDirectory(directory) + tableData)
    return data

makeHeaderInvalidSignature1Title = "Header Signature Invalid Value"
makeHeaderInvalidSignature1Description = "The signature field contains XXXX instead of wOFF."
makeHeaderInvalidSignature1Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# ------------------------------
# File Structure: Header: length
# ------------------------------

def makeHeaderInvalidLength1():
    header, directory, tableData = defaultTestData()
    header["length"] -= 4
    data = padData(packTestHeader(header) + packTestDirectory(directory) + tableData)
    return data

makeHeaderInvalidLength1Title = "Header Length Too Short"
makeHeaderInvalidLength1Description = "The length field contains a value that is four bytes shorter than the actual data."
makeHeaderInvalidLength1Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

def makeHeaderInvalidLength2():
    header, directory, tableData = defaultTestData()
    header["length"] += 4
    data = padData(packTestHeader(header) + packTestDirectory(directory) + tableData)
    return data

makeHeaderInvalidLength2Title = "Header Length Too Long"
makeHeaderInvalidLength2Description = "The length field contains a value that is four bytes longer than the actual data."
makeHeaderInvalidLength2Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# ---------------------------------
# File Structure: Header: numTables
# ---------------------------------

def makeHeaderInvalidNumTables1():
    header, directory, tableData = defaultTestData()
    header["numTables"] = 0
    data = padData(packTestHeader(header) + packTestDirectory(directory) + tableData)
    return data

makeHeaderInvalidNumTables1Title = "Header Number of Tables Set to Zero"
makeHeaderInvalidNumTables1Description = "The header contains 0 in the numTables field. A table directory and table data are present."
makeHeaderInvalidNumTables1Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# --------------------------------
# File Structure: Header: reserved
# --------------------------------

def makeHeaderInvalidReserved1():
    header, directory, tableData = defaultTestData()
    header["reserved"] = 1
    data = padData(packTestHeader(header) + packTestDirectory(directory) + tableData)
    return data

makeHeaderInvalidReserved1Title = "Header Reserved Invalid Value"
makeHeaderInvalidReserved1Description = "The reserved field contains 1."
makeHeaderInvalidReserved1Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# -------------------------------------
# File Structure: Header: totalSfntSize
# -------------------------------------

def makeHeaderIncorrectTotalSfntSize(big=False):
    header, directory, tableData = defaultTestData()
    numBytes = base128Size(header["totalSfntSize"])
    totalSfntSize = 128**(numBytes -1)
    if big:
        totalSfntSize *= 127
    else:
        totalSfntSize += 1
    assert numBytes == base128Size(totalSfntSize)
    header["totalSfntSize"] = totalSfntSize
    data = padData(packTestHeader(header) + packTestDirectory(directory) + tableData)
    return data

makeHeaderIncorrectTotalSfntSize1Title = "Header TotalSfntSize Too Small"
makeHeaderIncorrectTotalSfntSize1Description = "The totalSfntSize field contains a too small incorrect value."
makeHeaderIncorrectTotalSfntSize1Credits = [dict(title="Khaled Hosny", role="author", link="http://khaledhosny.org")]


makeHeaderIncorrectTotalSfntSize2Title = "Header TotalSfntSize Too Big"
makeHeaderIncorrectTotalSfntSize2Description = "The totalSfntSize field contains a too big incorrect value."
makeHeaderIncorrectTotalSfntSize2Credits = [dict(title="Khaled Hosny", role="author", link="http://khaledhosny.org")]

# --------------------------------------------
# File Structure: Data Blocks: Extraneous Data
# --------------------------------------------

# between header and table directory

def makeExtraneousData0():
    header, directory, tableData = defaultTestData()
    bogusByteLength = 4
    bogusBytes = b"\0" * bogusByteLength
    header["length"] += bogusByteLength
    data = padData(packTestHeader(header) + bogusBytes + packTestDirectory(directory) + tableData)
    return data

makeExtraneousData0Title = "Extraneous Data Between Header and Directory"
makeExtraneousData0Description = "There are four null bytes between the header and the table directory."
makeExtraneousData0Credits =  [dict(title="Khaled Hosny", role="author", link="http://khaledhosny.org")]

# between table directory and table data

def makeExtraneousData1():
    header, directory, tableData = defaultTestData()
    bogusByteLength = 4
    bogusBytes = b"\0" * bogusByteLength
    header["length"] += bogusByteLength
    data = padData(packTestHeader(header)
                   + packTestDirectory(directory)
                   + bogusBytes
                   + tableData)
    return data

makeExtraneousData1Title = "Extraneous Data Between Directory and Table Data"
makeExtraneousData1Description = "There are four null bytes between the table directory and the table data."
makeExtraneousData1Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# after table data with no metadata or private data

def makeExtraneousData2():
    header, directory, tableData = defaultTestData()
    bogusByteLength = 4
    bogusBytes = b"\0" * bogusByteLength
    header["length"] += bogusByteLength
    data = padData(packTestHeader(header) + packTestDirectory(directory) + tableData) + bogusBytes
    return data

makeExtraneousData2Title = "Extraneous Data After Table Data"
makeExtraneousData2Description = "There are four null bytes after the table data block and there is no metadata or private data."
makeExtraneousData2Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# between tabledata and metadata

def makeExtraneousData3():
    header, directory, tableData, metadata = defaultTestData(metadata=testDataWOFFMetadata)
    bogusByteLength = 4
    bogusBytes = b"\0" * bogusByteLength
    header["length"] += bogusByteLength
    header["metaOffset"] += bogusByteLength
    data = padData(packTestHeader(header) + packTestDirectory(directory) + tableData) + bogusBytes + packTestMetadata(metadata)
    return data

makeExtraneousData3Title = "Extraneous Data Between Table Data and Metadata"
makeExtraneousData3Description = "There are four null bytes between the table data and the metadata."
makeExtraneousData3Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# between tabledata and private data

def makeExtraneousData4():
    header, directory, tableData, privateData = defaultTestData(privateData=testDataWOFFPrivateData)
    bogusByteLength = 4
    bogusBytes = b"\0" * bogusByteLength
    header["length"] += bogusByteLength
    header["privOffset"] += bogusByteLength
    data = padData(packTestHeader(header) + packTestDirectory(directory) + tableData) + bogusBytes + packTestPrivateData(privateData)
    return data

makeExtraneousData4Title = "Extraneous Data Between Table Data and Private Data"
makeExtraneousData4Description = "There are four null bytes between the table data and the private data."
makeExtraneousData4Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# between metadata and private data

def makeExtraneousData5():
    header, directory, tableData, metadata, privateData = defaultTestData(metadata=testDataWOFFMetadata, privateData=testDataWOFFPrivateData)
    bogusByteLength = 4
    bogusBytes = b"\0" * bogusByteLength
    header["length"] += bogusByteLength
    header["privOffset"] += bogusByteLength
    data = padData(packTestHeader(header) + packTestDirectory(directory) + tableData) + packTestMetadata(metadata, havePrivateData=True) + bogusBytes + packTestPrivateData(privateData)
    return data

makeExtraneousData5Title = "Extraneous Data Between Metdata and Private Data"
makeExtraneousData5Description = "There are four null bytes between the metadata and the private data."
makeExtraneousData5Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# after metadata with no private data

def makeExtraneousData6():
    header, directory, tableData, metadata = defaultTestData(metadata=testDataWOFFMetadata)
    bogusByteLength = 4
    bogusBytes = b"\0" * bogusByteLength
    header["length"] += bogusByteLength
    data = padData(packTestHeader(header) + packTestDirectory(directory) + tableData) + packTestMetadata(metadata) + bogusBytes
    return data

makeExtraneousData6Title = "Extraneous Data After Metadata"
makeExtraneousData6Description = "There are four null bytes after the metadata and there is no private data."
makeExtraneousData6Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# after private data

def makeExtraneousData7():
    header, directory, tableData, privateData = defaultTestData(privateData=testDataWOFFPrivateData)
    bogusByteLength = 4
    bogusBytes = b"\0" * bogusByteLength
    header["length"] += bogusByteLength
    data = padData(packTestHeader(header) + packTestDirectory(directory) + tableData) + packTestPrivateData(privateData) + bogusBytes
    return data

makeExtraneousData7Title = "Extraneous Data After Private Data"
makeExtraneousData7Description = "There are four null bytes after the private data."
makeExtraneousData7Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# before last table

def makeExtraneousData8():
    header, directory, tableData = defaultTestData()

    table = sfntCFFTableData[directory[-1]["tag"]][0]
    tableData = brotli.decompress(tableData)
    tableData = brotli.compress(tableData[:-len(table)] + table + table)

    header["length"] = woffHeaderSize + len(packTestDirectory(directory)) + len(tableData)
    header["length"] += calcPaddingLength(header["length"])
    header["totalCompressedSize"] = len(tableData)

    data = padData(packTestHeader(header) + packTestDirectory(directory) + tableData)
    return data

makeExtraneousData8Title = "Extraneous Data Betwen Table Data"
makeExtraneousData8Description = "There is extraneous data before the last table."
makeExtraneousData8Credits = [dict(title="Khaled Hosny", role="author", link="http://khaledhosny.org")]


# -------------------------------------
# File Structure: Data Blocks: Overlaps
# -------------------------------------

# metadata overlaps the table data

def makeOverlappingData1():
    header, directory, tableData, metadata = defaultTestData(metadata=testDataWOFFMetadata)
    overlapLength = 4
    header["metaOffset"] -= overlapLength
    header["length"] -= overlapLength
    data = packTestHeader(header) + packTestDirectory(directory) + tableData[:-overlapLength] + packTestMetadata(metadata)
    return data

makeOverlappingData1Title = "Metadata Overlaps Table Data"
makeOverlappingData1Description = "The metadata offset is four bytes before the end of the table data."
makeOverlappingData1Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# private data overlaps the table data

def makeOverlappingData2():
    header, directory, tableData, privateData = defaultTestData(privateData=testDataWOFFPrivateData)
    overlapLength = 4
    header["privOffset"] -= overlapLength
    header["length"] -= overlapLength
    data = packTestHeader(header) + packTestDirectory(directory) + tableData[:-overlapLength] + packTestPrivateData(privateData)
    return data

makeOverlappingData2Title = "Private Data Overlaps Table Data"
makeOverlappingData2Description = "The private data offset is four bytes before the end of the table data."
makeOverlappingData2Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# private data overlaps the metadata

def makeOverlappingData3():
    header, directory, tableData, metadata, privateData = defaultTestData(metadata=testDataWOFFMetadata, privateData=testDataWOFFPrivateData)
    overlapLength = 4
    header["privOffset"] -= overlapLength
    header["length"] -= overlapLength
    data = padData(packTestHeader(header) + packTestDirectory(directory) + tableData) + packTestMetadata(metadata, havePrivateData=True)[:-overlapLength] + packTestPrivateData(privateData)
    return data

makeOverlappingData3Title = "Private Data Overlaps Metadata"
makeOverlappingData3Description = "The private data offset is four bytes before the end of the metadata."
makeOverlappingData3Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# ----------------------------------------------
# File Structure: Table Data: Compression Format
# ----------------------------------------------

# compression incompatible with Brotli

def makeTableBrotliCompressionTest1():
    header, directory, tableData = defaultTestData()
    zlibData = zlib.compress(brotli.decompress(tableData))
    length = woffHeaderSize + len(packTestDirectory(directory)) + len(zlibData)
    length += calcPaddingLength(length)
    header["totalCompressedSize"] = len(zlibData)
    header["length"] = length
    data = padData(packTestHeader(header) + packTestDirectory(directory) + zlibData)
    return data

makeTableBrotliCompressionTest1Title = "Font Table Data Invalid Compressed Data"
makeTableBrotliCompressionTest1Description = "Font table data is compressed with zlib instead of Brotli."
makeTableBrotliCompressionTest1Credits = [dict(title="Khaled Hosny", role="author", link="http://khaledhosny.org")]

# -----------------------------------------------
# File Structure: Table Data: Decompressed Length
# -----------------------------------------------

# decompressed length less than sum of origLength

def makeTableDecompressedLengthTest1():
    header, directory, tableData = defaultTestData()
    directory[0]["origLength"] += 1
    data = padData(packTestHeader(header) + packTestDirectory(directory) + tableData)
    return data

makeTableDecompressedLengthTest1Title = "Font Table Data Decompressed Length Less Than Original Length"
makeTableDecompressedLengthTest1Description = "The original length of the first table in the directory is increased by 1, making the decompressed length of the table data less than the sum of original table lengths."
makeTableDecompressedLengthTest1Credits = [dict(title="Khaled Hosny", role="author", link="http://khaledhosny.org")]

# decompressed length greater than sum of origLength

def makeTableDecompressedLengthTest2():
    header, directory, tableData = defaultTestData()
    directory[0]["origLength"] -= 1
    data = padData(packTestHeader(header) + packTestDirectory(directory) + tableData)
    return data

makeTableDecompressedLengthTest2Title = "Font Table Data Decompressed Length Greater Than Original Length"
makeTableDecompressedLengthTest2Description = "The original length of the first table in the directory is decreased by 1, making the decompressed length of the table data greater than the sum of original table lengths."
makeTableDecompressedLengthTest2Credits = [dict(title="Khaled Hosny", role="author", link="http://khaledhosny.org")]

def makeTableDecompressedLengthTest3():
    header, directory, tableData = defaultTestData(flavor="ttf")
    for entry in directory:
        if entry["tag"] == "glyf":
            entry["transformLength"] += 1
    data = padData(packTestHeader(header) + packTestDirectory(directory) + tableData)
    return data

makeTableDecompressedLengthTest3Title = "Font Table Data Decompressed Length Less Than Transformed Length"
makeTableDecompressedLengthTest3Description = "The transformed length of the glyf table in the directory is increased by 1, making the decompressed length of the table data less than the sum of transformed table lengths."
makeTableDecompressedLengthTest3Credits = [dict(title="Khaled Hosny", role="author", link="http://khaledhosny.org")]

def makeTableDecompressedLengthTest4():
    header, directory, tableData = defaultTestData(flavor="ttf")
    for entry in directory:
        if entry["tag"] == "glyf":
            entry["transformLength"] -= 1
    data = padData(packTestHeader(header) + packTestDirectory(directory) + tableData)
    return data

makeTableDecompressedLengthTest4Title = "Font Table Data Decompressed Length Greater Than Transformed Length"
makeTableDecompressedLengthTest4Description = "The transformed length of the glyf table in the directory is decreased by 1, making the decompressed length of the table data greater than the sum of transformed table lengths."
makeTableDecompressedLengthTest4Credits = [dict(title="Khaled Hosny", role="author", link="http://khaledhosny.org")]

# -------------------------------------------
# File Structure: Table Data: Transformations
# -------------------------------------------

def getModifiedSFNTData(path=sfntTTFSourcePath, noTransform=False, nonZeroLoca=False, longLoca=False):
    font = TTFont(path)

    loca = font["loca"]
    head = font["head"]

    if longLoca:
        head.indexToLocFormat = 1

    tableChecksums = {}
    tableData = {}
    tableOrder = [i for i in sorted(font.keys()) if len(i) == 4]
    for tag in tableOrder:
        tableChecksums[tag] = font.reader.tables[tag].checkSum
        if nonZeroLoca and tag == "loca":
            tableData[tag] = (font.getTableData(tag), b"\0" * 4)
        elif longLoca and tag == "loca":
            tableData[tag] = (b"\0" * len(loca) * 4, b"")
        elif noTransform:
            tableData[tag] = (font.getTableData(tag), font.getTableData(tag))
        else:
            tableData[tag] = transformTable(font, tag)
    totalData = b"".join([tableData[tag][1] for tag in tableOrder])
    compData = brotli.compress(totalData, brotli.MODE_FONT)
    if len(compData) >= len(totalData):
        compData = totalData
    font.close()
    del font
    return tableData, compData, tableOrder, tableChecksums

def makeTableNonZeroLocaTest1():
    sfntData = getModifiedSFNTData(nonZeroLoca=True)
    compressedData = sfntData[1]
    uncompressedData = sfntData[0]
    header, directory, tableData = defaultTestData(flavor="ttf", tableData=uncompressedData, compressedData=compressedData)
    data = padData(packTestHeader(header) + packTestDirectory(directory) + tableData)
    return data

makeTableNonZeroLocaTest1Title = "Font Table Data Loca Is Not Zero"
makeTableNonZeroLocaTest1Description = "The transformed loca table contains 4 zero bytes and its transformLength is 4."
makeTableNonZeroLocaTest1Credits = [dict(title="Khaled Hosny", role="author", link="http://khaledhosny.org")]

def makeLocaSizeTest1():
    sfntData = getModifiedSFNTData(longLoca=True)
    compressedData = sfntData[1]
    uncompressedData = sfntData[0]
    header, directory, tableData = defaultTestData(flavor="ttf", tableData=uncompressedData, compressedData=compressedData)
    data = padData(packTestHeader(header) + packTestDirectory(directory) + tableData)
    return data

makeLocaSizeTest1Title = "Loca Table With Long Format"
makeLocaSizeTest1Description = "A valid TTF flavoured font where the loca table uses the long format."
makeLocaSizeTest1Credits = [dict(title="Khaled Hosny", role="author", link="http://khaledhosny.org")]

def makeLocaSizeTest2():
    sfntData = getModifiedSFNTData(longLoca=False)
    compressedData = sfntData[1]
    uncompressedData = sfntData[0]
    header, directory, tableData = defaultTestData(flavor="ttf", tableData=uncompressedData, compressedData=compressedData)
    data = padData(packTestHeader(header) + packTestDirectory(directory) + tableData)
    return data

makeLocaSizeTest2Title = "Loca Table With Short Format"
makeLocaSizeTest2Description = "A valid TTF flavoured font where the loca table uses the short format."
makeLocaSizeTest2Credits = [dict(title="Khaled Hosny", role="author", link="http://khaledhosny.org")]

def makeLocaSizeTest3():
    header, directory, tableData = defaultTestData(flavor="cff")
    data = padData(packTestHeader(header) + packTestDirectory(directory) + tableData)
    return data

makeLocaSizeTest3Title = "No Loca Table"
makeLocaSizeTest3Description = "A valid CFF flavoured font which naturally have no loca table."
makeLocaSizeTest3Credits = [dict(title="Khaled Hosny", role="author", link="http://khaledhosny.org")]

def makeValidLoca1():
    from testCaseGeneratorLib.sfnt import getSFNTData
    tableData, compressedData, tableOrder, tableChecksums = getSFNTData(sfntTTFCompositeSourcePath)
    header, directory, tableData = defaultTestData(tableData=tableData, compressedData=compressedData, flavor="ttf")
    data = padData(packTestHeader(header) + packTestDirectory(directory) + tableData)
    return data

makeValidLoca1Title = "Font With Short Loca and Composite Glyphs"
makeValidLoca1Description = "Valid TTF flavored WOFF with simple composite glyphs where the loca table uses the short format, to check loca reconstruction"
makeValidLoca1Credits = [dict(title="Khaled Hosny", role="author", link="http://khaledhosny.org")]

def makeValidLoca2():
    sfntData = getModifiedSFNTData(path=sfntTTFCompositeSourcePath, longLoca=True)
    compressedData = sfntData[1]
    uncompressedData = sfntData[0]
    header, directory, tableData = defaultTestData(flavor="ttf", tableData=uncompressedData, compressedData=compressedData)
    data = padData(packTestHeader(header) + packTestDirectory(directory) + tableData)
    return data

makeValidLoca2Title = "Font With Long Loca and Composite Glyphs"
makeValidLoca2Description = "Valid TTF flavored WOFF with simple composite glyphs where the loca table uses the long format, to check loca reconstruction"
makeValidLoca2Credits = [dict(title="Khaled Hosny", role="author", link="http://khaledhosny.org")]

def makeGlyfBBox1():
    tableData, compressedData, tableOrder, tableChecksums = getSFNTData(sfntTTFCompositeSourcePath)
    header, directory, tableData = defaultTestData(tableData=tableData, compressedData=compressedData, flavor="ttf")
    data = padData(packTestHeader(header) + packTestDirectory(directory) + tableData)
    return data

makeGlyfBBox1Title = "Composite Glyph Without Bounding Box"
makeGlyfBBox1Description = "Valid TTF flavored WOFF with composite glyphs"
makeGlyfBBox1Credits = [dict(title="Khaled Hosny", role="author", link="http://khaledhosny.org")]

def makeLSB1():
    woffHeader, woffDirectory, woffCompressedTableData = defaultTestData(flavor="TTF")
    woffTableData = brotli.decompress(woffCompressedTableData)
    offset = 0
    for entry in woffDirectory:
        if entry["tag"] == "hmtx":
            assert entry["transformFlag"] == 1
            flags = woffTableData[offset]
            assert flags & (1 << 0)
            assert flags & (1 << 1)
        offset += entry["transformLength"]
    header, directory, tableData = defaultSFNTTestData(flavor="TTF")
    data = packSFNT(header, directory, tableData, flavor="TTF")
    return data

def makeHmtxTransform1():
    header, directory, tableData = defaultTestData(flavor="TTF")
    decompressedTableData = brotli.decompress(tableData)
    offset = 0
    for entry in directory:
        if entry["tag"] == "hmtx":
            assert entry["transformFlag"] == 1
            flags = decompressedTableData[offset]
            assert flags & (1 << 0)
            assert flags & (1 << 1)
        offset += entry["transformLength"]
    data = padData(packTestHeader(header) + packTestDirectory(directory) + tableData)
    return data

def makeGlyfOverlapBitmapSFNT():
    font = getTTFont(sfntTTFSourcePath, recalcBBoxes=True)
    glyf = font["glyf"]

    for glyphName in glyf.keys():
        glyph = glyf[glyphName]
        if glyph.numberOfContours > 0:
            glyph.flags[0] |= 0x40 # flagOverlapSimple

    tableData = getSFNTData(font)[0]
    font.close()
    del font
    header, directory, tableData = defaultSFNTTestData(tableData=tableData, flavor="TTF")
    data = packSFNT(header, directory, tableData, flavor="TTF")
    return data

def makeGlyfNoOverlapBitmapSFNT():
    font = getTTFont(sfntTTFSourcePath, recalcBBoxes=True)
    tableData = getSFNTData(font)[0]
    font.close()
    del font
    header, directory, tableData = defaultSFNTTestData(tableData=tableData, flavor="TTF")
    data = packSFNT(header, directory, tableData, flavor="TTF")
    return data


def makeGlyfOverlapBitmap():
    header, directory, tableData = defaultTestData(flavor="TTF")
    decompressedTableData = brotli.decompress(tableData)
    offset = 0
    for entry in directory:
        if entry["tag"] == "glyf":
            assert entry["transformFlag"] == 0
            flagsOffset = offset + 3
            nextTableOffset = offset + entry["transformLength"]

            flags = decompressedTableData[flagsOffset]
            flags |= (1 << 0)

            decompressedTableData = (decompressedTableData[:flagsOffset]
                                     + struct.pack(">B", flags)
                                     + decompressedTableData[flagsOffset + 1:nextTableOffset]
                                     + struct.pack(">B", 0b00110000)
                                     + decompressedTableData[nextTableOffset:])

            entry["transformLength"] += 1

        offset += entry["transformLength"]

    tableData = brotli.compress(decompressedTableData, brotli.MODE_FONT)

    header["length"] = woffHeaderSize + len(packTestDirectory(directory)) + len(tableData)
    header["length"] += calcPaddingLength(header["length"])
    header["totalCompressedSize"] = len(tableData)

    data = padData(packTestHeader(header) + packTestDirectory(directory) + tableData)
    return data

def makeGlyfNoOverlapBitmap():
    header, directory, tableData = defaultTestData(flavor="TTF")
    decompressedTableData = brotli.decompress(tableData)

    tableData = brotli.compress(decompressedTableData, brotli.MODE_FONT)

    header["length"] = woffHeaderSize + len(packTestDirectory(directory)) + len(tableData)
    header["length"] += calcPaddingLength(header["length"])
    header["totalCompressedSize"] = len(tableData)

    data = padData(packTestHeader(header) + packTestDirectory(directory) + tableData)
    return data

makeHmtxTransform1Title = "Transformed Hmtx Table"
makeHmtxTransform1Description = "Valid TTF flavored WOFF with transformed hmtx table."
makeHmtxTransform1Credits = [dict(title="Khaled Hosny", role="author", link="http://khaledhosny.org")]

def makeHmtxTransform2():
    header, directory, tableData = defaultTestData(flavor="TTF")
    decompressedTableData = brotli.decompress(tableData)
    offset = 0
    for entry in directory:
        if entry["tag"] == "hmtx":
            assert entry["transformFlag"] == 1
            flags = decompressedTableData[offset]
            for bit in range(2, 8):
                flags |= 1 << bit
            decompressedTableData = decompressedTableData[:offset] + struct.pack(">B", flags) + decompressedTableData[offset+1:]
            flags = decompressedTableData[offset]
            assert flags == 255
        offset += entry["transformLength"]

    tableData = brotli.compress(decompressedTableData, brotli.MODE_FONT)

    header["length"] = woffHeaderSize + len(packTestDirectory(directory)) + len(tableData)
    header["length"] += calcPaddingLength(header["length"])
    header["totalCompressedSize"] = len(tableData)

    data = padData(packTestHeader(header) + packTestDirectory(directory) + tableData)
    return data

makeHmtxTransform2Title = "Transformed Hmtx Table With All Flags Set"
makeHmtxTransform2Description = "Invalid TTF flavored WOFF with transformed hmtx table that has all flags bits (including reserved bits) set."
makeHmtxTransform2Credits = [dict(title="Khaled Hosny", role="author", link="http://khaledhosny.org")]

def makeHmtxTransform3():
    header, directory, tableData = defaultTestData(flavor="TTF")
    decompressedTableData = brotli.decompress(tableData)
    offset = 0
    for entry in directory:
        if entry["tag"] == "hmtx":
            assert entry["transformFlag"] == 1
            decompressedTableData = decompressedTableData[:offset] + b"\0" + decompressedTableData[offset+1:]
            flags = decompressedTableData[offset]
            assert flags == 0
        offset += entry["transformLength"]

    tableData = brotli.compress(decompressedTableData, brotli.MODE_FONT)

    header["length"] = woffHeaderSize + len(packTestDirectory(directory)) + len(tableData)
    header["length"] += calcPaddingLength(header["length"])
    header["totalCompressedSize"] = len(tableData)

    data = padData(packTestHeader(header) + packTestDirectory(directory) + tableData)
    return data

makeHmtxTransform3Title = "Transformed Hmtx Table With 0 Flags"
makeHmtxTransform3Description = "Invalid TTF flavored WOFF with transformed hmtx table that has 0 flags (null transform)."
makeHmtxTransform3Credits = [dict(title="Khaled Hosny", role="author", link="http://khaledhosny.org")]

# -----------------------------------------
# File Structure: Table Directory: Ordering
# -----------------------------------------

def makeWrongTableOrder1():
    tableData, compressedData, tableOrder, tableChecksums = getSFNTData(sfntTTFSourcePath, unsortGlyfLoca=True)
    header, directory, tableData = defaultTestData(tableData=tableData, compressedData=compressedData, flavor="ttf")
    data = padData(packTestHeader(header) + packTestDirectory(directory, unsortGlyfLoca=True) + tableData)
    return data

makeWrongTableOrder1Title = "WOFF2 With Wrong Table Order"
makeWrongTableOrder1Description = "An invalid WOFF2 font with loca before glyf in the table directory"
makeWrongTableOrder1Credits = [dict(title="Khaled Hosny", role="author", link="http://khaledhosny.org")]

# -----------------------------
# Metadata Display: Compression
# -----------------------------

def makeMetadataCompression1():
    header, directory, tableData, metadata = defaultTestData(metadata=testDataWOFFMetadata)
    metadata = metadata[0], metadata[0]
    diff = header["metaOrigLength"] - header["metaLength"]
    header["length"] += diff
    header["metaLength"] = header["metaOrigLength"]
    data = (padData(packTestHeader(header)
                   + packTestDirectory(directory)
                   + tableData)
            + bytes(packTestMetadata(metadata), "utf-8"))
    return data

makeMetadataCompression1Title = "Metadata No Compression"
makeMetadataCompression1Description = "The metadata is stored in an uncompressed state and therefore does not have the proper compression format."
makeMetadataCompression1Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

def makeMetadataCompression2():
    header, directory, tableData, metadata = defaultTestData(metadata=testDataWOFFMetadata)
    metadata = metadata[0], zlib.compress(bytes(metadata[0], "utf-8"))
    diff = len(metadata[1]) - header["metaLength"]
    header["metaLength"] += diff
    header["length"] += diff
    data = padData(packTestHeader(header) + packTestDirectory(directory) + tableData) + packTestMetadata(metadata)
    return data

makeMetadataCompression2Title = "Metadata Invalid Compression"
makeMetadataCompression2Description = "The metadata is compressed with Gzip and therefore does not have the proper compression format."
makeMetadataCompression2Credits = [dict(title="Khaled Hosny", role="author", link="http://khaledhosny.org")]

# --------------------------------
# Metadata Display: metaOrigLength
# --------------------------------

# <

def makeMetaOrigLengthTest1():
    header, directory, tableData, metadata = defaultTestData(metadata=testDataWOFFMetadata)
    header["metaOrigLength"] += 1
    data = padData(packTestHeader(header) + packTestDirectory(directory) + tableData) + packTestMetadata(metadata)
    return data

makeMetaOrigLengthTest1Title = "Decompressed Metadata Length Less Than metaOrigLength"
makeMetaOrigLengthTest1Description = "The metadata decompresses to a length that is 1 byte smaller than the length defined in metaOrigLength"
makeMetaOrigLengthTest1Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# >

def makeMetaOrigLengthTest2():
    header, directory, tableData, metadata = defaultTestData(metadata=testDataWOFFMetadata)
    header["metaOrigLength"] -= 1
    data = padData(packTestHeader(header) + packTestDirectory(directory) + tableData) + packTestMetadata(metadata)
    return data

makeMetaOrigLengthTest2Title = "Decompressed Metadata Length Greater Than metaOrigLength"
makeMetaOrigLengthTest2Description = "The metadata decompresses to a length that is 1 byte greater than the length defined in metaOrigLength"
makeMetaOrigLengthTest2Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# -----------------------------
# Metadata Display: Well-Formed
# -----------------------------

# <

metadataWellFormed1Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <description>
        <text>
            Text < text.
        </text>
    </description>
</metadata>
"""
metadataWellFormed1Title = "Unescaped < in Content"
metadataWellFormed1Description = "The text element in the description element contains an unescaped <."
metadataWellFormed1Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# &

metadataWellFormed2Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <description>
        <text>
            Text & text.
        </text>
    </description>
</metadata>
"""
metadataWellFormed2Title = "Unescaped & in Content"
metadataWellFormed2Description = "The text element in the description element contains an unescaped &."
metadataWellFormed2Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# mismatched elements

metadataWellFormed3Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <description>
        <text>
            Text.
        </text>
    </mismatch>
</metadata>
"""
metadataWellFormed3Title = "Mismatched Element Tags"
metadataWellFormed3Description = "One element begins with <description> but ends with </mismatch>."
metadataWellFormed3Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# unclosed element

metadataWellFormed4Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <description>
        <text>
            Text.
    </description>
</metadata>
"""
metadataWellFormed4Title = "Unclosed Element Tag"
metadataWellFormed4Description = "The text element element in the description element is not closed."
metadataWellFormed4Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# case mismatch

metadataWellFormed5Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <description>
        <text>
            Text.
        </text>
    </DESCRIPTION>
</metadata>
"""
metadataWellFormed5Title = "Case Mismatch in Element Tags"
metadataWellFormed5Description = "The <description> element is closed with <DESCRIPTION>."
metadataWellFormed5Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# more than one root

metadataWellFormed6Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <description>
        <text>
            Text.
        </text>
    </description>
</metadata>
<metadata version="1.0">
    <description>
        <text>
            Text.
        </text>
    </description>
</metadata>
"""
metadataWellFormed6Title = "More Than One Root Element"
metadataWellFormed6Description = "The metadata root element occurs twice."
metadataWellFormed6Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# unknown encoding

metadataWellFormed7Metadata = """
<?xml version="1.0" encoding="VSCACS-GFV-X-CQ34QTAB2Q-IS-NOT-A-VALID-ENCODING"?>
<metadata version="1.0">
    <description>
        <text>
            Text.
        </text>
    </description>
</metadata>
"""
metadataWellFormed7Title = "Unknown Encoding"
metadataWellFormed7Description = "The xml encoding is set to 'VSCACS-GFV-X-CQ34QTAB2Q-IS-NOT-A-VALID-ENCODING'."
metadataWellFormed7Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# --------------------------
# Metadata Display: Encoding
# --------------------------

# UTF-8

metadataEncoding1Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <uniqueid id="org.w3.webfonts.wofftest" />
</metadata>
"""
metadataEncoding1Title = "UTF-8 Encoding"
metadataEncoding1Description = "The xml encoding is set to UTF-8."
metadataEncoding1Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# Invalid

metadataEncoding2Metadata = """
<?xml version="1.0" encoding="UTF-16"?>
<metadata version="1.0">
    <uniqueid id="org.w3.webfonts.wofftest" />
</metadata>
""".strip().replace("    ", "\t").encode("utf-16")
if metadataEncoding2Metadata.startswith(codecs.BOM_UTF16):
    metadataEncoding2Metadata = metadataEncoding2Metadata.replace(codecs.BOM_UTF16, b"")
metadataEncoding2Title = "Invalid Encoding: UTF-16"
metadataEncoding2Description = "The xml encoding is set to UTF-16."
metadataEncoding2Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

metadataEncoding3Metadata = """
<?xml version="1.0" encoding="ISO-8859-1"?>
<metadata version="1.0">
    <uniqueid id="org.w3.webfonts.wofftest" />
</metadata>
"""
metadataEncoding3Title = "Invalid Encoding: ISO-8859-1"
metadataEncoding3Description = "The xml encoding is set to ISO-8859-1."
metadataEncoding3Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# no encoding

metadataEncoding4Metadata = """
<?xml version="1.0"?>
<metadata version="1.0">
    <uniqueid id="org.w3.webfonts.wofftest" />
</metadata>
"""
metadataEncoding4Title = "Implied UTF-8"
metadataEncoding4Description = "The xml encoding is not declared and there is no BOM."
metadataEncoding4Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# UTF-8 BOM

metadataEncoding5Metadata = """
%s<?xml version="1.0"?>
<metadata version="1.0">
    <uniqueid id="org.w3.webfonts.wofftest" />
</metadata>
""" % codecs.BOM_UTF8
metadataEncoding5Title = "UTF-8 BOM"
metadataEncoding5Description = "The xml encoding is not declared and there is a UTF-8 BOM."
metadataEncoding5Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# UTF-16 BOM

metadataEncoding6Metadata = """
<?xml version="1.0"?>
<metadata version="1.0">
    <uniqueid id="org.w3.webfonts.wofftest" />
</metadata>
""".strip().replace("    ", "\t").encode("utf-16")
assert metadataEncoding6Metadata.startswith(codecs.BOM_UTF16)
metadataEncoding6Title = "Invalid Encoding: UTF-8 BOM"
metadataEncoding6Description = "The xml encoding is not declared and there is a UTF-16 BOM."
metadataEncoding6Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# -------------------------------------------
# Metadata Display: Schema Validity: metadata
# -------------------------------------------

# valid

metadataSchemaMetadata1Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <uniqueid id="org.w3.webfonts.wofftest" />
</metadata>
"""
metadataSchemaMetadata1Title = "Valid metadata Element"
metadataSchemaMetadata1Description = "The metadata element matches the schema."
metadataSchemaMetadata1Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# top element is not metadata

metadataSchemaMetadata2Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<INVALID version="1.0">
    <uniqueid id="org.w3.webfonts.wofftest" />
</INVALID>
"""
metadataSchemaMetadata2Title = "Top element is Not metadata"
metadataSchemaMetadata2Description = "The top element is \"INVALID\" instead of \"metadata\"."
metadataSchemaMetadata2Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# missing version

metadataSchemaMetadata3Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata>
    <uniqueid id="org.w3.webfonts.wofftest" />
</metadata>
"""
metadataSchemaMetadata3Title = "No version Attribute in metadata Element"
metadataSchemaMetadata3Description = "The metadata element does not contain the required version attribute."
metadataSchemaMetadata3Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# invalid version

metadataSchemaMetadata4Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="ABC">
    <uniqueid id="org.w3.webfonts.wofftest" />
</metadata>
"""
metadataSchemaMetadata4Title = "Invalid version Attribute Value in metadata Element"
metadataSchemaMetadata4Description = "The metadata element version attribute is set to 'ABC'."
metadataSchemaMetadata4Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# unknown attribute

metadataSchemaMetadata5Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0" unknownattribute="Text">
    <uniqueid id="org.w3.webfonts.wofftest" />
</metadata>
"""
metadataSchemaMetadata5Title = "Unknown Attrbute in metadata Element"
metadataSchemaMetadata5Description = "The metadata element contains an unknown attribute."
metadataSchemaMetadata5Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# unknown element

metadataSchemaMetadata6Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <unknown attribute="Text" />
</metadata>
"""
metadataSchemaMetadata6Title = "Unknown Child Element metadata Element"
metadataSchemaMetadata6Description = "The metadata element contains an unknown child element."
metadataSchemaMetadata6Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# -------------------------------------------
# Metadata Display: Schema Validity: uniqueid
# -------------------------------------------

# valid

metadataSchemaUniqueid1Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <uniqueid id="org.w3.webfonts.wofftest" />
</metadata>
"""
metadataSchemaUniqueid1Title = "Valid uniqueid Element"
metadataSchemaUniqueid1Description = "The uniqueid element matches the schema."
metadataSchemaUniqueid1Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# does not exist

metadataSchemaUniqueid2Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
</metadata>
"""
metadataSchemaUniqueid2Title = "No uniqueid Element"
metadataSchemaUniqueid2Description = "The uniqueid element doesn't exist."
metadataSchemaUniqueid2Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# duplicate

metadataSchemaUniqueid3Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <uniqueid id="org.w3.webfonts.wofftest" />
    <uniqueid id="org.w3.webfonts.wofftest" />
</metadata>
"""
metadataSchemaUniqueid3Title = "More Than One uniqueid Element"
metadataSchemaUniqueid3Description = "The uniqueid element occurs twice."
metadataSchemaUniqueid3Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# missing id attribute

metadataSchemaUniqueid4Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <uniqueid />
</metadata>
"""
metadataSchemaUniqueid4Title = "No id Attribute in uniqueid Element"
metadataSchemaUniqueid4Description = "The uniqueid element does not contain the required id attribute."
metadataSchemaUniqueid4Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# unknown attribute

metadataSchemaUniqueid5Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <uniqueid id="org.w3.webfonts.wofftest" unknownattribute="Text" />
</metadata>
"""
metadataSchemaUniqueid5Title = "Unknown Attribute in uniqueid Element"
metadataSchemaUniqueid5Description = "The uniqueid element contains an unknown attribute."
metadataSchemaUniqueid5Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# unknown child

metadataSchemaUniqueid6Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <uniqueid id="org.w3.webfonts.wofftest">
        <unknown attribute="Text" />
    </uniqueid>
</metadata>
"""
metadataSchemaUniqueid6Title = "Child Element in uniqueid Element"
metadataSchemaUniqueid6Description = "The uniqueid element contains a child element."
metadataSchemaUniqueid6Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# content

metadataSchemaUniqueid7Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <uniqueid id="org.w3.webfonts.wofftest">
        Text
    </uniqueid>
</metadata>
"""
metadataSchemaUniqueid7Title = "Content in uniqueid Element"
metadataSchemaUniqueid7Description = "The uniqueid element contains content."
metadataSchemaUniqueid7Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# -----------------------------------------
# Metadata Display: Schema Validity: vendor
# -----------------------------------------

# valid

metadataSchemaVendor1Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <vendor name="Test Vendor" url="http://w3c.org/Fonts" />
</metadata>
"""
metadataSchemaVendor1Title = "Valid vendor Element"
metadataSchemaVendor1Description = "The vendor element matches the schema."
metadataSchemaVendor1Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

metadataSchemaVendor2Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <vendor name="Test Vendor" />
</metadata>
"""
metadataSchemaVendor2Title = "Valid vendor Element Without url Attribute"
metadataSchemaVendor2Description = "The vendor element does not contain a url attribute but it still matches the schema."
metadataSchemaVendor2Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# does not exist

metadataSchemaVendor3Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
</metadata>
"""
metadataSchemaVendor3Title = "No vendor Element"
metadataSchemaVendor3Description = "The vendor element doesn't exist."
metadataSchemaVendor3Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# duplicate

metadataSchemaVendor4Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <vendor name="Test Vendor" url="http://w3c.org/Fonts" />
    <vendor name="Test Vendor" url="http://w3c.org/Fonts" />
</metadata>
"""
metadataSchemaVendor4Title = "More Than One vendor Element"
metadataSchemaVendor4Description = "The vendor element occurs twice."
metadataSchemaVendor4Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# missing name attribute

metadataSchemaVendor5Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <vendor url="http://w3c.org/Fonts" />
</metadata>
"""
metadataSchemaVendor5Title = "No name Attribute in vendor Element"
metadataSchemaVendor5Description = "The vendor element does not contain the required name attribute."
metadataSchemaVendor5Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# dir attribute

metadataSchemaVendor6Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <vendor name="Test Vendor" url="http://w3c.org/Fonts" dir="ltr" />
</metadata>
"""
metadataSchemaVendor6Title = "Valid dir Attribute in vendor Element 1"
metadataSchemaVendor6Description = "The vendor element contains ltr as the value for the dir attribute."
metadataSchemaVendor6Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

metadataSchemaVendor7Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <vendor name="Test Vendor" url="http://w3c.org/Fonts" dir="rtl" />
</metadata>
"""
metadataSchemaVendor7Title = "Valid dir Attribute in vendor Element 2"
metadataSchemaVendor7Description = "The vendor element contains rtl as the value for the dir attribute."
metadataSchemaVendor7Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

metadataSchemaVendor8Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <vendor name="Test Vendor" url="http://w3c.org/Fonts" dir="INVALID" />
</metadata>
"""
metadataSchemaVendor8Title = "Invalid dir Attribute in vendor Element"
metadataSchemaVendor8Description = "The vendor element contains INVALID as the value for the dir attribute."
metadataSchemaVendor8Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# class attribute

metadataSchemaVendor9Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <vendor name="Test Vendor" url="http://w3c.org/Fonts" class="class1 class2 class3" />
</metadata>
"""
metadataSchemaVendor9Title = "Valid class Attribute in vendor Element"
metadataSchemaVendor9Description = "The vendor element contains \"class1 class2 class3\" as the value for the class attribute."
metadataSchemaVendor9Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# unknown attribute

metadataSchemaVendor10Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <vendor name="Test Vendor" url="http://w3c.org/Fonts" unknownattribute="Text" />
</metadata>
"""
metadataSchemaVendor10Title = "Unknown Attribute in vendor Element"
metadataSchemaVendor10Description = "The vendor element contains an unknown attribute."
metadataSchemaVendor10Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# unknown child

metadataSchemaVendor11Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <vendor name="Test Vendor" url="http://w3c.org/Fonts">
        <unknown attribute="Text" />
    </vendor>
</metadata>
"""
metadataSchemaVendor11Title = "Child Element in vendor Element"
metadataSchemaVendor11Description = "The vendor element contains a child element."
metadataSchemaVendor11Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# content

metadataSchemaVendor12Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <vendor name="Test Vendor" url="http://w3c.org/Fonts">
        Text
    </vendor>
</metadata>
"""
metadataSchemaVendor12Title = "Content in vendor Element"
metadataSchemaVendor12Description = "The vendor element contains content."
metadataSchemaVendor12Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# ------------------------------------------
# Metadata Display: Schema Validity: credits
# ------------------------------------------

# valid - single credit element

metadataSchemaCredits1Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <credits>
        <credit name="Credit 1" role="Role 1" url="http://w3c.org/Fonts" />
    </credits>
</metadata>
"""
metadataSchemaCredits1Title = "Valid credits Element With No Language Attribute And A Single credit Element"
metadataSchemaCredits1Description = "The credits element matches the schema and it contains one credit child element."
metadataSchemaCredits1Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# valid - multiple credit elements

metadataSchemaCredits2Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <credits>
        <credit name="Credit 1" role="Role 1" url="http://w3c.org/Fonts" />
        <credit name="Credit 2" role="Role 2" url="http://w3c.org/Fonts" />
    </credits>
</metadata>
"""
metadataSchemaCredits2Title = "Valid credits Element With Two credit Elements"
metadataSchemaCredits2Description = "The credits element matches the schema and it contains two credit child elements."
metadataSchemaCredits2Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# missing credit element

metadataSchemaCredits3Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <credits />
</metadata>
"""
metadataSchemaCredits3Title = "No credit Element in credits Element"
metadataSchemaCredits3Description = "The credits element does not contain a credit child element."
metadataSchemaCredits3Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# unknown attribute

metadataSchemaCredits4Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <credits unknownattribute="Text">
        <credit name="Credit 1" role="Role 1" url="http://w3c.org/Fonts" />
    </credits>
</metadata>
"""
metadataSchemaCredits4Title = "Unknown Attribute in credits Element"
metadataSchemaCredits4Description = "The credits element contains an unknown attribute."
metadataSchemaCredits4Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# unknown element

metadataSchemaCredits5Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <credits>
        <credit name="Credit 1" role="Role 1" url="http://w3c.org/Fonts" />
        <unknown attribute="Text" />
    </credits>
</metadata>
"""
metadataSchemaCredits5Title = "Unknown Child Element in credits Element"
metadataSchemaCredits5Description = "The credits element contains an unknown child element."
metadataSchemaCredits5Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# content

metadataSchemaCredits6Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <credits>
        Text
        <credit name="Credit 1" role="Role 1" url="http://w3c.org/Fonts" />
    </credits>
</metadata>
"""
metadataSchemaCredits6Title = "Content in credits Element"
metadataSchemaCredits6Description = "The credits element contains an content."
metadataSchemaCredits6Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# more than one credits element

metadataSchemaCredits7Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <credits>
        <credit name="Credit 1" role="Role 1" url="http://w3c.org/Fonts" />
    </credits>
    <credits>
        <credit name="Credit 2" role="Role 2" url="http://w3c.org/Fonts" />
    </credits>
</metadata>
"""
metadataSchemaCredits7Title = "Multiple credits Elements"
metadataSchemaCredits7Description = "The credits element occurs more than once."
metadataSchemaCredits7Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# -----------------------------------------
# Metadata Display: Schema Validity: credit
# -----------------------------------------

# valid

metadataSchemaCredit1Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <credits>
        <credit name="Credit 1" role="Role 1" url="http://w3c.org/Fonts" />
    </credits>
</metadata>
"""
metadataSchemaCredit1Title = "Valid credit Element"
metadataSchemaCredit1Description = "The credit element matches the schema."
metadataSchemaCredit1Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# valid no url

metadataSchemaCredit2Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <credits>
        <credit name="Credit 1" role="Role 1" />
    </credits>
</metadata>
"""
metadataSchemaCredit2Title = "Valid credit Element Without url Attribute"
metadataSchemaCredit2Description = "The credit element does not contain a url attribute but it still matches the schema."
metadataSchemaCredit2Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# valid no role

metadataSchemaCredit3Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <credits>
        <credit name="Credit 1" url="http://w3c.org/Fonts" />
    </credits>
</metadata>
"""
metadataSchemaCredit3Title = "Valid credit Element Without role Attribute"
metadataSchemaCredit3Description = "The credit element does not contain a role attribute but it still matches the schema."
metadataSchemaCredit3Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# no name

metadataSchemaCredit4Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <credits>
        <credit role="Role 1" url="http://w3c.org/Fonts" />
    </credits>
</metadata>
"""
metadataSchemaCredit4Title = "No name attribute in credit Element"
metadataSchemaCredit4Description = "The credit element does not contain a name attribute."
metadataSchemaCredit4Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# dir attribute

metadataSchemaCredit5Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <credits>
        <credit name="Credit 1" role="Role 1" url="http://w3c.org/Fonts" dir="ltr" />
    </credits>
</metadata>
"""
metadataSchemaCredit5Title = "Valid dir Attribute in credit Element 1"
metadataSchemaCredit5Description = "The credit element contains ltr as the value for the dir attribute."
metadataSchemaCredit5Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

metadataSchemaCredit6Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <credits>
        <credit name="Credit 1" role="Role 1" url="http://w3c.org/Fonts" dir="rtl" />
    </credits>
</metadata>
"""
metadataSchemaCredit6Title = "Valid dir Attribute in credit Element 2"
metadataSchemaCredit6Description = "The credit element contains rtl as the value for the dir attribute."
metadataSchemaCredit6Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

metadataSchemaCredit7Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <credits>
        <credit name="Credit 1" role="Role 1" url="http://w3c.org/Fonts" dir="INVALID" />
    </credits>
</metadata>
"""
metadataSchemaCredit7Title = "Invalid dir Attribute in credit Element"
metadataSchemaCredit7Description = "The credit element contains INVALID as the value for the dir attribute."
metadataSchemaCredit7Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# class attribute

metadataSchemaCredit8Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <credits>
        <credit name="Credit 1" role="Role 1" url="http://w3c.org/Fonts" class="class1 class2 class3" />
    </credits>
</metadata>
"""
metadataSchemaCredit8Title = "Valid class Attribute in credit Element"
metadataSchemaCredit8Description = "The credit element contains \"class1 class2 class3\" as the value for the class attribute."
metadataSchemaCredit8Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# unknown attribute

metadataSchemaCredit9Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <credits>
        <credit name="Credit 1" role="Role 1" url="http://w3c.org/Fonts" unknownattribute="Test" />
    </credits>
</metadata>
"""
metadataSchemaCredit9Title = "Unknown attribute in credit Element"
metadataSchemaCredit9Description = "The credit element contains an unknown attribute."
metadataSchemaCredit9Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# child element

metadataSchemaCredit10Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <credits>
        <credit name="Credit 1" role="Role 1" url="http://w3c.org/Fonts">
            <unknown attribute="Text" />
        </credit>
    </credits>
</metadata>
"""
metadataSchemaCredit10Title = "Child Element in credit Element"
metadataSchemaCredit10Description = "The credit element contains a child element."
metadataSchemaCredit10Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# content

metadataSchemaCredit11Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <credits>
        <credit name="Credit 1" role="Role 1" url="http://w3c.org/Fonts">
            Text
        </credit>
    </credits>
</metadata>
"""
metadataSchemaCredit11Title = "Content in credit Element"
metadataSchemaCredit11Description = "The credit element contains content."
metadataSchemaCredit11Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# ----------------------------------------------
# Metadata Display: Schema Validity: description
# ----------------------------------------------

# valid with url

metadataSchemaDescription1Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <description url="http://w3c.org/Fonts">
        <text>
            Description without language.
        </text>
    </description>
</metadata>
"""
metadataSchemaDescription1Title = "Valid description Element"
metadataSchemaDescription1Description = "The description element matches the schema."
metadataSchemaDescription1Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# valid without url

metadataSchemaDescription2Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <description>
        <text>
            Description without language.
        </text>
    </description>
</metadata>
"""
metadataSchemaDescription2Title = "Valid description Element Without url Attribute"
metadataSchemaDescription2Description = "The description element does not contain a url attribute but it still matches the schema."
metadataSchemaDescription2Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# valid one text element no language

metadataSchemaDescription3Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <description url="http://w3c.org/Fonts">
        <text>
            Description without language.
        </text>
    </description>
</metadata>
"""
metadataSchemaDescription3Title = "Valid description Element With One No Language Tagged text Element"
metadataSchemaDescription3Description = "The description element matches the schema. It contains one text element that does not have a language tag."
metadataSchemaDescription3Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# valid one text element with language

metadataSchemaDescription4Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <description url="http://w3c.org/Fonts">
        <text xml:lang="en">
            Description with "en" language.
        </text>
    </description>
</metadata>
"""
metadataSchemaDescription4Title = "Valid description Element With One Language Tagged text Element"
metadataSchemaDescription4Description = "The description element matches the schema. It contains one text element that has a language tag."
metadataSchemaDescription4Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# valid one text element with language using lang

metadataSchemaDescription5Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <description url="http://w3c.org/Fonts">
        <text lang="en">
            Description with "en" language.
        </text>
    </description>
</metadata>
"""
metadataSchemaDescription5Title = "Valid description Element With One Language Tagged (using lang) text Element"
metadataSchemaDescription5Description = "The description element matches the schema. It contains one text element that has a language tag using the lang tag instead of xml:lang."
metadataSchemaDescription5Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# valid two text elements no language and language

metadataSchemaDescription6Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <description url="http://w3c.org/Fonts">
        <text>
            Description without language.
        </text>
        <text xml:lang="en">
            Description with "en" language.
        </text>
    </description>
</metadata>
"""
metadataSchemaDescription6Title = "Valid description Element With Mixed text Element Language Tags 1"
metadataSchemaDescription6Description = "The description element matches the schema. One text element does not have a language tag. One text element has a language tag."
metadataSchemaDescription6Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# valid two text elements language and language

metadataSchemaDescription7Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <description url="http://w3c.org/Fonts">
        <text xml:lang="en">
            Description with "en" language.
        </text>
        <text xml:lang="fr">
            Description with "fr" language.
        </text>
    </description>
</metadata>
"""
metadataSchemaDescription7Title = "Valid description Element With Mixed text Element Language Tags 2"
metadataSchemaDescription7Description = "The description element matches the schema. Two text elements have a language tags."
metadataSchemaDescription7Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# more than one description

metadataSchemaDescription8Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <description url="http://w3c.org/Fonts">
        <text>
            Description without language.
        </text>
    </description>
    <description url="http://w3c.org/Fonts">
        <text>
            Description without language.
        </text>
    </description>
</metadata>
"""
metadataSchemaDescription8Title = "More Than One description Element"
metadataSchemaDescription8Description = "The description element occurs more than once."
metadataSchemaDescription8Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# no text element

metadataSchemaDescription9Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <description url="http://w3c.org/Fonts" />
</metadata>
"""
metadataSchemaDescription9Title = "No text Element in description Element"
metadataSchemaDescription9Description = "The description element does not contain a text child element."
metadataSchemaDescription9Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# unknown attribute

metadataSchemaDescription10Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <description url="http://w3c.org/Fonts" unknownattribute="Text">
        <text>
            Description without language.
        </text>
    </description>
</metadata>
"""
metadataSchemaDescription10Title = "Unknown Attribute in description Element"
metadataSchemaDescription10Description = "The description element contains an unknown attribute."
metadataSchemaDescription10Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# unknown child element

metadataSchemaDescription11Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <description url="http://w3c.org/Fonts">
        <text>
            Description without language.
        </text>
        <unknown attribute="Text" />
    </description>
</metadata>
"""
metadataSchemaDescription11Title = "Unknown Child Element in description Element"
metadataSchemaDescription11Description = "The description element contains an unknown child element."
metadataSchemaDescription11Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# content

metadataSchemaDescription12Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <description url="http://w3c.org/Fonts">
        Text
        <text>
            Description without language.
        </text>
    </description>
</metadata>
"""
metadataSchemaDescription12Title = "Content in description Element"
metadataSchemaDescription12Description = "The description element contains content."
metadataSchemaDescription12Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# dir attribute

metadataSchemaDescription13Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <description url="http://w3c.org/Fonts">
        <text dir="ltr">
            Description without language.
        </text>
    </description>
</metadata>
"""
metadataSchemaDescription13Title = "Valid description Element With dir Attribute in text Element 1"
metadataSchemaDescription13Description = "The description element contains a text element with ltr as the value for the dir attribute."
metadataSchemaDescription13Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

metadataSchemaDescription14Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <description url="http://w3c.org/Fonts">
        <text dir="rtl">
            Description without language.
        </text>
    </description>
</metadata>
"""
metadataSchemaDescription14Title = "Valid description Element With dir Attribute in text Element 2"
metadataSchemaDescription14Description = "The description element contains a text element with rtl as the value for the dir attribute."
metadataSchemaDescription14Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

metadataSchemaDescription15Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <description url="http://w3c.org/Fonts">
        <text dir="INVALID">
            Description without language.
        </text>
    </description>
</metadata>
"""
metadataSchemaDescription15Title = "Invalid description Element With dir Attribute in text Element"
metadataSchemaDescription15Description = "The description element contains a text element with INVALID as the value for the dir attribute."
metadataSchemaDescription15Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# class attribute

metadataSchemaDescription16Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <description url="http://w3c.org/Fonts">
        <text class="class1 class2 class3">
            Description without language.
        </text>
    </description>
</metadata>
"""
metadataSchemaDescription16Title = "Valid description Element With class Attribute in text Element"
metadataSchemaDescription16Description = "The description element contains a text element with \"class1 class2 class3\" as the value for the class attribute."
metadataSchemaDescription16Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# text element unknown attribute

metadataSchemaDescription17Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <description url="http://w3c.org/Fonts">
        <text unknownattribute="Text">
            Description without language.
        </text>
    </description>
</metadata>
"""
metadataSchemaDescription17Title = "Unknown Attribute in description Element text Element"
metadataSchemaDescription17Description = "The description element contains a text element with an unknown attribute."
metadataSchemaDescription17Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# text element child element

metadataSchemaDescription18Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <description url="http://w3c.org/Fonts">
        <text>
            Description without language.
            <unknown attribute="Text" />
        </text>
    </description>
</metadata>
"""
metadataSchemaDescription18Title = "Unknown Child Element in description Element text Element"
metadataSchemaDescription18Description = "The description element contains a text element with an unknown child element."
metadataSchemaDescription18Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# one div

metadataSchemaDescription19Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <description url="http://w3c.org/Fonts">
        <text>
            <div>Paragraph 1</div>
        </text>
    </description>
</metadata>
"""
metadataSchemaDescription19Title = "Valid description Element With One div Element in text Element"
metadataSchemaDescription19Description = "The description element contains a text element that contains a div element."
metadataSchemaDescription19Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# two div

metadataSchemaDescription20Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <description url="http://w3c.org/Fonts">
        <text>
            <div>Paragraph 1</div>
            <div>Paragraph 2</div>
        </text>
    </description>
</metadata>
"""
metadataSchemaDescription20Title = "Valid description Element With Two div Elements in text Element"
metadataSchemaDescription20Description = "The description element contains a text element that contains two div elements."
metadataSchemaDescription20Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# nested div

metadataSchemaDescription21Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <description url="http://w3c.org/Fonts">
        <text>
            <div>
                div 1 start
                <div>
                    div 2 start
                    <div>
                        div 3
                    </div>
                    div 2 end
                </div>
                div 1 end
            </div>
        </text>
    </description>
</metadata>
"""
metadataSchemaDescription21Title = "Valid description Element With Nested div Elements in text Element"
metadataSchemaDescription21Description = "The description element contains a text element that contains nested div elements."
metadataSchemaDescription21Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# div with dir

metadataSchemaDescription22Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <description url="http://w3c.org/Fonts">
        <text>
            <div dir="ltr">Paragraph 1</div>
        </text>
    </description>
</metadata>
"""
metadataSchemaDescription22Title = "Valid description Element With dir Attribute in div Element in text Element 1"
metadataSchemaDescription22Description = "The description element contains a text element that contains a div element with ltr as the value for the dir attribute."
metadataSchemaDescription22Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

metadataSchemaDescription23Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <description url="http://w3c.org/Fonts">
        <text>
            <div dir="rtl">Paragraph 1</div>
        </text>
    </description>
</metadata>
"""
metadataSchemaDescription23Title = "Valid description Element With dir Attribute in div Element in text Element 2"
metadataSchemaDescription23Description = "The description element contains a text element that contains a div element with rtl as the value for the dir attribute."
metadataSchemaDescription23Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

metadataSchemaDescription24Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <description url="http://w3c.org/Fonts">
        <text>
            <div dir="INVALID">Paragraph 1</div>
        </text>
    </description>
</metadata>
"""
metadataSchemaDescription24Title = "Invalid description Element With dir Attribute in div Element in text Element"
metadataSchemaDescription24Description = "The description element contains a text element that contains a div element with INVALID as the value for the dir attribute."
metadataSchemaDescription24Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# div with class

metadataSchemaDescription25Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <description url="http://w3c.org/Fonts">
        <text>
            <div class="class1 class2 class3">Paragraph 1</div>
        </text>
    </description>
</metadata>
"""
metadataSchemaDescription25Title = "Valid description Element With class Attribute in div Element in text Element"
metadataSchemaDescription25Description = "The description element contains a text element that contains a div element with \"class1 class2 class3\" as the value for the class attribute."
metadataSchemaDescription25Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# one span

metadataSchemaDescription26Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <description url="http://w3c.org/Fonts">
        <text>
            Text with <span>span</span>.
        </text>
    </description>
</metadata>
"""
metadataSchemaDescription26Title = "Valid description Element With One span Element in text Element"
metadataSchemaDescription26Description = "The description element contains a text element that contains a span element."
metadataSchemaDescription26Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# two span

metadataSchemaDescription27Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <description url="http://w3c.org/Fonts">
        <text>
             Text with <span>span 1</span> and <span>span 2</span>.
        </text>
    </description>
</metadata>
"""
metadataSchemaDescription27Title = "Valid description Element With Two span Elements in text Element"
metadataSchemaDescription27Description = "The description element contains a text element that contains two span elements."
metadataSchemaDescription27Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

metadataSchemaDescription28Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <description url="http://w3c.org/Fonts">
        <text>
             <span>
                 span 1 start
                 <span>
                     span 2 start
                     <span>
                         span 3
                     </span>
                     span 2 end
                 </span>
                 span 1 end
             </span>
        </text>
    </description>
</metadata>
"""
metadataSchemaDescription28Title = "Valid description Element With Nested span Elements in text Element"
metadataSchemaDescription28Description = "The description element contains a text element that contains nested span elements."
metadataSchemaDescription28Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# span with dir

metadataSchemaDescription29Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <description url="http://w3c.org/Fonts">
        <text>
            Text with <span dir="ltr">span</span>.
        </text>
    </description>
</metadata>
"""
metadataSchemaDescription29Title = "Valid description Element With dir Attribute in span Element in text Element 1"
metadataSchemaDescription29Description = "The description element contains a text element that contains a span element with ltr as the value for the dir attribute."
metadataSchemaDescription29Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

metadataSchemaDescription30Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <description url="http://w3c.org/Fonts">
        <text>
            Text with <span dir="rtl">span</span>.
        </text>
    </description>
</metadata>
"""
metadataSchemaDescription30Title = "Valid description Element With dir Attribute in span Element in text Element 2"
metadataSchemaDescription30Description = "The description element contains a text element that contains a span element with rtl as the value for the dir attribute."
metadataSchemaDescription30Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

metadataSchemaDescription31Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <description url="http://w3c.org/Fonts">
        <text>
            Text with <span dir="INVALID">span</span>.
        </text>
    </description>
</metadata>
"""
metadataSchemaDescription31Title = "Invalid description Element With dir Attribute in span Element in text Element"
metadataSchemaDescription31Description = "The description element contains a text element that contains a span element with INVALID as the value for the dir attribute."
metadataSchemaDescription31Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# span with class

metadataSchemaDescription32Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <description url="http://w3c.org/Fonts">
        <text>
            Text with <span class="class1 class2 class3">span</span>.
        </text>
    </description>
</metadata>
"""
metadataSchemaDescription32Title = "Valid description Element With class Attribute in span Element in text Element"
metadataSchemaDescription32Description = "The description element contains a text element that contains a span element with \"class1 class2 class3\" as the value for the class attribute."
metadataSchemaDescription32Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# ------------------------------------------
# Metadata Display: Schema Validity: license
# ------------------------------------------

# valid with url and license

metadataSchemaLicense1Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <license url="http://w3c.org/Fonts" id="License ID">
        <text>
            License without language.
        </text>
    </license>
</metadata>
"""
metadataSchemaLicense1Title = "Valid license Element"
metadataSchemaLicense1Description = "The license element matches the schema."
metadataSchemaLicense1Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# valid no url

metadataSchemaLicense2Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <license id="License ID">
        <text>
            License without language.
        </text>
    </license>
</metadata>
"""
metadataSchemaLicense2Title = "Valid license Element Without url Attribute"
metadataSchemaLicense2Description = "The license element does not have a url attribute but it still matches the schema."
metadataSchemaLicense2Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# valid no id

metadataSchemaLicense3Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <license url="http://w3c.org/Fonts">
        <text>
            License without language.
        </text>
    </license>
</metadata>
"""
metadataSchemaLicense3Title = "Valid license Element Without id Attribute"
metadataSchemaLicense3Description = "The license element does not have an id attribute but it still matches the schema."
metadataSchemaLicense3Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# valid one text element no language

metadataSchemaLicense4Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <license url="http://w3c.org/Fonts" id="License ID">
        <text>
            License without language.
        </text>
    </license>
</metadata>
"""
metadataSchemaLicense4Title = "Valid license Element With One No Language Tagged text Element"
metadataSchemaLicense4Description = "The license element matches the schema. It contains one text element that does not have a language tag."
metadataSchemaLicense4Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# valid one text element with language

metadataSchemaLicense5Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <license url="http://w3c.org/Fonts" id="License ID">
        <text xml:lang="en">
            License with "en" language.
        </text>
    </license>
</metadata>
"""
metadataSchemaLicense5Title = "Valid license Element With One Language Tagged text Element"
metadataSchemaLicense5Description = "The license element matches the schema. It contains one text element that has a language tag."
metadataSchemaLicense5Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# valid one text element with language

metadataSchemaLicense6Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <license url="http://w3c.org/Fonts" id="License ID">
        <text lang="en">
            License with "en" language.
        </text>
    </license>
</metadata>
"""
metadataSchemaLicense6Title = "Valid license Element With One Language Tagged (using lang) text Element"
metadataSchemaLicense6Description = "The license element matches the schema. It contains one text element that has a language tag using the lang tag instead of xml:lang."
metadataSchemaLicense6Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# valid two text elements no language and language

metadataSchemaLicense7Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <license url="http://w3c.org/Fonts" id="License ID">
        <text>
            License without language.
        </text>
        <text xml:lang="en">
            License with "en" language.
        </text>
    </license>
</metadata>
"""
metadataSchemaLicense7Title = "Valid license Element With Mixed text Element Language Tags 1"
metadataSchemaLicense7Description = "The license element matches the schema. One text element does not have a language tag. One text element has a language tag."
metadataSchemaLicense7Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# valid two text elements language and language

metadataSchemaLicense8Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <license url="http://w3c.org/Fonts" id="License ID">
        <text xml:lang="en">
            License with "en" language.
        </text>
        <text xml:lang="fr">
            License with "fr" language.
        </text>
    </license>
</metadata>
"""
metadataSchemaLicense8Title = "Valid license Element With Mixed text Element Language Tags 2"
metadataSchemaLicense8Description = "The license element matches the schema. Two text elements have a language tags."
metadataSchemaLicense8Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# more than one license

metadataSchemaLicense9Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <license url="http://w3c.org/Fonts" id="License ID">
        <text>
            License without language.
        </text>
    </license>
    <license url="http://w3c.org/Fonts">
        <text>
            License without language.
        </text>
    </license>
</metadata>
"""
metadataSchemaLicense9Title = "More Than One license Element"
metadataSchemaLicense9Description = "The license element occurs more than once."
metadataSchemaLicense9Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# no text element

metadataSchemaLicense10Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <license url="http://w3c.org/Fonts" id="License ID" />
</metadata>
"""
metadataSchemaLicense10Title = "No text Element in license Element"
metadataSchemaLicense10Description = "The license element does not contain a text child element."
metadataSchemaLicense10Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# unknown attribute

metadataSchemaLicense11Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <license url="http://w3c.org/Fonts" id="License ID" unknownattribute="Text">
        <text>
            License without language.
        </text>
    </license>
</metadata>
"""
metadataSchemaLicense11Title = "Unknown Attribute in license Element"
metadataSchemaLicense11Description = "The license element contains an unknown attribute."
metadataSchemaLicense11Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# unknown child element

metadataSchemaLicense12Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <license url="http://w3c.org/Fonts" id="License ID">
        <text>
            License without language.
        </text>
        <unknown attribute="Text" />
    </license>
</metadata>
"""
metadataSchemaLicense12Title = "Unknown Child Element in license Element"
metadataSchemaLicense12Description = "The license element contains an unknown child element."
metadataSchemaLicense12Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# content

metadataSchemaLicense13Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <license url="http://w3c.org/Fonts" id="License ID">
        Text
        <text>
            License without language.
        </text>
    </license>
</metadata>
"""
metadataSchemaLicense13Title = "Content in license Element"
metadataSchemaLicense13Description = "The license element contains content."
metadataSchemaLicense13Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# dir attribute

metadataSchemaLicense14Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <license url="http://w3c.org/Fonts">
        <text dir="ltr">
            License without language.
        </text>
    </license>
</metadata>
"""
metadataSchemaLicense14Title = "Valid license Element With dir Attribute in text Element 1"
metadataSchemaLicense14Description = "The license element contains a text element with ltr as the value for the dir attribute."
metadataSchemaLicense14Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

metadataSchemaLicense15Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <license url="http://w3c.org/Fonts">
        <text dir="rtl">
            License without language.
        </text>
    </license>
</metadata>
"""
metadataSchemaLicense15Title = "Valid license Element With dir Attribute in text Element 2"
metadataSchemaLicense15Description = "The license element contains a text element with rtl as the value for the dir attribute."
metadataSchemaLicense15Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

metadataSchemaLicense16Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <license url="http://w3c.org/Fonts">
        <text dir="INVALID">
            License without language.
        </text>
    </license>
</metadata>
"""
metadataSchemaLicense16Title = "Invalid license Element With dir Attribute in text Element"
metadataSchemaLicense16Description = "The license element contains a text element with INVALID as the value for the dir attribute."
metadataSchemaLicense16Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# class attribute

metadataSchemaLicense17Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <license url="http://w3c.org/Fonts">
        <text class="class1 class2 class3">
            License without language.
        </text>
    </license>
</metadata>
"""
metadataSchemaLicense17Title = "Valid license Element With class Attribute in text Element"
metadataSchemaLicense17Description = "The license element contains a text element with \"class1 class2 class3\" as the value for the class attribute."
metadataSchemaLicense17Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# text element unknown attribute

metadataSchemaLicense18Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <license url="http://w3c.org/Fonts" id="License ID">
        <text unknownattribute="Text">
            License without language.
        </text>
    </license>
</metadata>
"""
metadataSchemaLicense18Title = "Unknown Attribute in license Element text Element"
metadataSchemaLicense18Description = "The license element contains a text element with an unknown attribute."
metadataSchemaLicense18Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# text element child element

metadataSchemaLicense19Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <license url="http://w3c.org/Fonts" id="License ID">
        <text>
            License without language.
            <unknown attribute="Text" />
        </text>
    </license>
</metadata>
"""
metadataSchemaLicense19Title = "Unknown Child Element in license Element text Element"
metadataSchemaLicense19Description = "The license element contains a text element with an unknown child element."
metadataSchemaLicense19Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# one div

metadataSchemaLicense20Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <license url="http://w3c.org/Fonts">
        <text>
            <div>Paragraph 1</div>
        </text>
    </license>
</metadata>
"""
metadataSchemaLicense20Title = "Valid license Element With One div Element in text Element"
metadataSchemaLicense20Description = "The license element contains a text element that contains a div element."
metadataSchemaLicense20Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# two div

metadataSchemaLicense21Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <license url="http://w3c.org/Fonts">
        <text>
            <div>Paragraph 1</div>
            <div>Paragraph 2</div>
        </text>
    </license>
</metadata>
"""
metadataSchemaLicense21Title = "Valid license Element With Two div Elements in text Element"
metadataSchemaLicense21Description = "The license element contains a text element that contains two div elements."
metadataSchemaLicense21Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# nested div

metadataSchemaLicense22Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <license url="http://w3c.org/Fonts">
        <text>
            <div>
                div 1 start
                <div>
                    div 2 start
                    <div>
                        div 3
                    </div>
                    div 2 end
                </div>
                div 1 end
            </div>
        </text>
    </license>
</metadata>
"""
metadataSchemaLicense22Title = "Valid license Element With Nested div Elements in text Element"
metadataSchemaLicense22Description = "The license element contains a text element that contains nested div elements."
metadataSchemaLicense22Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# div with dir

metadataSchemaLicense23Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <license url="http://w3c.org/Fonts">
        <text>
            <div dir="ltr">Paragraph 1</div>
        </text>
    </license>
</metadata>
"""
metadataSchemaLicense23Title = "Valid license Element With dir Attribute in div Element in text Element 1"
metadataSchemaLicense23Description = "The license element contains a text element that contains a div element with ltr as the value for the dir attribute."
metadataSchemaLicense23Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

metadataSchemaLicense24Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <license url="http://w3c.org/Fonts">
        <text>
            <div dir="rtl">Paragraph 1</div>
        </text>
    </license>
</metadata>
"""
metadataSchemaLicense24Title = "Valid license Element With dir Attribute in div Element in text Element 2"
metadataSchemaLicense24Description = "The license element contains a text element that contains a div element with rtl as the value for the dir attribute."
metadataSchemaLicense24Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

metadataSchemaLicense25Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <license url="http://w3c.org/Fonts">
        <text>
            <div dir="INVALID">Paragraph 1</div>
        </text>
    </license>
</metadata>
"""
metadataSchemaLicense25Title = "Invalid license Element With dir Attribute in div Element in text Element"
metadataSchemaLicense25Description = "The license element contains a text element that contains a div element with INVALID as the value for the dir attribute."
metadataSchemaLicense25Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# div with class

metadataSchemaLicense26Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <license url="http://w3c.org/Fonts">
        <text>
            <div class="class1 class2 class3">Paragraph 1</div>
        </text>
    </license>
</metadata>
"""
metadataSchemaLicense26Title = "Valid license Element With class Attribute in div Element in text Element"
metadataSchemaLicense26Description = "The license element contains a text element that contains a div element with \"class1 class2 class3\" as the value for the class attribute."
metadataSchemaLicense26Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# one span

metadataSchemaLicense27Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <license url="http://w3c.org/Fonts">
        <text>
            Text with <span>span</span>.
        </text>
    </license>
</metadata>
"""
metadataSchemaLicense27Title = "Valid license Element With One span Element in text Element"
metadataSchemaLicense27Description = "The license element contains a text element that contains a span element."
metadataSchemaLicense27Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# two span

metadataSchemaLicense28Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <license url="http://w3c.org/Fonts">
        <text>
             Text with <span>span 1</span> and <span>span 2</span>.
        </text>
    </license>
</metadata>
"""
metadataSchemaLicense28Title = "Valid license Element With Two span Elements in text Element"
metadataSchemaLicense28Description = "The license element contains a text element that contains two span elements."
metadataSchemaLicense28Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# nested span

metadataSchemaLicense29Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <license url="http://w3c.org/Fonts">
        <text>
             <span>
                 span 1 start
                 <span>
                     span 2 start
                     <span>
                         span 3
                     </span>
                     span 2 end
                 </span>
                 span 1 end
             </span>
        </text>
    </license>
</metadata>
"""
metadataSchemaLicense29Title = "Valid license Element With Nested span Elements in text Element"
metadataSchemaLicense29Description = "The license element contains a text element that contains nested span elements."
metadataSchemaLicense29Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# span with dir

metadataSchemaLicense30Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <license url="http://w3c.org/Fonts">
        <text>
            Text with <span dir="ltr">span</span>.
        </text>
    </license>
</metadata>
"""
metadataSchemaLicense30Title = "Valid license Element With dir Attribute in span Element in text Element 1"
metadataSchemaLicense30Description = "The license element contains a text element that contains a span element with ltr as the value for the dir attribute."
metadataSchemaLicense30Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

metadataSchemaLicense31Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <license url="http://w3c.org/Fonts">
        <text>
            Text with <span dir="rtl">span</span>.
        </text>
    </license>
</metadata>
"""
metadataSchemaLicense31Title = "Valid license Element With dir Attribute in span Element in text Element 2"
metadataSchemaLicense31Description = "The license element contains a text element that contains a span element with rtl as the value for the dir attribute."
metadataSchemaLicense31Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

metadataSchemaLicense32Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <license url="http://w3c.org/Fonts">
        <text>
            Text with <span dir="INVALID">span</span>.
        </text>
    </license>
</metadata>
"""
metadataSchemaLicense32Title = "Invalid license Element With dir Attribute in span Element in text Element"
metadataSchemaLicense32Description = "The license element contains a text element that contains a span element with INVALID as the value for the dir attribute."
metadataSchemaLicense32Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# span with class

metadataSchemaLicense33Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <license url="http://w3c.org/Fonts">
        <text>
            Text with <span class="class1 class2 class3">span</span>.
        </text>
    </license>
</metadata>
"""
metadataSchemaLicense33Title = "Valid license Element With class Attribute in span Element in text Element"
metadataSchemaLicense33Description = "The license element contains a text element that contains a span element with \"class1 class2 class3\" as the value for the class attribute."
metadataSchemaLicense33Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# --------------------------------------------
# Metadata Display: Schema Validity: copyright
# --------------------------------------------

# valid one text element no language

metadataSchemaCopyright1Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <copyright>
        <text>
            Copyright without language.
        </text>
    </copyright>
</metadata>
"""
metadataSchemaCopyright1Title = "Valid copyright Element With One No Language Tagged text Element"
metadataSchemaCopyright1Description = "The copyright element matches the schema. It contains one text element that does not have a language tag."
metadataSchemaCopyright1Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# valid one text element with language

metadataSchemaCopyright2Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <copyright>
        <text xml:lang="en">
            Copyright with "en" language.
        </text>
    </copyright>
</metadata>
"""
metadataSchemaCopyright2Title = "Valid copyright Element With One Language Tagged text Element"
metadataSchemaCopyright2Description = "The copyright element matches the schema. It contains one text element that has a language tag."
metadataSchemaCopyright2Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# valid one text element with language using lang

metadataSchemaCopyright3Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <copyright>
        <text lang="en">
            Copyright with "en" language.
        </text>
    </copyright>
</metadata>
"""
metadataSchemaCopyright3Title = "Valid copyright Element With One Language Tagged (using lang) text Element"
metadataSchemaCopyright3Description = "The copyright element matches the schema. It contains one text element that has a language tag using the lang tag instead of xml:lang."
metadataSchemaCopyright3Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# valid two text elements no language and language

metadataSchemaCopyright4Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <copyright>
        <text>
            Copyright without language.
        </text>
        <text xml:lang="en">
            Copyright with "en" language.
        </text>
    </copyright>
</metadata>
"""
metadataSchemaCopyright4Title = "Valid copyright Element With Mixed text Element Language Tags 1"
metadataSchemaCopyright4Description = "The copyright element matches the schema. One text element does not have a language tag. One text element has a language tag."
metadataSchemaCopyright4Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# valid two text elements language and language

metadataSchemaCopyright5Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <copyright>
        <text xml:lang="en">
            Copyright with "en" language.
        </text>
        <text xml:lang="fr">
            Copyright with "fr" language.
        </text>
    </copyright>
</metadata>
"""
metadataSchemaCopyright5Title = "Valid copyright Element With Mixed text Element Language Tags 2"
metadataSchemaCopyright5Description = "The copyright element matches the schema. Two text elements have a language tags."
metadataSchemaCopyright5Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# more than one copyright

metadataSchemaCopyright6Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <copyright>
        <text>
            Copyright without language.
        </text>
    </copyright>
    <copyright>
        <text>
            Copyright without language.
        </text>
    </copyright>
</metadata>
"""
metadataSchemaCopyright6Title = "More Than One copyright Element"
metadataSchemaCopyright6Description = "The copyright element occurs more than once."
metadataSchemaCopyright6Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# no text element

metadataSchemaCopyright7Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <copyright />
</metadata>
"""
metadataSchemaCopyright7Title = "No text Element in copyright Element"
metadataSchemaCopyright7Description = "The copyright element does not contain a text child element."
metadataSchemaCopyright7Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# unknown attribute

metadataSchemaCopyright8Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <copyright unknownattribute="Text">
        <text>
            Copyright without language.
        </text>
    </copyright>
</metadata>
"""
metadataSchemaCopyright8Title = "Unknown Attribute in copyright Element"
metadataSchemaCopyright8Description = "The copyright element contains an unknown attribute."
metadataSchemaCopyright8Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# unknown child element

metadataSchemaCopyright9Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <copyright>
        <text>
            Copyright without language.
        </text>
        <unknown attribute="Text" />
    </copyright>
</metadata>
"""
metadataSchemaCopyright9Title = "Unknown Child Element in copyright Element"
metadataSchemaCopyright9Description = "The copyright element contains an unknown child element."
metadataSchemaCopyright9Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# content

metadataSchemaCopyright10Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <copyright>
        Text
        <text>
            Copyright without language.
        </text>
    </copyright>
</metadata>
"""
metadataSchemaCopyright10Title = "Content in copyright Element"
metadataSchemaCopyright10Description = "The copyright element contains content."
metadataSchemaCopyright10Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# text element with dir attribute

metadataSchemaCopyright11Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <copyright>
        <text dir="ltr">
            Copyright without language.
        </text>
    </copyright>
</metadata>
"""
metadataSchemaCopyright11Title = "Valid copyright Element With dir Attribute in text Element 1"
metadataSchemaCopyright11Description = "The copyright element contains a text element with ltr as the value for the dir attribute."
metadataSchemaCopyright11Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

metadataSchemaCopyright12Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <copyright>
        <text dir="rtl">
            Copyright without language.
        </text>
    </copyright>
</metadata>
"""
metadataSchemaCopyright12Title = "Valid copyright Element With dir Attribute in text Element 2"
metadataSchemaCopyright12Description = "The copyright element contains a text element with rtl as the value for the dir attribute."
metadataSchemaCopyright12Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

metadataSchemaCopyright13Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <copyright>
        <text dir="INVALID">
            Copyright without language.
        </text>
    </copyright>
</metadata>
"""
metadataSchemaCopyright13Title = "Invalid copyright Element With dir Attribute in text Element"
metadataSchemaCopyright13Description = "The copyright element contains a text element with INVALID as the value for the dir attribute."
metadataSchemaCopyright13Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# text element with class attribute

metadataSchemaCopyright14Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <copyright>
        <text class="class 1 class2 class3">
            Copyright without language.
        </text>
    </copyright>
</metadata>
"""
metadataSchemaCopyright14Title = "Valid copyright Element With class Attribute in text Element"
metadataSchemaCopyright14Description = "The copyright element contains a text element with \"class1 class2 class3\" as the value for the class attribute."
metadataSchemaCopyright14Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# text element unknown attribute

metadataSchemaCopyright15Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <copyright>
        <text unknownattribute="Text">
            Copyright without language.
        </text>
    </copyright>
</metadata>
"""
metadataSchemaCopyright15Title = "Unknown Attribute in copyright Element text Element"
metadataSchemaCopyright15Description = "The copyright element contains a text element with an unknown attribute."
metadataSchemaCopyright15Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# text element child element

metadataSchemaCopyright16Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <copyright>
        <text>
            Copyright without language.
            <unknown attribute="Text" />
        </text>
    </copyright>
</metadata>
"""
metadataSchemaCopyright16Title = "Unknown Child Element in copyright Element text Element"
metadataSchemaCopyright16Description = "The copyright element contains a text element with an unknown child element."
metadataSchemaCopyright16Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# one div

metadataSchemaCopyright17Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <copyright>
        <text>
            <div>Paragraph 1</div>
        </text>
    </copyright>
</metadata>
"""
metadataSchemaCopyright17Title = "Valid copyright Element With One div Element in text Element"
metadataSchemaCopyright17Description = "The copyright element contains a text element that contains a div element."
metadataSchemaCopyright17Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# two div

metadataSchemaCopyright18Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <copyright>
        <text>
            <div>Paragraph 1</div>
            <div>Paragraph 2</div>
        </text>
    </copyright>
</metadata>
"""
metadataSchemaCopyright18Title = "Valid copyright Element With Nested div Elements in text Element"
metadataSchemaCopyright18Description = "The copyright element contains a text element that contains nested div elements."
metadataSchemaCopyright18Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# nested div

metadataSchemaCopyright19Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <copyright>
        <text>
            <div>
                div 1 start
                <div>
                    div 2 start
                    <div>
                        div 3
                    </div>
                    div 2 end
                </div>
                div 1 end
            </div>
        </text>
    </copyright>
</metadata>
"""
metadataSchemaCopyright19Title = "Valid copyright Element With Two div Elements in text Element"
metadataSchemaCopyright19Description = "The copyright element contains a text element that contains two div elements."
metadataSchemaCopyright19Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# div with dir

metadataSchemaCopyright20Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <copyright>
        <text>
            <div dir="ltr">Paragraph 1</div>
        </text>
    </copyright>
</metadata>
"""
metadataSchemaCopyright20Title = "Valid copyright Element With dir Attribute in div Element in text Element 1"
metadataSchemaCopyright20Description = "The copyright element contains a text element that contains a div element with ltr as the value for the dir attribute."
metadataSchemaCopyright20Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

metadataSchemaCopyright21Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <copyright>
        <text>
            <div dir="rtl">Paragraph 1</div>
        </text>
    </copyright>
</metadata>
"""
metadataSchemaCopyright21Title = "Valid copyright Element With dir Attribute in div Element in text Element 2"
metadataSchemaCopyright21Description = "The copyright element contains a text element that contains a div element with rtl as the value for the dir attribute."
metadataSchemaCopyright21Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

metadataSchemaCopyright22Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <copyright>
        <text>
            <div dir="INVALID">Paragraph 1</div>
        </text>
    </copyright>
</metadata>
"""
metadataSchemaCopyright22Title = "Invalid copyright Element With dir Attribute in div Element in text Element"
metadataSchemaCopyright22Description = "The copyright element contains a text element that contains a div element with INVALID as the value for the dir attribute."
metadataSchemaCopyright22Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# div with class

metadataSchemaCopyright23Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <copyright>
        <text>
            <div class="class1 class2 class3">Paragraph 1</div>
        </text>
    </copyright>
</metadata>
"""
metadataSchemaCopyright23Title = "Valid copyright Element With class Attribute in div Element in text Element"
metadataSchemaCopyright23Description = "The copyright element contains a text element that contains a div element with \"class1 class2 class3\" as the value for the class attribute."
metadataSchemaCopyright23Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# one span

metadataSchemaCopyright24Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <copyright>
        <text>
            Text with <span>span</span>.
        </text>
    </copyright>
</metadata>
"""
metadataSchemaCopyright24Title = "Valid copyright Element With One span Element in text Element"
metadataSchemaCopyright24Description = "The copyright element contains a text element that contains a span element."
metadataSchemaCopyright24Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# two span

metadataSchemaCopyright25Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <copyright>
        <text>
             Text with <span>span 1</span> and <span>span 2</span>.
        </text>
    </copyright>
</metadata>
"""
metadataSchemaCopyright25Title = "Valid copyright Element With Two span Elements in text Element"
metadataSchemaCopyright25Description = "The copyright element contains a text element that contains two span elements."
metadataSchemaCopyright25Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# nested span

metadataSchemaCopyright26Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <copyright>
        <text>
             <span>
                 span 1 start
                 <span>
                     span 2 start
                     <span>
                         span 3
                     </span>
                     span 2 end
                 </span>
                 span 1 end
             </span>
        </text>
    </copyright>
</metadata>
"""
metadataSchemaCopyright26Title = "Valid copyright Element With Nested span Elements in text Element"
metadataSchemaCopyright26Description = "The copyright element contains a text element that contains nested span elements."
metadataSchemaCopyright26Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# span with dir

metadataSchemaCopyright27Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <copyright>
        <text>
            Text with <span dir="ltr">span</span>.
        </text>
    </copyright>
</metadata>
"""
metadataSchemaCopyright27Title = "Valid copyright Element With dir Attribute in span Element in text Element 1"
metadataSchemaCopyright27Description = "The copyright element contains a text element that contains a span element with ltr as the value for the dir attribute."
metadataSchemaCopyright27Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

metadataSchemaCopyright28Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <copyright>
        <text>
            Text with <span dir="rtl">span</span>.
        </text>
    </copyright>
</metadata>
"""
metadataSchemaCopyright28Title = "Valid copyright Element With dir Attribute in span Element in text Element 2"
metadataSchemaCopyright28Description = "The copyright element contains a text element that contains a span element with rtl as the value for the dir attribute."
metadataSchemaCopyright28Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

metadataSchemaCopyright29Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <copyright>
        <text>
            Text with <span dir="INVALID">span</span>.
        </text>
    </copyright>
</metadata>
"""
metadataSchemaCopyright29Title = "Invalid copyright Element With dir Attribute in span Element in text Element"
metadataSchemaCopyright29Description = "The copyright element contains a text element that contains a span element with INVALID as the value for the dir attribute."
metadataSchemaCopyright29Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# span with class

metadataSchemaCopyright30Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <copyright>
        <text>
            Text with <span class="class1 class2 class3">span</span>.
        </text>
    </copyright>
</metadata>
"""
metadataSchemaCopyright30Title = "Valid copyright Element With class Attribute in span Element in text Element"
metadataSchemaCopyright30Description = "The copyright element contains a text element that contains a span element with \"class1 class2 class3\" as the value for the class attribute."
metadataSchemaCopyright30Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# --------------------------------------------
# Metadata Display: Schema Validity: trademark
# --------------------------------------------

# valid one text element no language

metadataSchemaTrademark1Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <trademark>
        <text>
            Trademark without language.
        </text>
    </trademark>
</metadata>
"""
metadataSchemaTrademark1Title = "Valid trademark Element With One No Language Tagged text Element"
metadataSchemaTrademark1Description = "The trademark element matches the schema. It contains one text element that does not have a language tag."
metadataSchemaTrademark1Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# valid one text element with language

metadataSchemaTrademark2Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <trademark>
        <text xml:lang="en">
            Trademark with "en" language.
        </text>
    </trademark>
</metadata>
"""
metadataSchemaTrademark2Title = "Valid trademark Element With One Language Tagged text Element"
metadataSchemaTrademark2Description = "The trademark element matches the schema. It contains one text element that has a language tag."
metadataSchemaTrademark2Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# valid one text element with language using lang

metadataSchemaTrademark3Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <trademark>
        <text lang="en">
            Trademark with "en" language.
        </text>
    </trademark>
</metadata>
"""
metadataSchemaTrademark3Title = "Valid trademark Element With One Language Tagged (using lang) text Element"
metadataSchemaTrademark3Description = "The trademark element matches the schema. It contains one text element that has a language tag using the lang tag instead of xml:lang."
metadataSchemaTrademark3Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# valid two text elements no language and language

metadataSchemaTrademark4Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <trademark>
        <text>
            Trademark without language.
        </text>
        <text xml:lang="en">
            Trademark with "en" language.
        </text>
    </trademark>
</metadata>
"""
metadataSchemaTrademark4Title = "Valid trademark Element With Mixed text Element Language Tags 1"
metadataSchemaTrademark4Description = "The trademark element matches the schema. One text element does not have a language tag. One text element has a language tag."
metadataSchemaTrademark4Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# valid two text elements language and language

metadataSchemaTrademark5Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <trademark>
        <text xml:lang="en">
            Trademark with "en" language.
        </text>
        <text xml:lang="fr">
            Trademark with "fr" language.
        </text>
    </trademark>
</metadata>
"""
metadataSchemaTrademark5Title = "Valid trademark Element With Mixed text Element Language Tags 2"
metadataSchemaTrademark5Description = "The trademark element matches the schema. Two text elements have a language tags."
metadataSchemaTrademark5Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# more than one trademark

metadataSchemaTrademark6Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <trademark>
        <text>
            Trademark without language.
        </text>
    </trademark>
    <trademark>
        <text>
            Trademark without language.
        </text>
    </trademark>
</metadata>
"""
metadataSchemaTrademark6Title = "More Than One trademark Element"
metadataSchemaTrademark6Description = "The trademark element occurs more than once."
metadataSchemaTrademark6Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# no text element

metadataSchemaTrademark7Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <trademark />
</metadata>
"""
metadataSchemaTrademark7Title = "No text Element in trademark Element"
metadataSchemaTrademark7Description = "The trademark element does not contain a text child element."
metadataSchemaTrademark7Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# unknown attribute

metadataSchemaTrademark8Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <trademark unknownattribute="Text">
        <text>
            Trademark without language.
        </text>
    </trademark>
</metadata>
"""
metadataSchemaTrademark8Title = "Unknown Attribute in trademark Element"
metadataSchemaTrademark8Description = "The trademark element contains an unknown attribute."
metadataSchemaTrademark8Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# unknown child element

metadataSchemaTrademark9Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <trademark>
        <text>
            Trademark without language.
        </text>
    </trademark>
    <unknown attribute="Text" />
</metadata>
"""
metadataSchemaTrademark9Title = "Unknown Child Element in trademark Element"
metadataSchemaTrademark9Description = "The trademark element contains an unknown child element."
metadataSchemaTrademark9Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# content

metadataSchemaTrademark10Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <trademark>
        Text
        <text>
            Trademark without language.
        </text>
    </trademark>
</metadata>
"""
metadataSchemaTrademark10Title = "Content in trademark Element"
metadataSchemaTrademark10Description = "The trademark element contains content."
metadataSchemaTrademark10Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# text element dir attribute

metadataSchemaTrademark11Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <trademark>
        <text dir="ltr">
            Trademark without language.
        </text>
    </trademark>
</metadata>
"""
metadataSchemaTrademark11Title = "Valid trademark Element With dir Attribute in text Element 1"
metadataSchemaTrademark11Description = "The trademark element contains a text element with ltr as the value for the dir attribute."
metadataSchemaTrademark11Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

metadataSchemaTrademark12Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <trademark>
        <text dir="rtl">
            Trademark without language.
        </text>
    </trademark>
</metadata>
"""
metadataSchemaTrademark12Title = "Valid trademark Element With dir Attribute in text Element 2"
metadataSchemaTrademark12Description = "The trademark element contains a text element with rtl as the value for the dir attribute."
metadataSchemaTrademark12Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

metadataSchemaTrademark13Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <trademark>
        <text dir="INVALID">
            Trademark without language.
        </text>
    </trademark>
</metadata>
"""
metadataSchemaTrademark13Title = "Invalid trademark Element With dir Attribute in text Element"
metadataSchemaTrademark13Description = "The trademark element contains a text element with INVALID as the value for the dir attribute."
metadataSchemaTrademark13Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# text elemet with class attribute

metadataSchemaTrademark14Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <trademark>
        <text class="class1 class2 class3">
            Trademark without language.
        </text>
    </trademark>
</metadata>
"""
metadataSchemaTrademark14Title = "Valid trademark Element With class Attribute in text Element"
metadataSchemaTrademark14Description = "The trademark element contains a text element with \"class1 class2 class3\" as the value for the class attribute."
metadataSchemaTrademark14Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# text element unknown attribute

metadataSchemaTrademark15Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <trademark>
        <text unknownattribute="Text">
            Trademark without language.
        </text>
    </trademark>
</metadata>
"""
metadataSchemaTrademark15Title = "Unknown Attribute in trademark Element text Element"
metadataSchemaTrademark15Description = "The trademark element contains a text element with an unknown attribute."
metadataSchemaTrademark15Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# text element child element

metadataSchemaTrademark16Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <trademark>
        <text>
            Trademark without language.
            <unknown attribute="Text" />
        </text>
    </trademark>
</metadata>
"""
metadataSchemaTrademark16Title = "Unknown Child Element in trademark Element text Element"
metadataSchemaTrademark16Description = "The trademark element contains a text element with an unknown child element."
metadataSchemaTrademark16Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# one div

metadataSchemaTrademark17Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <trademark>
        <text>
            <div>Paragraph 1</div>
        </text>
    </trademark>
</metadata>
"""
metadataSchemaTrademark17Title = "Valid trademark Element With One div Element in text Element"
metadataSchemaTrademark17Description = "The trademark element contains a text element that contains a div element."
metadataSchemaTrademark17Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# two div

metadataSchemaTrademark18Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <trademark>
        <text>
            <div>Paragraph 1</div>
            <div>Paragraph 2</div>
        </text>
    </trademark>
</metadata>
"""
metadataSchemaTrademark18Title = "Valid trademark Element With Two div Elements in text Element"
metadataSchemaTrademark18Description = "The trademark element contains a text element that contains two div elements."
metadataSchemaTrademark18Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# nested div

metadataSchemaTrademark19Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <trademark>
        <text>
            <div>
                div 1 start
                <div>
                    div 2 start
                    <div>
                        div 3
                    </div>
                    div 2 end
                </div>
                div 1 end
            </div>
        </text>
    </trademark>
</metadata>
"""
metadataSchemaTrademark19Title = "Valid trademark Element With Nested div Elements in text Element"
metadataSchemaTrademark19Description = "The trademark element contains a text element that contains nested div elements."
metadataSchemaTrademark19Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# div with dir

metadataSchemaTrademark20Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <trademark>
        <text>
            <div dir="ltr">Paragraph 1</div>
        </text>
    </trademark>
</metadata>
"""
metadataSchemaTrademark20Title = "Valid trademark Element With dir Attribute in div Element in text Element 1"
metadataSchemaTrademark20Description = "The trademark element contains a text element that contains a div element with ltr as the value for the dir attribute."
metadataSchemaTrademark20Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

metadataSchemaTrademark21Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <trademark>
        <text>
            <div dir="rtl">Paragraph 1</div>
        </text>
    </trademark>
</metadata>
"""
metadataSchemaTrademark21Title = "Valid trademark Element With dir Attribute in div Element in text Element 2"
metadataSchemaTrademark21Description = "The trademark element contains a text element that contains a div element with rtl as the value for the dir attribute."
metadataSchemaTrademark21Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

metadataSchemaTrademark22Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <trademark>
        <text>
            <div dir="INVALID">Paragraph 1</div>
        </text>
    </trademark>
</metadata>
"""
metadataSchemaTrademark22Title = "Invalid trademark Element With dir Attribute in div Element in text Element"
metadataSchemaTrademark22Description = "The trademark element contains a text element that contains a div element with INVALID as the value for the dir attribute."
metadataSchemaTrademark22Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# div with class

metadataSchemaTrademark23Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <trademark>
        <text>
            <div class="class1 class2 class3">Paragraph 1</div>
        </text>
    </trademark>
</metadata>
"""
metadataSchemaTrademark23Title = "Valid trademark Element With class Attribute in div Element in text Element"
metadataSchemaTrademark23Description = "The trademark element contains a text element that contains a div element with \"class1 class2 class3\" as the value for the class attribute."
metadataSchemaTrademark23Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# one span

metadataSchemaTrademark24Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <trademark>
        <text>
            Text with <span>span</span>.
        </text>
    </trademark>
</metadata>
"""
metadataSchemaTrademark24Title = "Valid trademark Element With One span Element in text Element"
metadataSchemaTrademark24Description = "The trademark element contains a text element that contains a span element."
metadataSchemaTrademark24Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# two span

metadataSchemaTrademark25Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <trademark>
        <text>
             Text with <span>span 1</span> and <span>span 2</span>.
        </text>
    </trademark>
</metadata>
"""
metadataSchemaTrademark25Title = "Valid trademark Element With Two span Elements in text Element"
metadataSchemaTrademark25Description = "The trademark element contains a text element that contains two span elements."
metadataSchemaTrademark25Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# nested span

metadataSchemaTrademark26Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <trademark>
        <text>
             <span>
                 span 1 start
                 <span>
                     span 2 start
                     <span>
                         span 3
                     </span>
                     span 2 end
                 </span>
                 span 1 end
             </span>
        </text>
    </trademark>
</metadata>
"""
metadataSchemaTrademark26Title = "Valid trademark Element With Nested span Elements in text Element"
metadataSchemaTrademark26Description = "The trademark element contains a text element that contains nested span elements."
metadataSchemaTrademark26Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# span with dir

metadataSchemaTrademark27Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <trademark>
        <text>
            Text with <span dir="ltr">span</span>.
        </text>
    </trademark>
</metadata>
"""
metadataSchemaTrademark27Title = "Valid trademark Element With dir Attribute in span Element in text Element 1"
metadataSchemaTrademark27Description = "The trademark element contains a text element that contains a span element with ltr as the value for the dir attribute."
metadataSchemaTrademark27Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

metadataSchemaTrademark28Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <trademark>
        <text>
            Text with <span dir="rtl">span</span>.
        </text>
    </trademark>
</metadata>
"""
metadataSchemaTrademark28Title = "Valid trademark Element With dir Attribute in span Element in text Element 2"
metadataSchemaTrademark28Description = "The trademark element contains a text element that contains a span element with rtl as the value for the dir attribute."
metadataSchemaTrademark28Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

metadataSchemaTrademark29Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <trademark>
        <text>
            Text with <span dir="INVALID">span</span>.
        </text>
    </trademark>
</metadata>
"""
metadataSchemaTrademark29Title = "Invalid trademark Element With dir Attribute in span Element in text Element"
metadataSchemaTrademark29Description = "The trademark element contains a text element that contains a span element with INVALID as the value for the dir attribute."
metadataSchemaTrademark29Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# span with class

metadataSchemaTrademark30Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <trademark>
        <text>
            Text with <span class="class1 class2 class3">span</span>.
        </text>
    </trademark>
</metadata>
"""
metadataSchemaTrademark30Title = "Valid trademark Element With class Attribute in span Element in text Element"
metadataSchemaTrademark30Description = "The trademark element contains a text element that contains a span element with \"class1 class2 class3\" as the value for the class attribute."
metadataSchemaTrademark30Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# -------------------------------------------
# Metadata Display: Schema Validity: licensee
# -------------------------------------------

# valid

metadataSchemaLicensee1Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <licensee name="Licensee Name" />
</metadata>
"""
metadataSchemaLicensee1Title = "Valid licensee Element"
metadataSchemaLicensee1Description = "The licensee element matches the schema."
metadataSchemaLicensee1Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# duplicate

metadataSchemaLicensee2Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <licensee name="Licensee Name" />
    <licensee name="Licensee Name" />
</metadata>
"""
metadataSchemaLicensee2Title = "More Than One licensee Element"
metadataSchemaLicensee2Description = "The licensee element occurs more than once."
metadataSchemaLicensee2Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# missing name

metadataSchemaLicensee3Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <licensee />
</metadata>
"""
metadataSchemaLicensee3Title = "No name Attribute in licensee Element"
metadataSchemaLicensee3Description = "The licensee element does not contain the required name attribute."
metadataSchemaLicensee3Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# dir attribute

metadataSchemaLicensee4Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <licensee name="Licensee Name" dir="ltr" />
</metadata>
"""
metadataSchemaLicensee4Title = "Valid licensee Element With dir Attribute 1"
metadataSchemaLicensee4Description = "The licensee element has ltr as the value for the dir attribute."
metadataSchemaLicensee4Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

metadataSchemaLicensee5Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <licensee name="Licensee Name" dir="rtl" />
</metadata>
"""
metadataSchemaLicensee5Title = "Valid licensee Element With dir Attribute 2"
metadataSchemaLicensee5Description = "The licensee element has rtl as the value for the dir attribute."
metadataSchemaLicensee5Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

metadataSchemaLicensee6Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <licensee name="Licensee Name" dir="INVALID" />
</metadata>
"""
metadataSchemaLicensee6Title = "Invalid licensee Element With dir Attribute"
metadataSchemaLicensee6Description = "The licensee element has INVALID as the value for the dir attribute."
metadataSchemaLicensee6Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# class attribute

metadataSchemaLicensee7Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <licensee name="Licensee Name" class="class1 class2 class3" />
</metadata>
"""
metadataSchemaLicensee7Title = "Valid licensee Element With class Attribute"
metadataSchemaLicensee7Description = "The licensee element has \"class1 class2 class3\" as the value for the class attribute."
metadataSchemaLicensee7Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# unknown attribute

metadataSchemaLicensee8Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <licensee name="Licensee Name" unknownattribute="Text" />
</metadata>
"""
metadataSchemaLicensee8Title = "Unknown Attribute in licensee Element"
metadataSchemaLicensee8Description = "The licensee element occures more than once."
metadataSchemaLicensee8Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# child element

metadataSchemaLicensee9Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <licensee name="Licensee Name">
        <unknown attribute="Text" />
    </licensee>
</metadata>
"""
metadataSchemaLicensee9Title = "Child Element in licensee Element"
metadataSchemaLicensee9Description = "The licensee element contains a child element."
metadataSchemaLicensee9Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# content

metadataSchemaLicensee10Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <licensee name="Licensee Name">
        Text
    </licensee>
</metadata>
"""
metadataSchemaLicensee10Title = "Content in licensee Element"
metadataSchemaLicensee10Description = "The licensee element contains content."
metadataSchemaLicensee10Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# --------------------------------------------
# Metadata Display: Schema Validity: extension
# --------------------------------------------

# valid

metadataSchemaExtension1Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <extension id="Extension 1">
        <name>Name Without Language</name>
        <item id="Extension 1 - Item 1 ID">
            <name>Extension 1 - Item 1 - Name Without Language</name>
            <value>Extension 1 - Item 1 - Value Without Language</value>
        </item>
    </extension>
</metadata>
"""
metadataSchemaExtension1Title = "Valid extension Element"
metadataSchemaExtension1Description = "The extension element matches the schema."
metadataSchemaExtension1Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# valid two extensions

metadataSchemaExtension2Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <extension id="Extension 1">
        <name>Extension 1 - Name Without Language</name>
        <item id="Extension 1 - Item 1 ID">
            <name>Extension 1 - Item 1 - Name Without Language</name>
            <value>Extension 1 - Item 1 - Value Without Language</value>
        </item>
    </extension>
    <extension id="Extension 2">
        <name>Extension 2 - Name Without Language</name>
        <item id="Extension 2 - Item 1 ID">
            <name>Extension 2 - Item 1 - Name Without Language</name>
            <value>Extension 2 - Item 1 - Value Without Language</value>
        </item>
    </extension>
</metadata>
"""
metadataSchemaExtension2Title = "Two Valid extension Elements"
metadataSchemaExtension2Description = "Two extension elements match the schema."
metadataSchemaExtension2Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# valid no id

metadataSchemaExtension3Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <extension>
        <name>Extension 1 - Name Without Language</name>
        <item id="Extension 1 - Item 1 ID">
            <name>Extension 1 - Item 1 - Name Without Language</name>
            <value>Extension 1 - Item 1 - Value Without Language</value>
        </item>
    </extension>
</metadata>
"""
metadataSchemaExtension3Title = "Valid extension Element Without id Attribute"
metadataSchemaExtension3Description = "The extension element does not have an id attribute but it still matches the schema."
metadataSchemaExtension3Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# valid no name

metadataSchemaExtension4Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <extension id="Extension 1">
        <item id="Extension 1 - Item 1 ID">
            <name>Extension 1 - Item 1 - Name Without Language</name>
            <value>Extension 1 - Item 1 - Value Without Language</value>
        </item>
    </extension>
</metadata>
"""
metadataSchemaExtension4Title = "Valid extension Element Without name Element"
metadataSchemaExtension4Description = "The extension element does not have a name child element but it still matches the schema."
metadataSchemaExtension4Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# valid one untagged name one tagged name

metadataSchemaExtension5Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <extension id="Extension 1">
        <name>Extension 1 - Name Without Language</name>
        <name xml:lang="en">Extension 1 - Name With "en" Language</name>
        <item id="Extension 1 - Item 1 ID">
            <name>Extension 1 - Item 1 - Name Without Language</name>
            <value>Extension 1 - Item 1 - Value Without Language</value>
        </item>
    </extension>
</metadata>
"""
metadataSchemaExtension5Title = "Valid extension Element With Two name Elements 1"
metadataSchemaExtension5Description = "The extension element contains one name element without a lang attribute and another with a lang attribute."
metadataSchemaExtension5Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# valid two tagged names

metadataSchemaExtension6Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <extension id="Extension 1">
        <name xml:lang="en">Extension 1 - Name With "en" Language</name>
        <name xml:lang="fr">Extension 1 - Name With "fr" Language</name>
        <item id="Extension 1 - Item 1 ID">
            <name>Extension 1 - Item 1 - Name Without Language</name>
            <value>Extension 1 - Item 1 - Value Without Language</value>
        </item>
    </extension>
</metadata>
"""
metadataSchemaExtension6Title = "Valid extension Element With Two name Elements 2"
metadataSchemaExtension6Description = "The extension element contains two name elements with lang attributes."
metadataSchemaExtension6Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# valid more than one item

metadataSchemaExtension7Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <extension id="Extension 1">
        <name>Extension 1 - Name Without Language</name>
        <item id="Extension 1 - Item 1 ID">
            <name>Extension 1 - Item 1 - Name Without Language</name>
            <value>Extension 1 - Item 1 - Value Without Language</value>
        </item>
        <item id="Extension 1 - Item 2 ID">
            <name>Extension 1 - Item 2 - Name Without Language</name>
            <value>Extension 1 - Item 2 - Value Without Language</value>
        </item>
    </extension>
</metadata>
"""
metadataSchemaExtension7Title = "Valid extension Element With Two item Elements"
metadataSchemaExtension7Description = "The extension element contains two item child elements."
metadataSchemaExtension7Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# no item

metadataSchemaExtension8Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <extension id="Extension 1">
        <name>Extension 1 - Name Without Language</name>
    </extension>
</metadata>
"""
metadataSchemaExtension8Title = "No item Element in extension Element"
metadataSchemaExtension8Description = "The extension element does not contain an item child element."
metadataSchemaExtension8Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# unknown attribute

metadataSchemaExtension9Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <extension id="Extension 1" unknownattribute="Text">
        <name>Extension 1 - Name Without Language</name>
        <item id="Extension 1 - Item 1 ID">
            <name>Extension 1 - Item 1 - Name Without Language</name>
            <value>Extension 1 - Item 1 - Value Without Language</value>
        </item>
    </extension>
</metadata>
"""
metadataSchemaExtension9Title = "Unknown Attribute in extension Element"
metadataSchemaExtension9Description = "The extension element contains an unknown attribute."
metadataSchemaExtension9Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# unknown child

metadataSchemaExtension10Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <extension id="Extension 1">
        <name>Extension 1 - Name Without Language</name>
        <item id="Extension 1 - Item 1 ID">
            <name>Extension 1 - Item 1 - Name Without Language</name>
            <value>Extension 1 - Item 1 - Value Without Language</value>
        </item>
    </extension>
    <unknown attribute="Text" />
</metadata>
"""
metadataSchemaExtension10Title = "Unknown Child Element in extension Element"
metadataSchemaExtension10Description = "The extension element contains an unknown child element."
metadataSchemaExtension10Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# content

metadataSchemaExtension11Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <extension id="Extension 1">
        Text
        <name>Extension 1 - Name Without Language</name>
        <item id="Extension 1 - Item 1 ID">
            <name>Extension 1 - Item 1 - Name Without Language</name>
            <value>Extension 1 - Item 1 - Value Without Language</value>
        </item>
    </extension>
</metadata>
"""
metadataSchemaExtension11Title = "Content in extension Element"
metadataSchemaExtension11Description = "The extension element contains content."
metadataSchemaExtension11Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# ---------------------------------------------------
# Metadata Display: Schema Validity: extension - name
# ---------------------------------------------------

# valid no lang

metadataSchemaExtension12Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <extension id="Extension 1">
        <name>Extension 1 - Name Without Language</name>
        <item id="Extension 1 - Item 1 ID">
            <name>Extension 1 - Item 1 - Name Without Language</name>
            <value>Extension 1 - Item 1 - Value Without Language</value>
        </item>
    </extension>
</metadata>
"""
metadataSchemaExtension12Title = "Valid name Element in extension Element"
metadataSchemaExtension12Description = "The name element in the extension element matches the schema."
metadataSchemaExtension12Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# valid xml:lang

metadataSchemaExtension13Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <extension id="Extension 1">
        <name xml:lang="en">Extension 1 - Name With "en" Language</name>
        <item id="Extension 1 - Item 1 ID">
            <name>Extension 1 - Item 1 - Name Without Language</name>
            <value>Extension 1 - Item 1 - Value Without Language</value>
        </item>
    </extension>
</metadata>
"""
metadataSchemaExtension13Title = "Valid name Element With xml:lang Attribute in extension Element"
metadataSchemaExtension13Description = "The name element in the extension element contains a xml:lang attribute and it matches the schema."
metadataSchemaExtension13Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# valid lang

metadataSchemaExtension14Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <extension id="Extension 1">
        <name lang="en">Extension 1 - Name With "en" Language</name>
        <item id="Extension 1 - Item 1 ID">
            <name>Extension 1 - Item 1 - Name Without Language</name>
            <value>Extension 1 - Item 1 - Value Without Language</value>
        </item>
    </extension>
</metadata>
"""
metadataSchemaExtension14Title = "Valid name Element With lang Attribute in extension Element"
metadataSchemaExtension14Description = "The name element in the extension element contains a lang attribute and it matches the schema."
metadataSchemaExtension14Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# dir

metadataSchemaExtension15Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <extension id="Extension 1">
        <name dir="ltr">Extension 1 - Name Without Language</name>
        <item id="Extension 1 - Item 1 ID">
            <name>Extension 1 - Item 1 - Name Without Language</name>
            <value>Extension 1 - Item 1 - Value Without Language</value>
        </item>
    </extension>
</metadata>
"""
metadataSchemaExtension15Title = "Valid name Element With dir Attribute in extension Element 1"
metadataSchemaExtension15Description = "The name element in the extension element has ltr as the value for the dir attribute."
metadataSchemaExtension15Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

metadataSchemaExtension16Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <extension id="Extension 1">
        <name dir="rtl">Extension 1 - Name Without Language</name>
        <item id="Extension 1 - Item 1 ID">
            <name>Extension 1 - Item 1 - Name Without Language</name>
            <value>Extension 1 - Item 1 - Value Without Language</value>
        </item>
    </extension>
</metadata>
"""
metadataSchemaExtension16Title = "Valid name Element With dir Attribute in extension Element 2"
metadataSchemaExtension16Description = "The name element in the extension element has rtl as the value for the dir attribute."
metadataSchemaExtension16Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

metadataSchemaExtension17Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <extension id="Extension 1">
        <name dir="INVALID">Extension 1 - Name Without Language</name>
        <item id="Extension 1 - Item 1 ID">
            <name>Extension 1 - Item 1 - Name Without Language</name>
            <value>Extension 1 - Item 1 - Value Without Language</value>
        </item>
    </extension>
</metadata>
"""
metadataSchemaExtension17Title = "Invalid name Element With dir Attribute in extension Element"
metadataSchemaExtension17Description = "The name element in the extension element has INVALID as the value for the dir attribute."
metadataSchemaExtension17Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# class

metadataSchemaExtension18Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <extension id="Extension 1">
        <name class="class1 class2 class3">Extension 1 - Name Without Language</name>
        <item id="Extension 1 - Item 1 ID">
            <name>Extension 1 - Item 1 - Name Without Language</name>
            <value>Extension 1 - Item 1 - Value Without Language</value>
        </item>
    </extension>
</metadata>
"""
metadataSchemaExtension18Title = "Valid name Element With class Attribute in extension Element"
metadataSchemaExtension18Description = "The name element in the extension element has \"class1 class2 class3\" as the value for the class attribute."
metadataSchemaExtension18Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# unknown attribute

metadataSchemaExtension19Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <extension id="Extension 1">
        <name unknownattribute="Text">Extension 1 - Name Without Language</name>
        <item id="Extension 1 - Item 1 ID">
            <name>Extension 1 - Item 1 - Name Without Language</name>
            <value>Extension 1 - Item 1 - Value Without Language</value>
        </item>
    </extension>
</metadata>
"""
metadataSchemaExtension19Title = "Unknown Attribute in name Element in extension Element"
metadataSchemaExtension19Description = "The name element in the extension element contains an unknown attribute."
metadataSchemaExtension19Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# child element

metadataSchemaExtension20Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <extension id="Extension 1">
        <name>
            Extension 1 - Name Without Language
            <unknown attribute="Text" />
        </name>
        <item id="Extension 1 - Item 1 ID">
            <name>Extension 1 - Item 1 - Name Without Language</name>
            <value>Extension 1 - Item 1 - Value Without Language</value>
        </item>
    </extension>
</metadata>
"""
metadataSchemaExtension20Title = "Child Element in name Element in extension Element"
metadataSchemaExtension20Description = "The name element in the extension element contains a child element."
metadataSchemaExtension20Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# ---------------------------------------------------
# Metadata Display: Schema Validity: extension - item
# ---------------------------------------------------

# valid

metadataSchemaExtension21Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <extension id="Extension 1">
        <name>Extension 1 - Name Without Language</name>
        <item id="Extension 1 - Item 1 ID">
            <name>Extension 1 - Item 1 - Name Without Language</name>
            <value>Extension 1 - Item 1 - Value Without Language</value>
        </item>
    </extension>
</metadata>
"""
metadataSchemaExtension21Title = "Valid item Element in extension Element"
metadataSchemaExtension21Description = "The item element in the extension element matches the schema."
metadataSchemaExtension21Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# valid multiple languages

metadataSchemaExtension22Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <extension id="Extension 1">
        <name>Extension 1 - Name Without Language</name>
        <item id="Extension 1 - Item 1 ID">
            <name>Extension 1 - Item 1 - Name Without Language</name>
            <name xml:lang="en">Extension 1 - Item 1 - Name With "en" Language</name>
            <name xml:lang="fr">Extension 1 - Item 1 - Name With "fr" Language</name>
            <value>Extension 1 - Item 1 - Value Without Language</value>
            <value xml:lang="en">Extension 1 - Item 1 - Value With "en" Language</value>
            <value xml:lang="fr">Extension 1 - Item 1 - Value With "fr" Language</value>
        </item>
    </extension>
</metadata>
"""
metadataSchemaExtension22Title = "Valid item Element With Multiple Languages in extension Element"
metadataSchemaExtension22Description = "The item element in the extension element contains a variety of languages."
metadataSchemaExtension22Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# valid no id

metadataSchemaExtension23Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <extension id="Extension 1">
        <name>Extension 1 - Name Without Language</name>
        <item>
            <name>Extension 1 - Item 1 - Name Without Language</name>
            <value>Extension 1 - Item 1 - Value Without Language</value>
        </item>
    </extension>
</metadata>
"""
metadataSchemaExtension23Title = "Valid item Element Without id Attribute in extension Element"
metadataSchemaExtension23Description = "The item element in the extension element does not contain an id attribute but it still matches the schema."
metadataSchemaExtension23Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# valid name no tag and tagged

metadataSchemaExtension24Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <extension id="Extension 1">
        <name>Extension 1 - Name Without Language</name>
        <item id="Extension 1 - Item 1 ID">
            <name>Extension 1 - Item 1 - Name Without Language</name>
            <name xml:lang="en">Extension 1 - Item 1 - Name With "en" Language</name>
            <value>Extension 1 - Item 1 - Value Without Language</value>
        </item>
    </extension>
</metadata>
"""
metadataSchemaExtension24Title = "Valid item Element With Two name Elements in extension Element 1"
metadataSchemaExtension24Description = "The item element in the extension element contains one name child element with no lang attribute and one with a lang attribute."
metadataSchemaExtension24Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# valid name two tagged

metadataSchemaExtension25Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <extension id="Extension 1">
        <name>Extension 1 - Name Without Language</name>
        <item id="Extension 1 - Item 1 ID">
            <name xml:lang="en">Extension 1 - Item 1 - Name With "en" Language</name>
            <name xml:lang="fr">Extension 1 - Item 1 - Name With "fr" Language</name>
            <value>Extension 1 - Item 1 - Value Without Language</value>
        </item>
    </extension>
</metadata>
"""
metadataSchemaExtension25Title = "Valid item Element With Two name Elements in extension Element 2"
metadataSchemaExtension25Description = "The item element in the extension element contains two name child elements with lang attributes."
metadataSchemaExtension25Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# valid value no tag and tagged

metadataSchemaExtension26Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <extension id="Extension 1">
        <name>Extension 1 - Name Without Language</name>
        <item id="Extension 1 - Item 1 ID">
            <name>Extension 1 - Item 1 - Name Without Language</name>
            <value>Extension 1 - Item 1 - Value Without Language</value>
            <value xml:lang="en">Extension 1 - Item 1 - Value With "en" Language</value>
        </item>
    </extension>
</metadata>
"""
metadataSchemaExtension26Title = "Valid item Element With Two value Elements in extension Element 1"
metadataSchemaExtension26Description = "The item element in the extension element contains one value child element with no lang attribute and one with a lang attribute."
metadataSchemaExtension26Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# valid value two tagged

metadataSchemaExtension27Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <extension id="Extension 1">
        <name>Extension 1 - Name Without Language</name>
        <item id="Extension 1 - Item 1 ID">
            <name>Extension 1 - Item 1 - Name Without Language</name>
            <value xml:lang="en">Extension 1 - Item 1 - Value With "en" Language</value>
            <value xml:lang="fr">Extension 1 - Item 1 - Value With "fr" Language</value>
        </item>
    </extension>
</metadata>
"""
metadataSchemaExtension27Title = "Valid item Element With Two value Elements in extension Element 2"
metadataSchemaExtension27Description = "The item element in the extension element contains two value child elements with lang attributes."
metadataSchemaExtension27Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# no name

metadataSchemaExtension28Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <extension id="Extension 1">
        <name>Extension 1 - Name Without Language</name>
        <item id="Extension 1 - Item 1 ID">
            <value>Extension 1 - Item 1 - Value Without Language</value>
        </item>
    </extension>
</metadata>
"""
metadataSchemaExtension28Title = "No name Element in item Element in extension Element"
metadataSchemaExtension28Description = "The item element in the extension element does not contain a name child element."
metadataSchemaExtension28Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# no value

metadataSchemaExtension29Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <extension id="Extension 1">
        <name>Extension 1 - Name Without Language</name>
        <item id="Extension 1 - Item 1 ID">
            <name>Extension 1 - Item 1 - Name Without Language</name>
        </item>
    </extension>
</metadata>
"""
metadataSchemaExtension29Title = "No value Element in item Element in extension Element"
metadataSchemaExtension29Description = "The item element in the extension element does not contain a value child element."
metadataSchemaExtension29Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# unknown attribute

metadataSchemaExtension30Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <extension id="Extension 1">
        <name>Extension 1 - Name Without Language</name>
        <item id="Extension 1 - Item 1 ID" unknownattribute="Text">
            <name>Extension 1 - Item 1 - Name Without Language</name>
            <value>Extension 1 - Item 1 - Value Without Language</value>
        </item>
    </extension>
</metadata>
"""
metadataSchemaExtension30Title = "Unknown Attribute in item Element in extension Element"
metadataSchemaExtension30Description = "The item element in the extension element contains an unknown attribute."
metadataSchemaExtension30Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# unknown child element

metadataSchemaExtension31Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <extension id="Extension 1">
        <name>Extension 1 - Name Without Language</name>
        <item id="Extension 1 - Item 1 ID">
            <name>Extension 1 - Item 1 - Name Without Language</name>
            <value>Extension 1 - Item 1 - Value Without Language</value>
            <unknown attribute="Text" />
        </item>
    </extension>
</metadata>
"""
metadataSchemaExtension31Title = "Unknown Child Element in item Element in extension Element"
metadataSchemaExtension31Description = "The item element in the extension element contains an unknown child element."
metadataSchemaExtension31Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# content

metadataSchemaExtension32Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <extension id="Extension 1">
        <name>Extension 1 - Name Without Language</name>
        <item id="Extension 1 - Item 1 ID">
            Text
            <name>Extension 1 - Item 1 - Name Without Language</name>
            <value>Extension 1 - Item 1 - Value Without Language</value>
        </item>
    </extension>
</metadata>
"""
metadataSchemaExtension32Title = "Content in item Element in extension Element"
metadataSchemaExtension32Description = "The item element in the extension element contains content."
metadataSchemaExtension32Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# ----------------------------------------------------------
# Metadata Display: Schema Validity: extension - item - name
# ----------------------------------------------------------

# valid no lang

metadataSchemaExtension33Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <extension id="Extension 1">
        <name>Extension 1 - Name Without Language</name>
        <item id="Extension 1 - Item 1 ID">
            <name>Extension 1 - Item 1 - Name Without Language</name>
            <value>Extension 1 - Item 1 - Value Without Language</value>
        </item>
    </extension>
</metadata>
"""
metadataSchemaExtension33Title = "Valid name Element in item Element in extension Element"
metadataSchemaExtension33Description = "The name element in the item element in the extension element matches the schema."
metadataSchemaExtension33Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# valid xml:lang

metadataSchemaExtension34Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <extension id="Extension 1">
        <name>Extension 1 - Name Without Language</name>
        <item id="Extension 1 - Item 1 ID">
            <name xml:lang="en">Extension 1 - Item 1 - Name With "en" Language</name>
            <value>Extension 1 - Item 1 - Value Without Language</value>
        </item>
    </extension>
</metadata>
"""
metadataSchemaExtension34Title = "Valid name Element With xml:lang Attribute in item Element in extension Element"
metadataSchemaExtension34Description = "The name element in the item element in the extension element contains a xml:lang attribute and it matches the schema."
metadataSchemaExtension34Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# valid lang

metadataSchemaExtension35Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <extension id="Extension 1">
        <name>Extension 1 - Name Without Language</name>
        <item id="Extension 1 - Item 1 ID">
            <name lang="en">Extension 1 - Item 1 - Name With "en" Language</name>
            <value>Extension 1 - Item 1 - Value Without Language</value>
        </item>
    </extension>
</metadata>
"""
metadataSchemaExtension35Title = "Valid name Element With lang Attribute in item Element in extension Element"
metadataSchemaExtension35Description = "The name element in the item element in the extension element contains a lang attribute and it matches the schema."
metadataSchemaExtension35Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# dir attribute

metadataSchemaExtension36Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <extension id="Extension 1">
        <name>Extension 1 - Name Without Language</name>
        <item id="Extension 1 - Item 1 ID">
            <name dir="ltr">Extension 1 - Item 1 - Name Without Language</name>
            <value>Extension 1 - Item 1 - Value Without Language</value>
        </item>
    </extension>
</metadata>
"""
metadataSchemaExtension36Title = "Valid name Element With dir Attribute in item Element in extension Element 1"
metadataSchemaExtension36Description = "The name element in the item element in the extension element has ltr as the value for the dir attribute."
metadataSchemaExtension36Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

metadataSchemaExtension37Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <extension id="Extension 1">
        <name>Extension 1 - Name Without Language</name>
        <item id="Extension 1 - Item 1 ID">
            <name dir="rtl">Extension 1 - Item 1 - Name Without Language</name>
            <value>Extension 1 - Item 1 - Value Without Language</value>
        </item>
    </extension>
</metadata>
"""
metadataSchemaExtension37Title = "Valid name Element With dir Attribute in item Element in extension Element 2"
metadataSchemaExtension37Description = "The name element in the item element in the extension element has rtl as the value for the dir attribute."
metadataSchemaExtension37Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

metadataSchemaExtension38Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <extension id="Extension 1">
        <name>Extension 1 - Name Without Language</name>
        <item id="Extension 1 - Item 1 ID">
            <name dir="INVALID">Extension 1 - Item 1 - Name Without Language</name>
            <value>Extension 1 - Item 1 - Value Without Language</value>
        </item>
    </extension>
</metadata>
"""
metadataSchemaExtension38Title = "Invalid name Element With dir Attribute in item Element in extension Element"
metadataSchemaExtension38Description = "The name element in the item element in the extension element has INVALID as the value for the dir attribute."
metadataSchemaExtension38Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# class attribute

metadataSchemaExtension39Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <extension id="Extension 1">
        <name>Extension 1 - Name Without Language</name>
        <item id="Extension 1 - Item 1 ID">
            <name class="class1 class2 class3">Extension 1 - Item 1 - Name Without Language</name>
            <value>Extension 1 - Item 1 - Value Without Language</value>
        </item>
    </extension>
</metadata>
"""
metadataSchemaExtension39Title = "Valid name Element With class Attribute in item Element in extension Element"
metadataSchemaExtension39Description = "The name element in the item element in the extension element has \"class1 class2 class3\" as the value for the class attribute."
metadataSchemaExtension39Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# unknown attribute

metadataSchemaExtension40Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <extension id="Extension 1">
        <name>Extension 1 - Name Without Language</name>
        <item id="Extension 1 - Item 1 ID">
            <name unknownattribute="Text">Extension 1 - Item 1 - Name Without Language</name>
            <value>Extension 1 - Item 1 - Value Without Language</value>
        </item>
    </extension>
</metadata>
"""
metadataSchemaExtension40Title = "Unknown Attribute in name Element in item Element in extension Element"
metadataSchemaExtension40Description = "The name element in the item element in the extension element contains an unknown attribute."
metadataSchemaExtension40Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# child element

metadataSchemaExtension41Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <extension id="Extension 1">
        <name>Extension 1 - Name Without Language</name>
        <item id="Extension 1 - Item 1 ID">
            <name>
                Extension 1 - Item 1 - Name Without Language
                <unknown attribute="Text" />
            </name>
            <value>Extension 1 - Item 1 - Value Without Language</value>
        </item>
    </extension>
</metadata>
"""
metadataSchemaExtension41Title = "Child Element in name Element in item Element in extension Element"
metadataSchemaExtension41Description = "The name element in the item element in the extension element contains a child element."
metadataSchemaExtension41Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# -----------------------------------------------------------
# Metadata Display: Schema Validity: extension - item - value
# -----------------------------------------------------------

# valid no lang

metadataSchemaExtension42Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <extension id="Extension 1">
        <name>Extension 1 - Name Without Language</name>
        <item id="Extension 1 - Item 1 ID">
            <name>Extension 1 - Item 1 - Name Without Language</name>
            <value>Extension 1 - Item 1 - Value Without Language</value>
        </item>
    </extension>
</metadata>
"""
metadataSchemaExtension42Title = "Valid value Element in item Element in extension Element"
metadataSchemaExtension42Description = "The value element in the item element in the extension element matches the schema."
metadataSchemaExtension42Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# valid xml:lang

metadataSchemaExtension43Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <extension id="Extension 1">
        <name>Extension 1 - Name Without Language</name>
        <item id="Extension 1 - Item 1 ID">
            <name>Extension 1 - Item 1 - Name Without Language</name>
            <value xml:lang="en">Extension 1 - Item 1 - Value With "en" Language</value>
        </item>
    </extension>
</metadata>
"""
metadataSchemaExtension43Title = "Valid value Element With xml:lang Attribute in item Element in extension Element"
metadataSchemaExtension43Description = "The value element in the item element in the extension element contains a xml:lang attribute and it matches the schema."
metadataSchemaExtension43Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# valid lang

metadataSchemaExtension44Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <extension id="Extension 1">
        <name>Extension 1 - Name Without Language</name>
        <item id="Extension 1 - Item 1 ID">
            <name>Extension 1 - Item 1 - Name Without Language</name>
            <value lang="en">Extension 1 - Item 1 - Value With "en" Language</value>
        </item>
    </extension>
</metadata>
"""
metadataSchemaExtension44Title = "Valid value Element With lang Attribute in item Element in extension Element"
metadataSchemaExtension44Description = "The value element in the item element in the extension element contains a lang attribute and it matches the schema."
metadataSchemaExtension44Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# dir

metadataSchemaExtension45Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <extension id="Extension 1">
        <name>Extension 1 - Name Without Language</name>
        <item id="Extension 1 - Item 1 ID">
            <name>Extension 1 - Item 1 - Name Without Language</name>
            <value dir="ltr">Extension 1 - Item 1 - Value Without Language</value>
        </item>
    </extension>
</metadata>
"""
metadataSchemaExtension45Title = "Valid value Element With dir Attribute in item Element in extension Element 1"
metadataSchemaExtension45Description = "The value element in the item element in the extension element has ltr as the value for the dir attribute."
metadataSchemaExtension45Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

metadataSchemaExtension46Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <extension id="Extension 1">
        <name>Extension 1 - Name Without Language</name>
        <item id="Extension 1 - Item 1 ID">
            <name>Extension 1 - Item 1 - Name Without Language</name>
            <value dir="rtl">Extension 1 - Item 1 - Value Without Language</value>
        </item>
    </extension>
</metadata>
"""
metadataSchemaExtension46Title = "Valid value Element With dir Attribute in item Element in extension Element 2"
metadataSchemaExtension46Description = "The value element in the item element in the extension element has rtl as the value for the dir attribute."
metadataSchemaExtension46Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

metadataSchemaExtension47Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <extension id="Extension 1">
        <name>Extension 1 - Name Without Language</name>
        <item id="Extension 1 - Item 1 ID">
            <name>Extension 1 - Item 1 - Name Without Language</name>
            <value dir="INVALID">Extension 1 - Item 1 - Value Without Language</value>
        </item>
    </extension>
</metadata>
"""
metadataSchemaExtension47Title = "Invalid value Element With dir Attribute in item Element in extension Element"
metadataSchemaExtension47Description = "The value element in the item element in the extension element has INVALID as the value for the dir attribute."
metadataSchemaExtension47Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# class

metadataSchemaExtension48Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <extension id="Extension 1">
        <name>Extension 1 - Name Without Language</name>
        <item id="Extension 1 - Item 1 ID">
            <name>Extension 1 - Item 1 - Name Without Language</name>
            <value class="class1 class2 class3">Extension 1 - Item 1 - Value Without Language</value>
        </item>
    </extension>
</metadata>
"""
metadataSchemaExtension48Title = "Valid value Element With class Attribute in item Element in extension Element"
metadataSchemaExtension48Description = "The value element in the item element in the extension element has \"class1 class2 class3\" as the value for the dir attribute."
metadataSchemaExtension48Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# unknown attribute

metadataSchemaExtension49Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <extension id="Extension 1">
        <name>Extension 1 - Name Without Language</name>
        <item id="Extension 1 - Item 1 ID">
            <name>Extension 1 - Item 1 - Name Without Language</name>
            <value unknownattribute="Text">Extension 1 - Item 1 - Value Without Language</value>
        </item>
    </extension>
</metadata>
"""
metadataSchemaExtension49Title = "Unknown Attribute in value Element in item Element in extension Element"
metadataSchemaExtension49Description = "The value element in the item element in the extension element contains an unknown attribute."
metadataSchemaExtension49Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]

# child element

metadataSchemaExtension50Metadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <extension id="Extension 1">
        <name>Extension 1 - Name Without Language</name>
        <item id="Extension 1 - Item 1 ID">
            <name>Extension 1 - Item 1 - Name Without Language</name>
            <value>
                Extension 1 - Item 1 - Value Without Language
                <unknown attribute="Text" />
            </value>
        </item>
    </extension>
</metadata>
"""
metadataSchemaExtension50Title = "Child Element in value Element in item Element in extension Element"
metadataSchemaExtension50Description = "The value element in the item element in the extension element contains a child element."
metadataSchemaExtension50Credits = [dict(title="Tal Leming", role="author", link="http://typesupply.com")]
