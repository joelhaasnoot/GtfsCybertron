# GtfsCybertron #
## Home of all great GTFS Transformers ##

**License:** Apache

**Requirements:** Python, PyYaml

This framework aims to make it easy to transform the bad GTFS files that are out there to something you can use in your application.
Currently has support for input of a single GTFS file and outputing its changed version after processing.
A Yaml file is used to configure which transformers need to be run, and their configuration.  

Currently there's one actual working transformer:

- **KeyShortener**: Makes insanely long ids much smaller and starts numbering from zero. I use this to make my database much much smaller

But some ideas of new 'transformers' are:

- **CaseInsensitive**: Make ids case insensitive so they're easier to use in databases
- **KeySimplifier**: Not all keys need to be shorter, sometimes you want to keep the old ids but remove all the symbol cruft (removes |, _, *, and spaces, etc)
- **Validator**: Validate the files according to the GTFS spec
- **FieldAdder**: Add a custom field to all files in the feed



