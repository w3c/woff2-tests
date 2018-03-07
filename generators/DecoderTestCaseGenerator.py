"""
This script generates the decoder test cases. It will create a directory
one level up from the directory containing this script called "Decoder".
That directory will have the structure:

    /Format
        README.txt - information about how the tests were generated and how they should be modified
        /Tests
            testcaseindex.xht - index of all test cases
            test-case-name-number.otf/ttf - individual SFNT test case
            /resources
                index.css - index CSS file

Within this script, each test case is generated with a call to the
writeTest function. In this, SFNT data must be passed along with
details about the data. This function will generate the SFNT
and register the case in the suite index.
"""

import os
import shutil
import glob
import struct
import zipfile
from fontTools.misc import sstruct
from fontTools.ttLib import TTFont, getSearchRange
from fontTools.ttLib.sfnt import sfntDirectoryFormat, sfntDirectorySize, sfntDirectoryEntryFormat, sfntDirectoryEntrySize,\
                                 ttcHeaderFormat, ttcHeaderSize
from testCaseGeneratorLib.defaultData import defaultSFNTTestData, defaultTestData
from testCaseGeneratorLib.sfnt import packSFNT, getSFNTCollectionData, getWOFFCollectionData
from testCaseGeneratorLib.paths import resourcesDirectory, decoderDirectory, decoderTestDirectory,\
                                       decoderResourcesDirectory, sfntTTFSourcePath
from testCaseGeneratorLib.woff import packTestDirectory, packTestHeader
from testCaseGeneratorLib.html import generateDecoderIndexHTML, expandSpecLinks
from testCaseGeneratorLib.utilities import padData, calcPaddingLength, calcTableChecksum
from testCaseGeneratorLib import sharedCases
from testCaseGeneratorLib.sharedCases import *

# ------------------
# Directory Creation
# (if needed)
# ------------------

if not os.path.exists(decoderDirectory):
    os.makedirs(decoderDirectory)
if not os.path.exists(decoderTestDirectory):
    os.makedirs(decoderTestDirectory)
if not os.path.exists(decoderResourcesDirectory):
    os.makedirs(decoderResourcesDirectory)

# -------------------
# Move HTML Resources
# -------------------

# index css
destPath = os.path.join(decoderResourcesDirectory, "index.css")
if os.path.exists(destPath):
    os.remove(destPath)
shutil.copy(os.path.join(resourcesDirectory, "index.css"), destPath)

# ---------------
# Test Case Index
# ---------------

# As the tests are generated a log will be kept.
# This log will be translated into an index after
# all of the tests have been written.

indexNote = """
The tests in this suite represent SFNT data to be used for WOFF
conversion without any alteration or correction.
""".strip()

roundTripNote = """
These files are provided as test cases for checking that the
result of converting to WOFF and back to SFNT results in a file
that is functionaly equivalent to the original SFNT.
""".strip()

validationNote = """
These files are provided as test cases for checking that the
result of converting WOFF back to SFNT results in a file
that confirms the OFF structure validity.
""".strip()

groupDefinitions = [
    # identifier, title, spec section, category note
    ("roundtrip", "Round-Trip Tests", None, roundTripNote),
    ("validation", "OFF Validation Tests", None, validationNote),
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

def writeTest(identifier, title, description, data, specLink=None, credits=[], roundTrip=False, flavor="CFF"):
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

    data: The complete binary data for either the WOFF, or both WOFF and SFNT.

    specLink: The anchor in the WOFF spec that the test case is testing.

    credits: A list of dictionaries defining the credits for the test case. The
    dictionaries must have this form:

        title="Name of the autor or reviewer",
        role="author or reviewer",
        link="mailto:email or http://contactpage"

    roundTrip: A boolean indicating if this is a round-trip test.

    flavor: The flavor of the WOFF data. The options are CFF or TTF.
    """
    print "Compiling %s..." % identifier
    assert identifier not in registeredIdentifiers, "Duplicate identifier! %s" % identifier
    assert title not in registeredTitles, "Duplicate title! %s" % title
    assert description not in registeredDescriptions, "Duplicate description! %s" % description
    registeredIdentifiers.add(identifier)
    registeredTitles.add(title)
    registeredDescriptions.add(description)

    specLink = expandSpecLinks(specLink)

    # generate the SFNT
    if roundTrip:
        sfntPath = os.path.join(decoderTestDirectory, identifier)
        if flavor == "CFF":
            sfntPath += ".otf"
        else:
            sfntPath += ".ttf"
        f = open(sfntPath, "wb")
        f.write(data[1])
        f.close()
        data = data[0]
    woffPath = os.path.join(decoderTestDirectory, identifier) + ".woff2"
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
            roundTrip=roundTrip,
            specLink=specLink
        )
    )

def writeTestCollection(identifier, title, description, data, specLink=None, credits=[]):
    """
    This function generates all of the files needed by a test case and
    registers the case with the suite. The arguments:

    identifier: The base identifier for the test case. The identifier must be
    a - separated sequence of group name (from the groupDefinitions
    listed above) and test case description (arbitrary length).

    title: A thorough, but not too long, title for the test case.

    description: A detailed statement about what the test case is proving.

    data: A list of the complete binary data for WOFF.

    specLink: The anchor in the WOFF spec that the test case is testing.

    credits: A list of dictionaries defining the credits for the test case. The
    dictionaries must have this form:

        title="Name of the autor or reviewer",
        role="author or reviewer",
        link="mailto:email or http://contactpage"
    """
    assert description not in registeredDescriptions, "Duplicate description! %s" % description
    registeredDescriptions.add(description)

    specLink = expandSpecLinks(specLink)
    tag = identifier.split("-")[0]

    for i, d in enumerate(data):
        number = "%03d" % (i + 1)
        test_identifier = identifier + "-" + number
        test_title = title + " " + number
        print "Compiling %s..." % test_identifier

        assert test_title not in registeredTitles, "Duplicate title! %s" % test_title
        assert test_identifier not in registeredIdentifiers, "Duplicate identifier! %s" % test_identifier
        registeredIdentifiers.add(test_identifier)
        registeredTitles.add(test_title)

        woffPath = os.path.join(decoderTestDirectory, test_identifier) + ".woff2"
        f = open(woffPath, "wb")
        f.write(d)
        f.close()

        # register the test
        testRegistry[tag].append(
            dict(
                identifier=test_identifier,
                title=test_title,
                description=description,
                roundTrip=False,
                specLink=specLink
            )
        )

# -----
# Tests
# -----

def makeCollectionOffsetTables1():
    paths = [sfntTTFSourcePath, sfntTTFSourcePath, sfntTTFSourcePath]
    woffdata = getWOFFCollectionData(paths)
    sfntdata = getSFNTCollectionData(paths)

    return woffdata, sfntdata

writeTest(
    identifier="roundtrip-offset-tables-001",
    title="Font Collection Offset Tables",
    description="TTF flavored font collection to verify that the output file has the same number of font entries in the font collection and that each font entry is represented by the same set of font tables as the input file.",
    roundTrip=True,
    flavor="TTF",
    credits=[dict(title="Khaled Hosny", role="author", link="http://khaledhosny.org")],
    specLink="#conform-mustRestoreCollectionOffsetTables",
    data=makeCollectionOffsetTables1()
)

def makeFixCollection1():
    paths = [sfntTTFSourcePath, sfntTTFSourcePath, sfntTTFSourcePath]
    woffdata = getWOFFCollectionData(paths)
    sfntdata = getSFNTCollectionData(paths, DSIG=True)

    return woffdata, sfntdata

writeTest(
    identifier="roundtrip-collection-dsig-001",
    title="Font Collection With DSIG table",
    description="TTF flavored font collection with DSIG table to verify that the output file has the same number of font entries in the font collection and that DSIG table entry was deleted. Check the font collection header format and if it's set to version 2.0 make sure that it was either modified to have the TTC Header fields {ulDsigTag, ulDsigLength, ulDsigOffset} set to zeros, or that TTC Header was converted to version 1.0.",
    roundTrip=True,
    flavor="TTF",
    credits=[dict(title="Khaled Hosny", role="author", link="http://khaledhosny.org")],
    specLink="#conform-mustFixCollection",
    data=makeFixCollection1()
)

def makeCollectionOrder1():
    paths = [sfntTTFSourcePath, sfntTTFSourcePath, sfntTTFSourcePath]
    woffdata = getWOFFCollectionData(paths, reverseNames=True)
    sfntdata = getSFNTCollectionData(paths, reverseNames=True)

    return woffdata, sfntdata

writeTest(
    identifier="roundtrip-collection-order-001",
    title="Font Collection With Unsorted Fonts",
    description="TTF flavored font collection with fonts not in alphabetical order. The encoder/decoder must keep the original font order in the collection.",
    roundTrip=True,
    flavor="TTF",
    credits=[dict(title="Khaled Hosny", role="author", link="http://khaledhosny.org")],
    specLink="#conform-mustRestoreFontOrder",
    data=makeCollectionOrder1()
)

def makeHmtxLSB1():
    woffdata = makeHmtxTransform1()
    sfntdata = makeLSB1()

    return woffdata, sfntdata

writeTest(
    identifier="roundtrip-hmtx-lsb-001",
    title="Font With Hmtx Table",
    description="TTF flavored font with hmtx table. The encoder/decoder must keep he same 'hmtx' table entries as it was encoded in the original input file.",
    roundTrip=True,
    flavor="TTF",
    credits=[dict(title="Khaled Hosny", role="author", link="http://khaledhosny.org")],
    specLink="#conform-mustReconstructLSBs",
    data=makeHmtxLSB1(),
)

writeTest(
    identifier="validation-loca-format-001",
    title=makeValidLoca1Title,
    description=makeValidLoca1Description,
    credits=makeValidLoca1Credits,
    roundTrip=False,
    flavor="TTF",
    specLink="#conform-mustRecordLocaOffsets",
    data=makeValidLoca1()
)

writeTest(
    identifier="validation-loca-format-002",
    title=makeValidLoca2Title,
    description=makeValidLoca2Description,
    credits=makeValidLoca2Credits,
    roundTrip=False,
    flavor="TTF",
    specLink="#conform-mustRecordLocaOffsets",
    data=makeValidLoca2()
)

writeTest(
    identifier="validation-checksum-001",
    title="WOFF Checksum Calculation",
    description="Valid CFF flavored WOFF file, the output file is put through an OFF validator to check the validity of table checksums.",
    credits=[dict(title="Khaled Hosny", role="author", link="http://khaledhosny.org")],
    roundTrip=False,
    specLink="#conform-mustCalculateCheckSum",
    data=makeValidWOFF1()
)

writeTest(
    identifier="validation-checksum-002",
    title="WOFF Head Checksum Calculation",
    description="Valid CFF flavored WOFF file, the output file is put through an OFF validator to check the validity of head table checkSumAdjustment.",
    credits=[dict(title="Khaled Hosny", role="author", link="http://khaledhosny.org")],
    roundTrip=False,
    specLink="#conform-mustRecalculateHeadCheckSum",
    data=makeValidWOFF1()
)

metadata = [
    "schema-vendor-001", "schema-vendor-002", "schema-vendor-003",
    "schema-vendor-006", "schema-vendor-007", "schema-vendor-009",
    "schema-credits-002", "schema-credit-001", "schema-credit-002",
    "schema-credit-003", "schema-credit-005", "schema-credit-006",
    "schema-credit-008", "schema-description-001", "schema-description-002",
    "schema-description-003", "schema-description-004",
    "schema-description-005", "schema-description-006",
    "schema-description-007", "schema-license-001", "schema-license-002",
    "schema-license-003", "schema-license-004", "schema-license-005",
    "schema-license-006", "schema-license-007", "schema-license-008",
    "schema-copyright-001", "schema-copyright-002", "schema-copyright-003",
    "schema-copyright-004", "schema-copyright-005", "schema-trademark-002",
    "schema-trademark-003", "schema-trademark-004", "schema-trademark-005",
    "schema-licensee-001", "schema-extension-001", "schema-extension-002",
    "schema-extension-003", "schema-extension-004", "schema-extension-005",
    "schema-extension-006", "schema-extension-007", "schema-extension-012",
    "schema-extension-013", "schema-extension-014", "schema-extension-015",
    "schema-extension-016", "schema-extension-018", "schema-extension-021",
    "schema-extension-022", "schema-extension-023", "schema-extension-024",
    "schema-extension-025", "schema-extension-026", "schema-extension-027",
    "schema-extension-033", "schema-extension-034", "schema-extension-035",
    "schema-extension-036", "schema-extension-037", "schema-extension-039",
    "schema-extension-042", "schema-extension-043", "schema-extension-044",
    "schema-extension-045", "schema-extension-046", "schema-extension-048",
    "encoding-001", "encoding-004", "encoding-005", "schema-metadata-001",
    "schema-uniqueid-001", "schema-uniqueid-002", "schema-credits-001",
    "schema-description-013", "schema-description-014",
    "schema-description-016", "schema-description-019",
    "schema-description-020", "schema-description-021",
    "schema-description-022", "schema-description-023",
    "schema-description-025", "schema-description-026",
    "schema-description-027", "schema-description-028",
    "schema-description-029", "schema-description-030",
    "schema-description-032", "schema-license-010", "schema-license-014",
    "schema-license-015", "schema-license-017", "schema-license-020",
    "schema-license-021", "schema-license-022", "schema-license-023",
    "schema-license-024", "schema-license-026", "schema-license-027",
    "schema-license-028", "schema-license-029", "schema-license-030",
    "schema-license-031", "schema-license-033", "schema-copyright-011",
    "schema-copyright-012", "schema-copyright-014", "schema-copyright-017",
    "schema-copyright-018", "schema-copyright-019", "schema-copyright-020",
    "schema-copyright-021", "schema-copyright-023", "schema-copyright-024",
    "schema-copyright-025", "schema-copyright-026", "schema-copyright-027",
    "schema-copyright-028", "schema-copyright-030", "schema-trademark-001",
    "schema-trademark-011", "schema-trademark-012", "schema-trademark-014",
    "schema-trademark-017", "schema-trademark-018", "schema-trademark-019",
    "schema-trademark-020", "schema-trademark-021", "schema-trademark-023",
    "schema-trademark-024", "schema-trademark-025", "schema-trademark-026",
    "schema-trademark-027", "schema-trademark-028", "schema-trademark-030",
    "schema-licensee-004", "schema-licensee-005", "schema-licensee-007",
]

OFFData = [
    makeValidWOFF1(), makeValidWOFF2(), makeValidWOFF3(), makeValidWOFF4(),
    makeValidWOFF5(), makeValidWOFF6(), makeValidWOFF7(), makeValidWOFF8(),
    makeLocaSizeTest1(), makeLocaSizeTest2(), makeLocaSizeTest3(),
    makeGlyfBBox1()
]

for identifier in metadata:
    parts = identifier.split("-")
    number = int(parts[-1])
    group = parts[:-1]
    group = [i.title() for i in group]
    group = "".join(group)
    importBase = "metadata" + group + str(number)
    metadata = getattr(sharedCases, importBase + "Metadata")
    OFFData.append(makeMetadataTest(metadata)[0])

writeTestCollection(
    identifier="validation-off",
    title="Valid WOFF File",
    description="Valid WOFF file from the file format tests, the decoded file should run through a font validator to confirm the OFF structure validity.",
    credits=[dict(title="Khaled Hosny", role="author", link="http://khaledhosny.org")],
    specLink="#conform-mustProduceOFF",
    data=OFFData
)

# ------------------
# Generate the Index
# ------------------

print "Compiling index..."

testGroups = []

for tag, title, url, note in groupDefinitions:
    group = dict(title=title, url=url, testCases=testRegistry[tag], note=note)
    testGroups.append(group)

generateDecoderIndexHTML(directory=decoderTestDirectory, testCases=testGroups, note=indexNote)

# ----------------
# Generate the zip
# ----------------

print "Compiling zip file..."

zipPath = os.path.join(decoderTestDirectory, "DecoderTestFonts.zip")
if os.path.exists(zipPath):
    os.remove(zipPath)

allBinariesZip = zipfile.ZipFile(zipPath, "w")

sfntPattern = os.path.join(decoderTestDirectory, "*.*tf")
woffPattern = os.path.join(decoderTestDirectory, "*.woff2")
filesOnDisk = glob.glob(sfntPattern) + glob.glob(woffPattern)
for path in filesOnDisk:
    ext = os.path.splitext(path)[1]
    assert ext in (".otf", ".ttf", ".woff2")
    allBinariesZip.write(path, os.path.basename(path))

allBinariesZip.close()

# ---------------------
# Generate the Manifest
# ---------------------

print "Compiling manifest..."

manifest = []

for tag, title, url, note in groupDefinitions:
    for testCase in testRegistry[tag]:
        identifier = testCase["identifier"]
        title = testCase["title"]
        assertion = testCase["description"]
        links = "#" + testCase["specLink"].split("#")[-1]
        # XXX force the chapter onto the links
        links = "#TableDirectory," + links
        flags = ""
        credits = ""
        # format the line
        line = "%s\t%s\t%s\t%s\t%s\t%s" % (
            identifier,             # id
            "",                     # reference
            title,                  # title
            flags,                  # flags
            links,                  # links
            assertion               # assertion
        )
        # store
        manifest.append(line)

path = os.path.join(decoderDirectory, "manifest.txt")
if os.path.exists(path):
    os.remove(path)
f = open(path, "wb")
f.write("\n".join(manifest))
f.close()

# -----------------------
# Check for Unknown Files
# -----------------------

otfPattern = os.path.join(decoderTestDirectory, "*.otf")
ttfPattern = os.path.join(decoderTestDirectory, "*.ttf")
woffPattern = os.path.join(decoderTestDirectory, "*.woff2")
filesOnDisk = glob.glob(otfPattern) + glob.glob(ttfPattern) + glob.glob(woffPattern)

for path in filesOnDisk:
    identifier = os.path.basename(path)
    identifier = identifier.split(".")[0]
    if identifier not in registeredIdentifiers:
        print "Unknown file:", path
