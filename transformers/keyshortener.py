# -*- coding: utf-8 *-*

from base import BaseTransformer


class KeyShortener(BaseTransformer):
    # Store which files contain the "primary keys" and which the related "foreign keys"
    REQUIREMENTS = {'stop_id': {'primary': ['stops'], 'foreign': ['stop_times', 'transfers'] },
                    'service_id': {'primary': ['calendar', 'calendar_dates'], 'foreign': ['trips']},
                    'trip_id': {'primary': ['trips'], 'foreign': ['stop_times', 'frequencies']},
                    'route_id': {'primary': ['routes'], 'foreign': ['trips', 'fare_rules']},
                    'agency_id': {'primary': ['agency'], 'foreign': ['routes']},
                    'shape_id': {'primary': ['shapes'], 'foreign': ['trips']},
                    'fare_id': {'primary': ['fare_attributes'], 'foreign': ['fare_rules'] }
                    }
    
    replacement_keys = [] # Should be equal to replacements.keys(), optimization
    replacements = {}
    replacement_count = {}
    
    expected_order = []
    current_file = None

    def __init__(self, params):
        super(KeyShortener, self).__init__(params)
        for key in self.params['keys']:
            if key in self.REQUIREMENTS:
                self.replacement_count[key] = 1
                self.expected_order.extend(self.__getFileTuplesPerType(key, 'primary') + self.__getFileTuplesPerType(key, 'foreign'))
            else:
                del self.params['keys'][key] # Log an error here
        if 'prefix' not in self.params:
            self.params['prefix'] = ''
        

    def getInterestingFiles(self):
        files = []
        for key in self.params['keys']:
            # We'll need both files, so add them, but make sure in this order
            # as primary must always be before foreign
            files.extend(self.REQUIREMENTS[key]['primary'])
            files.extend(self.REQUIREMENTS[key]['foreign'])
        return files

    def beforeFile(self, filename, fileString):
        print "Got before event for %s" % filename
        if self.current_file is None and self.expected_order[0][0] == filename:
            print "Set current file"
            self.current_file = self.expected_order.pop(0)
        else:
            pass # Log an error here :(    
        return fileString;

    def processLine(self, filename, line):
        if self.current_file is None or self.current_file[0] != filename:
            print "This should NEVER happen :("
            return line
        
        key = self.current_file[1]
        type = self.current_file[2]
        if type == 'primary':
            if line[0] in self.replacement_keys:
                line[0] = self.replacements[line[0]]
            else:
                self.replacement_keys.append(line[0])
                new_id = self.params['prefix'] + str(self.replacement_count[key])
                self.replacements[line[0]] = new_id
                line[0] = new_id
                self.replacement_count[key] += 1
        elif type == 'foreign':
            column_pos = self.lookupHeaderName(filename, key) # Note this won't work if key != name of column
            if column_pos is not None and line[column_pos] in self.replacement_keys:
                line[column_pos] = self.replacements[line[column_pos]]
            else:
                pass # Log as not replaced - this should never happen, unless primary are not all processed before foreign
        return line

    def afterFile(self, filename, fileString):
        if self.current_file is not None:
            self.current_file = None
        else:
            pass # Log an error here :(
        return fileString;

    def __getFileTuplesPerType(self, key, type):
        return [(file, key, type) for file in self.REQUIREMENTS[key][type]]