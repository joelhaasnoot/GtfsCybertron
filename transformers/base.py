# -*- coding: utf-8 *-*


class BaseTransformer(object):
    params = {}
    headers = {}

    def __init__(self, params):
        if params is not None:
            self.params.update(params)

    def getInterestingFiles(self):
        return []

    def beforeFile(self, filename, fileString):
        return fileString

    def processHeader(self, filename, line):
        self.headers[filename] = line
        return line

    def processLine(self, filename, line):
        return line

    def afterFile(self, filename, fileString):
        return fileString
    
    # Utility functions
    def lookupHeaderName(self, filename, name):
        return self.headers[filename].index(name)
    
    def lookupHeaders(self, filename):
        return self.headers[filename]
        
     