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
import brotli
from fontTools.misc import sstruct
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib import TTFont, getTableModule
from fontTools.ttLib.sfnt import sfntDirectoryEntrySize
from testCaseGeneratorLib.defaultData import defaultTestData, defaultSFNTTestData
from testCaseGeneratorLib.sfnt import packSFNT, getSFNTData, getSFNTCollectionData, getTTFont
from testCaseGeneratorLib.paths import resourcesDirectory, authoringToolDirectory, authoringToolTestDirectory,\
                                       authoringToolResourcesDirectory, sfntTTFSourcePath, sfntTTFCompositeSourcePath
from testCaseGeneratorLib.html import generateAuthoringToolIndexHTML, expandSpecLinks
from testCaseGeneratorLib.utilities import calcPaddingLength, calcTableChecksum
from testCaseGeneratorLib.sharedCases import makeLSB1

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

tableDataNote = """
These files are valid SFNTs that excercise conversion of the table data.
""".strip()

tableDirectoryNote = """
These files are valid SFNTs that excercise conversion of the table directory.
""".strip()

collectionNote = """
These files are valid SFNTs that excercise conversion of font collections.
""".strip()

groupDefinitions = [
    # identifier, title, spec section, category note
    ("tabledirectory", "SFNT Table Directory Tests", expandSpecLinks("#DataTables"), tableDirectoryNote),
    ("tabledata", "SFNT Table Data Tests", expandSpecLinks("#DataTables"), tableDataNote),
    ("collection", "SFNT Collection Tests", expandSpecLinks("#DataTables"), collectionNote),
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
    elif flavor == "TTF":
        sfntPath += ".ttf"
    elif flavor == "TTC":
        sfntPath += ".ttc"
    elif flavor == "OTC":
        sfntPath += ".otc"
    else:
        assert False, "Unknown flavor: %s" % flavor
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

def makeGlyfBBox1(calcBBoxes=True, composite=False):
    font = getTTFont(sfntTTFSourcePath, recalcBBoxes=calcBBoxes)
    glyf = font["glyf"]
    hmtx = font["hmtx"]
    for name in ("bbox1", "bbox2"):
        pen = TTGlyphPen(None)
        if name == "bbox1":
            pen.moveTo((0, 0))
            pen.lineTo((0, 1000))
            pen.lineTo((1000, 1000))
            pen.lineTo((1000, 0))
            pen.closePath()
        else:
            pen.moveTo((0, 0))
            pen.qCurveTo((500, 750), (600, 500), (500, 250), (0, 0))
            pen.closePath()
        glyph = pen.glyph()
        if not calcBBoxes:
            glyph.recalcBounds(glyf)
            glyph.xMax -= 100
        glyf.glyphs[name] = glyph
        hmtx.metrics[name] = (0, 0)
        glyf.glyphOrder.append(name)

    if composite:
        name = "bbox3"
        pen = TTGlyphPen(glyf.glyphOrder)
        pen.addComponent("bbox1", [1, 0, 0, 1, 0, 0])
        pen.addComponent("bbox2", [1, 0, 0, 1, 1000, 0])
        glyph = pen.glyph()
        glyph.recalcBounds(glyf)
        glyf.glyphs[name] = glyph
        hmtx.metrics[name] = (0, 0)
        glyf.glyphOrder.append(name)

    tableData = getSFNTData(font)[0]
    font.close()
    del font
    header, directory, tableData = defaultSFNTTestData(tableData=tableData, flavor="TTF")
    data = packSFNT(header, directory, tableData, flavor="TTF")
    return data

writeTest(
    identifier="tabledata-transform-glyf-001",
    title="Valid TTF SFNT For Glyph BBox Calculation 1",
    description="TTF flavored SFNT font containing glyphs with the calculated bounding box matches the encoded one, the transformed glyf table in the output WOFF font must have bboxBitmap with all values as 0 and empty bboxStream.",
    shouldConvert=True,
    credits=[dict(title="Khaled Hosny", role="author", link="http://khaledhosny.org")],
    specLink="#conform-mustCalculateOmitBBoxValues",
    data=makeGlyfBBox1(),
    flavor="TTF"
)

writeTest(
    identifier="tabledata-transform-glyf-002",
    title="Valid TTF SFNT For Glyph BBox Calculation 2",
    description="TTF flavored SFNT font containing glyphs with the calculated bounding box differing from the encoded one, the transformed glyf table in the output WOFF font must have bboxBitmap and bboxStream set with the encoded bounding boxes.",
    shouldConvert=True,
    credits=[dict(title="Khaled Hosny", role="author", link="http://khaledhosny.org")],
    specLink="#conform-mustCalculateSetBBoxValues",
    data=makeGlyfBBox1(False),
    flavor="TTF"
)

writeTest(
    identifier="tabledata-transform-glyf-003",
    title="Valid TTF SFNT For Glyph BBox Calculation 3",
    description="TTF flavored SFNT font containing glyphs with the calculated bounding box differing from the encoded one and a composite glyph, the transformed glyf table in the output WOFF font must have bboxBitmap and bboxStream set with the encoded bounding boxes.",
    shouldConvert=True,
    credits=[dict(title="Khaled Hosny", role="author", link="http://khaledhosny.org")],
    specLink="#conform-mustSetCompositeBBoxValues",
    data=makeGlyfBBox1(False, True),
    flavor="TTF"
)

def makeGlyfBBox2(bbox):
    font = getTTFont(sfntTTFSourcePath, recalcBBoxes=False)
    glyf = font["glyf"]
    hmtx = font["hmtx"]

    name = "bbox1"
    glyph = getTableModule('glyf').Glyph()
    glyph.numberOfContours = 0
    glyph.xMin = glyph.xMax = glyph.yMin = glyph.yMax = bbox
    glyph.data = sstruct.pack(getTableModule('glyf').glyphHeaderFormat, glyph)
    glyf.glyphs[name] = glyph
    hmtx.metrics[name] = (0, 0)
    glyf.glyphOrder.append(name)

    tableData = getSFNTData(font)[0]
    font.close()
    del font

    header, directory, tableData = defaultSFNTTestData(tableData=tableData, flavor="TTF")
    data = packSFNT(header, directory, tableData, flavor="TTF")
    return data

writeTest(
    identifier="tabledata-transform-glyf-004",
    title="Invalid TTF SFNT With Empty Glyph BBox 1",
    description="TTF flavored SFNT font containing a glyph with zero contours and non-zero bounding box values.",
    shouldConvert=False,
    credits=[dict(title="Khaled Hosny", role="author", link="http://khaledhosny.org")],
    specLink="#conform-mustRejectNonEmptyBBox",
    data=makeGlyfBBox2(10),
    flavor="TTF"
)

writeTest(
    identifier="tabledata-transform-glyf-005",
    title="Invalid TTF SFNT With Empty Glyph BBox 2",
    description="TTF flavored SFNT font containing a glyph with zero contours and zero bounding box values, the transformed glyf table in the output WOFF font must have bboxBitmap with all values as 0 and empty bboxStream.",
    shouldConvert=True,
    credits=[dict(title="Khaled Hosny", role="author", link="http://khaledhosny.org")],
    specLink="#conform-mustClearEmptyBBox",
    data=makeGlyfBBox2(0),
    flavor="TTF"
)

writeTest(
    identifier="tabledata-transform-hmtx-001",
    title="Valid TTF SFNT For Glyph LSB Elemination 1",
    description="TTF flavored SFNT font containing two proportional and two monospaced glyphs with left side bearings matching the Xmin values of each corresponding glyph bonding box. The hmtx table must be transformed with version 1 transform, eliminating both lsb[] and leftSideBearing[] arrays with corresponding Flags bits set.",
    shouldConvert=True,
    credits=[dict(title="Khaled Hosny", role="author", link="http://khaledhosny.org")],
    specLink="#conform-mustEliminateLSBs #conform-mustCheckLeftSideBearings",
    data=makeLSB1(),
    flavor="TTF"
)

# -----------
# Collections
# -----------

def makeCollectionSharing1():
    data = getSFNTCollectionData([sfntTTFSourcePath, sfntTTFSourcePath], modifyNames=False)

    return data

writeTest(
    identifier="collection-sharing-001",
    title="Valid Font Collection With No Duplicate Tables",
    description="TTF flavored SFNT collection with all tables being shared, output WOFF font must not contain any duplicate tables.",
    shouldConvert=True,
    credits=[dict(title="Khaled Hosny", role="author", link="http://khaledhosny.org")],
    specLink="#conform-mustNotDuplicateTables",
    data=makeCollectionSharing1(),
    flavor="TTC"
)

def makeCollectionSharing2():
    data = getSFNTCollectionData([sfntTTFSourcePath, sfntTTFSourcePath])

    return data

writeTest(
    identifier="collection-sharing-002",
    title="Valid Font Collection With Shared Glyf/Loca",
    description="TTF flavored SFNT collection containing two fonts sharing the same glyf and loca tables.",
    shouldConvert=True,
    credits=[dict(title="Khaled Hosny", role="author", link="http://khaledhosny.org")],
    specLink="#conform-mustVerifyGlyfLocaShared",
    data=makeCollectionSharing2(),
    flavor="TTC"
)

def makeCollectionSharing3():
    data = getSFNTCollectionData([sfntTTFSourcePath, sfntTTFSourcePath, sfntTTFCompositeSourcePath])

    return data

writeTest(
    identifier="collection-sharing-003",
    title="Valid Font Collection With Shared And Unshared Glyf/Loca",
    description="TTF flavored SFNT collection containing three fonts, two of them sharing the same glyf and loca tables and the third using different glyf and loca tables.",
    shouldConvert=True,
    credits=[dict(title="Khaled Hosny", role="author", link="http://khaledhosny.org")],
    specLink="#conform-mustNotDuplicateTables",
    data=makeCollectionSharing3(),
    flavor="TTC"
)

def makeCollectionSharing4():
    data = getSFNTCollectionData([sfntTTFSourcePath, sfntTTFSourcePath], duplicates=["loca"])

    return data

writeTest(
    identifier="collection-sharing-004",
    title="Invalid Font Collection With Unshared Loca",
    description="An invalid TTF flavored SFNT collection containing two fonts sharing glyf but not loca table.",
    shouldConvert=False,
    credits=[dict(title="Khaled Hosny", role="author", link="http://khaledhosny.org")],
    specLink="#conform-mustRejectSingleGlyfLocaShared",
    data=makeCollectionSharing4(),
    flavor="TTC"
)

def makeCollectionSharing5():
    data = getSFNTCollectionData([sfntTTFSourcePath, sfntTTFSourcePath], duplicates=["glyf"])

    return data

writeTest(
    identifier="collection-sharing-005",
    title="Invalid Font Collection With Unshared Glyf",
    description="An invalid TTF flavored SFNT collection containing two fonts sharing loca but not glyf table.",
    shouldConvert=False,
    credits=[dict(title="Khaled Hosny", role="author", link="http://khaledhosny.org")],
    specLink="#conform-mustRejectSingleGlyfLocaShared",
    data=makeCollectionSharing5(),
    flavor="TTC"
)

def makeCollectionSharing6():
    data = getSFNTCollectionData([sfntTTFSourcePath, sfntTTFSourcePath], shared=["cmap"])

    return data

writeTest(
    identifier="collection-sharing-006",
    title="Font Collection With Single Shared Table",
    description="A valid TTF flavored SFNT collection containing two fonts sharing only the cmap table.",
    shouldConvert=True,
    credits=[dict(title="Khaled Hosny", role="author", link="http://khaledhosny.org")],
    specLink="#conform-mustEmitSingleEntryDirectory",
    data=makeCollectionSharing6(),
    flavor="TTC"
)

def makeCollectionTransform1():
    data = getSFNTCollectionData([sfntTTFSourcePath, sfntTTFCompositeSourcePath])

    return data

writeTest(
    identifier="collection-transform-glyf-001",
    title="Valid Font Collection With Multiple Glyf/Loca",
    description="TTF flavored SFNT collection with multiple unshared glyf and loca tables, all of them must be transformed in the output WOFF font.",
    shouldConvert=True,
    credits=[dict(title="Khaled Hosny", role="author", link="http://khaledhosny.org")],
    specLink="#conform-mustTransformMultipleGlyfLoca",
    data=makeCollectionTransform1(),
    flavor="TTC"
)

def makeCollectionHmtxTransform1():
    fonts = [getTTFont(sfntTTFSourcePath), getTTFont(sfntTTFSourcePath)]
    for i, font in enumerate(fonts):
        glyf = font["glyf"]
        hmtx = font["hmtx"]
        maxp = font["maxp"]
        for name in glyf.glyphs:
            glyph = glyf.glyphs[name]
            glyph.expand(glyf)
            if hasattr(glyph, "xMin"):
                # Move the glyph so that xMin is 0
                pen = TTGlyphPen(None)
                glyph.draw(pen, glyf, -glyph.xMin)
                glyph = pen.glyph()
                glyph.recalcBounds(glyf)
                assert glyph.xMin == 0
                glyf.glyphs[name] = glyph
                hmtx.metrics[name] = (glyph.xMax, 0)

        # Build a unique glyph for each font, but with the same advance and LSB
        name = "box"
        pen = TTGlyphPen(None)
        pen.moveTo([0, 0])
        pen.lineTo([0, 1000])
        if i > 0:
            pen.lineTo([0, 2000])
            pen.lineTo([1000, 2000])
        pen.lineTo([1000, 1000])
        pen.lineTo([1000, 0])
        pen.closePath()
        glyph = pen.glyph()
        glyph.recalcBounds(glyf)
        glyf.glyphs[name] = glyph
        hmtx.metrics[name] = (glyph.xMax, glyph.xMin)
        glyf.glyphOrder.append(name)
        maxp.recalc(font)
        data = hmtx.compile(font)
        hmtx.decompile(data, font)

    data = getSFNTCollectionData(fonts, shared=["hmtx"])

    return data

writeTest(
    identifier="collection-transform-hmtx-001",
    title="Valid Font Collection With Unshared Glyf And Shared Hmtx 1",
    description="TTF flavored SFNT collection with multiple unshared glyf tanles and one shared hmtx table where xMin and LSB of all glyphs is 0.",
    shouldConvert=True,
    credits=[dict(title="Khaled Hosny", role="author", link="http://khaledhosny.org")],
    specLink="#conform-mustCheckLSBAllGlyfTables",
    data=makeCollectionHmtxTransform1(),
    flavor="TTC"
)

def makeCollectionHmtxTransform2():
    fonts = [getTTFont(sfntTTFSourcePath), getTTFont(sfntTTFSourcePath)]
    for i, font in enumerate(fonts):
        glyf = font["glyf"]
        hmtx = font["hmtx"]
        maxp = font["maxp"]
        for name in glyf.glyphs:
            glyph = glyf.glyphs[name]
            glyph.expand(glyf)
            if hasattr(glyph, "xMin"):
                metrics = hmtx.metrics[name]
                if i == 0:
                    # Move the glyph so that xMin is 0
                    pen = TTGlyphPen(None)
                    glyph.draw(pen, glyf, -glyph.xMin)
                    glyph = pen.glyph()
                    glyph.recalcBounds(glyf)
                    assert glyph.xMin == 0
                    glyf.glyphs[name] = glyph
                hmtx.metrics[name] = (metrics[0], 0)

        # Build a unique glyph for each font, but with the same advance and LSB
        name = "box"
        pen = TTGlyphPen(None)
        pen.moveTo([0, 0])
        pen.lineTo([0, 1000])
        if i > 0:
            pen.lineTo([0, 2000])
            pen.lineTo([1000, 2000])
        pen.lineTo([1000, 1000])
        pen.lineTo([1000, 0])
        pen.closePath()
        glyph = pen.glyph()
        glyph.recalcBounds(glyf)
        glyf.glyphs[name] = glyph
        hmtx.metrics[name] = (glyph.xMax, glyph.xMin)
        glyf.glyphOrder.append(name)
        maxp.recalc(font)
        data = hmtx.compile(font)
        hmtx.decompile(data, font)

    data = getSFNTCollectionData(fonts, shared=["hmtx"])

    return data

writeTest(
    identifier="collection-transform-hmtx-002",
    title="Valid Font Collection With Unshared Glyf And Shared Hmtx 2",
    description="TTF flavored SFNT collection with multiple unshared glyf tanles and one shared hmtx table where LSB of all glyphs is 0, but xMin in some glyphs in the second glyf table is not 0.",
    shouldConvert=True,
    credits=[dict(title="Khaled Hosny", role="author", link="http://khaledhosny.org")],
    specLink="#conform-mustNotApplyLSBTransformForOTC",
    data=makeCollectionHmtxTransform2(),
    flavor="TTC"
)

writeTest(
    identifier="collection-pairing-001",
    title="Valid Font Collection With Glyf/Loca Pairs",
    description="TTF flavored SFNT collection with multiple unshared glyf and loca tables, glyf and loca tables from each font must be paired in the output WOFF font.",
    shouldConvert=True,
    credits=[dict(title="Khaled Hosny", role="author", link="http://khaledhosny.org")],
    specLink="#conform-mustReorderGlyfLoca",
    data=makeCollectionTransform1(),
    flavor="TTC"
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
    flavor="TTC"
)

writeTest(
    identifier="tabledirectory-collection-index-001",
    title="Valid Font Collection",
    description="TTF flavored SFNT collection. WOFF creation process must record the index of the matching TableDirectoryEntry into the CollectionFontEntry for each font.",
    shouldConvert=True,
    credits=[dict(title="Khaled Hosny", role="author", link="http://khaledhosny.org")],
    specLink="#conform-mustRecordCollectionEntryIndex",
    data=makeCollectionSharing2(),
    flavor="TTC"
)

def makeKnownTables():
    from testCaseGeneratorLib.woff import knownTableTags

    header, directory, tableData = defaultSFNTTestData(flavor="TTF")

    tags = [e["tag"] for e in directory]
    assert set(tags) < set(knownTableTags)

    data = packSFNT(header, directory, tableData, flavor="TTF")
    return data

writeTest(
    identifier="tabledirectory-knowntags-001",
    title="Valid TTF SFNT With All Tables Known",
    description="TTF flavored SFNT font with all tables known. Output WOFF2 table directory must use known table flag for all tables in the font.",
    shouldConvert=True,
    credits=[dict(title="Khaled Hosny", role="author", link="http://khaledhosny.org")],
    specLink="#conform-mustUseKnownTags",
    data=makeKnownTables(),
    flavor="TTF"
)

dummyTables = ("ZZZA", "ZZZB", "ZZZC")

def makeUnknownTables():
    from testCaseGeneratorLib.woff import knownTableTags

    header, directory, tableData = defaultSFNTTestData(flavor="TTF")
    # adjust the header
    header["numTables"] += len(dummyTables)
    # adjust the offsets
    shift = len(dummyTables) * sfntDirectoryEntrySize
    for entry in directory:
        entry["offset"] += shift
    # store the data
    sorter = [(entry["offset"], entry["length"]) for entry in directory]
    offset, length = max(sorter)
    offset = offset + length
    data = "\0" * 4
    checksum = calcTableChecksum(None, data)
    for tag in dummyTables:
        tableData[tag] = data
        entry = dict(
            tag=tag,
            offset=offset,
            length=4,
            checksum=checksum
        )
        directory.append(entry)
        offset += 4

    tags = [e["tag"] for e in directory]
    assert not set(tags) < set(knownTableTags)

    data = packSFNT(header, directory, tableData, flavor="TTF")
    return data

writeTest(
    identifier="tabledirectory-knowntags-002",
    title="Valid TTF SFNT With Some Tables Unknown",
    description="TTF flavored SFNT font with some tables unknown. Output WOFF2 table directory must use known table flag for known tables.",
    shouldConvert=True,
    credits=[dict(title="Khaled Hosny", role="author", link="http://khaledhosny.org")],
    specLink="#conform-mustUseKnownTags",
    data=makeUnknownTables(),
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

pattern = os.path.join(authoringToolTestDirectory, "*.?t?")
for path in glob.glob(pattern):
    ext = os.path.splitext(path)[1]
    assert ext in (".otf", ".ttf", ".otc", ".ttc")
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
otcPattern = os.path.join(authoringToolTestDirectory, "*.otc")
ttcPattern = os.path.join(authoringToolTestDirectory, "*.ttc")
filesOnDisk = glob.glob(otfPattern) + glob.glob(ttfPattern) + glob.glob(otcPattern) + glob.glob(ttcPattern)

for path in filesOnDisk:
    identifier = os.path.basename(path)
    identifier = identifier.split(".")[0]
    if identifier not in registeredIdentifiers:
        print "Unknown file:", path
