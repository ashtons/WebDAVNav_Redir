#!/usr/bin/env python
__author__ = "Sean Ashton"
__copyright__ = "Copyright (C) 2013 Schimera Pty Ltd"
__version__ = "0.1"

import BaseHTTPServer
from SocketServer import ThreadingMixIn
from BaseHTTPServer import HTTPServer
import ssl
from base64 import b64decode
from urlparse import urljoin
import hashlib
import argparse
import re
import random
from socket import gethostname

####### User Variables ######

SSL_CERTIFICATE = None  #'server.pem'
USE_BASE_AUTH = False

######
DEFAULT_FORMAT = 'http://{{host}}/{{username}}/'
PLUGIN_AVAILABLE = False

try:
    from plugin import advanced_redirect
    PLUGIN_AVAILABLE = True    
except:    
    pass

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    pass
    
class WebDAVNavHandler( BaseHTTPServer.BaseHTTPRequestHandler):
    name = 'WebDAVNav Redirector'    
    
    server_version = "%s %s" % (name, __version__)                                  
        
    def do_PROPFIND( self ):            
        if self.headers.getheader('Authorization') == None:           
            self.requestAuthentication()
        else:
            auth_header = self.headers.getheader('Authorization')          
            username = None
            (kind,_,data) = auth_header.partition(' ')                      
            if kind == 'Basic':     
                (username, _, _) = b64decode(data).partition(':')           
            elif kind == 'Digest':                               
                m = re.search('username="(.*?)"', data)
                username = m.group(1)                             
            if username and len(username) > 0:      
                advanced = False
                if PLUGIN_AVAILABLE: 
                    advanced = advanced_redirect(username)                  
                if not advanced:                       
                    tmp_1 = self.server.user_format.replace('{{username}}',username)
                    redirect_url = tmp_1.replace('{{host}}',gethostname())                                                
                else:
                    redirect_url = str(advanced)                               
                self.send_response(307)
                self.send_header("Location", redirect_url)
                self.end_headers()
            else:
                self.requestAuthentication()
                
    def requestAuthentication(self):        
        if USE_BASE_AUTH:
            return self.requestBasicAuthentication()
        else:
            return self.requestDigestAuthentication()
            
    def requestDigestAuthentication(self):        
        nonce = hashlib.md5(str(random.randint(1, 100000))).hexdigest()
        self.send_response(401) 
        self.send_header('Content-type', 'text/html')
        self.send_header('WWW-Authenticate', 'Digest realm="%s", qop="auth",nonce="%s", ' % (self.name, nonce))
        self.end_headers()     
        self.wfile.write('Authentication required')                                         
        
    def requestBasicAuthentication(self):
        self.send_response(401)
        self.send_header('WWW-Authenticate', 'Basic realm=\"%s\"' % self.name)
        self.send_header('Content-type', 'text/html')
        self.end_headers()    
        self.wfile.write('Authentication required')        
        
def httpd(handler_class=WebDAVNavHandler, server_address = ('', 8080)):
    parser = argparse.ArgumentParser(description=handler_class.name)
    parser.add_argument('-l', help='Address to listen on',default='')
    parser.add_argument('-p', help='Port to listen on',default='8080')
    parser.add_argument('-f', help='Redirect url format',default='http://{{host}}/{{username}}/')    
    args = parser.parse_args()        
    ip_address = str(args.l)
    tcp_port = int(args.p)   
    redirect_format = str(args.f)
    server_address = (ip_address,tcp_port)
    try:
        print handler_class.server_version           
        server = ThreadedHTTPServer(server_address, handler_class)
        if len(redirect_format) > 0 and redirect_format.startswith('http'):           
            server.user_format = redirect_format                     
        else:
            server.user_format = DEFAULT_FORMAT
        if SSL_CERTIFICATE is not None:
            server.socket = ssl.wrap_socket (server.socket, certfile= SSL_CERTIFICATE, server_side=True)
            print "SSL on"
        else:
            print "SSL off"        
        server.allow_reuse_address = True       
        sa = server.socket.getsockname()
        print "Redirecting WebDAV Nav on", sa[0], "port", sa[1], "..."
        print "Default redirect format %s" % redirect_format
        server.serve_forever() 
    except KeyboardInterrupt:
        server.socket.close()

if __name__ == "__main__":
    httpd( )
