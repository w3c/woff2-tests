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
                                       decoderResourcesDirectory, sfntTTFSourcePath, sfntTTFCompositeSourcePath
from testCaseGeneratorLib.woff import packTestDirectory, packTestHeader
from testCaseGeneratorLib.html import generateDecoderIndexHTML, expandSpecLinks
from testCaseGeneratorLib.utilities import padData, calcPaddingLength, calcTableChecksum
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
that confirms the OFF structure validity..
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

writeTest(
    identifier="validation-bbox-001",
    title="WOFF Empty Bbox Calculation",
    description="Valid CFF flavored WOFF file, the output file is put through an OFF validator to check that the bounding box of empty glyphs is set to zeros.",
    credits=[dict(title="Khaled Hosny", role="author", link="http://khaledhosny.org")],
    roundTrip=False,
    specLink="#conform-mustCalculateEmptyBBox",
    data=makeValidWOFF5()
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
