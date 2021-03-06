#!/usr/bin/python

import psycopg2
import psycopg2.extras
import json

GET_MAX_SIZE = 500
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

class Service(object):
    """ todo """
    
    def __init__(self, table):
        self.table = table
    
    def get(self, nb, **params):
        """ todo """
        if nb > GET_MAX_SIZE:
            print "error"
        
        # Define SQL String from params
        sql = "SELECT * FROM "+ self.table + " "
        cpt = 0
        values = list()
        for key, value in params.items():
            if cpt != 0:
                sql += "AND "
            else:
                sql += "WHERE "
            sql += str(key) +" = %s "
            values.append(value)
            cpt = cpt + 1

        sql += "LIMIT "+ str(nb) + " OFFSET 0"
        
        # Execute SQL statement
        db = DBFactory.get_instance()
        cur = db.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
        data = tuple(values)
        
        try:
            cur.execute(sql, data)
            result = cur.fetchall()    
            return result
                
        except Exception, e:
            raise e
    
    def getOne(self, **params):
        """todo"""
        try:
            return self.get(1, **params)[0]
        except Exception, e:
            raise e
            
    def add(self, returning=None, **params):
        """ todo """
        
        # Define SQL String from params
        sql = columns = values_str = returning_str = str()
        values = list()
        cpt = 1
        for key, value in params.items():
            if cpt < len(params):
                sep = ', '
            else:
                sep = ' '
            columns += str(key) + sep
            values.append(value)
            values_str += '%s' + sep
            cpt = cpt + 1

        if returning is not None:
            returning_str = 'RETURNING '+ returning

        sql += "INSERT INTO "+ self.table +" ( "+ columns + ") VALUES ( "+ values_str + " ) " + returning_str

        # Execute SQL statement
        db = DBFactory.get_instance()
        cur = db.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
        data = tuple(values)
        
        try:
            cur.execute(sql, data)
            db.commit()
            if returning is not None:
                result = cur.fetchone()[returning]   
                return result                
        except Exception, e:
            db.rollback()
            raise e   

    def update( self, returning, where, **params ):
        """ TODO """

        # Define SQL String from params
        sql = columns = values_str = where_str = returning_str = str()
        values = wheres = list()
        cpt = 1
        print len(params)
        for key, value in params.items():
            if cpt < len(params):
                sep = ', '
            else:
                sep = ' '
            values_str += str(key) +" = %s " + sep
            values.append(value)
            cpt = cpt + 1

        cpt = 0
        for key, value in where.items():
            if cpt != 0:
                sep = "AND "
            else:
                sep = "WHERE "
            where_str += sep + " "+ str(key) +" = %s " 
            wheres.append(value)
            cpt = cpt + 1

        if returning is not None:
            returning_str = 'RETURNING '+ returning

        sql += "UPDATE "+ self.table +" SET "+ values_str + " "+ where_str +" "+ returning_str
        print sql
        # Execute SQL statement
        db = DBFactory.get_instance()
        cur = db.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
        data = tuple(values)
        
        try:
            cur.execute(sql, data)
            db.commit()
            if returning is not None:
                return cur.fetchall()       
        except Exception, e:
            db.rollback()
            raise e   

            
class ShortenerService(Service):
    """ todo """

    def __init__(self):
        super(ShortenerService, self).__init__("shortener")

class LinkService(Service):
    """ todo """

    def __init__(self):
        super(LinkService, self).__init__("link")

    def getLast(self, shortener):
        db = DBFactory.get_instance()
        cur = db.cursor(cursor_factory = psycopg2.extras.RealDictCursor)

        sql = 'SELECT * '
        sql += 'FROM link '    
        sql += 'WHERE id_link = ( '
        sql += ' SELECT MAX(id_link) FROM link '
        sql += 'WHERE shortener = %s )'
        data = (shortener, )  

        try: 
            cur.execute(sql, data)
            result = cur.fetchone()          
            return result
        except Exception, e: 
            raise e

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
        