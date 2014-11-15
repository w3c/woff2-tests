"""
WOFF data packers.
"""

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

def packTestHeader(header):
    return sstruct.pack(woffHeaderFormat, header)

def packTestDirectory(directory):
    data = ""
    directory = [(entry["tag"], entry) for entry in directory]
    for tag, table in sorted(directory):
        data += sstruct.pack(woffDirectoryEntryFormat, table)
    return data

def packTestMetadata((origMetadata, compMetadata), havePrivateData=False):
    if havePrivateData:
        compMetadata = padData(compMetadata)
    return compMetadata

def packTestPrivateData(privateData):
    return privateData
