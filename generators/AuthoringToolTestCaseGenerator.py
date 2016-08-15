"""
This script generates the authoring tool test cases. It will create a directory
one level up from the directory containing this script called "AuthoringTool".
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
from fontTools.ttLib import getSearchRange
from fontTools.ttLib.sfnt import sfntDirectorySize, sfntDirectoryEntrySize
from testCaseGeneratorLib.defaultData import defaultSFNTTestData
from testCaseGeneratorLib.sfnt import packSFNT, getSFNTCollectionData
from testCaseGeneratorLib.paths import resourcesDirectory, authoringToolDirectory, authoringToolTestDirectory,\
                                       authoringToolResourcesDirectory, sfntTTFSourcePath, sfntTTFCompositeSourcePath
from testCaseGeneratorLib.html import generateAuthoringToolIndexHTML, expandSpecLinks
from testCaseGeneratorLib.utilities import padData, calcPaddingLength, calcTableChecksum

# ------------------
# Directory Creation
# (if needed)
# ------------------

if not os.path.exists(authoringToolDirectory):
    os.makedirs(authoringToolDirectory)
if not os.path.exists(authoringToolTestDirectory):
    os.makedirs(authoringToolTestDirectory)
if not os.path.exists(authoringToolResourcesDirectory):
    os.makedirs(authoringToolResourcesDirectory)

# -------------------
# Move HTML Resources
# -------------------

# index css
destPath = os.path.join(authoringToolResourcesDirectory, "index.css")
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
conversion without any alteration or correction. An authoring tool
may allow the explicit or silent modification and/or correction of
SFNT data. In such a case, the tests in this suite that are labeled
as "should not convert" may be converted, so long as the problems
in the files have been corrected. In that case, there is no longer
any access to the "input font" as defined in the WOFF specification,
so the bitwise identical tests should be skipped.
""".strip()

validNote = """
These files are valid SFNTs that should be converted to WOFF.
""".strip()

invalidSFNTNote = """
These files are invalid SFNTs that should not be converted to WOFF.
""".strip()

tableDataNote = """
These files are valid SFNTs that excercise conversion of the table data.
""".strip()

tableDirectoryNote = """
These files are valid SFNTs that excercise conversion of the table directory.
""".strip()

bitwiseNote = """
These files are provided as test cases for checking that the
result of converting to WOFF and back to SFNT results in a file
that is bitwise identical to the original SFNT.
""".strip()

groupDefinitions = [
    # identifier, title, spec section, category note
    ("validsfnt", "Valid SFNTs", None, validNote),
    ("invalidsfnt", "Invalid SFNT Tests", expandSpecLinks("#conform-incorrect-reject"), invalidSFNTNote),
    ("tabledata", "SFNT Table Data Tests", expandSpecLinks("#DataTables"), tableDataNote),
    ("tabledirectory", "SFNT Table Directory Tests", expandSpecLinks("#DataTables"), tableDirectoryNote),
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

def writeTest(identifier, title, description, data, specLink=None, credits=[], shouldConvert=False, flavor="CFF"):
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

    data: The complete binary data for the SFNT.

    specLink: The anchor in the WOFF spec that the test case is testing.

    credits: A list of dictionaries defining the credits for the test case. The
    dictionaries must have this form:

        title="Name of the autor or reviewer",
        role="author or reviewer",
        link="mailto:email or http://contactpage"

    shouldConvert: A boolean indicating if the SFNT is valid enough for
    conversion to WOFF.

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
    sfntPath = os.path.join(authoringToolTestDirectory, identifier)
    if flavor == "CFF":
        sfntPath += ".otf"
    else:
        sfntPath += ".ttf"
    f = open(sfntPath, "wb")
    f.write(data)
    f.close()

    # register the test
    tag = identifier.split("-")[0]
    testRegistry[tag].append(
        dict(
            identifier=identifier,
            title=title,
            description=description,
            shouldConvert=shouldConvert,
            specLink=specLink
        )
    )

# ---------------
# Valid SFNT Data
# ---------------

def makeValidSFNT(flavor="CFF"):
    header, directory, tableData = defaultSFNTTestData(flavor=flavor)
    data = packSFNT(header, directory, tableData, flavor=flavor)
    return data

# -----------
# Compression
# -----------


# ----
# DSIG
# ----

def makeDSIG(flavor="CFF"):
    header, directory, tableData = defaultSFNTTestData(flavor=flavor)
    # adjust the header
    header["numTables"] += 1
    # store the data
    data = "\0" * 4
    tableData["DSIG"] = data
    # offset the directory entries
    for entry in directory:
        entry["offset"] += sfntDirectoryEntrySize
    # find the offset
    entries = [(entry["offset"], entry) for entry in directory]
    entry = max(entries)[1]
    offset = entry["offset"] + entry["length"]
    offset += calcPaddingLength(offset)
    # make the entry
    directory.append(
        dict(
            tag="DSIG",
            offset=offset,
            length=4,
            checksum=calcTableChecksum("DSIG", data)
        )
    )
    # compile
    data = packSFNT(header, directory, tableData, flavor=flavor)
    return data

writeTest(
    identifier="tabledata-dsig-001",
    title="CFF SFNT With DSIG Table",
    description="The CFF flavored SFNT has a DSIG table. (Note: this is not a valid DSIG. It should not be used for testing anything other than the presence of the table after the conversion process.) The process of converting to WOFF should remove the DSIG table.",
    shouldConvert=True,
    credits=[dict(title="Khaled Hosny", role="author", link="http://khaledhosny.org")],
    specLink="#conform-mustRemoveDSIG",
    data=makeDSIG()
)

writeTest(
    identifier="tabledata-dsig-002",
    title="TTF SFNT With DSIG Table",
    description="The TFF flavored SFNT has a DSIG table. (Note: this is not a valid DSIG. It should not be used for testing anything other than the presence of the table after the conversion process.) The process of converting to WOFF should remove the DSIG table.",
    shouldConvert=True,
    credits=[dict(title="Khaled Hosny", role="author", link="http://khaledhosny.org")],
    specLink="#conform-mustRemoveDSIG",
    data=makeDSIG(flavor="TTF"),
    flavor="TTF"
)

# --------------------
# Bit 11 of head flags
# --------------------

writeTest(
    identifier="tabledata-bit11-001",
    title="Valid CFF SFNT For Bit 11",
    description="The bit 11 of the head table flags must be set for CFF flavored SFNT.",
    shouldConvert=True,
    credits=[dict(title="Khaled Hosny", role="author", link="http://khaledhosny.org")],
    specLink="#conform-mustSetBit11",
    data=makeValidSFNT()
)

writeTest(
    identifier="tabledata-bit11-002",
    title="Valid TTF SFNT For Bit 11",
    description="The bit 11 of the head table flags must be set for TTF flavored SFNT.",
    shouldConvert=True,
    credits=[dict(title="Khaled Hosny", role="author", link="http://khaledhosny.org")],
    specLink="#conform-mustSetBit11",
    data=makeValidSFNT(flavor="TTF"),
    flavor="TTF"
)

# ---------------
# Transformations
# ---------------


# -----------
# Collections
# -----------

def makeCollectionSharing1():
    data = getSFNTCollectionData([sfntTTFSourcePath, sfntTTFSourcePath], modifyNames=False)

    return data

writeTest(
    identifier="tabledata-sharing-001",
    title="Valid Font Collection With No Duplicate Tables",
    description="TTF flavored SFNT collection with all tables being shared, output WOFF font must not contain any duplicate tables.",
    shouldConvert=True,
    credits=[dict(title="Khaled Hosny", role="author", link="http://khaledhosny.org")],
    specLink="#conform-mustNotDuplicateTables",
    data=makeCollectionSharing1(),
    flavor="TTF"
)

def makeCollectionSharing2():
    data = getSFNTCollectionData([sfntTTFSourcePath, sfntTTFSourcePath])

    return data

writeTest(
    identifier="tabledata-sharing-002",
    title="Valid Font Collection With Shared Glyf/Loca",
    description="TTF flavored SFNT collection containing two fonts sharing the same glyf and loca tables.",
    shouldConvert=True,
    credits=[dict(title="Khaled Hosny", role="author", link="http://khaledhosny.org")],
    specLink="#conform-mustVerifyGlyfLocaShared",
    data=makeCollectionSharing2(),
    flavor="TTF"
)

def makeCollectionSharing3():
    data = getSFNTCollectionData([sfntTTFSourcePath, sfntTTFSourcePath, sfntTTFCompositeSourcePath])

    return data

writeTest(
    identifier="tabledata-sharing-003",
    title="Valid Font Collection With Shared And Unshared Glyf/Loca",
    description="TTF flavored SFNT collection containing three fonts, two of them sharing the same glyf and loca tables and the third using different glyf and loca tables.",
    shouldConvert=True,
    credits=[dict(title="Khaled Hosny", role="author", link="http://khaledhosny.org")],
    specLink="#conform-mustNotDuplicateTables",
    data=makeCollectionSharing3(),
    flavor="TTF"
)

def makeCollectionSharing4():
    data = getSFNTCollectionData([sfntTTFSourcePath, sfntTTFSourcePath], duplicates=["loca"])

    return data

writeTest(
    identifier="tabledata-sharing-004",
    title="Invalid Font Collection With Unshared Loca",
    description="An invalid TTF flavored SFNT collection containing two fonts sharing glyf but not loca table.",
    shouldConvert=False,
    credits=[dict(title="Khaled Hosny", role="author", link="http://khaledhosny.org")],
    specLink="#conform-mustRejectSingleGlyfLocaShared",
    data=makeCollectionSharing4(),
    flavor="TTF"
)

def makeCollectionSharing5():
    data = getSFNTCollectionData([sfntTTFSourcePath, sfntTTFSourcePath], duplicates=["glyf"])

    return data

writeTest(
    identifier="tabledata-sharing-005",
    title="Invalid Font Collection With Unshared Glyf",
    description="An invalid TTF flavored SFNT collection containing two fonts sharing loca but not glyf table.",
    shouldConvert=False,
    credits=[dict(title="Khaled Hosny", role="author", link="http://khaledhosny.org")],
    specLink="#conform-mustRejectSingleGlyfLocaShared",
    data=makeCollectionSharing5(),
    flavor="TTF"
)

def makeCollectionSharing6():
    data = getSFNTCollectionData([sfntTTFSourcePath, sfntTTFSourcePath], shared=["cmap"])

    return data

writeTest(
    identifier="tabledata-sharing-006",
    title="Font Collection With Single Shared Table",
    description="A valid TTF flavored SFNT collection containing two fonts sharing only the cmap table.",
    shouldConvert=True,
    credits=[dict(title="Khaled Hosny", role="author", link="http://khaledhosny.org")],
    specLink="#conform-mustEmitSingleEntryDirectory",
    data=makeCollectionSharing6(),
    flavor="TTF"
)

def makeCollectionTransform1():
    data = getSFNTCollectionData([sfntTTFSourcePath, sfntTTFCompositeSourcePath])

    return data

writeTest(
    identifier="tabledata-transform-002",
    title="Valid Font Collection With Multiple Glyf/Loca",
    description="TTF flavored SFNT collection with multiple unshared glyf and loca tables, all of them must be transformed in the output WOFF font.",
    shouldConvert=True,
    credits=[dict(title="Khaled Hosny", role="author", link="http://khaledhosny.org")],
    specLink="#conform-mustTransformMultipleGlyfLoca",
    data=makeCollectionTransform1(),
    flavor="TTF"
)

def makeCollectionOrder1():
    data = getSFNTCollectionData([sfntTTFSourcePath, sfntTTFSourcePath, sfntTTFSourcePath], reverseNames=True)

    return data

writeTest(
    identifier="tabledirectory-order-001",
    title="Valid Font Collection With Unsorted fonts",
    description="TTF flavored SFNT collection with fonts not in alphabetical order. WOFF creation process must reserve the font order.",
    shouldConvert=True,
    credits=[dict(title="Khaled Hosny", role="author", link="http://khaledhosny.org")],
    specLink="#conform-mustPreserveFontOrder",
    data=makeCollectionOrder1(),
    flavor="TTF"
)

writeTest(
    identifier="tabledirectory-collection-index-001",
    title="Valid Font Collection",
    description="TTF flavored SFNT collection. WOFF creation process must record the index of the matching TableDirectoryEntry into the CollectionFontEntry for each font.",
    shouldConvert=True,
    credits=[dict(title="Khaled Hosny", role="author", link="http://khaledhosny.org")],
    specLink="#conform-mustRecordCollectionEntryIndex",
    data=makeCollectionSharing2(),
    flavor="TTF"
)

# ------------------
# Generate the Index
# ------------------

print "Compiling index..."

testGroups = []

for tag, title, url, note in groupDefinitions:
    group = dict(title=title, url=url, testCases=testRegistry[tag], note=note)
    testGroups.append(group)

generateAuthoringToolIndexHTML(directory=authoringToolTestDirectory, testCases=testGroups, note=indexNote)

# ----------------
# Generate the zip
# ----------------

print "Compiling zip file..."

zipPath = os.path.join(authoringToolTestDirectory, "AuthoringToolTestFonts.zip")
if os.path.exists(zipPath):
    os.remove(zipPath)

allBinariesZip = zipfile.ZipFile(zipPath, "w")

pattern = os.path.join(authoringToolTestDirectory, "*.*tf")
for path in glob.glob(pattern):
    ext = os.path.splitext(path)[1]
    assert ext in (".otf", ".ttf")
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

path = os.path.join(authoringToolDirectory, "manifest.txt")
if os.path.exists(path):
    os.remove(path)
f = open(path, "wb")
f.write("\n".join(manifest))
f.close()

# -----------------------
# Check for Unknown Files
# -----------------------

otfPattern = os.path.join(authoringToolTestDirectory, "*.otf")
ttfPattern = os.path.join(authoringToolTestDirectory, "*.ttf")
filesOnDisk = glob.glob(otfPattern) + glob.glob(ttfPattern)

for path in filesOnDisk:
    identifier = os.path.basename(path)
    identifier = identifier.split(".")[0]
    if identifier not in registeredIdentifiers:
        print "Unknown file:", path
