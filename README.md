genmodel automatically generates django models by using their descriptions in a settings file. If you have a frequently changing schema, or a very large schema that would be tedious to update manually, you can simply use genmodel to do the heavy lifting. The output will be a complete python file that can be saved and run out of the box. However, if you use this to manage a frequently changing schema I recommend checking the output.

Usage:

::
    
    genmodel --settings=modelsettings > path/to/models.py

All output is sent to stdout, and errors or warnings are sent to stderr. However, if an error occurs there will be no output.

The settings file is imported as a module relative to the current working directory (or in your sys path), so in the above example your settings file should be modelsettings.py. To import a file in models/manifest.py you would use `genmodel --settings=models.manifest.py` 

If no settings file is specified, genmodel will look in your current working for gensettings.py (django settings files are often called settings.py, so this name was chosen to avoid conflicts)

Example settings file:

::
    
    # Only necessary if you want to use regex filters:
    import re
    
    # this must be a url-style connection string. genmodel will use this to read the tables and get the column names/types
    CONNECTION = 'mysql+mysqldb://scott:tiger@localhost/foo'
    
    # Need code at the top of your models.py file? Put that in this string. This way you can just replace the entire file.
    FILE_HEADER = "#additional headers, imports, etc"

    # And the footer:
    FILE_FOOTER = "# Footer of the file"
    
    # If you have any methods that should be included in ALL models, define them as follows:
    METHODS = '''
        def __str__(self):
            return "String representation of my model"
    '''
    #Your indenting will be preserved, so make sure it's indented correctly for the output file.

    # Now define the tables you want. Each table should be a key on the dictionary, with another object as the value, but each parameter on the model is optional
    TABLES = {
        'mytable_name': {
            'primary_key':'id', #this should be the name of your primary key. It must match exactly.
            'excludes':[re.compile(r'^excludeme'),'excluded_field'], # see below
            'methods':'''
        def Meta:
            db_table = 'mytable_name'
            '''
        }
    }

Include and exclude directives accept a list of compiled regex objects and strings. Your table definition may have an excludes or includes directive (but not both). If you have an includes directive then at least one item on the list must match any given column for it to be included in the model, while excludes are the opposite where none can match. When you use a string then it's looking for an exact match.
