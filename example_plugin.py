__author__ = "Sean Ashton"
__copyright__ = "Copyright (C) 2013 Schimera Pty Ltd"
__version__ = "0.1"

def advanced_redirect(username):
    return False #Use the standard format rules    
    #generate custom URL based on username
    #return "http://example.org/%s" % username 
    #generate custom URL by DB lookup
    #return redirect_sqlite(username)
    
    
def redirect_sqlite(username):
    import sqlite3
    conn = sqlite3.connect("user_table.db")
    cursor = conn.cursor()
    sql = "SELECT username,url FROM users WHERE username=?"
    cursor.execute(sql, [(username)])
    row = cursor.fetchone() 
    if row is not None:
        return row[1]
    else:
        return False