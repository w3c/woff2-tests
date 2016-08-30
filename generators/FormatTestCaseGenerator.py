"""
This script generates the format test cases. It will create a directory
one level up from the directory containing this script called "Format".
That directory will have the structure:

    /Format
        README.txt - information about how the tests were generated and how they should be modified
        /Tests
            testcaseindex.xht - index of all test cases
            test-case-name-number.woff2 - individual WOFF test case
            /resources
                index.css - index CSS file

Within this script, each test case is generated with a call to the
writeTest function or the writeMetadataTest function. In these,
WOFF data must be passed along with details about the data.
This function will generate the WOFF and register the case in
the suite index.
"""

import os
import shutil
import glob
import struct
import zipfile
from fontTools.misc import sstruct
from testCaseGeneratorLib.woff import packTestHeader, packTestDirectory, packTestMetadata, packTestPrivateData
from testCaseGeneratorLib.defaultData import defaultTestData, testDataWOFFMetadata, testDataWOFFPrivateData
from testCaseGeneratorLib.paths import resourcesDirectory, formatDirectory, formatTestDirectory, formatResourcesDirectory
from testCaseGeneratorLib.html import generateFormatIndexHTML, expandSpecLinks
from testCaseGeneratorLib import sharedCases
from testCaseGeneratorLib.sharedCases import *

# ------------------
# Directory Creation
# (if needed)
# ------------------

if not os.path.exists(formatDirectory):
    os.makedirs(formatDirectory)
if not os.path.exists(formatTestDirectory):
    os.makedirs(formatTestDirectory)
if not os.path.exists(formatResourcesDirectory):
    os.makedirs(formatResourcesDirectory)

# -------------------
# Move HTML Resources
# -------------------

# index css
destPath = os.path.join(formatResourcesDirectory, "index.css")
if os.path.exists(destPath):
    os.remove(destPath)
shutil.copy(os.path.join(resourcesDirectory, "index.css"), destPath)

# ---------------
# Test Case Index
# ---------------

# As the tests are generated a log will be kept.
# This log will be translated into an index after
# all of the tests have been written.

groupDefinitions = [
    # identifier, title, spec section
    ("valid", "Valid WOFFs", None),
    ("header", "WOFF Header Tests", expandSpecLinks("#woff20Header")),
    ("blocks", "WOFF Data Block Tests", expandSpecLinks("#FileStructure")),
    ("directory", "WOFF Table Directory Tests", expandSpecLinks("#table_dir_format")),
    ("tabledata", "WOFF Table Data Tests", expandSpecLinks("#DataTables")),
    ("metadata", "WOFF Metadata Tests", expandSpecLinks("#Metadata")),
    ("privatedata", "WOFF Private Data Tests", expandSpecLinks("#Private"))
]

testRegistry = {}
for group in groupDefinitions:
    tag = group[0]
    testRegistry[tag] = []

# -----------------
# Test Case Writing
# -----------------

registeredIdentifiers = set()
registeredTitles = set()
registeredDescriptions = set()

def writeTest(identifier, title, description, data, specLink=None, credits=[], valid=False):
    """
    This function generates all of the files needed by a test case and
    registers the case with the suite. The arguments:

    identifier: The identifier for the test case. The identifier must be
    a - separated sequence of group name (from the groupDefinitions
    listed above), test case description (arbitrary length) and a number
    to make the name unique. The number should be zero padded to a length
    of three characters (ie "001" instead of "1").

    title: A thorough, but not too long, title for the test case.

    description: A detailed statement about what the test case is proving.

    data: The complete binary data for the WOFF2.

    specLink: A space separated list of anchors that the test case is testing. Assumed to
    refer to the WOFF2 spec unless prefixed "woff1:".

    credits: A list of dictionaries defining the credits for the test case. The
    dictionaries must have this form:

        title="Name of the autor or reviewer",
        role="author or reviewer",
        link="mailto:email or http://contactpage"

    valid: A boolean indicating if the WOFF2 is valid.
    """

    print "Compiling %s..." % identifier
    assert identifier not in registeredIdentifiers, "Duplicate identifier! %s" % identifier
    assert title not in registeredTitles, "Duplicate title! %s" % title
    assert description not in registeredDescriptions, "Duplicate description! %s" % description
    registeredIdentifiers.add(identifier)
    registeredTitles.add(title)
    registeredDescriptions.add(description)

    specLink = expandSpecLinks(specLink)

    # generate the WOFF
    woffPath = os.path.join(formatTestDirectory, identifier) + ".woff2"
    f = open(woffPath, "wb")
    f.write(data)
    f.close()

    # register the test
    tag = identifier.split("-")[0]
    testRegistry[tag].append(
        dict(
            identifier=identifier,
            title=title,
            description=description,
            valid=valid,
            specLink=specLink
        )
    )

def writeMetadataTest(identifier, title=None, description=None, credits=[], specLink=None, valid=False, metadata=None):
    """
    This is a convenience functon that eliminates the need to
    make a complete WOFF when only the metadata is being tested.
    Refer to the writeTest documentation for the meaning of the
    various arguments.
    """
    # dynamically get some data from the shared cases as needed
    if title is None:
        assert description is None
        assert metadata is None
        parts = identifier.split("-")
        assert parts[0] == "metadata"
        number = int(parts[-1])
        group = parts[1:-1]
        group = [i.title() for i in group]
        group = "".join(group)
        importBase = "metadata" + group + str(number)
        title = getattr(sharedCases, importBase + "Title")
        description = getattr(sharedCases, importBase + "Description")
        credits = getattr(sharedCases, importBase + "Credits")
        metadata = getattr(sharedCases, importBase + "Metadata")
    assert metadata is not None
    assert valid is not None
    # compile the WOFF
    data, metadata = makeMetadataTest(metadata)
    # pass to the more verbose function
    if specLink is None:
        specLink = "#Metadata"
    kwargs = dict(
        title=title,
        description=description,
        credits=credits,
        specLink=specLink,
        valid=valid,
        data=data
    )
    writeTest(
        identifier,
        **kwargs
    )

# -----------
# Valid Files
# -----------

# CFF

writeTest(
    identifier="valid-001",
    title=makeValidWOFF1Title,
    description=makeValidWOFF1Description,
    credits=makeValidWOFF1Credits,
    valid=True,
    specLink="#conform-metadata-optional #conform-private",
    data=makeValidWOFF1()
)

writeTest(
    identifier="valid-002",
    title=makeValidWOFF2Title,
    description=makeValidWOFF2Description,
    credits=makeValidWOFF2Credits,
    valid=True,
    data=makeValidWOFF2(),
)

writeTest(
    identifier="valid-003",
    title=makeValidWOFF3Title,
    description=makeValidWOFF3Description,
    credits=makeValidWOFF3Credits,
    valid=True,
    data=makeValidWOFF3()
)

writeTest(
    identifier="valid-004",
    title=makeValidWOFF4Title,
    description=makeValidWOFF4Description,
    credits=makeValidWOFF4Credits,
    valid=True,
    data=makeValidWOFF4(),
)

# TTF

writeTest(
    identifier="valid-005",
    title=makeValidWOFF5Title,
    description=makeValidWOFF5Description,
    credits=makeValidWOFF5Credits,
    valid=True,
    specLink="#conform-metadata-optional #conform-private",
    data=makeValidWOFF5()
)

writeTest(
    identifier="valid-006",
    title=makeValidWOFF6Title,
    description=makeValidWOFF6Description,
    credits=makeValidWOFF6Credits,
    valid=True,
    data=makeValidWOFF6(),
)

writeTest(
    identifier="valid-007",
    title=makeValidWOFF7Title,
    description=makeValidWOFF7Description,
    credits=makeValidWOFF7Credits,
    valid=True,
    data=makeValidWOFF7()
)

writeTest(
    identifier="valid-008",
    title=makeValidWOFF8Title,
    description=makeValidWOFF8Description,
    credits=makeValidWOFF8Credits,
    valid=True,
    data=makeValidWOFF8(),
)

# ---------------------------------
# File Structure: Header: signature
# ---------------------------------

writeTest(
    identifier="header-signature-001",
    title=makeHeaderInvalidSignature1Title,
    description=makeHeaderInvalidSignature1Description,
    credits=makeHeaderInvalidSignature1Credits,
    valid=False,
    specLink="#conform-magicNumber",
    data=makeHeaderInvalidSignature1()
)

# ------------------------------
# File Structure: Header: flavor
# ------------------------------

# TTF flavor but CFF data

def makeHeaderInvalidFlavor1():
    header, directory, tableData = defaultTestData()
    header["flavor"] = "\000\001\000\000"
    data = padData(packTestHeader(header) + packTestDirectory(directory) + tableData)
    return data

writeTest(
    identifier="header-flavor-001",
    title="Header Flavor Incorrectly Set to 0x00010000",
    description="The header flavor is set to 0x00010000 but the table data contains CFF data, not TTF data.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    valid=False,
    specLink="#woff20Header",
    data=makeHeaderInvalidFlavor1()
)

# CFF flavor but TTF data

def makeHeaderInvalidFlavor2():
    header, directory, tableData = defaultTestData(flavor="ttf")
    header["flavor"] = "OTTO"
    data = padData(packTestHeader(header) + packTestDirectory(directory) + tableData)
    return data

writeTest(
    identifier="header-flavor-002",
    title="Header Flavor Incorrectly Set to OTTO",
    description="The header flavor is set to OTTO but the table data contains TTF data, not CFF data.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    valid=False,
    specLink="#woff20Header",
    data=makeHeaderInvalidFlavor2()
)

# ------------------------------
# File Structure: Header: length
# ------------------------------

writeTest(
    identifier="header-length-001",
    title=makeHeaderInvalidLength1Title,
    description=makeHeaderInvalidLength1Description,
    credits=makeHeaderInvalidLength1Credits,
    valid=False,
    specLink="#woff20Header",
    data=makeHeaderInvalidLength1()
)

writeTest(
    identifier="header-length-002",
    title=makeHeaderInvalidLength2Title,
    description=makeHeaderInvalidLength2Description,
    credits=makeHeaderInvalidLength2Credits,
    valid=False,
    specLink="#woff20Header",
    data=makeHeaderInvalidLength2()
)

# ---------------------------------
# File Structure: Header: numTables
# ---------------------------------

writeTest(
    identifier="header-numTables-001",
    title=makeHeaderInvalidNumTables1Title,
    description=makeHeaderInvalidNumTables1Description,
    credits=makeHeaderInvalidNumTables1Credits,
    valid=False,
    specLink="#woff20Header",
    data=makeHeaderInvalidNumTables1()
)

# --------------------------------
# File Structure: Header: reserved
# --------------------------------

writeTest(
    identifier="header-reserved-001",
    title=makeHeaderInvalidReserved1Title,
    description=makeHeaderInvalidReserved1Description,
    credits=makeHeaderInvalidReserved1Credits,
    valid=False,
    specLink="#conform-mustSetReserved2Zero",
    data=makeHeaderInvalidReserved1()
)

# -----------------------------------------
# File Structure: Table Directory: Ordering
# -----------------------------------------

writeTest(
    identifier="directory-table-order-001",
    title="WOFF2 With Correct Table Order",
    description="A valid WOFF2 font with tables ordered correctly in the table directory",
    credits=[dict(title="Khaled Hosny", role="author", link="http://khaledhosny.org")],
    valid=True,
    specLink="#conform-tableOrdering",
    data=makeValidWOFF1()
)

writeTest(
    identifier="directory-table-order-002",
    title=makeWrongTableOrder1Title,
    description=makeWrongTableOrder1Description,
    credits=makeWrongTableOrder1Credits,
    valid=True,
    specLink="#conform-tableOrdering",
    data=makeWrongTableOrder1()
)

# --------------------------------------------
# File Structure: Data Blocks: Extraneous Data
# --------------------------------------------

# between table directory and table data

writeTest(
    identifier="blocks-extraneous-data-001",
    title=makeExtraneousData1Title,
    description=makeExtraneousData1Description,
    credits=makeExtraneousData1Credits,
    valid=False,
    specLink="#conform-noextraneous",
    data=makeExtraneousData1()
)

# after table data with no metadata or private data

writeTest(
    identifier="blocks-extraneous-data-002",
    title=makeExtraneousData2Title,
    description=makeExtraneousData2Description,
    credits=makeExtraneousData2Credits,
    valid=False,
    specLink="#conform-noextraneous",
    data=makeExtraneousData2()
)

# between tabledata and metadata

writeTest(
    identifier="blocks-extraneous-data-003",
    title=makeExtraneousData3Title,
    description=makeExtraneousData3Description,
    credits=makeExtraneousData3Credits,
    valid=False,
    specLink="#conform-noextraneous",
    data=makeExtraneousData3()
)

# between tabledata and private data

writeTest(
    identifier="blocks-extraneous-data-004",
    title=makeExtraneousData4Title,
    description=makeExtraneousData4Description,
    credits=makeExtraneousData4Credits,
    valid=False,
    specLink="#conform-noextraneous",
    data=makeExtraneousData4()
)

# between metadata and private data

writeTest(
    identifier="blocks-extraneous-data-005",
    title=makeExtraneousData5Title,
    description=makeExtraneousData5Description,
    credits=makeExtraneousData5Credits,
    valid=False,
    specLink="#conform-noextraneous",
    data=makeExtraneousData5()
)

# after metadata with no private data

writeTest(
    identifier="blocks-extraneous-data-006",
    title=makeExtraneousData6Title,
    description=makeExtraneousData6Description,
    credits=makeExtraneousData6Credits,
    valid=False,
    specLink="#conform-noextraneous",
    data=makeExtraneousData6()
)

# after private data

writeTest(
    identifier="blocks-extraneous-data-007",
    title=makeExtraneousData7Title,
    description=makeExtraneousData7Description,
    credits=makeExtraneousData7Credits,
    valid=False,
    specLink="#conform-noextraneous",
    data=makeExtraneousData7()
)

# before last table

writeTest(
    identifier="tabledata-extraneous-data-001",
    title=makeExtraneousData8Title,
    description=makeExtraneousData8Description,
    credits=makeExtraneousData8Credits,
    valid=False,
    specLink="#conform-noExtraData",
    data=makeExtraneousData8()
)

# -------------------------------------------------
# File Structure: Data Blocks: Metadata Not Present
# -------------------------------------------------

# metadata length = zero but the offset > zero

def makeMetadataZeroData2():
    header, directory, tableData = defaultTestData()
    header["metaLength"] = 0
    header["metaOffset"] = header["length"]
    data = padData(packTestHeader(header) + packTestDirectory(directory) + tableData)
    return data

writeTest(
    identifier="blocks-metadata-absent-002",
    title="Metadata Offset Not Set to Zero",
    description="The metadata length is set to zero but the offset is set to the end of the file.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    valid=False,
    specLink="#conform-metadata-afterfonttable",
    data=makeMetadataZeroData2()
)

# ---------------------------------------------
# File Structure: Data Blocks: Metadata Padding
# ---------------------------------------------

# padding after metadata but no private data

def makeMetadataPadding1():
    header, directory, tableData, metadata = defaultTestData(metadata=testDataWOFFMetadata)
    metadata = packTestMetadata(metadata)
    paddingLength = calcPaddingLength(len(metadata))
    assert paddingLength
    header["length"] += paddingLength
    metadata += "\0" * paddingLength
    data = padData(packTestHeader(header) + packTestDirectory(directory) + tableData) + metadata
    return data

writeTest(
    identifier="blocks-metadata-padding-001",
    title="Metadata Has Unnecessary Padding",
    description="The metadata block is padded to a four-byte boundary but there is no private data.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    valid=False,
    specLink="#conform-metadata-noprivatepad",
    data=makeMetadataPadding1()
)

writeTest(
    identifier="blocks-metadata-padding-002",
    title="Metadata Has No Padding",
    description="The metadata block is not padded and there is no private data.",
    credits=[dict(title="Khaled Hosny", role="author", link="http://khaledhosny.org")],
    valid=True,
    specLink="#conform-metadata-noprivatepad",
    data=makeValidWOFF2()
)

writeTest(
    identifier="blocks-metadata-padding-003",
    title="Metadata Has Correct Padding",
    description="The metadata block is padded to a four-byte boundary and there is private data.",
    credits=[dict(title="Khaled Hosny", role="author", link="http://khaledhosny.org")],
    valid=True,
    specLink="#conform-metadata-noprivatepad",
    data=makeValidWOFF4()
)

def makeMetadataPadding2():
    header, directory, tableData, metadata = defaultTestData(metadata=testDataWOFFMetadata)
    metadata = packTestMetadata(metadata)
    data = packTestHeader(header) + packTestDirectory(directory) + tableData
    assert calcPaddingLength(len(data)) != 0
    data += metadata
    return data

writeTest(
    identifier="blocks-metadata-padding-004",
    title="Metadata Beginning Has No Padding",
    description="The beginning of the metadata block is not padded.",
    credits=[dict(title="Khaled Hosny", role="author", link="http://khaledhosny.org")],
    valid=False,
    specLink="#conform-metadata-padalign",
    data=makeMetadataPadding2()
)

# -------------------------------------
# File Structure: Data Blocks: Ordering
# -------------------------------------

# metadata after private

def makeDataBlockOrdering3():
    header, directory, tableData, metadata, privateData = defaultTestData(metadata=testDataWOFFMetadata, privateData=testDataWOFFPrivateData)
    # move the metadata
    header["privOffset"] = header["metaOffset"]
    privateLength = header["privLength"]
    header["metaOffset"] = header["privOffset"] + privateLength
    # remove padding
    assert calcPaddingLength(privateLength) == 0
    header["length"] -= calcPaddingLength(header["metaLength"])
    # pack
    data = padData(packTestHeader(header) + packTestDirectory(directory) + tableData) + packTestPrivateData(privateData) + metadata[1]
    # done
    return data

writeTest(
    identifier="blocks-ordering-003",
    title="Metadata After Private Data",
    description="The metadata block is stored after the private data block.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    valid=False,
    specLink="#conform-metadata-afterfonttable",
    data=makeDataBlockOrdering3()
)

writeTest(
    identifier="blocks-ordering-004",
    title="Private Data Before Metadata",
    description="The private data block is stored before the metadata block.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    valid=False,
    specLink="#conform-private-last",
    data=makeDataBlockOrdering3()
)

# -----------------------------------------
# File Structure: Data Blocks: Private Data
# -----------------------------------------

# private data not on 4-byte boundary

def makeDataBlockPrivateData1():
    header, directory, tableData, metadata, privateData = defaultTestData(metadata=testDataWOFFMetadata, privateData=testDataWOFFPrivateData)
    paddingLength = calcPaddingLength(header["metaLength"])
    assert paddingLength > 0
    header["length"] -= paddingLength
    header["privOffset"] -= paddingLength
    data = padData(packTestHeader(header) + packTestDirectory(directory) + tableData) + packTestMetadata(metadata)
    data += packTestPrivateData(privateData)
    return data

writeTest(
    identifier="blocks-private-001",
    title="Private Data Does Not Begin of 4-Byte Boundary",
    description="The private data does not begin on a four byte boundary because the metadata is not padded.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    valid=False,
    specLink="#conform-private-padalign",
    data=makeDataBlockPrivateData1()
)

# data after private data

def makeDataBlockPrivateData2():
    header, directory, tableData, privateData = defaultTestData(privateData=testDataWOFFPrivateData)
    header["length"] += 4
    data = padData(packTestHeader(header) + packTestDirectory(directory) + tableData) + packTestPrivateData(privateData)
    data += 4 * '\0'
    return data

writeTest(
    identifier="blocks-private-002",
    title="Data After Private Data",
    description="The private data does not correspond to the end of the WOFF2 file because there are 4 null bytes after it.",
    credits=[dict(title="Khaled Hosny", role="author", link="http://khaledhosny.org")],
    valid=False,
    specLink="#conform-private-end",
    data=makeDataBlockPrivateData2()
)

# ----------------------------------------------
# File Structure: Table Data: Compression Format
# ----------------------------------------------

# compression incompatible with Brotli

writeTest(
    identifier="tabledata-brotli-001",
    title=makeTableBrotliCompressionTest1Title,
    description=makeTableBrotliCompressionTest1Description,
    credits=makeTableBrotliCompressionTest1Credits,
    valid=False,
    specLink="#conform-mustUseBrotli-FontData",
    data=makeTableBrotliCompressionTest1()
)

# -----------------------------------------------
# File Structure: Table Data: Decompressed Length
# -----------------------------------------------

# decompressed length less than sum of origLength

writeTest(
    identifier="tabledata-decompressed-length-001",
    title=makeTableDecompressedLengthTest1Title,
    description=makeTableDecompressedLengthTest1Description,
    credits=makeTableDecompressedLengthTest1Credits,
    valid=False,
    specLink="#conform-mustMatchUncompressedSize",
    data=makeTableDecompressedLengthTest1()
)

# decompressed length greater than sum of origLength

writeTest(
    identifier="tabledata-decompressed-length-002",
    title=makeTableDecompressedLengthTest2Title,
    description=makeTableDecompressedLengthTest2Description,
    credits=makeTableDecompressedLengthTest2Credits,
    valid=False,
    specLink="#conform-mustMatchUncompressedSize",
    data=makeTableDecompressedLengthTest2()
)

# decompressed length less than sum of transformLength

writeTest(
    identifier="tabledata-decompressed-length-003",
    title=makeTableDecompressedLengthTest3Title,
    description=makeTableDecompressedLengthTest3Description,
    credits=makeTableDecompressedLengthTest3Credits,
    valid=False,
    specLink="#conform-mustMatchUncompressedSize",
    data=makeTableDecompressedLengthTest3()
)

# decompressed length greater than sum of transformLength

writeTest(
    identifier="tabledata-decompressed-length-004",
    title=makeTableDecompressedLengthTest4Title,
    description=makeTableDecompressedLengthTest4Description,
    credits=makeTableDecompressedLengthTest4Credits,
    valid=False,
    specLink="#conform-mustMatchUncompressedSize",
    data=makeTableDecompressedLengthTest4()
)

# -------------------------------------------
# File Structure: Table Data: Transformations
# -------------------------------------------

# loca's transformLength is not zero

writeTest(
    identifier="tabledata-transform-length-001",
    title=makeTableNonZeroLocaTest1Title,
    description=makeTableNonZeroLocaTest1Description,
    credits=makeTableNonZeroLocaTest1Credits,
    valid=False,
    specLink="#conform-transformedLocaMustBeZero",
    data=makeTableNonZeroLocaTest1()
)

def makeNoTransformLength():
    header, directory, tableData = defaultTestData(flavor="ttf", skipTransformLength=True)
    data = padData(packTestHeader(header) + packTestDirectory(directory, skipTransformLength=True) + tableData)
    return data

writeTest(
    identifier="tabledata-transform-length-002",
    title="Transform Length Is Not Set",
    description="The transformed tables does not have transformLength set.",
    credits=[dict(title="Khaled Hosny", role="author", link="http://khaledhosny.org")],
    valid=False,
    specLink="#conform-mustIncludeTransformLength",
    data=makeNoTransformLength()
)

writeTest(
    identifier="tabledata-loca-size-001",
    title=makeLocaSizeTest1Title,
    description=makeLocaSizeTest1Description,
    credits=makeLocaSizeTest1Credits,
    valid=True,
    specLink="#conform-OriginalLocaSize",
    data=makeLocaSizeTest1()
)

writeTest(
    identifier="tabledata-loca-size-002",
    title=makeLocaSizeTest2Title,
    description=makeLocaSizeTest2Description,
    credits=makeLocaSizeTest2Credits,
    valid=True,
    specLink="#conform-OriginalLocaSize",
    data=makeLocaSizeTest2()
)

writeTest(
    identifier="tabledata-loca-size-003",
    title=makeLocaSizeTest3Title,
    description=makeLocaSizeTest3Description,
    credits=makeLocaSizeTest3Credits,
    valid=True,
    specLink="#conform-OriginalLocaSize",
    data=makeLocaSizeTest3()
)

writeTest(
    identifier="tabledata-hmtx-transform-001",
    title=makeHmtxTransform1Title,
    description=makeHmtxTransform1Description,
    credits=makeHmtxTransform1Credits,
    valid=True,
    specLink="#conform-transformFlagsMustBeSet",
    data=makeHmtxTransform1()
)

writeTest(
    identifier="tabledata-hmtx-transform-002",
    title=makeHmtxTransform3Title,
    description=makeHmtxTransform3Description,
    credits=makeHmtxTransform3Credits,
    valid=False,
    specLink="#conform-transformFlagsMustBeSet",
    data=makeHmtxTransform3()
)

writeTest(
    identifier="tabledata-hmtx-transform-003",
    title=makeHmtxTransform2Title,
    description=makeHmtxTransform2Description,
    credits=makeHmtxTransform2Credits,
    valid=False,
    specLink="#conform-reservedFlagsMustBeZero",
    data=makeHmtxTransform2()
)

def makeMismatchedLocaGlyfTransform(tag):
    tableData, compressedData, tableOrder, tableChecksums = getSFNTData(sfntTTFSourcePath)
    tagData = tableData[tag]
    header, directory, tableData = defaultTestData(flavor="ttf")
    decompressedTableData = brotli.decompress(tableData)
    offset = 0
    for entry in directory:
        if entry["tag"] == tag:
            decompressedTableData = decompressedTableData[:offset] + tagData[0] + decompressedTableData[offset:]
            entry["transformLength"] = entry["origLength"]
            entry["transformFlag"] = 3
        offset += entry["transformLength"]

    tableData = brotli.compress(decompressedTableData, brotli.MODE_FONT)

    header["length"] = woffHeaderSize + len(packTestDirectory(directory)) + len(tableData)
    header["length"] += calcPaddingLength(header["length"])
    header["totalCompressedSize"] = len(tableData)

    data = padData(packTestHeader(header) + packTestDirectory(directory) + tableData)
    return data

writeTest(
    identifier="tabledata-transform-glyf-loca-001",
    title="Transformed Glyf With Unransformed Loca",
    description="The glyf table is transformed while loca table is not.",
    credits=[dict(title="Khaled Hosny", role="author", link="http://khaledhosny.org")],
    valid=False,
    specLink="#conform-transformedLocaMustAccompanyGlyf",
    data=makeMismatchedLocaGlyfTransform("loca")
)

writeTest(
    identifier="tabledata-transform-glyf-loca-002",
    title="Transformed Loca With Unransformed Glyf",
    description="The glyf table is not transformed while loca table is transformed.",
    credits=[dict(title="Khaled Hosny", role="author", link="http://khaledhosny.org")],
    valid=False,
    specLink="#conform-transformedLocaMustAccompanyGlyf",
    data=makeMismatchedLocaGlyfTransform("glyf")
)

# composite glyph with bbox
writeTest(
    identifier="tabledata-glyf-composite-bbox-001",
    title=makeGlyfBBox1Title,
    description=makeGlyfBBox1Description,
    credits=makeGlyfBBox1Credits,
    valid=True,
    specLink="#conform-mustHaveCompositeBBox",
    data=makeGlyfBBox1()
)

# -----------------
# Metadata: Padding
# -----------------

# metadata not padded with null bytes

def makeMetadataPadding1():
    header, directory, tableData, metadata, privateData = defaultTestData(metadata=testDataWOFFMetadata, privateData=testDataWOFFPrivateData)
    paddingLength = calcPaddingLength(header["metaLength"])
    assert paddingLength > 0
    metadata, compMetadata = metadata
    compMetadata += ("\x01" * paddingLength)
    metadata = (metadata, compMetadata)
    data = padData(packTestHeader(header) + packTestDirectory(directory) + tableData) + packTestMetadata(metadata) + packTestPrivateData(privateData)
    return data

writeTest(
    identifier="metadata-padding-001",
    title="Padding Between Metadata and Private Data is Non-Null",
    description="Metadata is padded with \\01 instead of \\00.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    valid=False,
    specLink="#conform-private-padalign",
    data=makeMetadataPadding1()
)

# -----------------------------
# Metadata Display: Compression
# -----------------------------

writeTest(
    identifier="metadata-compression-001",
    title=makeMetadataCompression1Title,
    description=makeMetadataCompression1Description,
    credits=makeMetadataCompression1Credits,
    valid=False,
    data=makeMetadataCompression1(),
    specLink="woff1:#conform-metadata-alwayscompress"
)

writeTest(
    identifier="metadata-compression-002",
    title=makeMetadataCompression2Title,
    description=makeMetadataCompression2Description,
    credits=makeMetadataCompression2Credits,
    valid=False,
    data=makeMetadataCompression2(),
    specLink="#conform-mustBeBrotliCompressedMetadata"
)

# --------------------------------
# Metadata Display: metaOrigLength
# --------------------------------

# <

writeTest(
    identifier="metadata-metaOrigLength-001",
    title=makeMetaOrigLengthTest1Title,
    description=makeMetaOrigLengthTest1Description,
    credits=makeMetaOrigLengthTest1Credits,
    valid=False,
    specLink="woff1:#conform-metaOrigLength",
    data=makeMetaOrigLengthTest1()
)

# >

writeTest(
    identifier="metadata-metaOrigLength-002",
    title=makeMetaOrigLengthTest2Title,
    description=makeMetaOrigLengthTest2Description,
    credits=makeMetaOrigLengthTest2Credits,
    valid=False,
    specLink="woff1:#conform-metaOrigLength",
    data=makeMetaOrigLengthTest2()
)

# -----------------------------
# Metadata Display: Well-Formed
# -----------------------------

# <

writeMetadataTest(
    identifier="metadata-well-formed-001",
    specLink="woff1:#conform-metaOrigLength",
    valid=False,
)

# &

writeMetadataTest(
    identifier="metadata-well-formed-002",
    specLink="woff1:#conform-metaOrigLength",
    valid=False,
)

# mismatched elements

writeMetadataTest(
    identifier="metadata-well-formed-003",
    specLink="woff1:#conform-metaOrigLength",
    valid=False,
)

# unclosed element

writeMetadataTest(
    identifier="metadata-well-formed-004",
    specLink="woff1:#conform-metaOrigLength",
    valid=False,
)

# case mismatch

writeMetadataTest(
    identifier="metadata-well-formed-005",
    specLink="woff1:#conform-metaOrigLength",
    valid=False,
)

# more than one root

writeMetadataTest(
    identifier="metadata-well-formed-006",
    specLink="woff1:#conform-metaOrigLength",
    valid=False,
)

# unknown encoding

writeMetadataTest(
    identifier="metadata-well-formed-007",
    specLink="woff1:#conform-metaOrigLength",
    valid=False,
)

# --------------------------
# Metadata Display: Encoding
# --------------------------

# UTF-8

writeMetadataTest(
    identifier="metadata-encoding-001",
    specLink="woff1:#conform-metadata-encoding",
    valid=True,
)

# Invalid encoding: UTF-16

writeMetadataTest(
    identifier="metadata-encoding-002",
    specLink="woff1:#conform-metadata-encoding",
    valid=False,
)

# Invalid encoding: ISO-8859-1
writeMetadataTest(
    identifier="metadata-encoding-003",
    specLink="woff1:#conform-metadata-encoding",
    valid=False,
)

# no encoding; implicit UTF-8

writeMetadataTest(
    identifier="metadata-encoding-004",
    specLink="woff1:#conform-metadata-encoding",
    valid=True,
)

# UTF-8 BOM

writeMetadataTest(
    identifier="metadata-encoding-005",
    specLink="woff1:#conform-metadata-encoding",
    valid=True,
)

# UTF-16 BOM

writeMetadataTest(
    identifier="metadata-encoding-006",
    specLink="woff1:#conform-metadata-encoding",
    valid=False,
)

# -------------------------------------------
# Metadata Display: Schema Validity: metadata
# -------------------------------------------

# valid

writeMetadataTest(
    identifier="metadata-schema-metadata-001",
    specLink="woff1:#conform-metadata-wellformed",
    valid=True,
)

# top element not metadata

writeMetadataTest(
    identifier="metadata-schema-metadata-002",
    specLink="woff1:#conform-metadataelement-required",
    valid=False,
)

# missing version

writeMetadataTest(
    identifier="metadata-schema-metadata-003",
    specLink="woff1:#conform-metadataversion-required",
    valid=False,
)

# invalid version

writeMetadataTest(
    identifier="metadata-schema-metadata-004",
    specLink="woff1:#conform-metadata-schemavalid",
    valid=False,
)

# unknown attribute

writeMetadataTest(
    identifier="metadata-schema-metadata-005",
    specLink="woff1:#conform-metadata-schemavalid",
    valid=False,
)

# unknown element

writeMetadataTest(
    identifier="metadata-schema-metadata-006",
    specLink="woff1:#conform-metadata-schemavalid",
    valid=False,
)

# -------------------------------------------
# Metadata Display: Schema Validity: uniqueid
# -------------------------------------------

# valid

writeMetadataTest(
    identifier="metadata-schema-uniqueid-001",
    specLink="woff1:#conform-metadata-schemavalid",
    valid=True,
)

# does not exist

writeMetadataTest(
    identifier="metadata-schema-uniqueid-002",
    #TODO: link
    valid=True,
)

# duplicate

writeMetadataTest(
    identifier="metadata-schema-uniqueid-003",
    specLink="woff1:#conform-metadata-schemavalid",
    valid=False,
)

# missing id attribute

writeMetadataTest(
    identifier="metadata-schema-uniqueid-004",
    specLink="woff1:#conform-metadata-id-required",
    valid=False,
)

# unknown attribute

writeMetadataTest(
    identifier="metadata-schema-uniqueid-005",
    specLink="woff1:#conform-metadata-schemavalid",
    valid=False,
)

# unknown child

writeMetadataTest(
    identifier="metadata-schema-uniqueid-006",
    specLink="woff1:#conform-metadata-schemavalid",
    valid=False,
)

# content

writeMetadataTest(
    identifier="metadata-schema-uniqueid-007",
    specLink="woff1:#conform-metadata-schemavalid",
    valid=False,
)

# -----------------------------------------
# Metadata Display: Schema Validity: vendor
# -----------------------------------------

# valid

writeMetadataTest(
    identifier="metadata-schema-vendor-001",
    valid=True,
)

writeMetadataTest(
    identifier="metadata-schema-vendor-002",
    valid=True,
)

# does not exist

writeMetadataTest(
    identifier="metadata-schema-vendor-003",
    valid=True,
)

# duplicate

writeMetadataTest(
    identifier="metadata-schema-vendor-004",
    specLink="woff1:#conform-metadata-schemavalid",
    valid=False,
)

# missing name attribute

writeMetadataTest(
    identifier="metadata-schema-vendor-005",
    specLink="woff1:#conform-metadata-vendor-required",
    valid=False,
)

# dir attribute

writeMetadataTest(
    identifier="metadata-schema-vendor-006",
    valid=True,
)

writeMetadataTest(
    identifier="metadata-schema-vendor-007",
    valid=True,
)

writeMetadataTest(
    identifier="metadata-schema-vendor-008",
    valid=False,
)

# class attribute

writeMetadataTest(
    identifier="metadata-schema-vendor-009",
    valid=True,
)

# unknown attribute

writeMetadataTest(
    identifier="metadata-schema-vendor-010",
    specLink="woff1:#conform-metadata-schemavalid",
    valid=False,
)

# unknown child

writeMetadataTest(
    identifier="metadata-schema-vendor-011",
    specLink="woff1:#conform-metadata-schemavalid",
    valid=False,
)

# content

writeMetadataTest(
    identifier="metadata-schema-vendor-012",
    specLink="woff1:#conform-metadata-schemavalid",
    valid=False,
)

# ------------------------------------------
# Metadata Display: Schema Validity: credits
# ------------------------------------------

# valid - single credit element

writeMetadataTest(
    identifier="metadata-schema-credits-001",
    specLink="woff1:#conform-metadata-schemavalid woff1:#conform-textlang",
    valid=True,
)

# valid - multiple credit elements

writeMetadataTest(
    identifier="metadata-schema-credits-002",
    valid=True,
)

# missing credit element

writeMetadataTest(
    identifier="metadata-schema-credits-003",
    specLink="woff1:#conform-metadata-schemavalid",
    valid=False,
)

# unknown attribute

writeMetadataTest(
    identifier="metadata-schema-credits-004",
    specLink="woff1:#conform-metadata-schemavalid",
    valid=False,
)

# unknown element

writeMetadataTest(
    identifier="metadata-schema-credits-005",
    specLink="woff1:#conform-metadata-schemavalid",
    valid=False,
)

# content

writeMetadataTest(
    identifier="metadata-schema-credits-006",
    specLink="woff1:#conform-metadata-schemavalid",
    valid=False,
)

# multiple credits

writeMetadataTest(
    identifier="metadata-schema-credits-007",
    specLink="woff1:#conform-metadata-schemavalid",
    valid=False,
)

# -----------------------------------------
# Metadata Display: Schema Validity: credit
# -----------------------------------------

# valid

writeMetadataTest(
    identifier="metadata-schema-credit-001",
    valid=True,
)

# valid no url

writeMetadataTest(
    identifier="metadata-schema-credit-002",
    valid=True,
)

# valid no role

writeMetadataTest(
    identifier="metadata-schema-credit-003",
    valid=True,
)

# no name

writeMetadataTest(
    identifier="metadata-schema-credit-004",
    specLink="woff1:#conform-creditnamerequired",
    valid=False,
)

# dir attribute

writeMetadataTest(
    identifier="metadata-schema-credit-005",
    valid=True,
)

writeMetadataTest(
    identifier="metadata-schema-credit-006",
    valid=True,
)

writeMetadataTest(
    identifier="metadata-schema-credit-007",
    valid=False,
)

# class attribute

writeMetadataTest(
    identifier="metadata-schema-credit-008",
    valid=True,
)

# unknown attribute

writeMetadataTest(
    identifier="metadata-schema-credit-009",
    specLink="woff1:#conform-metadata-schemavalid",
    valid=False,
)

# child element

writeMetadataTest(
    identifier="metadata-schema-credit-010",
    specLink="woff1:#conform-metadata-schemavalid",
    valid=False,
)

# content

writeMetadataTest(
    identifier="metadata-schema-credit-011",
    specLink="woff1:#conform-metadata-schemavalid",
    valid=False,
)

# ----------------------------------------------
# Metadata Display: Schema Validity: description
# ----------------------------------------------

# valid with url

writeMetadataTest(
    identifier="metadata-schema-description-001",
    valid=True,
)

# valid without url

writeMetadataTest(
    identifier="metadata-schema-description-002",
    valid=True,
)

# valid one text element no language

writeMetadataTest(
    identifier="metadata-schema-description-003",
    valid=True,
)

# valid one text element with language

writeMetadataTest(
    identifier="metadata-schema-description-004",
    valid=True,
)

# valid one text element with language using lang

writeMetadataTest(
    identifier="metadata-schema-description-005",
    valid=True,
)

# valid two text elements no language and language

writeMetadataTest(
    identifier="metadata-schema-description-006",
    valid=True,
)

# valid two text elements language and language

writeMetadataTest(
    identifier="metadata-schema-description-007",
    valid=True,
)

# more than one description

writeMetadataTest(
    identifier="metadata-schema-description-008",
    specLink="woff1:#conform-metadata-schemavalid",
    valid=False,
)

# no text element

writeMetadataTest(
    identifier="metadata-schema-description-009",
    specLink="woff1:#conform-localizable-text-required",
    valid=False,
)

# unknown attribute

writeMetadataTest(
    identifier="metadata-schema-description-010",
    specLink="woff1:#conform-metadata-schemavalid",
    valid=False,
)

# unknown child element

writeMetadataTest(
    identifier="metadata-schema-description-011",
    specLink="woff1:#conform-metadata-schemavalid",
    valid=False,
)

# content

writeMetadataTest(
    identifier="metadata-schema-description-012",
    specLink="woff1:#conform-metadata-schemavalid",
    valid=False,
)

# dir attribute

writeMetadataTest(
    identifier="metadata-schema-description-013",
    specLink="woff1:#conform-metadata-schemavalid",
    valid=True,
)

writeMetadataTest(
    identifier="metadata-schema-description-014",
    specLink="woff1:#conform-metadata-schemavalid",
    valid=True,
)

writeMetadataTest(
    identifier="metadata-schema-description-015",
    specLink="woff1:#conform-metadata-schemavalid",
    valid=False,
)

# class attribute

writeMetadataTest(
    identifier="metadata-schema-description-016",
    specLink="woff1:#conform-metadata-schemavalid",
    valid=True,
)

# text element unknown attribute

writeMetadataTest(
    identifier="metadata-schema-description-017",
    specLink="woff1:#conform-metadata-schemavalid",
    valid=False,
)

# text element child element

writeMetadataTest(
    identifier="metadata-schema-description-018",
    specLink="woff1:#conform-metadata-schemavalid",
    valid=False,
)

# one div

writeMetadataTest(
    identifier="metadata-schema-description-019",
    specLink="woff1:#conform-metadata-schemavalid",
    valid=True,
)

# two div

writeMetadataTest(
    identifier="metadata-schema-description-020",
    specLink="woff1:#conform-metadata-schemavalid",
    valid=True,
)

# nested div

writeMetadataTest(
    identifier="metadata-schema-description-021",
    specLink="woff1:#conform-metadata-schemavalid",
    valid=True,
)

# div with dir

writeMetadataTest(
    identifier="metadata-schema-description-022",
    specLink="woff1:#conform-metadata-schemavalid",
    valid=True,
)

writeMetadataTest(
    identifier="metadata-schema-description-023",
    specLink="woff1:#conform-metadata-schemavalid",
    valid=True,
)

writeMetadataTest(
    identifier="metadata-schema-description-024",
    specLink="woff1:#conform-metadata-schemavalid",
    valid=False,
)

# div with class

writeMetadataTest(
    identifier="metadata-schema-description-025",
    specLink="woff1:#conform-metadata-schemavalid",
    valid=True,
)

# one span

writeMetadataTest(
    identifier="metadata-schema-description-026",
    specLink="woff1:#conform-metadata-schemavalid",
    valid=True,
)

# two span

writeMetadataTest(
    identifier="metadata-schema-description-027",
    specLink="woff1:#conform-metadata-schemavalid",
    valid=True,
)

# nested span

writeMetadataTest(
    identifier="metadata-schema-description-028",
    specLink="woff1:#conform-metadata-schemavalid",
    valid=True,
)

# span with dir

writeMetadataTest(
    identifier="metadata-schema-description-029",
    specLink="woff1:#conform-metadata-schemavalid",
    valid=True,
)

writeMetadataTest(
    identifier="metadata-schema-description-030",
    specLink="woff1:#conform-metadata-schemavalid",
    valid=True,
)

writeMetadataTest(
    identifier="metadata-schema-description-031",
    specLink="woff1:#conform-metadata-schemavalid",
    valid=False,
)

# span with class

writeMetadataTest(
    identifier="metadata-schema-description-032",
    specLink="woff1:#conform-metadata-schemavalid",
    valid=True,
)

# ------------------------------------------
# Metadata Display: Schema Validity: license
# ------------------------------------------

# valid with url and license

writeMetadataTest(
    identifier="metadata-schema-license-001",
    valid=True,
)

# valid no url

writeMetadataTest(
    identifier="metadata-schema-license-002",
    valid=True,
)

# valid no id

writeMetadataTest(
    identifier="metadata-schema-license-003",
    valid=True,
)

# valid one text element no language

writeMetadataTest(
    identifier="metadata-schema-license-004",
    valid=True,
)

# valid one text element with language

writeMetadataTest(
    identifier="metadata-schema-license-005",
    valid=True,
)

# valid one text element with language using lang

writeMetadataTest(
    identifier="metadata-schema-license-006",
    valid=True,
)

# valid two text elements no language and language

writeMetadataTest(
    identifier="metadata-schema-license-007",
    valid=True,
)

# valid two text elements language and language

writeMetadataTest(
    identifier="metadata-schema-license-008",
    valid=True,
)

# more than one license

writeMetadataTest(
    identifier="metadata-schema-license-009",
    specLink="woff1:#conform-metadata-schemavalid",
    valid=False,
)

# no text element

writeMetadataTest(
    identifier="metadata-schema-license-010",
    specLink="woff1:#conform-localizable-text-required",
    valid=True,
)

# unknown attribute

writeMetadataTest(
    identifier="metadata-schema-license-011",
    specLink="woff1:#conform-metadata-schemavalid",
    valid=False,
)

# unknown child element

writeMetadataTest(
    identifier="metadata-schema-license-012",
    specLink="woff1:#conform-metadata-schemavalid",
    valid=False,
)

# content

writeMetadataTest(
    identifier="metadata-schema-license-013",
    specLink="woff1:#conform-metadata-schemavalid",
    valid=False,
)

# text element dir attribute

writeMetadataTest(
    identifier="metadata-schema-license-014",
    specLink="woff1:#conform-metadata-schemavalid",
    valid=True,
)

writeMetadataTest(
    identifier="metadata-schema-license-015",
    specLink="woff1:#conform-metadata-schemavalid",
    valid=True,
)

writeMetadataTest(
    identifier="metadata-schema-license-016",
    specLink="woff1:#conform-metadata-schemavalid",
    valid=False,
)

# text element class attribute

writeMetadataTest(
    identifier="metadata-schema-license-017",
    specLink="woff1:#conform-metadata-schemavalid",
    valid=True,
)

# text element unknown attribute

writeMetadataTest(
    identifier="metadata-schema-license-018",
    specLink="woff1:#conform-metadata-schemavalid",
    valid=False,
)

# text element child element

writeMetadataTest(
    identifier="metadata-schema-license-019",
    specLink="woff1:#conform-metadata-schemavalid",
    valid=False,
)

# one div

writeMetadataTest(
    identifier="metadata-schema-license-020",
    specLink="woff1:#conform-metadata-schemavalid",
    valid=True,
)

# two div

writeMetadataTest(
    identifier="metadata-schema-license-021",
    specLink="woff1:#conform-metadata-schemavalid",
    valid=True,
)

# nested div

writeMetadataTest(
    identifier="metadata-schema-license-022",
    specLink="woff1:#conform-metadata-schemavalid",
    valid=True,
)

# div with dir

writeMetadataTest(
    identifier="metadata-schema-license-023",
    specLink="woff1:#conform-metadata-schemavalid",
    valid=True,
)

writeMetadataTest(
    identifier="metadata-schema-license-024",
    specLink="woff1:#conform-metadata-schemavalid",
    valid=True,
)

writeMetadataTest(
    identifier="metadata-schema-license-025",
    specLink="woff1:#conform-metadata-schemavalid",
    valid=False,
)

# div with class

writeMetadataTest(
    identifier="metadata-schema-license-026",
    specLink="woff1:#conform-metadata-schemavalid",
    valid=True,
)

# one span

writeMetadataTest(
    identifier="metadata-schema-license-027",
    specLink="woff1:#conform-metadata-schemavalid",
    valid=True,
)

# two span

writeMetadataTest(
    identifier="metadata-schema-license-028",
    specLink="woff1:#conform-metadata-schemavalid",
    valid=True,
)

# nested span

writeMetadataTest(
    identifier="metadata-schema-license-029",
    specLink="woff1:#conform-metadata-schemavalid",
    valid=True,
)

# span with dir

writeMetadataTest(
    identifier="metadata-schema-license-030",
    specLink="woff1:#conform-metadata-schemavalid",
    valid=True,
)

writeMetadataTest(
    identifier="metadata-schema-license-031",
    specLink="woff1:#conform-metadata-schemavalid",
    valid=True,
)

writeMetadataTest(
    identifier="metadata-schema-license-032",
    specLink="woff1:#conform-metadata-schemavalid",
    valid=False,
)

# span with class

writeMetadataTest(
    identifier="metadata-schema-license-033",
    specLink="woff1:#conform-metadata-schemavalid",
    valid=True,
)

# --------------------------------------------
# Metadata Display: Schema Validity: copyright
# --------------------------------------------

# valid one text element no language

writeMetadataTest(
    identifier="metadata-schema-copyright-001",
    valid=True,
)

# valid one text element with language

writeMetadataTest(
    identifier="metadata-schema-copyright-002",
    valid=True,
)

# valid one text element with language using lang

writeMetadataTest(
    identifier="metadata-schema-copyright-003",
    valid=True,
)

# valid two text elements no language and language

writeMetadataTest(
    identifier="metadata-schema-copyright-004",
    valid=True,
)

# valid two text elements language and language

writeMetadataTest(
    identifier="metadata-schema-copyright-005",
    valid=True,
)

# more than one copyright

writeMetadataTest(
    identifier="metadata-schema-copyright-006",
    specLink="woff1:#conform-metadata-schemavalid",
    valid=False,
)

# no text element

writeMetadataTest(
    identifier="metadata-schema-copyright-007",
    specLink="woff1:#conform-localizable-text-required",
    valid=False,
)

# unknown attribute

writeMetadataTest(
    identifier="metadata-schema-copyright-008",
    specLink="woff1:#conform-metadata-schemavalid",
    valid=False,
)

# unknown child element

writeMetadataTest(
    identifier="metadata-schema-copyright-009",
    specLink="woff1:#conform-metadata-schemavalid",
    valid=False,
)

# content

writeMetadataTest(
    identifier="metadata-schema-copyright-010",
    specLink="woff1:#conform-metadata-schemavalid",
    valid=False,
)

# text element with dir attribute

writeMetadataTest(
    identifier="metadata-schema-copyright-011",
    specLink="woff1:#conform-metadata-schemavalid",
    valid=True,
)

writeMetadataTest(
    identifier="metadata-schema-copyright-012",
    specLink="woff1:#conform-metadata-schemavalid",
    valid=True,
)

writeMetadataTest(
    identifier="metadata-schema-copyright-013",
    specLink="woff1:#conform-metadata-schemavalid",
    valid=False,
)

# text element with class attribute

writeMetadataTest(
    identifier="metadata-schema-copyright-014",
    specLink="woff1:#conform-metadata-schemavalid",
    valid=True,
)

# text element unknown attribute

writeMetadataTest(
    identifier="metadata-schema-copyright-015",
    specLink="woff1:#conform-metadata-schemavalid",
    valid=False,
)

# text element child element

writeMetadataTest(
    identifier="metadata-schema-copyright-016",
    specLink="woff1:#conform-metadata-schemavalid",
    valid=False,
)

# one div

writeMetadataTest(
    identifier="metadata-schema-copyright-017",
    specLink="woff1:#conform-metadata-schemavalid",
    valid=True,
)

# two div

writeMetadataTest(
    identifier="metadata-schema-copyright-018",
    specLink="woff1:#conform-metadata-schemavalid",
    valid=True,
)

# nested div

writeMetadataTest(
    identifier="metadata-schema-copyright-019",
    specLink="woff1:#conform-metadata-schemavalid",
    valid=True,
)

# div with dir

writeMetadataTest(
    identifier="metadata-schema-copyright-020",
    specLink="woff1:#conform-metadata-schemavalid",
    valid=True,
)

writeMetadataTest(
    identifier="metadata-schema-copyright-021",
    specLink="woff1:#conform-metadata-schemavalid",
    valid=True,
)

writeMetadataTest(
    identifier="metadata-schema-copyright-022",
    specLink="woff1:#conform-metadata-schemavalid",
    valid=False,
)

# div with class

writeMetadataTest(
    identifier="metadata-schema-copyright-023",
    specLink="woff1:#conform-metadata-schemavalid",
    valid=True,
)

# one span

writeMetadataTest(
    identifier="metadata-schema-copyright-024",
    specLink="woff1:#conform-metadata-schemavalid",
    valid=True,
)

# two span

writeMetadataTest(
    identifier="metadata-schema-copyright-025",
    specLink="woff1:#conform-metadata-schemavalid",
    valid=True,
)

# nested span

writeMetadataTest(
    identifier="metadata-schema-copyright-026",
    specLink="woff1:#conform-metadata-schemavalid",
    valid=True,
)

# span with dir

writeMetadataTest(
    identifier="metadata-schema-copyright-027",
    specLink="woff1:#conform-metadata-schemavalid",
    valid=True,
)

writeMetadataTest(
    identifier="metadata-schema-copyright-028",
    specLink="woff1:#conform-metadata-schemavalid",
    valid=True,
)

writeMetadataTest(
    identifier="metadata-schema-copyright-029",
    specLink="woff1:#conform-metadata-schemavalid",
    valid=False,
)

# span with class

writeMetadataTest(
    identifier="metadata-schema-copyright-030",
    specLink="woff1:#conform-metadata-schemavalid",
    valid=True,
)

# --------------------------------------------
# Metadata Display: Schema Validity: trademark
# --------------------------------------------

# valid one text element no language

writeMetadataTest(
    identifier="metadata-schema-trademark-001",
    specLink="woff1:#conform-metadata-schemavalid",
    valid=True,
)

# valid one text element with language

writeMetadataTest(
    identifier="metadata-schema-trademark-002",
    valid=True,
)

# valid one text element with language using lang

writeMetadataTest(
    identifier="metadata-schema-trademark-003",
    valid=True,
)

# valid two text elements no language and language

writeMetadataTest(
    identifier="metadata-schema-trademark-004",
    valid=True,
)

# valid two text elements language and language

writeMetadataTest(
    identifier="metadata-schema-trademark-005",
    valid=True,
)

# more than one trademark

writeMetadataTest(
    identifier="metadata-schema-trademark-006",
    specLink="woff1:#conform-metadata-schemavalid",
    valid=False,
)

# no text element

writeMetadataTest(
    identifier="metadata-schema-trademark-007",
    specLink="woff1:#conform-localizable-text-required",
    valid=False,
)

# unknown attribute

writeMetadataTest(
    identifier="metadata-schema-trademark-008",
    specLink="woff1:#conform-metadata-schemavalid",
    valid=False,
)

# unknown child element

writeMetadataTest(
    identifier="metadata-schema-trademark-009",
    specLink="woff1:#conform-metadata-schemavalid",
    valid=False,
)

# content

writeMetadataTest(
    identifier="metadata-schema-trademark-010",
    specLink="woff1:#conform-metadata-schemavalid",
    valid=False,
)

# text element with dir attribute

writeMetadataTest(
    identifier="metadata-schema-trademark-011",
    specLink="woff1:#conform-metadata-schemavalid",
    valid=True,
)

writeMetadataTest(
    identifier="metadata-schema-trademark-012",
    specLink="woff1:#conform-metadata-schemavalid",
    valid=True,
)

writeMetadataTest(
    identifier="metadata-schema-trademark-013",
    specLink="woff1:#conform-metadata-schemavalid",
    valid=False,
)

# text element with class attribute

writeMetadataTest(
    identifier="metadata-schema-trademark-014",
    specLink="woff1:#conform-metadata-schemavalid",
    valid=True,
)

# text element unknown attribute

writeMetadataTest(
    identifier="metadata-schema-trademark-015",
    specLink="woff1:#conform-metadata-schemavalid",
    valid=False,
)

# text element child element

writeMetadataTest(
    identifier="metadata-schema-trademark-016",
    specLink="woff1:#conform-metadata-schemavalid",
    valid=False,
)

# one div

writeMetadataTest(
    identifier="metadata-schema-trademark-017",
    specLink="woff1:#conform-metadata-schemavalid",
    valid=True,
)

# two div

writeMetadataTest(
    identifier="metadata-schema-trademark-018",
    specLink="woff1:#conform-metadata-schemavalid",
    valid=True,
)

# nested div

writeMetadataTest(
    identifier="metadata-schema-trademark-019",
    specLink="woff1:#conform-metadata-schemavalid",
    valid=True,
)

# div with dir

writeMetadataTest(
    identifier="metadata-schema-trademark-020",
    specLink="woff1:#conform-metadata-schemavalid",
    valid=True,
)

writeMetadataTest(
    identifier="metadata-schema-trademark-021",
    specLink="woff1:#conform-metadata-schemavalid",
    valid=True,
)

writeMetadataTest(
    identifier="metadata-schema-trademark-022",
    specLink="woff1:#conform-metadata-schemavalid",
    valid=False,
)

# div with class

writeMetadataTest(
    identifier="metadata-schema-trademark-023",
    specLink="woff1:#conform-metadata-schemavalid",
    valid=True,
)

# one span

writeMetadataTest(
    identifier="metadata-schema-trademark-024",
    specLink="woff1:#conform-metadata-schemavalid",
    valid=True,
)

# two span

writeMetadataTest(
    identifier="metadata-schema-trademark-025",
    specLink="woff1:#conform-metadata-schemavalid",
    valid=True,
)

# nested span

writeMetadataTest(
    identifier="metadata-schema-trademark-026",
    specLink="woff1:#conform-metadata-schemavalid",
    valid=True,
)

# span with dir

writeMetadataTest(
    identifier="metadata-schema-trademark-027",
    specLink="woff1:#conform-metadata-schemavalid",
    valid=True,
)

writeMetadataTest(
    identifier="metadata-schema-trademark-028",
    specLink="woff1:#conform-metadata-schemavalid",
    valid=True,
)

writeMetadataTest(
    identifier="metadata-schema-trademark-029",
    specLink="woff1:#conform-metadata-schemavalid",
    valid=False,
)

# span with class

writeMetadataTest(
    identifier="metadata-schema-trademark-030",
    specLink="woff1:#conform-metadata-schemavalid",
    valid=True,
)

# -------------------------------------------
# Metadata Display: Schema Validity: uniqueid
# -------------------------------------------

# valid

writeMetadataTest(
    identifier="metadata-schema-licensee-001",
    valid=True,
)

# duplicate

writeMetadataTest(
    identifier="metadata-schema-licensee-002",
    specLink="woff1:#conform-metadata-schemavalid",
    valid=False,
)

# missing name

writeMetadataTest(
    identifier="metadata-schema-licensee-003",
    specLink="woff1:#conform-licensee-required",
    valid=False,
)

# dir attribute

writeMetadataTest(
    identifier="metadata-schema-licensee-004",
    specLink="woff1:#conform-metadata-schemavalid",
    valid=True,
)

writeMetadataTest(
    identifier="metadata-schema-licensee-005",
    specLink="woff1:#conform-metadata-schemavalid",
    valid=True,
)

writeMetadataTest(
    identifier="metadata-schema-licensee-006",
    specLink="woff1:#conform-metadata-schemavalid",
    valid=False,
)

# class attribute

writeMetadataTest(
    identifier="metadata-schema-licensee-007",
    specLink="woff1:#conform-metadata-schemavalid",
    valid=True,
)

# unknown attribute

writeMetadataTest(
    identifier="metadata-schema-licensee-008",
    specLink="woff1:#conform-metadata-schemavalid",
    valid=False,
)

# child element

writeMetadataTest(
    identifier="metadata-schema-licensee-009",
    specLink="woff1:#conform-metadata-schemavalid",
    valid=False,
)

# content

writeMetadataTest(
    identifier="metadata-schema-licensee-010",
    specLink="woff1:#conform-metadata-schemavalid",
    valid=False,
)

# --------------------------------------------
# Metadata Display: Schema Validity: extension
# --------------------------------------------

# valid

writeMetadataTest(
    identifier="metadata-schema-extension-001",
    valid=True,
)

# valid two extensions

writeMetadataTest(
    identifier="metadata-schema-extension-002",
    valid=True,
)

# valid no id

writeMetadataTest(
    identifier="metadata-schema-extension-003",
    valid=True,
)

# valid no name

writeMetadataTest(
    identifier="metadata-schema-extension-004",
    valid=True,
)

# valid one untagged name one tagged name

writeMetadataTest(
    identifier="metadata-schema-extension-005",
    valid=True,
)

# valid two tagged names

writeMetadataTest(
    identifier="metadata-schema-extension-006",
    valid=True,
)

# valid more than one item

writeMetadataTest(
    identifier="metadata-schema-extension-007",
    valid=True,
)

# no item

writeMetadataTest(
    identifier="metadata-schema-extension-008",
    specLink="woff1:#conform-extension-itemrequired",
    valid=False,
)

# unknown attribute

writeMetadataTest(
    identifier="metadata-schema-extension-009",
    specLink="woff1:#conform-metadata-schemavalid",
    valid=False,
)

# unknown child

writeMetadataTest(
    identifier="metadata-schema-extension-010",
    specLink="woff1:#conform-metadata-schemavalid",
    valid=False,
)

# content

writeMetadataTest(
    identifier="metadata-schema-extension-011",
    specLink="woff1:#conform-metadata-schemavalid",
    valid=False,
)

# ---------------------------------------------------
# Metadata Display: Schema Validity: extension - name
# ---------------------------------------------------

# valid no lang

writeMetadataTest(
    identifier="metadata-schema-extension-012",
    valid=True,
)

# valid xml:lang

writeMetadataTest(
    identifier="metadata-schema-extension-013",
    valid=True,
)

# valid lang

writeMetadataTest(
    identifier="metadata-schema-extension-014",
    valid=True,
)

# dir attribute

writeMetadataTest(
    identifier="metadata-schema-extension-015",
    valid=True,
)

writeMetadataTest(
    identifier="metadata-schema-extension-016",
    valid=True,
)

writeMetadataTest(
    identifier="metadata-schema-extension-017",
    valid=False,
)

# class attribute

writeMetadataTest(
    identifier="metadata-schema-extension-018",
    valid=True,
)

# unknown attribute

writeMetadataTest(
    identifier="metadata-schema-extension-019",
    specLink="woff1:#conform-metadata-schemavalid",
    valid=False,
)

# child element

writeMetadataTest(
    identifier="metadata-schema-extension-020",
    specLink="woff1:#conform-metadata-schemavalid",
    valid=False,
)

# ---------------------------------------------------
# Metadata Display: Schema Validity: extension - item
# ---------------------------------------------------

# valid

writeMetadataTest(
    identifier="metadata-schema-extension-021",
    valid=True,
)

# valid multiple languages

writeMetadataTest(
    identifier="metadata-schema-extension-022",
    valid=True,
)

# valid no id

writeMetadataTest(
    identifier="metadata-schema-extension-023",
    valid=True,
)

# valid name no tag and tagged

writeMetadataTest(
    identifier="metadata-schema-extension-024",
    valid=True,
)

# valid name two tagged

writeMetadataTest(
    identifier="metadata-schema-extension-025",
    valid=True,
)

# valid value no tag and tagged

writeMetadataTest(
    identifier="metadata-schema-extension-026",
    valid=True,
)

# valid value two tagged

writeMetadataTest(
    identifier="metadata-schema-extension-027",
    valid=True,
)

# no name

writeMetadataTest(
    identifier="metadata-schema-extension-028",
    specLink="woff1:#conform-metadata-schemavalid woff1:#conform-namerequired",
    valid=False,
)

# no value

writeMetadataTest(
    identifier="metadata-schema-extension-029",
    specLink="woff1:#conform-metadata-schemavalid woff1:#conform-valuerequired",
    valid=False,
)

# unknown attribute

writeMetadataTest(
    identifier="metadata-schema-extension-030",
    specLink="woff1:#conform-metadata-schemavalid",
    valid=False,
)

# unknown child element

writeMetadataTest(
    identifier="metadata-schema-extension-031",
    specLink="woff1:#conform-metadata-schemavalid",
    valid=False,
)

# content

writeMetadataTest(
    identifier="metadata-schema-extension-032",
    specLink="woff1:#conform-metadata-schemavalid",
    valid=False,
)

# ----------------------------------------------------------
# Metadata Display: Schema Validity: extension - item - name
# ----------------------------------------------------------

# valid no lang

writeMetadataTest(
    identifier="metadata-schema-extension-033",
    valid=True,
)

# valid xml:lang

writeMetadataTest(
    identifier="metadata-schema-extension-034",
    valid=True,
)

# valid lang

writeMetadataTest(
    identifier="metadata-schema-extension-035",
    valid=True,
)

# dir attribute

writeMetadataTest(
    identifier="metadata-schema-extension-036",
    valid=True,
)

writeMetadataTest(
    identifier="metadata-schema-extension-037",
    valid=True,
)

writeMetadataTest(
    identifier="metadata-schema-extension-038",
    valid=False,
)

# class attribute

writeMetadataTest(
    identifier="metadata-schema-extension-039",
    valid=True,
)

# unknown attribute

writeMetadataTest(
    identifier="metadata-schema-extension-040",
    specLink="woff1:#conform-metadata-schemavalid",
    valid=False,
)

# child element

writeMetadataTest(
    identifier="metadata-schema-extension-041",
    specLink="woff1:#conform-metadata-schemavalid",
    valid=False,
)

# -----------------------------------------------------------
# Metadata Display: Schema Validity: extension - item - value
# -----------------------------------------------------------

# valid no lang

writeMetadataTest(
    identifier="metadata-schema-extension-042",
    valid=True,
)

# valid xml:lang

writeMetadataTest(
    identifier="metadata-schema-extension-043",
    valid=True,
)

# valid lang

writeMetadataTest(
    identifier="metadata-schema-extension-044",
    valid=True,
)

# dir attribute

writeMetadataTest(
    identifier="metadata-schema-extension-045",
    valid=True,
)

writeMetadataTest(
    identifier="metadata-schema-extension-046",
    valid=True,
)

writeMetadataTest(
    identifier="metadata-schema-extension-047",
    valid=False,
)

# class attribute

writeMetadataTest(
    identifier="metadata-schema-extension-048",
    valid=True,
)

# unknown attribute

writeMetadataTest(
    identifier="metadata-schema-extension-049",
    specLink="woff1:#conform-metadata-schemavalid",
    valid=False,
)

# child element

writeMetadataTest(
    identifier="metadata-schema-extension-050",
    specLink="woff1:#conform-metadata-schemavalid",
    valid=False,
)

# ------------------
# Generate the Index
# ------------------

print "Compiling index..."

testGroups = []

for tag, title, url in groupDefinitions:
    group = dict(title=title, url=url, testCases=testRegistry[tag])
    testGroups.append(group)

generateFormatIndexHTML(directory=formatTestDirectory, testCases=testGroups)

# ----------------
# Generate the zip
# ----------------

print "Compiling zip file..."

zipPath = os.path.join(formatTestDirectory, "FormatTestFonts.zip")
if os.path.exists(zipPath):
    os.remove(zipPath)

allBinariesZip = zipfile.ZipFile(zipPath, "w")

pattern = os.path.join(formatTestDirectory, "*.woff2")
for path in glob.glob(pattern):
    ext = os.path.splitext(path)[1]
    allBinariesZip.write(path, os.path.basename(path))

allBinariesZip.close()

# ---------------------
# Generate the Manifest
# ---------------------

print "Compiling manifest..."

manifest = []

for tag, title, url in groupDefinitions:
    for testCase in testRegistry[tag]:
        identifier = testCase["identifier"]
        title = testCase["title"]
        assertion = testCase["description"]
        links = "#" + testCase["specLink"].split("#")[-1]
        flags = ""
        credits = ""
        # format the line
        line = "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s" % (
            identifier,             # id
            "",                     # reference
            title,                  # title
            flags,                  # flags
            links,                  # links
            "DUMMY",                # revision
            credits,                # credits
            assertion               # assertion
        )
        # store
        manifest.append(line)

path = os.path.join(formatDirectory, "manifest.txt")
if os.path.exists(path):
    os.remove(path)
f = open(path, "wb")
f.write("\n".join(manifest))
f.close()

# -----------------------
# Check for Unknown Files
# -----------------------

woffPattern = os.path.join(formatTestDirectory, "*.woff2")
filesOnDisk = glob.glob(woffPattern)

for path in filesOnDisk:
    identifier = os.path.basename(path)
    identifier = identifier.split(".")[0]
    if identifier not in registeredIdentifiers:
        print "Unknown file:", path
