#!/usr/bin/python
#
# c 
# ODBShorten API
# ===================================================
# "Because the Internet is the new memory of Humanity,
# It can not be lost by stupidity."
# Learn more about ODBShorten project: http://wiki.hoa.ro/doku.php?id=projects:obdshorten
#
# ODBShorten API desc
#
# Author: Arthur Hoaro <arthur@hoa.ro> <website>
# Version: 0.1.0-dev
# Licence: GNU Lesser General Public License <http://www.gnu.org/licenses/lgpl-3.0.txt>
# Code: URL
# Documentation: http://wiki.hoa.ro/doku.php?id=projects:obdshorten:api
# 
# ODBShorten client and ODBShorten API are currently
# in development mode and should not be used in another way
#

import bottle # Web server
from bottle import error
from bottle import response
import psycopg2
import psycopg2.extras  
from bottle import run, route, request
import json
import base64
import datetime
import sys
#from errors import *

dthandler = lambda obj: obj.isoformat() if isinstance(obj, datetime.datetime) else None
ERROR_KEY = ''
MESSAGE_KEY = ''
ERRORS = dict()
CONNECTION_STRING = ''

class DBFactory:
    """Singleton DB Factory"""

    db_instance = None

    def get_instance(cls):
        if cls.db_instance is None:
            cls.db_instance = psycopg2.connect(cls.connection_string())
        return cls.db_instance
    get_instance = classmethod( get_instance )

    def getConnectionString(cls):
        return CONNECTION_STRING
    connection_string = classmethod( getConnectionString )

##
# API HOME
##
@route('/')
def index():
    """ Display welcome & instruction messages """
    return "<p>Welcome to my extra simple bottle.py powered server !</p> \
           <p>There are two ways to invoke the web service :\
       <ul><li>http://localhost:8080/up?s=type_your_string_here</li>\
       <li>http://localhost:8080/up?URL=http://url_to_file.txt</li></ul>"

@error(404)
def error404(error):
    response.content_type = 'application/json'
    return json.dumps({ERROR_KEY: 404, MESSAGE_KEY: 'URL not found'})
  
##
# SHORTENER
##
@route('/shortener/get')
def getShortener(name = None, id = None):
    """
    Returns a shortener by its name
    @param id (optional): shortener's id (having priority)
    OR
    @param name (optional): shortener name (e.g. bitly)
    """
    if name is None:
        name = request.GET.get('name', default=None)
    if id is None:
        id = request.GET.get('id', default=None)
    
    if name is None and id is None:
        return {
            ERROR_KEY: ERRORS['INVALID_PARAMETERS'], 
            MESSAGE_KEY: 'Invalid parameters',
            'route': '/shortener/get',
            'params': {
                'id': 'get shortener by ID (having priority)',
                'name': 'get shortener by name'
            }
        }

    db = DBFactory.get_instance()
    cur = db.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
    sql = "SELECT * "
    sql += "FROM shortener "
    if id is not None:
        sql += "WHERE id_shortener = %s;"
        data = (id, )
    else:
        sql += "WHERE name=%s;"
        data = (name,)

    try:
        cur.execute(sql, data)
        result = cur.fetchone()

        if len(result) > 0:
            return json.dumps(result, default=dthandler)
        else:
            return {
                ERROR_KEY: ERRORS['SHORTENER_NOT_FOUND'], 
                MESSAGE_KEY: 'Shortener not found',
            }
    except Exception, e:
        return {
            ERROR_KEY: ERRORS['UNEXPECTED'], 
            MESSAGE_KEY: str(e),
        }

##
# LINK
##
@route('/link/add')
def addLink(shortener = None, varPart = None, real = None):
    """
    Add a new link in DB, returns ID of added link
    @param shortener: shortener id or shortener name
    @param var_part: variable part of shortened link
    @param real: the real link (should be encode by the client)
    """
    
    if shortener is None:
        shortener = request.GET.get('shortener', default=None)
    if varPart is None:
        varPart = request.GET.get('var_part', default=None)
    if real is None:
        real = request.GET.get('real', default=None)

    if shortener is None or varPart is None or real is None:
        return { 
            ERROR_KEY: ERRORS['INVALID_PARAMETERS'],
            MESSAGE_KEY: 'Invalid parameters',
            'route': '/link/add',
            'params': {
                'shortener': 'shortener id or shortener name',
                'varPart': 'variable part of shortened link',
                'real': 'the real link (should be encode by the client)'
            }
        }

    try:
        id_shortener = int(shortener)
    except ValueError:
        sdata = getShortener(None, shortener)
        if 'id_shortener' in sdata:
            id_shortener = sdata['id_shortener']
        else:
            return sdata

    db = DBFactory.get_instance()
    cur = db.cursor(cursor_factory = psycopg2.extras.RealDictCursor)

    sql = 'INSERT INTO link '
    sql += '(shortener, var_part, real, dateadd, last_edit) '
    sql += 'VALUES (%s, %s, %s, now(), now()) '        
    sql += 'RETURNING id_link;'
    data = (id_shortener, varPart, real)

    try: 
        cur.execute(sql, data)
        db.commit()
        rid = cur.fetchone()['id_link']
        if rid is not None :
            return { 'id_link': rid }
        else:
            return { ERROR_KEY: ERRORS['LINK_ADD_FAIL'], MESSAGE_KEY: 'Link add failed'}
        
    except psycopg2.IntegrityError: 
        db.rollback()
        data = json.loads(getLinkByVar(id_shortener, varPart))
        if ERROR_KEY not in data:
            return json.dumps(
                { 
                    ERROR_KEY: ERRORS['LINK_DUPLICATE'], 
                    MESSAGE_KEY: 'Link already exists', 
                    'id_link': data['id_link'], 
                    'shortener': data['shortener'],
                    'var_part': data['var_part'],
                    'real': data['real'],
                    'dateadd': data['dateadd'],
                    'last_edit': data['last_edit'],
                }, default=dthandler)
        else: 
            return json.dumps(data, default=dthandler)
    except Exception, e:
        return { ERROR_KEY: ERRORS['UNEXPECTED'], MESSAGE_KEY: str(e) }

@route('/link/get/last')
def getLinkByVar(id_shortener = None):
    """
    Returns the last link of a shortener (sort by var_part)
    @param shortener: shortener's id
    """

    if id_shortener is None:
        id_shortener = request.GET.get('shortener', default=None)

    if id_shortener is None:
        return { ERROR_KEY: ERRORS['INVALID_PARAMETERS'], MESSAGE_KEY: 'Invalid parameters',
            'route': '/link/get/last',
            'params': {
                'shortener': 'shortener\'s id',
        } }


    db = DBFactory.get_instance()
    cur = db.cursor(cursor_factory = psycopg2.extras.RealDictCursor)

    sql = 'SELECT * '
    sql += 'FROM link '    
    sql += 'WHERE id_link = ( '
    sql += ' SELECT MAX(id_link) FROM link '
    sql += 'WHERE shortener = %s )'
    data = (id_shortener, )  

    try: 
        cur.execute(sql, data)
        result = cur.fetchone()
        if result is not None:            
            return json.dumps(result, default=dthandler)
        else:
            return { ERROR_KEY: ERRORS['LINK_NOT_FOUND'], MESSAGE_KEY: 'Link not found',}
    except Exception, e: 
        return { ERROR_KEY: ERRORS['UNEXPECTED'], MESSAGE_KEY: str(e) }

@route('/link/get/byvar')
def getLinkByVar(id_shortener = None, varPart = None):
    """
    Returns a link by its shortener and varpart
    @param shortener: shortener's id or name
    @param var_part: variable part of shortened link
    """

    if id_shortener is None:
        id_shortener = request.GET.get('shortener', default=None)
    if varPart is None:
        varPart = request.GET.get('var_part', default=None)

    if id_shortener is None or varPart is None:
        return { ERROR_KEY: ERRORS['INVALID_PARAMETERS'], MESSAGE_KEY: 'Invalid parameters',
            'route': '/link/get/byvar',
            'params': {
                'shortener': 'shortener\'s id or name',
                'var_part': 'variable part of shortened link',
        } }


    db = DBFactory.get_instance()
    cur = db.cursor(cursor_factory = psycopg2.extras.RealDictCursor)

    sql = 'SELECT * '
    sql += 'FROM link '
    sql += 'WHERE shortener = %s '
    sql += 'AND var_part = %s;'
    data = (id_shortener, varPart)                

    try: 
        cur.execute(sql, data)
        result = cur.fetchone()
        if len(result) > 0:            
            return json.dumps(result, default=dthandler)
        else:
            return { ERROR_KEY: ERRORS['LINK_NOT_FOUND'], MESSAGE_KEY: 'Link not found',}
    except Exception, e: 
        return { ERROR_KEY: ERRORS['UNEXPECTED'], MESSAGE_KEY: str(e) }
        

@route('/link/update')
def updatelink(id_link = None, newreal = None):
    """
    Update the real URL of a link, return its ID
    @param id_link: link ID
    @param real: real URL
    """

    if id_link is None:

        id_link = request.GET.get('id_link', default=None)
    if newreal is None:
        newreal = request.GET.get('real', default=None)

    if id_link is None or newreal is None:
        return { ERROR_KEY: ERRORS['INVALID_PARAMETERS'], MESSAGE_KEY: 'Invalid parameters',
            'route': '/link/update',
            'params': {
                'id_link': 'link ID',
                'real': 'real URL',
        } }


    db = DBFactory.get_instance()
    cur = db.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
    
    sql = 'UPDATE link '
    sql += 'SET real = %s, '
    sql += 'last_edit = now() '
    sql += 'WHERE id_link = %s '
    sql += 'RETURNING id_link'
    data = ( newreal,  id_link )        
    try: 
        cur.execute(sql, data)
        db.commit()
        if( len(cur.fetchall()) > 0 ):
            return{ 'id': id_link }
        else:
            return { ERROR_KEY: ERRORS['LINK_NOTHING_UPDATE'], MESSAGE_KEY: 'Nothing to update' }
    except Exception, e: 
        db.rollback()
        return { ERROR_KEY: ERRORS['UNEXPECTED'],MESSAGE_KEY: str(e)}

@route('/errors.json')
def getErrors():
    response.content_type = 'application/json'
    return open('errors.json').read()

def loadErrors(filename):
    try:
        data = json.load(open(filename))
        global ERROR_KEY, MESSAGE_KEY, ERRORS
        ERROR_KEY = data['ERROR_KEY']
        MESSAGE_KEY = data['MESSAGE_KEY']
        ERRORS = data['ERROR_CODES']
        return True
    except Exception, e:
        return False

def loadConf(filename):
    try:
        data = json.load(open(filename))
        global CONNECTION_STRING
        CONNECTION_STRING = "host='"+ data['database']['host'] +"' "
        CONNECTION_STRING += "dbname='"+ data['database']['db'] +"' "
        CONNECTION_STRING += "user='"+ data['database']['user'] +"' "
        CONNECTION_STRING += "password='"+ data['database']['password'] +"'"
        return True
    except Exception, e:
        print str(e)
        return False

##
# MAIN
##
if __name__ == '__main__':
    if loadErrors('errors.json') is False:
        print "EROOR: Unable to load 'errors.json' file"
        sys.exit()
    if loadConf('conf.json') is False:
        print "EROOR: Unable to load 'conf.json' file"
        sys.exit()

    bottle.debug(True) # display traceback 
    run(host='0.0.0.0', port=7500, reloader=True)
    
