import SocketServer
import sys,os
import logging
logging.basicConfig(level=logging.INFO)

# include data object
from techrec import *

""" CONNECTION HANDLER """
class ConnHandler(SocketServer.BaseRequestHandler):
  def __init__(self, db, *args, **keys):
    self.db 	= db
    SocketServer.BaseRequestHandler.__init__(self, *args, **keys)

  def handle(self):

    self.data = self.request.recv(1024).strip()
    logging.debug("DATA: %s - %s" % (self.client_address[0], self.data) )

    tmp = Rec(asjson=self.data)


    if tmp.err():
      respmsg = "Data ERROR"
    else:
      respmsg = "OK"
    
    logging.debug("Created REC %s" % tmp)

    self.db.add( tmp ) 
    self.db.printall()
    self.request.sendall( respmsg )

def handler_factory(db):
  def createHandler(*args, **keys):
    return ConnHandler(db, *args, **keys)
  return createHandler

""" MAIN SERVER """
class recserver:
  def __init__(self, host="localhost", port=9999):
    self.host = host
    self.port = port
    self.db   = RecDB()

  def start(self):
    try:
      # self.server = SocketServer.TCPServer((self.host, self.port), ConnHandler)
      self.server =   SocketServer.TCPServer((self.host, self.port), handler_factory( self.db ) )
    except:
      sys.exit("Bind error.")

    logging.info("Server ready to serve forever.")
    self.server.serve_forever()     

def loadall():
  """
  # Testing DB
  db = RecDB()
  a = Rec(name="Mimmo1",starttime="ora",endtime="fine")
  db.add( a )
  db.printall()
  db.search( Rec(name="Mimmo1") )
  """
  # Loading Server TODO: make thread
  r = recserver() 
  r.start()


# Loading Server
if __name__ == "__main__":
  loadall()
  
