"""
Default data for the test cases.
"""

import brotli
from copy import deepcopy
from fontTools.ttLib.sfnt import sfntDirectoryFormat, sfntDirectorySize, sfntDirectoryEntryFormat, sfntDirectoryEntrySize
from sfnt import getSFNTData
from woff import packTestDirectory, packTestCollectionHeader, packTestCollectionDirectory, woffHeaderSize, knownTableTags
from paths import sfntCFFSourcePath, sfntTTFSourcePath
from utilities import calcPaddingLength, calcTableChecksum

# ---------
# SFNT Data
# ---------

originalSFNTChecksums = {}

sfntTTFTableData, sfntTTFCompressedData, sfntTTFTableOrder, sfntTTFTableChecksums = getSFNTData(sfntTTFSourcePath)
for tag, checksum in sfntTTFTableChecksums.items():
    data = sfntTTFTableData[tag]
    if data in originalSFNTChecksums:
        assert originalSFNTChecksums[data] == checksum
    originalSFNTChecksums[data] = checksum

sfntCFFTableData, sfntCFFCompressedData, sfntCFFTableOrder, sfntCFFTableChecksums = getSFNTData(sfntCFFSourcePath)
for tag, checksum in sfntCFFTableChecksums.items():
    data = sfntCFFTableData[tag]
    if data in originalSFNTChecksums:
        assert originalSFNTChecksums[data] == checksum
    originalSFNTChecksums[data] = checksum

# --------
# Metadata
# --------

testDataWOFFMetadata = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
	<uniqueid id="org.w3.webfonts.wofftest" />
	<vendor name="Test Vendor" url="http://w3c.org/Fonts" />
	<credits>
		<credit name="Credit 1" role="Role 1" url="http://w3c.org/Fonts" />
		<credit name="Credit 2" role="Role 2" url="http://w3c.org/Fonts" />
	</credits>
	<description url="http://w3c.org/Fonts">
		<text>
			Description without language.
		</text>
		<text lang="en">
			Description with "en" language.
		</text>
		<text lang="fr">
			Description with "fr" language.
		</text>
	</description>
	<license url="http://w3c.org/Fonts" id="License ID">
		<text>
			License without language.
		</text>
		<text lang="en">
			License with "en" language.
		</text>
		<text lang="fr">
			License with "fr" language.
		</text>
	</license>
	<copyright>
		<text>
			Copyright without language.
		</text>
		<text lang="en">
			Copyright with "en" language.
		</text>
		<text lang="fr">
			Copyright with "fr" language.
		</text>
	</copyright>
	<trademark>
		<text>
			Trademark without language.
		</text>
		<text lang="en">
			Trademark with "en" language.
		</text>
		<text lang="fr">
			Trademark with "fr" language.
		</text>
	</trademark>
	<licensee name="Licensee Name" />
	<extension id="Extension 1">
		<name>Extension 1 - Name Without Language</name>
		<name lang="en">Extension 1 - Name With "en" Language</name>
		<name lang="fr">Extension 1 - Name With "fr" Language</name>
		<item id="Extension 1 - Item 1 ID">
			<name>Extension 1 - Item 1 - Name Without Language</name>
			<name lang="en">Extension 1 - Item 1 - Name With "en" Language</name>
			<name lang="fr">Extension 1 - Item 1 - Name With "fr" Language</name>
			<value>Extension 1 - Item 1 - Value Without Language</value>
			<value lang="en">Extension 1 - Item 1 - Value With "en" Language</value>
			<value lang="fr">Extension 1 - Item 1 - Value With "fr" Language</value>
		</item>
		<item id="Extension 1 - Item 2 ID">
			<name>Extension 1 - Item 2 - Name Without Language</name>
			<name lang="en">Extension 1 - Item 2 - Name With "en" Language</name>
			<name lang="fr">Extension 1 - Item 2 - Name With "fr" Language</name>
			<value>Extension 1 - Item 2 - Value Without Language</value>
			<value lang="en">Extension 1 - Item 2 - Value With "en" Language</value>
			<value lang="fr">Extension 1 - Item 2 - Value With "fr" Language</value>
		</item>
	</extension>
	<extension id="Extension 2">
		<name>Extension 2 - Name Without Language</name>
		<name lang="en">Extension 2 - Name With "en" Language</name>
		<name lang="fr">Extension 2 - Name With "fr" Language</name>
		<item id="Extension 2 - Item 1 ID">
			<name>Extension 2 - Item 1 - Name Without Language</name>
			<name lang="en">Extension 2 - Item 1 - Name With "en" Language</name>
			<name lang="fr">Extension 2 - Item 1 - Name With "fr" Language</name>
			<value>Extension 2 - Item 1 - Value Without Language</value>
			<value lang="en">Extension 2 - Item 1 - Value With "en" Language</value>
			<value lang="fr">Extension 2 - Item 1 - Value With "fr" Language</value>
		</item>
		<item id="Extension 2 - Item 2 ID">
			<name>Extension 2 - Item 2 - Name Without Language</name>
			<name lang="en">Extension 2 - Item 2 - Name With "en" Language</name>
			<name lang="fr">Extension 2 - Item 2 - Name With "fr" Language</name>
			<value>Extension 2 - Item 2 - Value Without Language</value>
			<value lang="en">Extension 2 - Item 2 - Value With "en" Language</value>
			<value lang="fr">Extension 2 - Item 2 - Value With "fr" Language</value>
		</item>
		<item id="Extension 2 - Item 3 ID">
			<name>Extension 2 - Item 3 - Name Without Language</name>
			<name lang="en">Extension 2 - Item 3 - Name With "en" Language</name>
			<name lang="fr">Extension 2 - Item 3 - Name With "fr" Language</name>
			<value>Extension 2 - Item 3 - Value Without Language</value>
			<value lang="en">Extension 2 - Item 3 - Value With "en" Language</value>
		</item>
	</extension>
</metadata>
""".strip()

# ------------
# Private Data
# ------------

testDataWOFFPrivateData = "\0" * 100

# -----------------------
# Default Data Structures
# -----------------------

# WOFF

testDataWOFFHeader = dict(
    signature="wOF2",
    flavor="OTTO",
    length=0,
    reserved=0,
    numTables=0,
    totalSfntSize=0,
    totalCompressedSize=0,
    majorVersion=0,
    minorVersion=0,
    metaOffset=0,
    metaLength=0,
    metaOrigLength=0,
    privOffset=0,
    privLength=0
)

testTTFDataWOFFDirectory = []
for tag in sfntTTFTableOrder:
    d = dict(
        tag=tag,
        origLength=0,
        transformLength=0,
        transformFlag=0,
    )
    testTTFDataWOFFDirectory.append(d)

testCFFDataWOFFDirectory = []
for tag in sfntCFFTableOrder:
    d = dict(
        tag=tag,
        origLength=0,
        transformLength=0,
        transformFlag=0,
    )
    testCFFDataWOFFDirectory.append(d)

# SFNT

testDataSFNTHeader = dict(
    sfntVersion="OTTO",
    numTables=0,
    searchRange=0,
    entrySelector=0,
    rangeShift=0
)

testTTFDataSFNTDirectory = []
for tag in sfntTTFTableOrder:
    d = dict(
        tag=tag,
        offset=0,
        length=0,
        checksum=0
    )
    testTTFDataSFNTDirectory.append(d)

testCFFDataSFNTDirectory = []
for tag in sfntCFFTableOrder:
    d = dict(
        tag=tag,
        offset=0,
        length=0,
        checksum=0
    )
    testCFFDataSFNTDirectory.append(d)

# --------------------
# Default Data Creator
# --------------------

def defaultTestData(header=None, directory=None, collectionHeader=None, collectionDirectory=None, tableData=None, compressedData=None, metadata=None, privateData=None, flavor="cff", Base128Bug=False, knownTags=knownTableTags, skipTransformLength=False):
    isCollection = collectionDirectory is not None
    parts = []
    # setup the header
    if header is None:
        header = deepcopy(testDataWOFFHeader)
    parts.append(header)
    # setup the directory
    if directory is None:
        if flavor == "cff":
            directory = deepcopy(testCFFDataWOFFDirectory)
        else:
            directory = deepcopy(testTTFDataWOFFDirectory)
    parts.append(directory)
    if isCollection:
        if collectionHeader is None:
            collectionHeader = dict(version=0x00010000, numFonts=len(collectionDirectory))
        parts.append(collectionHeader)
        parts.append(collectionDirectory)
    # setup the table data
    if tableData is None:
        if flavor == "cff":
            tableData = deepcopy(sfntCFFTableData)
        else:
            tableData = deepcopy(sfntTTFTableData)
    if compressedData is None:
        if flavor == "cff":
            compressedData = deepcopy(sfntCFFCompressedData)
        else:
            compressedData = deepcopy(sfntTTFCompressedData)
    parts.append(compressedData)
    # sanity checks
    assert len(directory) == len(tableData)
    if not isCollection:
        assert set(tableData.keys()) == set([entry["tag"] for entry in directory])
    # apply the directory data to the header
    header["numTables"] = len(directory)
    if isCollection:
        header["flavor"] = "ttcf"
    elif "CFF " in tableData:
        header["flavor"] = "OTTO"
    else:
        header["flavor"] = "\000\001\000\000"
    # apply the table data to the directory and the header
    if isCollection:
        # TTC header
        header["totalSfntSize"] = 12 + 4 * collectionHeader["numFonts"]
        header["totalSfntSize"] += sfntDirectorySize * collectionHeader["numFonts"]
        for entry in collectionDirectory:
            header["totalSfntSize"] += sfntDirectoryEntrySize * entry["numTables"]
    else:
        header["totalSfntSize"] = sfntDirectorySize + (len(directory) * sfntDirectoryEntrySize)
    header["totalCompressedSize"] = len(compressedData)
    for i, entry in enumerate(directory):
        tag = entry["tag"]
        if isCollection:
            origData, transformData = tableData[i][1]
        else:
            origData, transformData = tableData[tag]
        entry["origLength"] = len(origData)
        entry["transformLength"] = len(transformData)
        if tag == "hmtx" and entry["origLength"] > entry["transformLength"]:
            entry["transformFlag"] = 1
        header["totalSfntSize"] += entry["origLength"]
        header["totalSfntSize"] += calcPaddingLength(header["totalSfntSize"])
    header["length"] = woffHeaderSize + len(packTestDirectory(directory, knownTags=knownTags, skipTransformLength=skipTransformLength, Base128Bug=Base128Bug))
    if isCollection:
        header["length"] += len(packTestCollectionHeader(collectionHeader))
        header["length"] += len(packTestCollectionDirectory(collectionDirectory))
    header["length"] += len(compressedData)
    header["length"] += calcPaddingLength(header["length"])
    # setup the metadata
    if metadata is not None:
        if isinstance(metadata, tuple):
            metadata, compMetadata = metadata
        else:
            compMetadata = None
        if compMetadata is None:
            compMetadata = brotli.compress(metadata, brotli.MODE_TEXT)
        header["metaOffset"] = header["length"]
        header["metaLength"] = len(compMetadata)
        header["metaOrigLength"] = len(metadata)
        header["length"] += len(compMetadata)
        if privateData is not None:
            header["length"] += calcPaddingLength(len(compMetadata))
        parts.append((metadata, compMetadata))
    # setup the private data
    if privateData is not None:
        header["privOffset"] = header["length"]
        header["privLength"] = len(privateData)
        header["length"] += len(privateData)
        parts.append(privateData)
    # return the parts
    return parts

# -------------------------
# Default SFNT Data Creator
# -------------------------

def defaultSFNTTestData(tableData=None, flavor="cff"):
    parts = []
    # setup the header
    header = deepcopy(testDataSFNTHeader)
    parts.append(header)
    # setup the directory
    if flavor == "cff":
        directory = deepcopy(testCFFDataSFNTDirectory)
    else:
        directory = deepcopy(testTTFDataSFNTDirectory)
    parts.append(directory)
    # setup the table data
    if tableData is None:
        if flavor == "cff":
            tableData = deepcopy(sfntCFFTableData)
        else:
            tableData = deepcopy(sfntTTFTableData)
    for tag, (data, transformData) in tableData.items():
        tableData[tag] = data
    parts.append(tableData)
    # sanity checks
    assert len(directory) == len(tableData)
    assert set(tableData.keys()) == set([entry["tag"] for entry in directory])
    # apply the directory data to the header
    header["numTables"] = len(directory)
    if flavor == "cff":
        header["flavor"] = "OTTO"
    else:
        header["flavor"] = "\000\001\000\000"
    # apply the table data to the directory and the header
    offset = sfntDirectorySize + (len(directory) * sfntDirectoryEntrySize)
    for entry in directory:
        tag = entry["tag"]
        data = tableData[tag]
        length = len(data)
        # measure
        paddedLength = length + calcPaddingLength(length)
        # store
        entry["offset"] = offset
        entry["length"] = length
        if data in originalSFNTChecksums:
            checksum = originalSFNTChecksums[data]
        else:
            checksum = calcTableChecksum(tag, data)
        entry["checksum"] = checksum
        # next
        offset += paddedLength
    # return the parts
    return parts
