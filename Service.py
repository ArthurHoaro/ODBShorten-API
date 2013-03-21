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
        sql = "SELECT * FROM "+ self.table +" WHERE "
        cpt = 0
        for key, value in params.items():
            if cpt != 0:
                sql += "AND "
            sql += str(key) +" = %s "
        sql += "LIMIT "+ nb + " OFFSET 0"
        
        # Execute SQL statement
        db = DBFactory.get_instance()
        cur = db.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
        data = params.items()
        
        try:
            cur.execute(sql, data)
            result = cur.fetch()    
            return result
                
        except Exception, e:
            raise e
            
            
    def add(self, **params):
        """ todo """
        
        # Define SQL String from params
        sql = "SELECT * FROM "+ self.table +" WHERE "
        cpt = 0
        for key, value in params.items():
            if cpt != 0:
                sql += "AND "
            sql += str(key) +" = %s "
        sql += "LIMIT "+ nb + " OFFSET 0"
        
        # Execute SQL statement
        db = DBFactory.get_instance()
        cur = db.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
        data = params.items()
        
        try:
            cur.execute(sql, data)
            result = cur.fetch()    
            return result
                
        except Exception, e:
            raise e
            
class ShortenerService(Service):
    """ todo """

    def __init__(self):
        super(Service, self).__init__("Shortener")
        