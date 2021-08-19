import urllib.request

opener = urllib.request.build_opener()
opener.addheaders = [("Testing", "True")]
urllib.request.install_opener(opener)
/Users/gaurav.sheni/autonormalize/docs/source/images/set-headers.py