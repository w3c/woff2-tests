"""
WOFF data packers.
"""

import struct
from copy import deepcopy
from fontTools.misc import sstruct
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

woffDirectoryEntryFormat = """
    > # big endian
    flags:           B
    tag:             4s
    origLength:      L # XXX
    transformLength: L # XXX
"""
woffDirectoryEntrySize = sstruct.calcsize(woffDirectoryEntryFormat)

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
    bboxBitmap:            B
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
    bboxBitmap=0,
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

transformedTables = ("glyf", "loca")

def transformTable(font, tag):
    origData = font.getTableData(tag)
    transformedData = origData
    if tag in transformedTables:
        if tag == "glyf":
            transformedData = tramsformGlyf(font)
        elif tag == "loca":
            transformedData = ""
        else:
            assert False, "Unknown transformed table tag: %s" % tag

    return (origData, transformedData)

def pack255UInt16(n):
    ret = ""
    if n < 253:
        ret += struct.pack(">B", n)
    elif n < 506:
        ret += struct.pack(">BB", 255, n - 253)
    elif n < 762:
        ret += struct.pack(">BB", 254, n - 506)
    else:
        ret += struct.pack(">H", n)

    return ret

def tramsformGlyf(font):
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

    for glyphName in glyf.keys():
        glyph = glyf[glyphName]
        if glyph.isComposite():
            assert False
        else:
            # nContourStream
            nContourStream += struct.pack(">h", glyph.numberOfContours)

            # nPointsStream
            lastPointIndex = 0
            for i in range(glyph.numberOfContours):
                nPointsStream += pack255UInt16(glyph.endPtsOfContours[i] - lastPointIndex + (i == 0))
                lastPointIndex = glyph.endPtsOfContours[i]

            # flagStream

            # glyphStream

            # instructionStream

    header = deepcopy(woffTransformedGlyfHeader)
    header["numGlyphs"] = len(glyf.keys())
    header["indexFormat"] = head.indexToLocFormat
    header["nContourStreamSize"] = len(nContourStream)
    header["nPointsStreamSize"] = len(nPointsStream)
    header["flagStreamSize"] = len(flagStream)
    header["glyphStreamSize"] = len(glyphStream)
    header["compositeStreamSize"] = len(compositeStream)
    header["bboxStreamSize"] = len(bboxStream)
    header["instructionStreamSize"] = len(instructionStream)

    data = sstruct.pack(woffTransformedGlyfHeaderFormat, header)
    return data

def base128Size(n):
    size = 1;
    while n >= 128:
        size += 1
        n = n >> 7
    return size

def packBase128(n):
    size = base128Size(n)
    ret = ""
    for i in range(size):
        b = (n >> (7 * (size - i - 1))) & 0x7f
        if i < size - 1:
            b = b | 0x80
        ret += struct.pack(">B", b)
    return ret

def packTestHeader(header):
    return sstruct.pack(woffHeaderFormat, header)

def packTestDirectory(directory):
    data = ""
    directory = [(entry["tag"], entry) for entry in directory]
    for tag, table in sorted(directory):
        if tag in knownTableTags:
            data += struct.pack(">B", knownTableTags.index(tag))
        else:
            data += struct.pack(">B", len(knownTableTags))
            data += struct.pack(">4s", tag)
        data += packBase128(table["origLength"])
        if tag in transformedTables:
            data += packBase128(table["transformLength"])
    return data

def packTestTableData(directory, tableData, calcCheckSum=True):
    return padData(tableData)

def packTestMetadata((origMetadata, compMetadata), havePrivateData=False):
    if havePrivateData:
        compMetadata = padData(compMetadata)
    return compMetadata

def packTestPrivateData(privateData):
    return privateData
