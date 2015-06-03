"""
This script generates the User Agent test cases. It will create a directory
one level up from the directory containing this script called "UserAgent".
That directory will have the structure:

    /UserAgent
        README.txt - information about how the tests were generated and how they should be modified
        /FontsToInstall
            fonts that must be installed locally
        /Tests
            testcaseindex.xht - index of all test cases
            test-case-name-number.xht - individual test case
            test-case-name-number-ref - reference that uses locally installed fonts for rendering comparison
            /resources
                index.css - index CSS file
                test-case-name-number.woff2 - individual WOFF test case

The individual test cases follow the CSS Test Format
(http://wiki.csswg.org/test/css2.1/format).

Within this script, each test case is generated with a call to the
writeFileStructureTest function or the writeMetadataSchemaValidityTest
function. In these, WOFF data must be passed along with details about
the data. This function will generate the WOFF and HTML files and
it will register the case in the suite index.
"""

import os
import shutil
import glob
from testCaseGeneratorLib.woff import packTestHeader, packTestDirectory, packTestMetadata, packTestPrivateData
from testCaseGeneratorLib.defaultData import defaultTestData, testDataWOFFMetadata, testDataWOFFPrivateData
from testCaseGeneratorLib.html import generateSFNTDisplayTestHTML, generateSFNTDisplayRefHTML, generateSFNTDisplayIndexHTML
from testCaseGeneratorLib.paths import resourcesDirectory, userAgentDirectory, userAgentTestDirectory, userAgentTestResourcesDirectory, userAgentFontsToInstallDirectory, sfntTTFCompositeSourcePath
from testCaseGeneratorLib import sharedCases
from testCaseGeneratorLib.sharedCases import *

# ------------------------
# Specification URL
# This is used frequently.
# ------------------------

specificationURL = "http://dev.w3.org/webfonts/WOFF2/spec/"

# ------------------
# Directory Creation
# (if needed)
# ------------------

if not os.path.exists(userAgentDirectory):
    os.makedirs(userAgentDirectory)

if not os.path.exists(userAgentTestDirectory):
    os.makedirs(userAgentTestDirectory)

if not os.path.exists(userAgentTestResourcesDirectory):
    os.makedirs(userAgentTestResourcesDirectory)

# ---------------------
# Move Fonts To Install
# ---------------------

if not os.path.exists(userAgentFontsToInstallDirectory):
    os.mkdir(userAgentFontsToInstallDirectory)

# CFF Reference
destPath = os.path.join(userAgentFontsToInstallDirectory, "SFNT-CFF-Reference.otf")
if os.path.exists(destPath):
    os.remove(destPath)
shutil.copy(os.path.join(resourcesDirectory, "SFNT-CFF-Reference.otf"), os.path.join(destPath))
# CFF Fallback
destPath = os.path.join(userAgentFontsToInstallDirectory, "SFNT-CFF-Fallback.otf")
if os.path.exists(destPath):
    os.remove(destPath)
shutil.copy(os.path.join(resourcesDirectory, "SFNT-CFF-Fallback.otf"), os.path.join(destPath))
# TTF Reference
destPath = os.path.join(userAgentFontsToInstallDirectory, "SFNT-TTF-Reference.ttf")
if os.path.exists(destPath):
    os.remove(destPath)
shutil.copy(os.path.join(resourcesDirectory, "SFNT-TTF-Reference.ttf"), os.path.join(destPath))
# TTF Fallback
destPath = os.path.join(userAgentFontsToInstallDirectory, "SFNT-TTF-Fallback.ttf")
if os.path.exists(destPath):
    os.remove(destPath)
shutil.copy(os.path.join(resourcesDirectory, "SFNT-TTF-Fallback.ttf"), os.path.join(destPath))

# -------------------
# Move HTML Resources
# -------------------

# index css
destPath = os.path.join(userAgentTestResourcesDirectory, "index.css")
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
    ("valid", "Valid WOFFs", specificationURL+"#FileStructure"),
    ("datatypes", "Data types", specificationURL+"#DataTypes"),
    ("header", "WOFF Header Tests", specificationURL+"#woff20Header"),
    ("blocks", "WOFF Data Block Tests", specificationURL+"#FileStructure"),
    ("directory", "WOFF Table Directory Tests", specificationURL+"#table_dir_format"),
    ("tabledata", "WOFF Table Data Tests", specificationURL+"#DataTables"),
    ("metadata", "WOFF Metadata Tests", specificationURL+"#Metadata"),
    ("privatedata", "WOFF Private Data Tests", specificationURL+"#Private"),
    ("metadatadisplay", "WOFF Metadata Display Tests", specificationURL+"#Metadata"),
    ("available", "Availability", specificationURL+"#conform-css3font-available"),
]

testRegistry = {}
for group in groupDefinitions:
    tag = group[0]
    testRegistry[tag] = []

groupChapterURLs = {}
for tag, title, url in groupDefinitions:
    groupChapterURLs[tag] = "#" + url.split("#")[-1]

# ---------------
# File Generators
# ---------------

registeredIdentifiers = set()
registeredTitles = set()
registeredAssertions = set()

def writeFileStructureTest(identifier, flavor="CFF",
        title=None, assertion=None,
        sfntDisplaySpecLink=None, metadataDisplaySpecLink=None,
        credits=[], flags=[],
        shouldDisplaySFNT=None, metadataIsValid=None,
        data=None, metadataToDisplay=None,
        extraSFNTNotes=[], extraMetadataNotes=[]
        ):
    """
    This function generates all of the files needed by a test case and
    registers the case with the suite. The arguments:

    identifier: The identifier for the test case. The identifier must be
    a - separated sequence of group name (from the groupDefinitions
    listed above), test case description (arbitrary length) and a number
    to make the name unique. The number should be zero padded to a length
    of three characters (ie "001" instead of "1").

    flavor: The flavor of the WOFF data. The options are CFF or TTF.

    title: A thorough, but not too long, title for the test case.

    assertion: A detailed statement about what the test case is proving.

    sfntDisplaySpecLink: A space separated list of anchors in the WOFF spec
    that the test case is testing. This anchor should only reference the
    SFNT display conformance.

    metadataDisplaySpecLink: The anchor in the WOFF spec that the test case
    is testing. This anchor should only reference the metadata display conformance.

    credits: A list of dictionaries defining the credits for the test case. The
    dictionaries must have this form:

        title="Name of the autor or reviewer",
        role="author or reviewer",
        link="mailto:email or http://contactpage"

    flags: A list of requirement flags. The options are defined in the
    CSS Test Format specification.

    shouldDisplaySFNT: A boolean indicating if the SFNT should be used for display or not.

    metadataIsValid: A boolean indicating if the metadata is valid.

    data: The complete binary data for the WOFF.

    metadataToDisplay: A string of metadata to display in the HTML. This should
    be set when the metadata is valid.

    extraSFNTNotes: Additional notes about the SFNT data that should be
    displayed in the HTML.

    extraMetadataNotes: Additional notes about the metadata that should be
    displayed in the HTML.
    """
    print "Compiling %s..." % identifier
    assert identifier not in registeredIdentifiers, "Duplicate identifier! %s" % identifier
    assert title not in registeredTitles, "Duplicate title! %s" % title
    assert assertion not in registeredAssertions, "Duplicate assertion! %s" % assertion
    registeredIdentifiers.add(identifier)
    registeredTitles.add(title)
    registeredAssertions.add(assertion)

    if sfntDisplaySpecLink is None:
        sfntDisplaySpecLink = ""
    sfntDisplaySpecLink = [specificationURL + i for i in sfntDisplaySpecLink.split(" ")]
    if metadataDisplaySpecLink is not None:
        metadataDisplaySpecLink = specificationURL + metadataDisplaySpecLink
    flags = list(flags)
    flags += ["font"] # fonts must be installed for all of these tests

    tag = identifier.split("-")[0]

    # generate the WOFF
    woffPath = os.path.join(userAgentTestResourcesDirectory, identifier) + ".woff2"
    f = open(woffPath, "wb")
    f.write(data)
    f.close()

    # generate the test and ref html
    kwargs = dict(
        fileName=identifier,
        directory=userAgentTestDirectory,
        flavor=flavor,
        title=title,
        sfntDisplaySpecLink=sfntDisplaySpecLink,
        metadataDisplaySpecLink=metadataDisplaySpecLink,
        assertion=assertion,
        credits=credits,
        flags=flags,
        shouldDisplay=shouldDisplaySFNT,
        metadataIsValid=metadataIsValid,
        metadataToDisplay=metadataToDisplay,
        extraSFNTNotes=extraSFNTNotes,
        extraMetadataNotes=extraMetadataNotes,
        chapterURL=groupChapterURLs[tag]
    )
    generateSFNTDisplayTestHTML(**kwargs)
    generateSFNTDisplayRefHTML(**kwargs)

    # register the test
    testRegistry[tag].append(
        dict(
            identifier=identifier,
            flags=flags,
            title=title,
            assertion=assertion,
            sfntExpectation=shouldDisplaySFNT,
            sfntURL=sfntDisplaySpecLink,
            metadataURL=metadataDisplaySpecLink,
            metadataExpectation=metadataIsValid,
            credits=credits,
            hasReferenceRendering=True
        )
    )

def writeMetadataSchemaValidityTest(identifier,
    title=None,
    assertion=None,
    credits=[],
    sfntDisplaySpecLink=None,
    metadataDisplaySpecLink=None,
    metadataIsValid=None,
    metadata=None):
    """
    This is a convenience functon that eliminates the need to
    make a complete WOFF when only the metadata is being tested.
    Refer to the writeFileStructureTest documentation for
    the meaning of the various arguments.
    """
    # dynamically get some data from the shared cases as needed
    if title is None:
        assert assertion is None
        assert metadata is None
        parts = identifier.split("-")
        assert parts[0] == "metadatadisplay"
        number = int(parts[-1])
        group = parts[1:-1]
        group = [i.title() for i in group]
        group = "".join(group)
        importBase = "metadata" + group + str(number)
        title = getattr(sharedCases, importBase + "Title")
        assertion = getattr(sharedCases, importBase + "Description")
        credits = getattr(sharedCases, importBase + "Credits")
        metadata = getattr(sharedCases, importBase + "Metadata")
    assert metadata is not None
    assert metadataIsValid is not None
    # compile the WOFF
    data, metadata = makeMetadataTest(metadata)
    # pass to the more verbose function
    if metadataDisplaySpecLink is None:
        if not metadataIsValid:
            metadataDisplaySpecLink = "#conform-invalid-mustignore"
        else:
            metadataDisplaySpecLink = "#Metadata"
    if sfntDisplaySpecLink is None:
        sfntDisplaySpecLink = "#conform-metadata-noeffect"
    kwargs = dict(
        title=title,
        assertion=assertion,
        credits=credits,
        sfntDisplaySpecLink=sfntDisplaySpecLink,
        metadataDisplaySpecLink=metadataDisplaySpecLink,
        shouldDisplaySFNT=True,
        metadataIsValid=metadataIsValid,
        data=data
    )
    if metadataIsValid:
        kwargs["metadataToDisplay"] = metadata
    writeFileStructureTest(
        identifier,
        **kwargs
    )

# -----------
# Valid Files
# -----------

# CFF

writeFileStructureTest(
    identifier="valid-001",
    title=makeValidWOFF1Title,
    assertion=makeValidWOFF1Description,
    credits=makeValidWOFF1Credits,
    shouldDisplaySFNT=True,
    sfntDisplaySpecLink="#conform-metadata-noeffect #conform-private-noeffect",
    data=makeValidWOFF1()
)

writeFileStructureTest(
    identifier="valid-002",
    title=makeValidWOFF2Title,
    assertion=makeValidWOFF2Description,
    credits=makeValidWOFF2Credits,
    shouldDisplaySFNT=True,
    metadataIsValid=True,
    sfntDisplaySpecLink="#conform-metadata-noeffect #conform-private-noeffect",
    data=makeValidWOFF2(),
    metadataToDisplay=testDataWOFFMetadata,
    metadataDisplaySpecLink="#conform-metadata-maydisplay"
)

writeFileStructureTest(
    identifier="valid-003",
    title=makeValidWOFF3Title,
    assertion=makeValidWOFF3Description,
    credits=makeValidWOFF3Credits,
    sfntDisplaySpecLink="#conform-metadata-noeffect #conform-private-noeffect",
    shouldDisplaySFNT=True,
    data=makeValidWOFF3()
)

writeFileStructureTest(
    identifier="valid-004",
    title=makeValidWOFF4Title,
    assertion=makeValidWOFF4Description,
    credits=makeValidWOFF4Credits,
    shouldDisplaySFNT=True,
    metadataIsValid=True,
    sfntDisplaySpecLink="#conform-metadata-noeffect #conform-private-noeffect",
    data=makeValidWOFF4(),
    metadataToDisplay=testDataWOFFMetadata,
    metadataDisplaySpecLink="#conform-metadata-maydisplay"
)

# TTF

writeFileStructureTest(
    identifier="valid-005",
    flavor="TTF",
    title=makeValidWOFF5Title,
    assertion=makeValidWOFF5Description,
    credits=makeValidWOFF5Credits,
    sfntDisplaySpecLink="#conform-metadata-noeffect #conform-private-noeffect",
    shouldDisplaySFNT=True,
    data=makeValidWOFF5()
)

writeFileStructureTest(
    identifier="valid-006",
    flavor="TTF",
    title=makeValidWOFF6Title,
    assertion=makeValidWOFF6Description,
    credits=makeValidWOFF6Credits,
    shouldDisplaySFNT=True,
    metadataIsValid=True,
    sfntDisplaySpecLink="#conform-metadata-noeffect #conform-private-noeffect",
    data=makeValidWOFF6(),
    metadataToDisplay=testDataWOFFMetadata,
    metadataDisplaySpecLink="#conform-metadata-maydisplay"
)

writeFileStructureTest(
    identifier="valid-007",
    flavor="TTF",
    title=makeValidWOFF7Title,
    assertion=makeValidWOFF7Description,
    credits=makeValidWOFF7Credits,
    shouldDisplaySFNT=True,
    sfntDisplaySpecLink="#conform-metadata-noeffect #conform-private-noeffect",
    data=makeValidWOFF7()
)

writeFileStructureTest(
    identifier="valid-008",
    flavor="TTF",
    title=makeValidWOFF8Title,
    assertion=makeValidWOFF8Description,
    credits=makeValidWOFF8Credits,
    shouldDisplaySFNT=True,
    metadataIsValid=True,
    sfntDisplaySpecLink="#conform-metadata-noeffect #conform-private-noeffect",
    data=makeValidWOFF8(),
    metadataToDisplay=testDataWOFFMetadata,
    metadataDisplaySpecLink="#conform-metadata-maydisplay"
)

# ---------------------------------
# File Structure: Header: signature
# ---------------------------------

writeFileStructureTest(
    identifier="header-signature-001",
    title=makeHeaderInvalidSignature1Title,
    assertion=makeHeaderInvalidSignature1Description,
    credits=makeHeaderInvalidSignature1Credits,
    shouldDisplaySFNT=False,
    sfntDisplaySpecLink="#conform-noMagicNumber-reject",
    data=makeHeaderInvalidSignature1()
)

# ------------------------------
# File Structure: Header: length
# ------------------------------

writeFileStructureTest(
    identifier="header-length-001",
    title=makeHeaderInvalidLength1Title,
    assertion=makeHeaderInvalidLength1Description,
    credits=makeHeaderInvalidLength1Credits,
    shouldDisplaySFNT=False,
    sfntDisplaySpecLink="#woff20Header",
    data=makeHeaderInvalidLength1()
)

writeFileStructureTest(
    identifier="header-length-002",
    title=makeHeaderInvalidLength2Title,
    assertion=makeHeaderInvalidLength2Description,
    credits=makeHeaderInvalidLength2Credits,
    shouldDisplaySFNT=False,
    sfntDisplaySpecLink="#woff20Header",
    data=makeHeaderInvalidLength2()
)

# ---------------------------------
# File Structure: Header: numTables
# ---------------------------------

writeFileStructureTest(
    identifier="header-numTables-001",
    title=makeHeaderInvalidNumTables1Title,
    assertion=makeHeaderInvalidNumTables1Description,
    credits=makeHeaderInvalidNumTables1Credits,
    shouldDisplaySFNT=False,
    sfntDisplaySpecLink="#woff20Header",
    data=makeHeaderInvalidNumTables1()
)

# --------------------------------
# File Structure: Header: reserved
# --------------------------------

writeFileStructureTest(
    identifier="header-reserved-001",
    title=makeHeaderInvalidReserved1Title,
    assertion=makeHeaderInvalidReserved1Description,
    credits=makeHeaderInvalidReserved1Credits,
    shouldDisplaySFNT=True,
    sfntDisplaySpecLink="#conform-mustNotUseReservedValue",
    data=makeHeaderInvalidReserved1()
)

# --------------------------------------------
# File Structure: Data Blocks: Extraneous Data
# --------------------------------------------

# between table directory and table data

writeFileStructureTest(
    identifier="blocks-extraneous-data-001",
    title=makeExtraneousData1Title,
    assertion=makeExtraneousData1Description,
    credits=makeExtraneousData1Credits,
    shouldDisplaySFNT=False,
    sfntDisplaySpecLink="#conform-extraneous-reject",
    data=makeExtraneousData1()
)

# after table data with no metadata or private data

writeFileStructureTest(
    identifier="blocks-extraneous-data-002",
    title=makeExtraneousData2Title,
    assertion=makeExtraneousData2Description,
    credits=makeExtraneousData2Credits,
    shouldDisplaySFNT=False,
    sfntDisplaySpecLink="#conform-extraneous-reject",
    data=makeExtraneousData2()
)

# between tabledata and metadata

writeFileStructureTest(
    identifier="blocks-extraneous-data-003",
    title=makeExtraneousData3Title,
    assertion=makeExtraneousData3Description,
    credits=makeExtraneousData3Credits,
    shouldDisplaySFNT=False,
    sfntDisplaySpecLink="#conform-extraneous-reject",
    data=makeExtraneousData3()
)

# between tabledata and private data

writeFileStructureTest(
    identifier="blocks-extraneous-data-004",
    title=makeExtraneousData4Title,
    assertion=makeExtraneousData4Description,
    credits=makeExtraneousData4Credits,
    shouldDisplaySFNT=False,
    sfntDisplaySpecLink="#conform-extraneous-reject",
    data=makeExtraneousData4()
)

# between metadata and private data

writeFileStructureTest(
    identifier="blocks-extraneous-data-005",
    title=makeExtraneousData5Title,
    assertion=makeExtraneousData5Description,
    credits=makeExtraneousData5Credits,
    shouldDisplaySFNT=False,
    sfntDisplaySpecLink="#conform-extraneous-reject",
    data=makeExtraneousData5()
)

# after metadata with no private data

writeFileStructureTest(
    identifier="blocks-extraneous-data-006",
    title=makeExtraneousData6Title,
    assertion=makeExtraneousData6Description,
    credits=makeExtraneousData6Credits,
    shouldDisplaySFNT=False,
    sfntDisplaySpecLink="#conform-extraneous-reject",
    data=makeExtraneousData6()
)

# after private data

writeFileStructureTest(
    identifier="blocks-extraneous-data-007",
    title=makeExtraneousData7Title,
    assertion=makeExtraneousData7Description,
    credits=makeExtraneousData7Credits,
    shouldDisplaySFNT=False,
    sfntDisplaySpecLink="#conform-extraneous-reject",
    data=makeExtraneousData7()
)

# -------------------------------------
# File Structure: Data Blocks: Overlaps
# -------------------------------------

# metadata overlaps the table data

writeFileStructureTest(
    identifier="blocks-overlap-001",
    title=makeOverlappingData1Title,
    assertion=makeOverlappingData1Description,
    credits=makeOverlappingData1Credits,
    shouldDisplaySFNT=False,
    sfntDisplaySpecLink="#conform-overlap-reject",
    data=makeOverlappingData1()
)

# private data overlaps the table data

writeFileStructureTest(
    identifier="blocks-overlap-002",
    title=makeOverlappingData2Title,
    assertion=makeOverlappingData2Description,
    credits=makeOverlappingData2Credits,
    shouldDisplaySFNT=False,
    sfntDisplaySpecLink="#conform-overlap-reject",
    data=makeOverlappingData2()
)

# private data overlaps the metadata

writeFileStructureTest(
    identifier="blocks-overlap-003",
    title=makeOverlappingData3Title,
    assertion=makeOverlappingData3Description,
    credits=makeOverlappingData3Credits,
    shouldDisplaySFNT=False,
    sfntDisplaySpecLink="#conform-overlap-reject",
    data=makeOverlappingData3()
)

# ----------------------------------------------
# File Structure: Table Data: Compression Format
# ----------------------------------------------

# compression incompatible with Brotli

writeFileStructureTest(
    identifier="tabledata-brotli-001",
    title=makeTableBrotliCompressionTest1Title,
    assertion=makeTableBrotliCompressionTest1Description,
    credits=makeTableBrotliCompressionTest1Credits,
    shouldDisplaySFNT=False,
    sfntDisplaySpecLink="#conform-mustBeInvalidated-FailDecompress",
    data=makeTableBrotliCompressionTest1()
)

# -----------------------------------------------
# File Structure: Table Data: Decompressed Length
# -----------------------------------------------

# decompressed length less than sum of origLength

writeFileStructureTest(
    identifier="tabledata-decompressed-length-001",
    title=makeTableDecompressedLengthTest1Title,
    assertion=makeTableDecompressedLengthTest1Description,
    credits=makeTableDecompressedLengthTest1Credits,
    shouldDisplaySFNT=False,
    sfntDisplaySpecLink="#conform-mustBeInvalidated-FailSize",
    data=makeTableDecompressedLengthTest1()
)

# decompressed length greater than sum of origLength

writeFileStructureTest(
    identifier="tabledata-decompressed-length-002",
    title=makeTableDecompressedLengthTest2Title,
    assertion=makeTableDecompressedLengthTest2Description,
    credits=makeTableDecompressedLengthTest2Credits,
    shouldDisplaySFNT=False,
    sfntDisplaySpecLink="#conform-mustBeInvalidated-FailSize",
    data=makeTableDecompressedLengthTest2()
)

# decompressed length less than sum of transformLength

writeFileStructureTest(
    identifier="tabledata-decompressed-length-003",
    title=makeTableDecompressedLengthTest3Title,
    assertion=makeTableDecompressedLengthTest3Description,
    credits=makeTableDecompressedLengthTest3Credits,
    shouldDisplaySFNT=False,
    sfntDisplaySpecLink="#conform-mustBeInvalidated-FailSize",
    data=makeTableDecompressedLengthTest3()
)

# decompressed length greater than sum of transformLength

writeFileStructureTest(
    identifier="tabledata-decompressed-length-004",
    title=makeTableDecompressedLengthTest4Title,
    assertion=makeTableDecompressedLengthTest4Description,
    credits=makeTableDecompressedLengthTest4Credits,
    shouldDisplaySFNT=False,
    sfntDisplaySpecLink="#conform-mustBeInvalidated-FailSize",
    data=makeTableDecompressedLengthTest4()
)

# -------------------------------------------
# File Structure: Table Data: Transformations
# -------------------------------------------

# loca's transformLength is not zero

writeFileStructureTest(
    identifier="tabledata-non-zero-loca-001",
    title=makeTableNonZeroLocaTest1Title,
    assertion=makeTableNonZeroLocaTest1Description,
    credits=makeTableNonZeroLocaTest1Credits,
    shouldDisplaySFNT=False,
    sfntDisplaySpecLink="#conform-mustRejectLoca",
    data=makeTableNonZeroLocaTest1()
)

def makeTableBadOrigLengthLocaTest1():
    header, directory, tableData = defaultTestData(flavor="ttf")
    for entry in directory:
        if entry["tag"] == "loca":
            entry["origLength"] -= 4
    data = padData(packTestHeader(header) + packTestDirectory(directory) + tableData)
    return data

writeFileStructureTest(
    identifier="tabledata-bad-origlength-loca-001",
    title="Font Table Data Small Loca Original Length",
    assertion="The origLength of the loca table is 4 bytes less than the calculated size",
    credits=[dict(title="Khaled Hosny", role="author", link="http://khaledhosny.org")],
    shouldDisplaySFNT=False,
    sfntDisplaySpecLink="#conform-mustRejectLoca",
    data=makeTableBadOrigLengthLocaTest1()
)

def makeTableBadOrigLengthLocaTest2():
    header, directory, tableData = defaultTestData(flavor="ttf")
    for entry in directory:
        if entry["tag"] == "loca":
            entry["origLength"] += 4
    data = padData(packTestHeader(header) + packTestDirectory(directory) + tableData)
    return data

writeFileStructureTest(
    identifier="tabledata-bad-origlength-loca-002",
    title="Font Table Data Large Loca Original Length",
    assertion="The origLength of the loca table is 4 bytes more than the calculated size",
    credits=[dict(title="Khaled Hosny", role="author", link="http://khaledhosny.org")],
    shouldDisplaySFNT=False,
    sfntDisplaySpecLink="#conform-mustRejectLoca",
    data=makeTableBadOrigLengthLocaTest2()
)

def makeGlyfNoBBox1():
    header, directory, tableData = defaultTestData()
    data = padData(packTestHeader(header) + packTestDirectory(directory) + tableData)
    return data

# glyph without explicit bbox
writeFileStructureTest(
    identifier="tabledata-glyf-no-bbox-001",
    flavor="TTF",
    title="Glyph Without Explicit Bounding Box",
    assertion="Valid TTF flavored WOFF with a glyph with no explicit bounding box",
    credits=[dict(title="Khaled Hosny", role="author", link="http://khaledhosny.org")],
    sfntDisplaySpecLink="#conform-mustCalculateBBox",
    shouldDisplaySFNT=True,
    data=makeGlyfNoBBox1()
)

def makeGlyfNoBBox2():
    from testCaseGeneratorLib.sfnt import getSFNTData
    tableData, compressedData, tableOrder, tableChecksums = getSFNTData(sfntTTFCompositeSourcePath, noCompositeBBox=True)
    header, directory, tableData = defaultTestData(tableData=tableData, compressedData=compressedData, flavor="ttf")
    data = padData(packTestHeader(header) + packTestDirectory(directory) + tableData)
    return data

# glyph without explicit bbox
writeFileStructureTest(
    identifier="tabledata-glyf-no-bbox-002",
    flavor="TTF",
    title="Composite Glyph Without Bounding Box",
    assertion="Invalid TTF flavored WOFF due to composite glyphs without bounding box",
    credits=[dict(title="Khaled Hosny", role="author", link="http://khaledhosny.org")],
    sfntDisplaySpecLink="#conform-mustRejectNoCompositeBBox",
    shouldDisplaySFNT=False,
    data=makeGlyfNoBBox2()
)

def makeCompositeData():
    from testCaseGeneratorLib.sfnt import getSFNTData
    tableData, compressedData, tableOrder, tableChecksums = getSFNTData(sfntTTFCompositeSourcePath)
    header, directory, tableData = defaultTestData(tableData=tableData, compressedData=compressedData, flavor="ttf")
    data = padData(packTestHeader(header) + packTestDirectory(directory) + tableData)
    return data

# valide font with composite glyphs
writeFileStructureTest(
    identifier="tabledata-valid-loca-001",
    flavor="TTF",
    title="Valid Font With Composite Glyphs",
    assertion="Valid TTF flavored WOFF with simple and composite glyphs",
    credits=[dict(title="Khaled Hosny", role="author", link="http://khaledhosny.org")],
    sfntDisplaySpecLink="#conform-mustRecordLocaOffsets",
    shouldDisplaySFNT=True,
    data=makeCompositeData()
)

# --------------------------
# File Structure: Data Types
# --------------------------
def make255UInt16Alt1(alt):
    from testCaseGeneratorLib.sfnt import getSFNTData
    tableData, compressedData, tableOrder, tableChecksums = getSFNTData(sfntTTFSourcePath, alt255UInt16=alt)
    header, directory, tableData = defaultTestData(tableData=tableData, compressedData=compressedData, flavor="ttf")
    data = padData(packTestHeader(header) + packTestDirectory(directory) + tableData)
    return data

# default 255UInt16 representation
writeFileStructureTest(
    identifier="datatypes-alt-255uint16-001",
    flavor="TTF",
    title="Default Representation of 255UInt16",
    assertion="Valid TTF flavored WOFF using default representation of 255UInt16",
    credits=[dict(title="Khaled Hosny", role="author", link="http://khaledhosny.org")],
    sfntDisplaySpecLink="#conform-mustAccept255UInt16",
    shouldDisplaySFNT=True,
    data=make255UInt16Alt1(0)
)

# 506 as [253, 1, 250]
writeFileStructureTest(
    identifier="datatypes-alt-255uint16-002",
    flavor="TTF",
    title="Alternate Representation of 255UInt16 1",
    assertion="Valid TTF flavored WOFF using alternate representation of 255UInt16",
    credits=[dict(title="Khaled Hosny", role="author", link="http://khaledhosny.org")],
    sfntDisplaySpecLink="#conform-mustAccept255UInt16",
    shouldDisplaySFNT=True,
    data=make255UInt16Alt1(1)
)

# 506 as [255, 253]
writeFileStructureTest(
    identifier="datatypes-alt-255uint16-003",
    flavor="TTF",
    title="Alternate Representation of 255UInt16 2",
    assertion="Valid TTF flavored WOFF using another alternate representation of 255UInt16",
    credits=[dict(title="Khaled Hosny", role="author", link="http://khaledhosny.org")],
    sfntDisplaySpecLink="#conform-mustAccept255UInt16",
    shouldDisplaySFNT=True,
    data=make255UInt16Alt1(2)
)

# -----------------------------------
# File Structure: Metadata: No Effect
# -----------------------------------

# have no metadata

def makeMetadataNoEffect1():
    header, directory, tableData = defaultTestData()
    data = padData(packTestHeader(header) + packTestDirectory(directory) + tableData)
    return data

writeFileStructureTest(
    identifier="metadata-noeffect-001",
    title="No Metadata Present",
    assertion="The file has no metadata.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    shouldDisplaySFNT=True,
    sfntDisplaySpecLink="#conform-metadata-noeffect",
    data=makeMetadataNoEffect1()
)

# have metadata

def makeMetadataNoEffect2():
    header, directory, tableData, metadata = defaultTestData(metadata=testDataWOFFMetadata)
    data = padData(packTestHeader(header) + packTestDirectory(directory) + tableData) + packTestMetadata(metadata)
    return data

writeFileStructureTest(
    identifier="metadata-noeffect-002",
    title="Metadata Present",
    assertion="The file has metadata.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    shouldDisplaySFNT=True,
    sfntDisplaySpecLink="#conform-metadata-noeffect",
    metadataIsValid=True,
    metadataDisplaySpecLink="#conform-metadata-maydisplay",
    data=makeMetadataNoEffect2()
)

# ---------------------------------------
# File Structure: Private Data: No Effect
# ---------------------------------------

# have no private data

def makePrivateDataNoEffect1():
    header, directory, tableData = defaultTestData()
    data = padData(packTestHeader(header) + packTestDirectory(directory) + tableData)
    return data

writeFileStructureTest(
    identifier="privatedata-noeffect-001",
    title="No Private Data Present",
    assertion="The file has no private data.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    shouldDisplaySFNT=True,
    sfntDisplaySpecLink="#conform-private-noeffect",
    data=makePrivateDataNoEffect1()
)

# have private data

def makePrivateDataNoEffect2():
    header, directory, tableData, privateData = defaultTestData(privateData=testDataWOFFPrivateData)
    data = padData(packTestHeader(header) + packTestDirectory(directory) + tableData) + packTestPrivateData(privateData)
    return data

writeFileStructureTest(
    identifier="privatedata-noeffect-002",
    title="Private Data Present",
    assertion="The file has private data.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    shouldDisplaySFNT=True,
    sfntDisplaySpecLink="#conform-private-noeffect",
    data=makePrivateDataNoEffect2()
)

# -------------------------------
# Metadata Display: Authoritative
# -------------------------------

metadataAuthoritativeXML = """
<?xml version="1.0" encoding="UTF-8"?>
<metadata version="1.0">
    <uniqueid id="PASS" />
    <description>
        <text>
            PASS
        </text>
    </description>
    <copyright>
        <text>
            PASS
        </text>
    </copyright>
    <trademark>
        <text>
            PASS
        </text>
    </trademark>
    <vendor name="PASS" url="PASS" />
    <credits>
        <credit name="PASS" url="PASS" />
    </credits>
    <license url="PASS">
        <text>
            PASS
        </text>
    </license>
</metadata>
""".strip().replace("    ", "\t")

def makeMetadataAuthoritativeTest1():
    from cStringIO import StringIO
    from fontTools.ttLib import TTFont
    from fontTools.ttLib.tables._n_a_m_e import NameRecord
    from testCaseGeneratorLib.paths import sfntCFFSourcePath
    from testCaseGeneratorLib.sfnt import getSFNTData
    from testCaseGeneratorLib.defaultData import sfntCFFTableOrder
    setToFAIL = [
        0,  # copyright
        3,  # unique id
        7,  # trademark
        8,  # manufacturer
        9,  # designer
        10, # description
        11, # vendor url
        12, # designer url
        13, # license
        14  # license url
    ]
    # open the SFNT
    font = TTFont(sfntCFFSourcePath)
    # overwrite parts of the name table that overlap the metadata
    nameTable = font["name"]
    newNames = []
    for record in nameTable.names:
        if record.nameID in setToFAIL:
            continue
        newNames.append(record)
    string = "FAIL".encode("utf8")
    for nameID in setToFAIL:
        for platformID, platEncID, langID in [(1, 0, 0), (3, 1, 1033)]:
            record = NameRecord()
            record.nameID = nameID
            record.platformID = platformID
            record.platEncID = platEncID
            record.langID = langID
            if record.platformID == 0 or (record.platformID == 3 and record.platEncID in (0, 1)):
                record.string = string.encode("utf_16_be")
            else:
                record.string = string.encode("latin1")
            newNames.append(record)
    newNames.sort()
    nameTable.names = newNames
    # save the SFNT
    f = StringIO()
    font.save(f, reorderTables=False)
    f.seek(0)
    # load the table data
    tableData, compressedData, tableOrder, tableChecksums = getSFNTData(f)
    # make sure that the table order is the same as the original
    assert tableOrder == sfntCFFTableOrder
    # compile the WOFF
    header, directory, tableData, metadata = defaultTestData(tableData=tableData, compressedData=compressedData, metadata=metadataAuthoritativeXML)
    data = padData(packTestHeader(header) + packTestDirectory(directory) + tableData) + packTestMetadata(metadata)
    return data

writeFileStructureTest(
    identifier="metadatadisplay-authoritative-001",
    title="Metadata Out of Sync With name Table",
    assertion="The name table and metadata fields are out of sync. The name table contains FAIL and the metadata contains PASS for unique id, vendor name, vendor url, credit name, credit url, description, license, license url, copyright and trademark.",
    credits=[dict(title="Tal Leming", role="author", link="http://typesupply.com")],
    shouldDisplaySFNT=True,
    metadataIsValid=True,
    metadataToDisplay=metadataAuthoritativeXML,
    metadataDisplaySpecLink="#conform-metadata-authoritative",
    data=makeMetadataAuthoritativeTest1(),
    extraMetadataNotes=["The Extended Metadata Block test fails if the word FAIL appears in the metadata display."]
)

# -----------------------------
# Metadata Display: Compression
# -----------------------------

writeFileStructureTest(
    identifier="metadatadisplay-compression-001",
    title=makeMetadataCompression1Title,
    assertion=makeMetadataCompression1Description,
    credits=makeMetadataCompression1Credits,
    shouldDisplaySFNT=True,
    metadataIsValid=False,
    metadataDisplaySpecLink="#conform-metadata-alwayscompress",
    data=makeMetadataCompression1(),
)

# --------------------------------
# Metadata Display: metaOrigLength
# --------------------------------

# <

writeFileStructureTest(
    identifier="metadatadisplay-metaOrigLength-001",
    title=makeMetaOrigLengthTest1Title,
    assertion=makeMetaOrigLengthTest1Description,
    credits=makeMetaOrigLengthTest1Credits,
    shouldDisplaySFNT=True,
    metadataIsValid=False,
    sfntDisplaySpecLink="#conform-metaOrigLength",
    data=makeMetaOrigLengthTest1()
)

# >

writeFileStructureTest(
    identifier="metadatadisplay-metaOrigLength-002",
    title=makeMetaOrigLengthTest2Title,
    assertion=makeMetaOrigLengthTest2Description,
    credits=makeMetaOrigLengthTest2Credits,
    shouldDisplaySFNT=True,
    metadataIsValid=False,
    sfntDisplaySpecLink="#conform-metaOrigLength",
    data=makeMetaOrigLengthTest2()
)

# -----------------------------
# Metadata Display: Well-Formed
# -----------------------------

# <

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-well-formed-001",
    metadataDisplaySpecLink="#conform-invalid-mustignore",
    metadataIsValid=False,
)

# &

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-well-formed-002",
    metadataDisplaySpecLink="#conform-invalid-mustignore",
    metadataIsValid=False,
)

# mismatched elements

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-well-formed-003",
    metadataDisplaySpecLink="#conform-invalid-mustignore",
    metadataIsValid=False,
)

# unclosed element

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-well-formed-004",
    metadataDisplaySpecLink="#conform-invalid-mustignore",
    metadataIsValid=False,
)

# case mismatch

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-well-formed-005",
    metadataDisplaySpecLink="#conform-invalid-mustignore",
    metadataIsValid=False,
)

# more than one root

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-well-formed-006",
    metadataDisplaySpecLink="#conform-invalid-mustignore",
    metadataIsValid=False,
)

# unknown encoding

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-well-formed-007",
    metadataDisplaySpecLink="#conform-invalid-mustignore",
    metadataIsValid=False,
)

# --------------------------
# Metadata Display: Encoding
# --------------------------

# UTF-8

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-encoding-001",
    metadataIsValid=True,
)

# Invalid

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-encoding-002",
    metadataIsValid=False,
)

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-encoding-003",
    metadataDisplaySpecLink="#conform-invalid-mustignore",
    metadataIsValid=False,
)

# no encoding

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-encoding-004",
    metadataIsValid=True,
)

# UTF-8 BOM

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-encoding-005",
    metadataIsValid=True,
)

# UTF-16 BOM

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-encoding-006",
    metadataDisplaySpecLink="#conform-invalid-mustignore",
    metadataIsValid=False,
)

# -------------------------------------------
# Metadata Display: Schema Validity: metadata
# -------------------------------------------

# valid

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-metadata-001",
    metadataIsValid=True,
)

# top element not metadata

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-metadata-002",
    metadataIsValid=False,
)

# missing version

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-metadata-003",
    metadataIsValid=False,
)

# invalid version

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-metadata-004",
    metadataIsValid=False,
)

# unknown attribute

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-metadata-005",
    metadataIsValid=False,
)

# unknown element

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-metadata-006",
    metadataIsValid=False,
)

# -------------------------------------------
# Metadata Display: Schema Validity: uniqueid
# -------------------------------------------

# valid

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-uniqueid-001",
    metadataIsValid=True,
)

# does not exist

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-uniqueid-002",
    metadataIsValid=True,
)

# duplicate

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-uniqueid-003",
    metadataIsValid=False,
)

# missing id attribute

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-uniqueid-004",
    metadataDisplaySpecLink="#conform-metadata-id-required",
    metadataIsValid=False,
)

# unknown attribute

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-uniqueid-005",
    metadataIsValid=False,
)

# unknown child

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-uniqueid-006",
    metadataIsValid=False,
)

# content

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-uniqueid-007",
    metadataIsValid=False,
)

# -----------------------------------------
# Metadata Display: Schema Validity: vendor
# -----------------------------------------

# valid

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-vendor-001",
    metadataIsValid=True,
)

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-vendor-002",
    metadataIsValid=True,
)

# does not exist

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-vendor-003",
    metadataIsValid=True,
)

# duplicate

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-vendor-004",
    metadataIsValid=False,
)

# missing name attribute

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-vendor-005",
    metadataDisplaySpecLink="#conform-metadata-vendor-required",
    metadataIsValid=False,
)

# dir attribute

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-vendor-006",
    metadataIsValid=True,
)

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-vendor-007",
    metadataIsValid=True,
)

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-vendor-008",
    metadataIsValid=False,
)

# class attribute

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-vendor-009",
    metadataIsValid=True,
)

# unknown attribute

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-vendor-010",
    metadataIsValid=False,
)

# unknown child

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-vendor-011",
    metadataIsValid=False,
)

# content

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-vendor-012",
    metadataIsValid=False,
)

# ------------------------------------------
# Metadata Display: Schema Validity: credits
# ------------------------------------------

# valid - single credit element

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-credits-001",
    metadataIsValid=True,
)

# valid - multiple credit elements

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-credits-002",
    metadataIsValid=True,
)

# missing credit element

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-credits-003",
    metadataIsValid=False,
)

# unknown attribute

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-credits-004",
    metadataIsValid=False,
)

# unknown element

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-credits-005",
    metadataIsValid=False,
)

# content

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-credits-006",
    metadataIsValid=False,
)

# multiple credits

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-credits-007",
    metadataIsValid=False,
)

# -----------------------------------------
# Metadata Display: Schema Validity: credit
# -----------------------------------------

# valid

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-credit-001",
    metadataIsValid=True,
)

# valid no url

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-credit-002",
    metadataIsValid=True,
)

# valid no role

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-credit-003",
    metadataIsValid=True,
)

# no name

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-credit-004",
    metadataIsValid=False,
)

# dir attribute

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-credit-005",
    metadataIsValid=True,
)

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-credit-006",
    metadataIsValid=True,
)

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-credit-007",
    metadataIsValid=False,
)

# class attribute

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-credit-008",
    metadataIsValid=True,
)

# unknown attribute

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-credit-009",
    metadataIsValid=False,
)

# child element

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-credit-010",
    metadataIsValid=False,
)

# content

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-credit-011",
    metadataIsValid=False,
)

# ----------------------------------------------
# Metadata Display: Schema Validity: description
# ----------------------------------------------

# valid with url

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-description-001",
    metadataIsValid=True,
)

# valid without url

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-description-002",
    metadataIsValid=True,
)

# valid one text element no language

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-description-003",
    metadataIsValid=True,
)

# valid one text element with language

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-description-004",
    metadataIsValid=True,
)

# valid one text element with language using lang

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-description-005",
    metadataIsValid=True,
)

# valid two text elements no language and language

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-description-006",
    metadataIsValid=True,
)

# valid two text elements language and language

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-description-007",
    metadataIsValid=True,
)

# more than one description

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-description-008",
    metadataIsValid=False,
)

# no text element

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-description-009",
    metadataIsValid=False,
)

# unknown attribute

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-description-010",
    metadataIsValid=False,
)

# unknown child element

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-description-011",
    metadataIsValid=False,
)

# content

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-description-012",
    metadataIsValid=False,
)

# dir

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-description-013",
    metadataIsValid=True,
)

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-description-014",
    metadataIsValid=True,
)

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-description-015",
    metadataIsValid=False,
)

# class

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-description-016",
    metadataIsValid=True,
)

# text element unknown attribute

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-description-017",
    metadataIsValid=False,
)

# text element child element

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-description-018",
    metadataIsValid=False,
)

# one div

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-description-019",
    metadataIsValid=True,
)

# two div

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-description-020",
    metadataIsValid=True,
)

# nested div

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-description-021",
    metadataIsValid=True,
)

# div with dir

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-description-022",
    metadataIsValid=True,
)

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-description-023",
    metadataIsValid=True,
)

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-description-024",
    metadataIsValid=False,
)

# div with class

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-description-025",
    metadataIsValid=True,
)

# one span

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-description-026",
    metadataIsValid=True,
)

# two span

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-description-027",
    metadataIsValid=True,
)

# nested span

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-description-028",
    metadataIsValid=True,
)

# span with dir

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-description-029",
    metadataIsValid=True,
)

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-description-030",
    metadataIsValid=True,
)

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-description-031",
    metadataIsValid=False,
)

# span with class

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-description-032",
    metadataIsValid=True,
)

# ------------------------------------------
# Metadata Display: Schema Validity: license
# ------------------------------------------

# valid with url and license

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-license-001",
    metadataIsValid=True,
)

# valid no url

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-license-002",
    metadataIsValid=True,
)

# valid no id

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-license-003",
    metadataIsValid=True,
)

# valid one text element no language

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-license-004",
    metadataIsValid=True,
)

# valid one text element with language

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-license-005",
    metadataIsValid=True,
)

# valid one text element with language using lang

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-license-006",
    metadataIsValid=True,
)

# valid two text elements no language and language

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-license-007",
    metadataIsValid=True,
)

# valid two text elements language and language

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-license-008",
    metadataIsValid=True,
)

# more than one license

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-license-009",
    metadataIsValid=False,
)

# no text element

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-license-010",
    metadataIsValid=True,
)

# unknown attribute

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-license-011",
    metadataIsValid=False,
)

# unknown child element

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-license-012",
    metadataIsValid=False,
)

# content

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-license-013",
    metadataIsValid=False,
)

# text element dir attribute

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-license-014",
    metadataIsValid=True,
)

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-license-015",
    metadataIsValid=True,
)

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-license-016",
    metadataIsValid=False,
)

# text element class attribute

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-license-017",
    metadataIsValid=True,
)

# text element unknown attribute

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-license-018",
    metadataIsValid=False,
)

# text element child element

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-license-019",
    metadataIsValid=False,
)

# one div

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-license-020",
    metadataIsValid=True,
)

# two div

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-license-021",
    metadataIsValid=True,
)

# nested div

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-license-022",
    metadataIsValid=True,
)


# div with dir

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-license-023",
    metadataIsValid=True,
)

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-license-024",
    metadataIsValid=True,
)

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-license-025",
    metadataIsValid=False,
)

# div with class

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-license-026",
    metadataIsValid=True,
)

# one span

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-license-027",
    metadataIsValid=True,
)

# two span

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-license-028",
    metadataIsValid=True,
)

# nested span

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-license-029",
    metadataIsValid=True,
)

# span with dir

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-license-030",
    metadataIsValid=True,
)

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-license-031",
    metadataIsValid=True,
)

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-license-032",
    metadataIsValid=False,
)

# span with class

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-license-033",
    metadataIsValid=True,
)

# --------------------------------------------
# Metadata Display: Schema Validity: copyright
# --------------------------------------------

# valid one text element no language

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-copyright-001",
    metadataIsValid=True,
)

# valid one text element with language

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-copyright-002",
    metadataIsValid=True,
)

# valid one text element with language using lang

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-copyright-003",
    metadataIsValid=True,
)

# valid two text elements no language and language

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-copyright-004",
    metadataIsValid=True,
)

# valid two text elements language and language

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-copyright-005",
    metadataIsValid=True,
)

# more than one copyright

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-copyright-006",
    metadataIsValid=False,
)

# no text element

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-copyright-007",
    metadataIsValid=False,
)

# unknown attribute

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-copyright-008",
    metadataIsValid=False,
)

# unknown child element

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-copyright-009",
    metadataIsValid=False,
)

# content

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-copyright-010",
    metadataIsValid=False,
)

# text element with dir attribute

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-copyright-011",
    metadataIsValid=True,
)

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-copyright-012",
    metadataIsValid=True,
)

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-copyright-013",
    metadataIsValid=False,
)

# text elemet with class attribute

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-copyright-014",
    metadataIsValid=True,
)

# text element unknown attribute

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-copyright-015",
    metadataIsValid=False,
)

# text element child element

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-copyright-016",
    metadataIsValid=False,
)

# one div

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-copyright-017",
    metadataIsValid=True,
)

# two div

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-copyright-018",
    metadataIsValid=True,
)

# nested div

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-copyright-019",
    metadataIsValid=True,
)

# div with dir

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-copyright-020",
    metadataIsValid=True,
)

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-copyright-021",
    metadataIsValid=True,
)

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-copyright-022",
    metadataIsValid=False,
)

# div with class

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-copyright-023",
    metadataIsValid=True,
)

# one span

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-copyright-024",
    metadataIsValid=True,
)

# two span

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-copyright-025",
    metadataIsValid=True,
)

# nested span

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-copyright-026",
    metadataIsValid=True,
)

# span with dir

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-copyright-027",
    metadataIsValid=True,
)

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-copyright-028",
    metadataIsValid=True,
)

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-copyright-029",
    metadataIsValid=False,
)

# span with class

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-copyright-030",
    metadataIsValid=True,
)

# --------------------------------------------
# Metadata Display: Schema Validity: trademark
# --------------------------------------------

# valid one text element no language

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-trademark-001",
    metadataIsValid=True,
)

# valid one text element with language

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-trademark-002",
    metadataIsValid=True,
)

# valid one text element with language using lang

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-trademark-003",
    metadataIsValid=True,
)

# valid two text elements no language and language

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-trademark-004",
    metadataIsValid=True,
)

# valid two text elements language and language

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-trademark-005",
    metadataIsValid=True,
)

# more than one trademark

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-trademark-006",
    metadataIsValid=False,
)

# no text element

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-trademark-007",
    metadataIsValid=False,
)

# unknown attribute

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-trademark-008",
    metadataIsValid=False,
)

# unknown child element

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-trademark-009",
    metadataIsValid=False,
)

# content

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-trademark-010",
    metadataIsValid=False,
)

# text element dir attribute

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-trademark-011",
    metadataIsValid=True,
)

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-trademark-012",
    metadataIsValid=True,
)

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-trademark-013",
    metadataIsValid=False,
)

# text element with class attribute

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-trademark-014",
    metadataIsValid=True,
)

# text element unknown attribute

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-trademark-015",
    metadataIsValid=False,
)

# text element child element

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-trademark-016",
    metadataIsValid=False,
)

# one div

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-trademark-017",
    metadataIsValid=True,
)

# two div

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-trademark-018",
    metadataIsValid=True,
)

# nested div

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-trademark-019",
    metadataIsValid=True,
)

# div with dir

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-trademark-020",
    metadataIsValid=True,
)

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-trademark-021",
    metadataIsValid=True,
)

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-trademark-022",
    metadataIsValid=False,
)

# div with class

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-trademark-023",
    metadataIsValid=True,
)

# one span

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-trademark-024",
    metadataIsValid=True,
)

# two span

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-trademark-025",
    metadataIsValid=True,
)

# nested span

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-trademark-026",
    metadataIsValid=True,
)

# span with dir

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-trademark-027",
    metadataIsValid=True,
)

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-trademark-028",
    metadataIsValid=True,
)

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-trademark-029",
    metadataIsValid=False,
)

# span with class

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-trademark-030",
    metadataIsValid=True,
)

# -------------------------------------------
# Metadata Display: Schema Validity: licensee
# -------------------------------------------

# valid

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-licensee-001",
    metadataIsValid=True,
)

# duplicate

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-licensee-002",
    metadataIsValid=False,
)

# missing name

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-licensee-003",
    metadataIsValid=False,
)

# dir attribute

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-licensee-004",
    metadataIsValid=True,
)

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-licensee-005",
    metadataIsValid=True,
)

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-licensee-006",
    metadataIsValid=False,
)

# class attribute

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-licensee-007",
    metadataIsValid=True,
)

# unknown attribute

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-licensee-008",
    metadataIsValid=False,
)

# child element

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-licensee-009",
    metadataIsValid=False,
)

# content

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-licensee-010",
    metadataIsValid=False,
)

# --------------------------------------------
# Metadata Display: Schema Validity: extension
# --------------------------------------------

# valid

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-extension-001",
    metadataIsValid=True,
)

# valid two extensions

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-extension-002",
    metadataIsValid=True,
)

# valid no id

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-extension-003",
    metadataIsValid=True,
)

# valid no name

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-extension-004",
    metadataIsValid=True,
)

# valid one untagged name one tagged name

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-extension-005",
    metadataIsValid=True,
)

# valid two tagged names

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-extension-006",
    metadataIsValid=True,
)

# valid more than one item

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-extension-007",
    metadataIsValid=True,
)

# no item

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-extension-008",
    metadataIsValid=False,
)

# unknown attribute

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-extension-009",
    metadataIsValid=False,
)

# unknown child

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-extension-010",
    metadataIsValid=False,
)

# content

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-extension-011",
    metadataIsValid=False,
)

# ---------------------------------------------------
# Metadata Display: Schema Validity: extension - name
# ---------------------------------------------------

# valid no lang

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-extension-012",
    metadataIsValid=True,
)

# valid xml:lang

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-extension-013",
    metadataIsValid=True,
)

# valid lang

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-extension-014",
    metadataIsValid=True,
)

# dir attribute

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-extension-015",
    metadataIsValid=True,
)

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-extension-016",
    metadataIsValid=True,
)

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-extension-017",
    metadataIsValid=False,
)

# class atribute

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-extension-018",
    metadataIsValid=True,
)

# unknown attribute

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-extension-019",
    metadataIsValid=False,
)

# child element

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-extension-020",
    metadataIsValid=False,
)

# ---------------------------------------------------
# Metadata Display: Schema Validity: extension - item
# ---------------------------------------------------

# valid

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-extension-021",
    metadataIsValid=True,
)

# valid multiple languages

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-extension-022",
    metadataIsValid=True,
)

# valid no id

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-extension-023",
    metadataIsValid=True,
)

# valid name no tag and tagged

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-extension-024",
    metadataIsValid=True,
)

# valid name two tagged

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-extension-025",
    metadataIsValid=True,
)

# valid value no tag and tagged

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-extension-026",
    metadataIsValid=True,
)

# valid value two tagged

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-extension-027",
    metadataIsValid=True,
)

# no name

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-extension-028",
    metadataIsValid=False,
)

# no value

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-extension-029",
    metadataIsValid=False,
)

# unknown attribute

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-extension-030",
    metadataIsValid=False,
)

# unknown child element

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-extension-031",
    metadataIsValid=False,
)

# content

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-extension-032",
    metadataIsValid=False,
)

# ----------------------------------------------------------
# Metadata Display: Schema Validity: extension - item - name
# ----------------------------------------------------------

# valid no lang

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-extension-033",
    metadataIsValid=True,
)

# valid xml:lang

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-extension-034",
    metadataIsValid=True,
)

# valid lang

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-extension-035",
    metadataIsValid=True,
)

# dir attribute

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-extension-036",
    metadataIsValid=True,
)

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-extension-037",
    metadataIsValid=True,
)

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-extension-038",
    metadataIsValid=False,
)

# class attribute

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-extension-039",
    metadataIsValid=True,
)

# unknown attribute

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-extension-040",
    metadataIsValid=False,
)

# child element

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-extension-041",
    metadataIsValid=False,
)

# -----------------------------------------------------------
# Metadata Display: Schema Validity: extension - item - value
# -----------------------------------------------------------

# valid no lang

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-extension-042",
    metadataIsValid=True,
)

# valid xml:lang

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-extension-043",
    metadataIsValid=True,
)

# valid lang

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-extension-044",
    metadataIsValid=True,
)

# dir attribute

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-extension-045",
    metadataIsValid=True,
)

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-extension-046",
    metadataIsValid=True,
)

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-extension-047",
    metadataIsValid=False,
)

# class attribute

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-extension-048",
    metadataIsValid=True,
)

# unknown attribute

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-extension-049",
    metadataIsValid=False,
)

# child element

writeMetadataSchemaValidityTest(
    identifier="metadatadisplay-schema-extension-050",
    metadataIsValid=False,
)

# ------------
# Availability
# ------------

# the HTML for this case is generated manually
# as is the index entry

available1 = """
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
	<head>
		<meta http-equiv="content-type" content="text/html;charset=UTF-8"/>
		<title>WOFF Test: Font access</title>
		<link rel="author" title="Chris Lilley" href="http://www.w3.org/People" />
		<link rel="help" href="#General" />
		<link rel="help" href="#conform-css3font-available" />
		<meta name="flags" content="font" />
		<meta name="assert" content="Linked fonts are only available to the documents that reference them" />
		<style type="text/css"><![CDATA[
			body {
				font-size: 20px;
			}
			pre {
				font-size: 12px;
			}
			iframe {
				width: 24em;
				height: 300px;
				border: thin solid green
			}
		]]></style>
	</head>
	<body>
		<p><a href="../../FontsToInstall">Test fonts</a> must be installed for this test. The WOFF being tested will be loaded over the network so please wait until the download is complete before determing the success of this test.</p>
		<p>Test passes if the word PASS appears <em>twice</em> below.</p>
		<iframe src="available-001a.xht" />
		<iframe src="available-001b.xht" />

	</body>
</html>
""".strip()
p = os.path.join(userAgentTestDirectory, "available-001.xht")
f = open(p, "wb")
f.write(available1)
f.close()

available2 = """
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
	<head>
		<meta http-equiv="content-type" content="text/html;charset=UTF-8"/>
		<title>WOFF Test: Font access</title>
		<link rel="author" title="Tal Leming" href="http://typesupply.com" />
		<link rel="author" title="Chris Lilley" href="http://www.w3.org/People" />
		<link rel="help" href="#General" />
		<link rel="help" href="#conform-css3font-available" />
		<meta name="flags" content="font" />
		<meta name="assert" content="Linked fonts are only available to the documents that reference them" />
		<style type="text/css"><![CDATA[
			@font-face {
				font-family: "WOFF Test";
				src: url("resources/valid-001.woff2") format("woff2");
			}
			body {
				font-size: 20px;
			}
			pre {
				font-size: 12px;
			}
			.test {
				font-family: "WOFF Test", "WOFF Test CFF Fallback";
				font-size: 200px;
				margin-top: 50px;
			}
		]]></style>
	</head>
	<body>
		<div class="test">P</div>
	</body>
</html>
""".strip()
p = os.path.join(userAgentTestDirectory, "available-001a.xht")
f = open(p, "wb")
f.write(available2)
f.close()

available3 = """
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
	<head>
		<meta http-equiv="content-type" content="text/html;charset=UTF-8"/>
		<title>WOFF Test: Font access</title>
		<link rel="author" title="Tal Leming" href="http://typesupply.com" />
		<link rel="author" title="Chris Lilley" href="http://www.w3.org/People" />
		<link rel="help" href="#General" />
		<link rel="help" href="#conform-css3font-available" />
		<meta name="flags" content="font" />
		<meta name="assert" content="Linked fonts are only available to the documents that reference them" />
		<style type="text/css"><![CDATA[
			body {
				font-size: 20px;
			}
			pre {
				font-size: 12px;
			}
			.test {
				font-family: "WOFF Test", "WOFF Test CFF Fallback";
				font-size: 200px;
				margin-top: 50px;
			}
		]]></style>
	</head>
	<body>
		<div class="test">F</div>
	</body>
</html>
""".strip()
p = os.path.join(userAgentTestDirectory, "available-001b.xht")
f = open(p, "wb")
f.write(available3)
f.close()

identifier = "available-001"
title = "Font access"
assertion = "Linked fonts are only available to the documents that reference them"

testRegistry[tag].append(
    dict(
        identifier=identifier,
        flags=["font"],
        title=title,
        assertion=assertion,
        sfntExpectation=True,
        sfntURL=[specificationURL+"#General", specificationURL+"#conform-css3font-available"],
        metadataExpectation=None,
        metadataURL=None,
        credits=[dict(title="Chris Lilley", role="author", link="http://www.w3.org/People")],
        hasReferenceRendering=False
    )
)
registeredIdentifiers.add(identifier)
registeredTitles.add(title)
registeredAssertions.add(assertion)

# ------------------
# Generate the Index
# ------------------

print "Compiling index..."

testGroups = []

for tag, title, url in groupDefinitions:
    group = dict(title=title, url=url, testCases=testRegistry[tag])
    testGroups.append(group)

generateSFNTDisplayIndexHTML(directory=userAgentTestDirectory, testCases=testGroups)

# ---------------------
# Generate the Manifest
# ---------------------

print "Compiling manifest..."

manifest = []

for tag, title, url in groupDefinitions:
    for testCase in testRegistry[tag]:
        identifier = testCase["identifier"]
        title = testCase["title"]
        assertion = testCase["assertion"]
        # gather the flags
        flags = testCase["flags"]
        flags = ",".join(flags)
        # gather the links
        links = []
        if testCase["sfntURL"]:
            for url in testCase["sfntURL"]:
                if "#" in url:
                    links.append("#" + url.split("#")[-1])
        if testCase["metadataURL"] and "#" in testCase["metadataURL"]:
            links.append("#" + testCase["metadataURL"].split("#")[-1])
        links = ",".join(links)
        # gather the credits
        credits = testCase["credits"]
        credits = ["%s <%s>" % (credit["title"], credit["link"]) for credit in credits]
        credits = ",".join(credits)
        # format the line
        line = "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s" % (
            identifier,             # id
            identifier + "-ref",    # reference
            title,                  # title
            flags,                  # flags
            links,                  # links
            "DUMMY",                # revision
            credits,                # credits
            assertion               # assertion
        )
        # store
        manifest.append(line)

path = os.path.join(userAgentDirectory, "manifest.txt")
if os.path.exists(path):
    os.remove(path)
f = open(path, "wb")
f.write("\n".join(manifest))
f.close()

# -----------------------
# Check for Unknown Files
# -----------------------

skip = "testcaseindex available-001a available-001b".split(" ")

xhtPattern = os.path.join(userAgentTestDirectory, "*.xht")
woffPattern = os.path.join(userAgentTestResourcesDirectory, "*.woff2")

filesOnDisk = glob.glob(xhtPattern)
filesOnDisk += glob.glob(woffPattern)

for path in filesOnDisk:
    identifier = os.path.basename(path)
    identifier = identifier.split(".")[0]
    identifier = identifier.replace("-ref", "")
    if identifier not in registeredIdentifiers and identifier not in skip:
        print "Unknown file:", path
