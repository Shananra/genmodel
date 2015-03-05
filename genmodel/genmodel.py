#!/usr/bin/env python

import sys,os,inspect,argparse,importlib,traceback,sqlalchemy,re
from sqlalchemy.ext.declarative import declarative_base
from colorama import Fore, Back, Style
try:
    from genmodel.query_strings import column_queries
except:
    from query_strings import column_queries
from urllib.parse import urlparse
sys.path.insert(0,os.getcwd())
parser = argparse.ArgumentParser()
parser.add_argument('--settings','-s',help="python file containing the settings. See the documentation for format and possible values.")
parser.add_argument('--dialect',help="django or sqlalchemy")
args = parser.parse_args()


if args.settings == None:
    args.settings = "gensettings"

try:
    settings = importlib.import_module(args.settings)
except ImportError:
    traceback.print_exc()
    print(Fore.RED+"Error: cannot find settings file!"+Fore.RESET+"\nTry adding the module include path using the --settings parameter, or create a file called gensettings.py",file=sys.stderr)
    exit()

try:
    mytables = settings.TABLES
except:
    print(Fore.RED+"Error: Missing required setting TABLES in settings flie\n"+Fore.RESET,file=sys.stderr)

try:
    myconn = settings.CONNECTION
except ValueError:
    print(Fore.RED+"Error: Missing required setting CONNECTION in settings flie\n"+Fore.RESET,file=sys.stderr)
    exit()
if not hasattr(settings,'dialect') or settings.dialect == None:
    settings.dialect = 'sqlalchemy'

engine = sqlalchemy.create_engine(myconn)
engine.connect()
Base = declarative_base()

comps = urlparse(myconn)
dialect = comps.scheme.split('+')[0]

result = engine.execute(column_queries[dialect])


def un_camel(name):
    s = re.sub('(?!_)(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s).lower()
    

def is_match(items,mystr):
    result = False
    if items.__class__.__name__ != 'list':
        items = [items]
    for item in items:
        if item.__class__.__name__ == 'SRE_Pattern':
            result = result or bool(item.match(mystr))
        elif item.__class__.__name__ == 'str':
            result = result or bool(item == mystr)
        else:
            print(Fore.RED+"Exclude/Include parameters must be a string, compiled regex using re.compile(), or a list of strings and regexes.\nEncountered "+item.__class__.__name__+" instead."+Fore.RESET,file=sys.sttderr)
            exit()
    return result

def run_table(tablename):
    global output
    result = engine.execute(column_queries[dialect] % {'table_name':tablename})
    
    if int('excludes' in mytables[tablename]) != int('includes' in mytables[tablename]) > 1:
        print(Fore.RED+"The table "+tablename+" has both an excludes and includes parameter."+Fore.RESET+"\nOnly one such parameter can be processed on the same table.\n",file=sys.stderr)
        exit()
    base = 'models.Model' if settings.dialect == 'django' else 'base'
    output += "\nclass %(tablename)s(%(base)s):\n" % {'tablename':tablename,'base':base}
    if hasattr(settings,'METHODS'):
        output += settings.METHODS+"\n"
    if 'methods' in mytables[tablename]:
        output += mytables[tablename]['methods']+"\n"
    
    for item in result:
        if 'excludes' in mytables[tablename]:
            if is_match(mytables[tablename]['excludes'],item[0]):
                continue
        elif 'includes' in mytables[tablename]:
            if not is_match(mytables[tablename]['excludes'],item[0]):
                continue
        pkey = ''
        if 'primary_key' in mytables[tablename]:
            if item[0] == mytables[tablename]['primary_key']:
                pkey=', primary_key=True'
        if settings.dialect == 'django':
            output += "    %(fieldname)s = %(fvalue)s\n" % {'fieldname':item[0],'fvalue':{
                'varchar':"models.CharField(max_length=%(length)s,blank=True%(pkey)s)" % {'length':item[2],'pkey':pkey},
                'nvarchar':"models.CharField(max_length=%(length)s,blank=True%(pkey)s)" % {'length':item[2],'pkey':pkey},
                'int':"models.IntegerField(blank=True%(pkey)s)" % {'length':item[2],'pkey':pkey},
                'decimal':"models.DecimalField(max_digits=%(length)s,decimal_places=4,blank=True%(pkey)s)" % {'length':int(item[2]) + 4,'pkey':pkey},
                'money':"models.DecimalField(max_digits=%(length)s,decimal_places=2,blank=True%(pkey)s)" % {'length':int(item[2])+2,'pkey':pkey},
                'bit':'models.BooleanField(blank=True)',
                'smallint':'models.IntegerField(blank=True)',
                'tinyint':'models.IntegerField(blank=True)',
                'datetime':'models.DateTimeField(blank=True)',
                'char':"models.CharField(max_length=%(length)s,blank=True%(pkey)s)" % {'length':item[2],'pkey':pkey},
                'nchar':"models.CharField(max_length=%(length)s,blank=True%(pkey)s)" % {'length':item[2],'pkey':pkey}
            }[item[1]]}
        elif settings.dialect == 'sqlalchemy':
            output += "    %(fieldname)s = %(fvalue)s\n" % {'fieldname':un_camel(item[0]),'fvalue':{
                'varchar':"Column('%(column)s', String(%(length)s), nullable=True%(pkey)s)" % {'column':item[0],'length':item[2],'pkey':pkey},
                'nvarchar':"Column('%(column)s', Unicode(%(length)s), nullable=True%(pkey)s)" % {'column':item[0],'length':item[2],'pkey':pkey},
                'int':"Column('%(column)s', Integer)" % {'column':item[0],'length':item[2],'pkey':pkey},
                'decimal':"Column('%(column)s', DECIMAL, nullable=True%(pkey)s)" % {'column':item[0],'length':int(item[2]) + 4,'pkey':pkey},
                'money':"Column('%(column)s', Numeric, nullable=True%(pkey)s)" % {'column':item[0],'length':int(item[2])+2,'pkey':pkey},
                'bit':"Column('%(column)s', Boolean, nullable=True)" % {'column':item[0]},
                'smallint':"Column('%(column)s', Integer, nullable=True)" % {'column':item[0]},
                'tinyint':"Column('%(column)s', Integer, nullable=True)" % {'column':item[0]},
                'datetime':"Column('%(column)s', DateTime, nullable=True)" % {'column':item[0]},
                'char':"Column('%(column)s', CHAR(length=%(length)s), nullable=True%(pkey)s)" % {'column': item[0],'length':item[2],'pkey':pkey},
                'nchar':"Column('%(column)s', Unicode(length=%(length)s), nullable=True%(pkey)s)" % {'column': item[0],'length':item[2],'pkey':pkey}
            }[item[1]]}
        

def main():
    global output
    
    if settings.dialect == 'django':
        output = "from django.db import models\n"
    elif settings.dialect == 'sqlalchemy':
        output = "from sqlalchemy.types import * \n"
    else:
        print(Fore.RED+"Unknown dialect: "+settings.dialect+Fore.RESET,file=sys.stderr)
    
    try:
        output += settings.FILE_HEADER
    except ValueError:
        pass
    for mytable in mytables:
        run_table(mytable)

    if hasattr(settings,'FILE_FOOTER'):
        output += settings.FILE_FOOTER

    print(output)

if __name__ == '__main__':
    main()

