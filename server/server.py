import SocketServer
import sys,os
import logging
logging.basicConfig(level=logging.INFO)

"""
RESPONSE HTML
http://stackoverflow.com/questions/6391280/simplehttprequesthandler-override-do-get
"""

import ast
# include data object
from techrec import *
import SimpleHTTPServer

""" CONNECTION HANDLER """
# class ConnHandler(SocketServer.BaseRequestHandler):
class ConnHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
  def __init__(self, *args, **keys):
    self.db 	= RecDB()
    # logging.info("Connected from: %s" % self.client_address[0] )
    SocketServer.BaseRequestHandler.__init__(self, *args, **keys)
    # SimpleHTTPServer.SimpleHTTPRequestHandler.__init__(self, *args, **keys)

  def strip_http_headers(self,http_reply):   
    p = http_reply.find('\r\n\r\n')
    if p >= 0:
        return http_reply[p+4:]
    return http_reply
    
  def handle(self):
    
    self.data = self.request.recv(1024).strip()
    body = [ ast.literal_eval( self.strip_http_headers( self.data ) ) ]
    print("DATA:", self.data)
    logging.debug("Received from %s:\n%s\n%s" % (self.client_address[0], self.data, body) )
    try: 
        tmp = Rec(asjson=body)
    except:
        self.request.send( "ERORE" )
        return 
    if tmp.err():
      respmsg = "Data ERROR"
    else:
      respmsg = "OK"
    
    logging.debug("Created REC %s" % tmp)

    self.db.add( tmp ) 
    self.db.printall()
    
    _responsemsg = "{}"
    responsemsg = formatresponse( _responsemsg )
    # print "SEND RESPONSE:", responsemsg
    # self.request.sendall( responsemsg )
    # self.request.send( responsemsg )
    _resmsg = json.dumps({'return':'ok'})
    print "SEnd BACK:" , _resmsg
    #TODO: check response
    #if True:
    #else:
    self.request.sendall( _resmsg )
    return 
    
def formatresponse( data ):   
    return "HTTP/1.0 200 OK\r\nContent-Type:application/json\r\nConnection:close\r\n\r\n{0}\r\n".format( data )
   
class MyTCPServer(SocketServer.ThreadingTCPServer):
    allow_reuse_address = True
      
"""def handler_factory(db):
  def createHandler(*args, **keys):
    return ConnHandler(db, *args, **keys)
  return createHandler
"""
""" MAIN SERVER """
class recserver:
  def __init__(self, host="localhost", port=9999):
    self.host = host
    self.port = port
    

  def start(self):

    self.server = SocketServer.TCPServer((self.host, self.port), ConnHandler)
    self.server = MyTCPServer((self.host, self.port), ConnHandler)
    # self.server =   SocketServer.TCPServer((self.host, self.port), handler_factory( self.db ) )


    logging.info("Server ready to serve forever.")
    try:
        self.server.serve_forever()
    except KeyboardInterrupt:
        logging.debug("Closing Socket")
        self.server.socket.close()

def testdb():
  db = RecDB()
  a = Rec(name="Mimmo1",starttime="ora",endtime="fine")
  db.add( a )
  db.printall()
  db.search( Rec(name="Mimmo1") )
    
def loadall():
  # TODO: make thread
  r = recserver() 
  r.start()

# Loading Server
if __name__ == "__main__":
  loadall()