"""
Paths to important directories and files.
"""

import os

def dirname(path, depth=1):
    """
    >>> path = "/5/4/3/2/1"
    >>> dirname(path)
    '/5/4/3/2'
    >>> dirname(path, 2)
    '/5/4/3'
    >>> dirname(path, 3)
    '/5/4'
    >>> dirname(path, 4)
    '/5'
    """
    for i in range(depth):
        path = os.path.dirname(path)
    return path

mainDirectory = dirname(__file__)
mainDirectory = dirname(mainDirectory, 2)

# directory for SFNT data, test case templates,
resourcesDirectory = os.path.join(mainDirectory, "generators", "resources")
# paths to specific resources
sfntCFFSourcePath = os.path.join(resourcesDirectory, "SFNT-CFF.otf")
sfntTTFSourcePath = os.path.join(resourcesDirectory, "SFNT-TTF.ttf")
sfntTTFCompositeSourcePath = os.path.join(resourcesDirectory, "SFNT-TTF-Composite.ttf")

# directories for test output
userAgentDirectory = os.path.join(mainDirectory, "UserAgent")
userAgentTestDirectory = os.path.join(userAgentDirectory, "WOFF2")
userAgentTestResourcesDirectory = os.path.join(userAgentTestDirectory, "support")

formatDirectory = os.path.join(mainDirectory, "Format")
formatTestDirectory = os.path.join(formatDirectory, "Tests", "xhtml1")
formatResourcesDirectory = os.path.join(formatTestDirectory, "resources")

authoringToolDirectory = os.path.join(mainDirectory, "AuthoringTool")
authoringToolTestDirectory = os.path.join(authoringToolDirectory, "Tests", "xhtml1")
authoringToolResourcesDirectory = os.path.join(authoringToolTestDirectory, "resources")

decoderDirectory = os.path.join(mainDirectory, "Decoder")
decoderTestDirectory = os.path.join(decoderDirectory, "Tests", "xhtml1")
decoderResourcesDirectory = os.path.join(decoderTestDirectory, "resources")

if __name__ == "__main__":
    import doctest
    doctest.testmod()
