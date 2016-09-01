"""
WOFF data packers.
"""

import struct
from copy import deepcopy
from fontTools.misc import sstruct
from fontTools.misc.arrayTools import calcIntBounds
from utilities import padData, calcHeadCheckSumAdjustment

# ------------------
# struct Description
# ------------------

woffHeaderFormat = """
    > # big endian
    signature:      4s
    flavor:         4s
    length:         L
    numTables:      H
    reserved:       H
    totalSfntSize:  L
    totalCompressedSize: L
    majorVersion:   H
    minorVersion:   H
    metaOffset:     L
    metaLength:     L
    metaOrigLength: L
    privOffset:     L
    privLength:     L
"""
woffHeaderSize = sstruct.calcsize(woffHeaderFormat)

woffTransformedGlyfHeaderFormat = """
    > # big endian
    version:               L
    numGlyphs:             H
    indexFormat:           H
    nContourStreamSize:    L
    nPointsStreamSize:     L
    flagStreamSize:        L
    glyphStreamSize:       L
    compositeStreamSize:   L
    bboxStreamSize:        L
    instructionStreamSize: L
"""

woffTransformedGlyfHeader = dict(
    version=0,
    numGlyphs=0,
    indexFormat=0,
    nContourStreamSize=0,
    nPointsStreamSize=0,
    flagStreamSize=0,
    glyphStreamSize=0,
    compositeStreamSize=0,
    bboxStreamSize=0,
    instructionStreamSize=0,
)

# ------------
# Data Packing
# ------------

knownTableTags = (
    "cmap", "head", "hhea", "hmtx", "maxp", "name", "OS/2", "post", "cvt ",
    "fpgm", "glyf", "loca", "prep", "CFF ", "VORG", "EBDT", "EBLC", "gasp",
    "hdmx", "kern", "LTSH", "PCLT", "VDMX", "vhea", "vmtx", "BASE", "GDEF",
    "GPOS", "GSUB", "EBSC", "JSTF", "MATH", "CBDT", "CBLC", "COLR", "CPAL",
    "SVG ", "sbix", "acnt", "avar", "bdat", "bloc", "bsln", "cvar", "fdsc",
    "feat", "fmtx", "fvar", "gvar", "hsty", "just", "lcar", "mort", "morx",
    "opbd", "prop", "trak", "Zapf", "Silf", "Glat", "Gloc", "Feat", "Sill",
)

unknownTableTagFlag = 63

transformedTables = ("glyf", "loca")

def transformTable(font, tag, glyphBBox="", alt255UInt16=False):
    if tag == "head":
        font["head"].flags |= 1 << 11

    origData = font.getTableData(tag)
    transformedData = origData

    transform = False
    if (tag == "hmtx" and "glyf" in font) or (tag in transformedTables):
        transform = True

    if transform:
        if tag == "glyf":
            transformedData = transformGlyf(font, glyphBBox=glyphBBox, alt255UInt16=alt255UInt16)
        elif tag == "loca":
            transformedData = ""
        elif tag == "hmtx":
            transformedData = transformHmtx(font)
        else:
            assert False, "Unknown transformed table tag: %s" % tag

        #assert len(transformedData) < len(origData), (tag, len(transformedData), len(origData))

    return (origData, transformedData)

def pack255UInt16(n, alternate=0):
    if n < 253:
        ret = struct.pack(">B", n)
    elif n < 506:
        ret = struct.pack(">BB", 255, n - 253)
    elif n < 762:
        if not alternate:
            ret = struct.pack(">BB", 254, n - 506)
        elif alternate == 1 or n > 508:
            ret = struct.pack(">BH", 253, n)
        elif alternate == 2:
            ret = struct.pack(">BB", 255, n - 253)
    else:
        ret = struct.pack(">BH", 253, n)

    return ret

def packTriplet(x, y, onCurve):
    x = int(round(x))
    y = int(round(y))
    absX = abs(x)
    absY = abs(y)
    onCurveBit = 0
    xSignBit = 0
    ySignBit = 0
    if not onCurve:
        onCurveBit = 128
    if x > 0:
        xSignBit = 1
    if y > 0:
        ySignBit = 1
    xySignBits = xSignBit + 2 * ySignBit

    fmt = ">B"
    flags = ""
    glyphs = ""
    if x == 0 and absY < 1280:
        flags += struct.pack(fmt, onCurveBit + ((absY & 0xf00) >> 7) + ySignBit)
        glyphs += struct.pack(fmt, absY & 0xff)
    elif y == 0 and absX < 1280:
        flags += struct.pack(fmt, onCurveBit + 10 + ((absX & 0xf00) >> 7) + xSignBit)
        glyphs += struct.pack(fmt, absX & 0xff)
    elif absX < 65 and absY < 65:
        flags += struct.pack(fmt, onCurveBit + 20 + ((absX - 1) & 0x30) + (((absY - 1) & 0x30) >> 2) + xySignBits)
        glyphs += struct.pack(fmt, (((absX - 1) & 0xf) << 4) | ((absY - 1) & 0xf))
    elif absX < 769 and absY < 769:
        flags += struct.pack(fmt, onCurveBit + 84 + 12 * (((absX - 1) & 0x300) >> 8) + (((absY - 1) & 0x300) >> 6) + xySignBits)
        glyphs += struct.pack(fmt, (absX - 1) & 0xff)
        glyphs += struct.pack(fmt, (absY - 1) & 0xff)
    elif absX < 4096 and absY < 4096:
        flags += struct.pack(fmt, onCurveBit + 120 + xySignBits)
        glyphs += struct.pack(fmt, absX >> 4)
        glyphs += struct.pack(fmt, ((absX & 0xf) << 4) | (absY >> 8))
        glyphs += struct.pack(fmt, absY & 0xff)
    else:
        flags += struct.pack(fmt, onCurveBit + 124 + xySignBits)
        glyphs += struct.pack(fmt, absX >> 8)
        glyphs += struct.pack(fmt, absX & 0xff)
        glyphs += struct.pack(fmt, absY >> 8)
        glyphs += struct.pack(fmt, absY & 0xff)

    return (flags, glyphs)

def transformGlyf(font, glyphBBox="", alt255UInt16=False):
    glyf = font["glyf"]
    head = font["head"]

    nContourStream = ""
    nPointsStream = ""
    flagStream = ""
    glyphStream = ""
    compositeStream = ""
    bboxStream = ""
    instructionStream = ""
    bboxBitmap = []
    bboxBitmapStream = ""

    for i in range(4 * ((len(glyf.keys()) + 31) / 32)):
        bboxBitmap.append(0)

    for glyphName in glyf.glyphOrder:
        glyph = glyf[glyphName]
        glyphId = glyf.getGlyphID(glyphName)

        alternate255UInt16 = 0

        # nContourStream
        nContourStream += struct.pack(">h", glyph.numberOfContours)

        haveInstructions = False

        if glyph.numberOfContours == 0:
            if glyphBBox == "empty":
                bboxBitmap[glyphId >> 3] |= 0x80 >> (glyphId & 7)
                bboxStream += struct.pack(">hhhh", 0, 0, 0, 0)
            continue
        elif glyph.isComposite():
            # compositeStream
            more = True
            for i in range(len(glyph.components)):
                if i == len(glyph.components) - 1:
                    haveInstructions = hasattr(glyph, "program")
                    more = False
                compositeStream += glyph.components[i].compile(more, haveInstructions, glyf)
        else:
            # nPointsStream
            lastPointIndex = 0
            for i in range(glyph.numberOfContours):
                nPoints = glyph.endPtsOfContours[i] - lastPointIndex + (i == 0)
                data = pack255UInt16(nPoints, alternate=alternate255UInt16)
                if nPoints == 506 and alt255UInt16:
                    num = [ord(v) for v in data]
                    if alternate255UInt16 == 0:
                        assert num == [254, 0]
                    elif alternate255UInt16 == 1:
                        assert num == [253, 1, 250]
                    else:
                        assert num == [255, 253]
                    alternate255UInt16 += 1
                nPointsStream += data
                lastPointIndex = glyph.endPtsOfContours[i]

            # flagStream & glyphStream
            lastX = 0
            lastY = 0
            lastPointIndex = 0
            for i in range(glyph.numberOfContours):
                for j in range(lastPointIndex, glyph.endPtsOfContours[i] + 1):
                    x, y = glyph.coordinates[j]
                    onCurve = glyph.flags[j] & 0x01
                    dx = x - lastX
                    dy = y - lastY
                    lastX = x
                    lastY = y
                    flags, data = packTriplet(dx, dy, onCurve)
                    flagStream += flags
                    glyphStream += data
                lastPointIndex = glyph.endPtsOfContours[i] + 1
            haveInstructions = True

        if haveInstructions:
            instructions = glyph.program.getBytecode()
            # instructionLength
            glyphStream += pack255UInt16(len(instructions), alternate=alt255UInt16)

            # instructionStream
            instructionStream += instructions

        writeBBox = False
        if glyph.isComposite():
            writeBBox = glyphBBox != "nocomposite"
        else:
            coords = glyph.getCoordinates(glyf)[0]
            oldBounds = (glyph.xMin, glyph.yMin, glyph.xMax, glyph.yMax)
            newBounds = calcIntBounds(coords)
            writeBBox = oldBounds != newBounds

        if writeBBox:
            # bboxBitmap
            bboxBitmap[glyphId >> 3] |= 0x80 >> (glyphId & 7)

            # bboxStream
            bboxStream += struct.pack(">hhhh", glyph.xMin, glyph.yMin, glyph.xMax, glyph.yMax)

    bboxBitmapStream = "".join([struct.pack(">B", v) for v in bboxBitmap])

    header = deepcopy(woffTransformedGlyfHeader)
    header["numGlyphs"] = len(glyf.keys())
    header["indexFormat"] = head.indexToLocFormat
    header["nContourStreamSize"] = len(nContourStream)
    header["nPointsStreamSize"] = len(nPointsStream)
    header["flagStreamSize"] = len(flagStream)
    header["glyphStreamSize"] = len(glyphStream)
    header["compositeStreamSize"] = len(compositeStream)
    header["bboxStreamSize"] = len(bboxStream) + len(bboxBitmapStream)
    header["instructionStreamSize"] = len(instructionStream)

    data = sstruct.pack(woffTransformedGlyfHeaderFormat, header)
    data += nContourStream + nPointsStream + flagStream
    data += glyphStream + compositeStream
    data += bboxBitmapStream + bboxStream
    data += instructionStream

    return data

def transformHmtx(font):
    glyf = font["glyf"]
    hhea = font["hhea"]
    hmtx = font["hmtx"]
    maxp = font["maxp"]

    origData = font.getTableData("hmtx")

    for name in hmtx.metrics:
        advance, lsb = hmtx.metrics[name]
        xMin = 0
        if hasattr(glyf[name], "xMin"):
            xMin = glyf[name].xMin
        if lsb != xMin:
            return origData

    hasLsb = False
    hasLeftSideBearing = False

    if hhea.numberOfHMetrics != maxp.numGlyphs:
        hasLeftSideBearing = True

    for index, name in enumerate(hmtx.metrics):
        if index >= hhea.numberOfHMetrics:
            break
        advance, lsb = hmtx.metrics[name]
        xMin = 0
        if hasattr(glyf[name], "xMin"):
            xMin = glyf[name].xMin
        if lsb != xMin:
            hasLsb = True
            break

    flags = 0
    if not hasLsb:
        flags |= 1 << 0
    if not hasLeftSideBearing:
        flags |= 1 << 1

    data = struct.pack(">B", flags)
    for index, name in enumerate(hmtx.metrics):
        if index >= hhea.numberOfHMetrics:
            break
        advance, lsb = hmtx.metrics[name]
        data += struct.pack(">H", advance)

    if hasLsb:
        for index, name in enumerate(hmtx.metrics):
            if index >= hhea.numberOfHMetrics:
                break
            advance, lsb = hmtx.metrics[name]
            data += struct.pack(">H", lsb)

    if hasLeftSideBearing:
        for index, name in enumerate(hmtx.metrics):
            if index < hhea.numberOfHMetrics:
                continue
            advance, lsb = hmtx.metrics[name]
            data += struct.pack(">H", lsb)

    assert len(data) < len(origData)
    return data

def base128Size(n):
    size = 1;
    while n >= 128:
        size += 1
        n = n >> 7
    return size

def packBase128(n, bug=False):
    size = base128Size(n)
    ret = ""
    if bug:
        ret += struct.pack(">B", 0x80)
    for i in range(size):
        b = (n >> (7 * (size - i - 1))) & 0x7f
        if i < size - 1:
            b = b | 0x80
        ret += struct.pack(">B", b)
    return ret

def packTestHeader(header):
    return sstruct.pack(woffHeaderFormat, header)

def _setTransformBits(flag, tranasform):
    if tranasform == 1:
        flag |= 1 << 6
    elif tranasform == 2:
        flag |= 1 << 7
    elif tranasform == 3:
        flag |= 1 << 6 | 1 << 7
    return flag

def packTestDirectory(directory, knownTags=knownTableTags, skipTransformLength=False, isCollection=False, unsortGlyfLoca=False, Base128Bug=False):
    data = ""
    directory = [(entry["tag"], entry) for entry in directory]
    if not isCollection:
        directory = sorted(directory)
    if unsortGlyfLoca:
        loca = None
        glyf = None
        for i, entry in enumerate(directory):
            if   entry[0] == "loca": loca = i
            elif entry[0] == "glyf": glyf = i
        assert loca
        assert glyf
        directory.insert(glyf, directory.pop(loca))
    for tag, table in directory:
        transformFlag = table["transformFlag"]
        assert transformFlag <= 3
        if tag in knownTags:
            data += struct.pack(">B", _setTransformBits(knownTableTags.index(tag), transformFlag))
        else:
            data += struct.pack(">B", _setTransformBits(unknownTableTagFlag, transformFlag))
            data += struct.pack(">4s", tag)
        data += packBase128(table["origLength"], bug=Base128Bug)
        transformed = False
        if tag in transformedTables:
            transformed = True
            if transformFlag == 3:
                transformed = False
        else:
            transformed = transformFlag != 0

        if transformed and not skipTransformLength:
            data += packBase128(table["transformLength"], bug=Base128Bug)
    return data

def packTestCollectionHeader(header):
    return struct.pack(">L", header["version"]) + pack255UInt16(header["numFonts"])

def packTestCollectionDirectory(directory):
    data = ""
    for entry in directory:
        data += pack255UInt16(entry["numTables"])
        data += struct.pack(">4s", entry["flavor"])
        for i in entry["index"]:
            data += pack255UInt16(entry["index"][i])
    return data

def packTestMetadata((origMetadata, compMetadata), havePrivateData=False):
    if havePrivateData:
        compMetadata = padData(compMetadata)
    return compMetadata

def packTestPrivateData(privateData):
    return privateData
