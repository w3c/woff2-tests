"""
WOFF data packers.
"""

import struct
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
