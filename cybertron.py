# -*- coding: utf-8 *-*

#   Copyright 2013 Joel Haasnoot
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

import os, sys, codecs, zipfile
import yaml

class TransformerService:
    params = {}

    in_file = None
    out_file = None

    # Dictionary of transformer classes
    transformers = {}
    # Dictionary of transformer params
    transform_params = None
    # Dictionary of files per transformer
    interested_files = {}

    def __init__(self):
        pass

    def run(self, args):
        if len(args) < 4:
            return self.help()

        # Parse params and init transformers
        self.initParams(args[1])
        self.initTransformers()

        # Setup files
        self.in_file = zipfile.ZipFile(args[2], 'r')
        self.out_file = zipfile.ZipFile(args[3], 'w', zipfile.ZIP_DEFLATED)

        # Copy the files we aren't going to be modifying
        self.copyFiles()

        # Do Transformations
        for transformer in self.transformers:
            for filename in self.interested_files[transformer]:
                content = self.readFile(filename)
                # Pre processors
                content = self.transformers[transformer].beforeFile(filename, content)
                # Process line by line
                output = ""
                lines = content.splitlines(False)
                # Process headers
                output += ','.join(self.transformers[transformer].processHeader(filename, lines[0].split(','))) + os.linesep
                
                # Process content lines
                for line in lines[1:]:
                    columns = line.split(',')
                    line = self.transformers[transformer].processLine(filename, columns)
                    output += ','.join(line) + os.linesep
                #Post processors
                output = self.transformers[transformer].afterFile(filename, output)
                self.writeFileToZip(filename, output)
                

        # Close zip files properly
        self.in_file.close()
        self.out_file.close()

    def help(self):
        print "Usage: transform.py <parameter file> <GTFS in> <GTFS out>"

    def initParams(self, filename):
        param_stream = open(filename, 'r')
        params = yaml.load(param_stream)

        # Program definitions
        if 'Base' in params:
            self.params.update(params['Base'])
            del params['Base']

        #Transformer definitions
        self.transform_params = params

    def initTransformers(self):
        for key in self.transform_params.keys():
            try:
                transformer_module = getattr(getattr(__import__("transformers",
                    fromlist=[key.lower()]), key.lower()), key)
                self.transformers[key] = transformer_module(self.transform_params[key])
            except AttributeError:
                print "Error importing %s, make sure file and class match" % key
                return
            self.interested_files[key] = self.transformers[key].getInterestingFiles()

    def copyFiles(self):
        all_files = set([filename[0:-4] for filename in self.in_file.namelist() if filename.endswith('.txt')])
        interesting_files = [filename for key in self.interested_files for filename in self.interested_files[key]]
        for filename in (all_files - set(interesting_files)):
            print filename
            self.copyFileToZip(filename)

    def readFile(self, filename, type='txt'):
        c = self.in_file.open("%s.%s" % (filename, type))
        c = codecs.EncodedFile(c, 'utf-8', 'utf-8').read()
        #c = c.decode('utf-8')
        return c
        
    def writeFileToZip(self, filename, contents, type='txt'):
        self.out_file.writestr("%s.%s" % (filename, type), contents)
        
    def copyFileToZip(self, filename):
        contents = self.readFile(filename)
        self.writeFileToZip(filename, contents)

if  __name__ == '__main__':
    transform = TransformerService()
    transform.run(sys.argv)
