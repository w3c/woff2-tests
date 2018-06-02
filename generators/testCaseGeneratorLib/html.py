"""
Test case HTML generator.
"""

import os
import cgi

from paths import userAgentTestResourcesDirectory

# ------------------------
# Specification URLs
# This is used frequently.
# ------------------------

specificationURL = "http://dev.w3.org/webfonts/WOFF2/spec/"
woff1SpecificationURL = "http://www.w3.org/TR/WOFF/"

# ------------------
# SFNT Display Tests
# ------------------

testPassCharacter = "P"
testFailCharacter = "F"
refPassCharacter = testPassCharacter

testCSS = """
@import url("support/test-fonts.css");
@font-face {
	font-family: "WOFF Test";
	src: url("%s/%s.woff2") format("woff2");
}
body {
	font-size: 20px;
}
pre {
	font-size: 12px;
}
.test {
	font-family: "WOFF Test", "WOFF Test %s Fallback";
	font-size: 200px;
	margin-top: 50px;
}
""".strip()

refCSS = """
@import url("support/test-fonts.css");
body {
	font-size: 20px;
}
pre {
	font-size: 12px;
}
.test {
	font-family: "WOFF Test %s Reference";
	font-size: 200px;
	margin-top: 50px;
}
""".strip()

def escapeAttributeText(text):
    text = cgi.escape(text)
    replacements = {
        "\"" : "&quot;",
    }
    for before, after in replacements.items():
        text = text.replace(before, after)
    return text

def _generateSFNTDisplayTestHTML(
    css, bodyCharacter,
    fileName=None, refFileName=None, flavor=None,
    title=None, specLinks=[], assertion=None,
    credits=[], flags=[],
    metadataIsValid=None,
    metadataToDisplay=None,
    extraSFNTNotes=[],
    extraMetadataNotes=[],
    chapterURL=None
    ):
    assert flavor is not None
    assert title is not None
    assert specLinks
    assert assertion is not None
    html = [
        "<!DOCTYPE html PUBLIC \"-//W3C//DTD XHTML 1.0 Strict//EN\" \"http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd\">",
        "<html xmlns=\"http://www.w3.org/1999/xhtml\">"
    ]
    # head
    html.append("\t<head>")
    ## encoding
    s = "\t\t<meta http-equiv=\"content-type\" content=\"text/html;charset=UTF-8\"/>"
    html.append(s)
    ## title
    s = "\t\t<title>WOFF Test: %s</title>" % cgi.escape(title)
    html.append(s)
    ## author
    for credit in credits:
        role = credit.get("role")
        title = credit.get("title")
        link = credit.get("link")
        date = credit.get("date")
        s = "\t\t<link rel=\"%s\" title=\"%s\" href=\"%s\" />" % (role, title, link)
        if date:
            s += " <!-- %s -->" % date
        html.append(s)
    ## link
    assert chapterURL is not None
    s = "\t\t<link rel=\"help\" href=\"%s\" />" % chapterURL
    html.append(s)
    for link in specLinks:
        s = "\t\t<link rel=\"help\" href=\"%s\" />" % link
        html.append(s)
    ## reviewer
    s = '\t\t<link rel="reviewer" title="Chris Lilley" href="mailto:chris@w3.org" />'
    html.append(s)
    # matching reference
    if refFileName:
        s = '\t\t<link rel="match" href="%s" />' % refFileName
        html.append(s)
    ## flags
    if flags:
        s = "\t\t<meta name=\"flags\" content=\"%s\" />" % " ".join(flags)
        html.append(s)
    ## assertion
    s = "\t\t<meta name=\"assert\" content=\"%s\" />" % escapeAttributeText(assertion)
    html.append(s)
    ## css
    html.append("\t\t<style type=\"text/css\"><![CDATA[")
    s = "\n".join(["\t\t\t" + line for line in css.splitlines()])
    html.append(s)
    html.append("\t\t]]></style>")
    ## close
    html.append("\t</head>")
    # body
    html.append("\t<body>")
    ## note
    if metadataIsValid is None:
        s = "\t\t<p>Test passes if the word PASS appears below.</p>"
    else:
        if not metadataIsValid:
            s = "\t\t<p>If the UA does not display WOFF metadata, the test passes if the word PASS appears below.</p>\n"
            s += "\t\t<p>The Extended Metadata Block is not valid and must not be displayed. If the UA does display it, the test fails.</p>"
        else:
            s = "\t\t<p>Test passes if the word PASS appears below.</p>\n"
            s += "\t\t<p>The Extended Metadata Block is valid and may be displayed to the user upon request.</p>"
    html.append(s)
    # extra notes
    for note in extraSFNTNotes:
        s = "\t\t<p>%s</p>" % cgi.escape(note)
        html.append(s)
    for note in extraMetadataNotes:
        s = "\t\t<p>%s</p>" % cgi.escape(note)
        html.append(s)
    ## test case
    s = "\t\t<div class=\"test\">%s</div>" % bodyCharacter
    html.append(s)
    ## show metadata
    if metadataToDisplay:
        s = "\t\t<p>The XML contained in the Extended Metadata Block is below.</p>"
        html.append(s)
        html.append("\t\t<pre>")
        html.append(cgi.escape(metadataToDisplay))
        html.append("\t\t</pre>")
    ## close
    html.append("\t</body>")
    # close
    html.append("</html>")
    # finalize
    html = "\n".join(html)
    return html

def generateSFNTDisplayTestHTML(
    fileName=None, directory=None, flavor=None, title=None,
    sfntDisplaySpecLink=None, metadataDisplaySpecLink=None, assertion=None,
    credits=[], flags=[],
    shouldDisplay=None, metadataIsValid=None, metadataToDisplay=None,
    extraSFNTNotes=[], extraMetadataNotes=[],
    chapterURL=None
    ):
    bodyCharacter = testFailCharacter
    if shouldDisplay:
        bodyCharacter = testPassCharacter
    dirName = os.path.basename(userAgentTestResourcesDirectory)
    css = testCSS % (dirName, fileName, flavor)
    specLinks = []
    if sfntDisplaySpecLink:
        specLinks += sfntDisplaySpecLink
    if metadataDisplaySpecLink:
        specLinks.append(metadataDisplaySpecLink)
    html = _generateSFNTDisplayTestHTML(
        css, bodyCharacter,
        fileName=fileName,
        refFileName='%s-ref.xht' % fileName,
        flavor=flavor,
        title=title,
        specLinks=specLinks,
        assertion=assertion,
        credits=credits, flags=flags,
        metadataIsValid=metadataIsValid,
        metadataToDisplay=metadataToDisplay,
        extraSFNTNotes=extraSFNTNotes,
        extraMetadataNotes=extraMetadataNotes,
        chapterURL=chapterURL
    )
    # write the file
    path = os.path.join(directory, fileName) + ".xht"
    f = open(path, "wb")
    f.write(html)
    f.close()

def generateSFNTDisplayRefHTML(
        fileName=None, directory=None, flavor=None, title=None,
        sfntDisplaySpecLink=None, metadataDisplaySpecLink=None,
        assertion=None, credits=[], flags=[],
        shouldDisplay=None, metadataIsValid=None, metadataToDisplay=None,
        extraSFNTNotes=[], extraMetadataNotes=[],
        chapterURL=None
    ):
    bodyCharacter = refPassCharacter
    css = refCSS % flavor
    specLinks = []
    if sfntDisplaySpecLink:
        specLinks += sfntDisplaySpecLink
    if metadataDisplaySpecLink:
        specLinks.append(metadataDisplaySpecLink)
    html = _generateSFNTDisplayTestHTML(
        css, bodyCharacter,
        fileName=fileName, flavor=flavor,
        title=title,
        specLinks=specLinks,
        assertion=assertion,
        credits=credits, flags=flags,
        metadataIsValid=metadataIsValid,
        metadataToDisplay=metadataToDisplay,
        extraSFNTNotes=extraSFNTNotes,
        extraMetadataNotes=extraMetadataNotes,
        chapterURL=chapterURL
    )
    # write the file
    path = os.path.join(directory, fileName) + "-ref.xht"
    f = open(path, "wb")
    f.write(html)
    f.close()

def poorManMath(text):
    import re
    return re.sub(r"\^\{(.*.)\}", r"<sup>\1</sup>", text)

def generateSFNTDisplayIndexHTML(directory=None, testCases=[]):
    testCount = sum([len(group["testCases"]) for group in testCases])
    html = [
        "<!DOCTYPE html PUBLIC \"-//W3C//DTD XHTML 1.1//EN\" \"http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd\">",
        "<html xmlns=\"http://www.w3.org/1999/xhtml\">",
        "\t<head>",
        "\t\t<title>WOFF 2.0: User Agent Test Suite</title>",
        "\t\t<style type=\"text/css\">",
        "\t\t\t@import \"%s/index.css\";" % os.path.basename(userAgentTestResourcesDirectory),
        "\t\t</style>",
        "\t</head>",
        "\t<body>",
        "\t\t<h1>WOFF 2.0: User Agent Test Suite (%d tests)</h1>" % testCount
    ]
    # add the test groups
    for group in testCases:
        title = group["title"]
        title = cgi.escape(title)
        # write the group header
        html.append("")
        html.append("\t\t<h2 class=\"testCategory\">%s</h2>" % title)
        # write the individual test cases
        for test in group["testCases"]:
            identifier = test["identifier"]
            title = test["title"]
            title = cgi.escape(title)
            title = poorManMath(title)
            assertion = test["assertion"]
            assertion = cgi.escape(assertion)
            assertion = poorManMath(assertion)
            sfntExpectation = test["sfntExpectation"]
            if sfntExpectation:
                sfntExpectation = "Display"
            else:
                sfntExpectation = "Reject"
            sfntURL = test["sfntURL"]
            metadataExpectation = test["metadataExpectation"]
            if metadataExpectation is None:
                metadataExpectation = "None"
            elif metadataExpectation:
                metadataExpectation = "Display"
            else:
                metadataExpectation = "Reject"
            metadataURL = test["metadataURL"]
            # start the test case div
            html.append("\t\t<div class=\"testCase\" id=\"%s\">" % identifier)
            # start the overview div
            html.append("\t\t\t<div class=\"testCaseOverview\">")
            # title
            html.append("\t\t\t\t<h3><a href=\"#%s\">%s</a>: %s</h3>" % (identifier, identifier, title))
            # assertion
            html.append("\t\t\t\t<p>%s</p>" % assertion)
            # close the overview div
            html.append("\t\t\t</div>")
            # start the details div
            html.append("\t\t\t<div class=\"testCaseDetails\">")
            # start the pages div
            html.append("\t\t\t\t<div class=\"testCasePages\">")
            # test page
            html.append("\t\t\t\t\t<p><a href=\"%s.xht\">Test</a></p>" % identifier)
            # reference page
            if test["hasReferenceRendering"]:
                html.append("\t\t\t\t\t<p><a href=\"%s-ref.xht\">Reference Rendering</a></p>" % identifier)
            # close the pages div
            html.append("\t\t\t\t</div>")
            # start the expectations div
            html.append("\t\t\t\t<div class=\"testCaseExpectations\">")
            # sfnt expectation
            string = "SFNT Expectation: %s" % sfntExpectation
            if sfntURL:
                links = []
                for url in sfntURL:
                    if "#" in url:
                        url = "<a href=\"%s\">%s</a>" % (url, url.split("#")[-1])
                        links.append(url)
                    else:
                        url = "<a href=\"%s\">documentation</a>" % url
                        links.append(url)
                string += " (%s)" % " ".join(links)
            html.append("\t\t\t\t\t<p>%s</p>" % string)
            # metadata expectation
            string = "Metadata Expectation: %s" % metadataExpectation
            if metadataURL:
                if "#" in metadataURL:
                    s = "(%s)" % metadataURL.split("#")[-1]
                else:
                    s = "(documentation)"
                string += " <a href=\"%s\">%s</a>" % (metadataURL, s)
            html.append("\t\t\t\t\t<p>%s</p>" % string)
            # close the expectations div
            html.append("\t\t\t\t</div>")
            # close the details div
            html.append("\t\t\t</div>")
            # close the test case div
            html.append("\t\t</div>")

    # close body
    html.append("\t</body>")
    # close html
    html.append("</html>")
    # finalize
    html = "\n".join(html)
    # write
    path = os.path.join(directory, "testcaseindex.xht")
    f = open(path, "wb")
    f.write(html)
    f.close()

def generateFormatIndexHTML(directory=None, testCases=[]):
    testCount = sum([len(group["testCases"]) for group in testCases])
    html = [
        "<!DOCTYPE html PUBLIC \"-//W3C//DTD XHTML 1.1//EN\" \"http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd\">",
        "<html xmlns=\"http://www.w3.org/1999/xhtml\">",
        "\t<head>",
        "\t\t<title>WOFF 2.0: Format Test Suite</title>",
        "\t\t<style type=\"text/css\">",
        "\t\t\t@import \"resources/index.css\";",
        "\t\t</style>",
        "\t</head>",
        "\t<body>",
        "\t\t<h1>WOFF 2.0: Format Test Suite (%d tests)</h1>" % testCount,
    ]
    # add a download note
    html.append("\t\t<div class=\"mainNote\">")
    html.append("\t\t\tThe files used in these test can be obtained individually <a href=\"../xhtml1\">here</a> or as a single zip file <a href=\"FormatTestFonts.zip\">here</a>.")
    html.append("\t\t</div>")
    # add the test groups
    for group in testCases:
        title = group["title"]
        title = cgi.escape(title)
        # write the group header
        html.append("")
        html.append("\t\t<h2 class=\"testCategory\">%s</h2>" % title)
        # write the individual test cases
        for test in group["testCases"]:
            identifier = test["identifier"]
            title = test["title"]
            title = cgi.escape(title)
            description = test["description"]
            description = cgi.escape(description)
            valid = test["valid"]
            if valid:
                valid = "Yes"
            else:
                valid = "No"
            specLink = test["specLink"]
            # start the test case div
            html.append("\t\t<div class=\"testCase\" id=\"%s\">" % identifier)
            # start the overview div
            html.append("\t\t\t<div class=\"testCaseOverview\">")
            # title
            html.append("\t\t\t\t<h3><a href=\"#%s\">%s</a>: %s</h3>" % (identifier, identifier, title))
            # assertion
            html.append("\t\t\t\t<p>%s</p>" % description)
            # close the overview div
            html.append("\t\t\t</div>")
            # start the details div
            html.append("\t\t\t<div class=\"testCaseDetails\">")
            # validity
            string = "Valid: <span id=\"%s-validity\">%s</span>" % (identifier, valid)
            html.append("\t\t\t\t\t<p>%s</p>" % string)
            # documentation
            if specLink is not None:
                links = specLink.split(' ')

                html.append("\t\t\t\t\t<p>")
                for link in links:
                    name = 'Documentation'
                    if '#' in link:
                        name = link.split('#')[1]
                    string = "\t\t\t\t\t\t<a href=\"%s\">%s</a> " % (link, name)
                    html.append(string)
                html.append("\t\t\t\t\t</p>")

            # close the details div
            html.append("\t\t\t</div>")
            # close the test case div
            html.append("\t\t</div>")
    # close body
    html.append("\t</body>")
    # close html
    html.append("</html>")
    # finalize
    html = "\n".join(html)
    # write
    path = os.path.join(directory, "testcaseindex.xht")
    f = open(path, "wb")
    f.write(html)
    f.close()

def generateAuthoringToolIndexHTML(directory=None, testCases=[], note=None):
    testCount = sum([len(group["testCases"]) for group in testCases])
    html = [
        "<!DOCTYPE html PUBLIC \"-//W3C//DTD XHTML 1.1//EN\" \"http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd\">",
        "<html xmlns=\"http://www.w3.org/1999/xhtml\">",
        "\t<head>",
        "\t\t<title>WOFF 2.0: Authoring Tool Test Suite</title>",
        "\t\t<style type=\"text/css\">",
        "\t\t\t@import \"resources/index.css\";",
        "\t\t</style>",
        "\t</head>",
        "\t<body>",
        "\t\t<h1>WOFF 2.0: Authoring Tool Test Suite (%d tests)</h1>" % testCount,
    ]
    # add a download note
    html.append("\t\t<div class=\"mainNote\">")
    html.append("\t\t\tThe files used in these test can be obtained individually <a href=\"../xhtml1\">here</a> or as a single zip file <a href=\"AuthoringToolTestFonts.zip\">here</a>.")
    html.append("\t\t</div>")
    # add the note
    if note:
        html.append("\t\t<div class=\"mainNote\">")
        for line in note.splitlines():
            html.append("\t\t\t" + line)
        html.append("\t\t</div>")
    # add the test groups
    for group in testCases:
        title = group["title"]
        title = cgi.escape(title)
        # write the group header
        html.append("")
        html.append("\t\t<h2 class=\"testCategory\">%s</h2>" % title)
        # write the group note
        note = group["note"]
        if note:
            html.append("\t\t<div class=\"testCategoryNote\">")
            for line in note.splitlines():
                html.append("\t\t\t" + line)
            html.append("\t\t</div>")
        # write the individual test cases
        for test in group["testCases"]:
            identifier = test["identifier"]
            title = test["title"]
            title = cgi.escape(title)
            description = test["description"]
            description = cgi.escape(description)
            shouldConvert = test["shouldConvert"]
            if shouldConvert:
                shouldConvert = "Yes"
            else:
                shouldConvert = "No"
            specLink = test["specLink"]
            # start the test case div
            html.append("\t\t<div class=\"testCase\" id=\"%s\">" % identifier)
            # start the overview div
            html.append("\t\t\t<div class=\"testCaseOverview\">")
            # title
            html.append("\t\t\t\t<h3><a href=\"#%s\">%s</a>: %s</h3>" % (identifier, identifier, title))
            # assertion
            html.append("\t\t\t\t<p>%s</p>" % description)
            # close the overview div
            html.append("\t\t\t</div>")
            # start the details div
            html.append("\t\t\t<div class=\"testCaseDetails\">")
            # validity
            string = "Should Convert to WOFF: <span id=\"%s-shouldconvert\">%s</span>" % (identifier, shouldConvert)
            html.append("\t\t\t\t\t<p>%s</p>" % string)
            # documentation
            if specLink is not None:
                links = specLink.split(' ')

                html.append("\t\t\t\t\t<p>")
                for link in links:
                    name = 'Documentation'
                    if '#' in link:
                        name = link.split('#')[1]
                    string = "\t\t\t\t\t\t<a href=\"%s\">%s</a> " % (link, name)
                    html.append(string)
                html.append("\t\t\t\t\t</p>")

            # close the details div
            html.append("\t\t\t</div>")
            # close the test case div
            html.append("\t\t</div>")
    # close body
    html.append("\t</body>")
    # close html
    html.append("</html>")
    # finalize
    html = "\n".join(html)
    # write
    path = os.path.join(directory, "testcaseindex.xht")
    f = open(path, "wb")
    f.write(html)
    f.close()

def generateDecoderIndexHTML(directory=None, testCases=[], note=None):
    testCount = sum([len(group["testCases"]) for group in testCases])
    html = [
        "<!DOCTYPE html PUBLIC \"-//W3C//DTD XHTML 1.1//EN\" \"http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd\">",
        "<html xmlns=\"http://www.w3.org/1999/xhtml\">",
        "\t<head>",
        "\t\t<title>WOFF 2.0: Decoder Test Suite</title>",
        "\t\t<style type=\"text/css\">",
        "\t\t\t@import \"resources/index.css\";",
        "\t\t</style>",
        "\t</head>",
        "\t<body>",
        "\t\t<h1>WOFF 2.0: Decoder Test Suite (%d tests)</h1>" % testCount,
    ]
    # add a download note
    html.append("\t\t<div class=\"mainNote\">")
    html.append("\t\t\tThe files used in these test can be obtained individually <a href=\"../xhtml1\">here</a> or as a single zip file <a href=\"AuthoringToolTestFonts.zip\">here</a>.")
    html.append("\t\t</div>")
    # add the note
    if note:
        html.append("\t\t<div class=\"mainNote\">")
        for line in note.splitlines():
            html.append("\t\t\t" + line)
        html.append("\t\t</div>")
    # add the test groups
    for group in testCases:
        title = group["title"]
        title = cgi.escape(title)
        # write the group header
        html.append("")
        html.append("\t\t<h2 class=\"testCategory\">%s</h2>" % title)
        # write the group note
        note = group["note"]
        if note:
            html.append("\t\t<div class=\"testCategoryNote\">")
            for line in note.splitlines():
                html.append("\t\t\t" + line)
            html.append("\t\t</div>")
        # write the individual test cases
        for test in group["testCases"]:
            identifier = test["identifier"]
            title = test["title"]
            title = cgi.escape(title)
            description = test["description"]
            description = cgi.escape(description)
            roundTrip = test["roundTrip"]
            if roundTrip:
                roundTrip = "Yes"
            else:
                roundTrip = "No"
            specLink = test["specLink"]
            # start the test case div
            html.append("\t\t<div class=\"testCase\" id=\"%s\">" % identifier)
            # start the overview div
            html.append("\t\t\t<div class=\"testCaseOverview\">")
            # title
            html.append("\t\t\t\t<h3><a href=\"#%s\">%s</a>: %s</h3>" % (identifier, identifier, title))
            # assertion
            html.append("\t\t\t\t<p>%s</p>" % description)
            # close the overview div
            html.append("\t\t\t</div>")
            # start the details div
            html.append("\t\t\t<div class=\"testCaseDetails\">")
            # validity
            string = "Round-Trip Test: <span id=\"%s-shouldconvert\">%s</span>" % (identifier, roundTrip)
            html.append("\t\t\t\t\t<p>%s</p>" % string)
            # documentation
            if specLink is not None:
                links = specLink.split(' ')

                html.append("\t\t\t\t\t<p>")
                for link in links:
                    name = 'Documentation'
                    if '#' in link:
                        name = link.split('#')[1]
                    string = "\t\t\t\t\t\t<a href=\"%s\">%s</a> " % (link, name)
                    html.append(string)
                html.append("\t\t\t\t\t</p>")

            # close the details div
            html.append("\t\t\t</div>")
            # close the test case div
            html.append("\t\t</div>")
    # close body
    html.append("\t</body>")
    # close html
    html.append("</html>")
    # finalize
    html = "\n".join(html)
    # write
    path = os.path.join(directory, "testcaseindex.xht")
    f = open(path, "wb")
    f.write(html)
    f.close()



def expandSpecLinks(links):
    """
    This function expands anchor-only references to fully qualified spec links.
    #name expands to <woff2specurl>#name. woff1:#name expands to
    <woff1specurl>#name.

    links: 0..N space-separated #anchor references
    """
    if links is None or len(links) == 0:
        links = ""

    specLinks = []
    for link in links.split(" "):
        if link.startswith("woff1:"):
            link = woff1SpecificationURL + link[6:]
        else:
            link = specificationURL + link

        specLinks.append(link)

    return " ".join(specLinks)
