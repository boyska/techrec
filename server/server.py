import SocketServer

import sys,os

import logging
logging.basicConfig(level=logging.INFO)

from techrec import *

""" CONNECTION HANDLER """
class ConnHandler(SocketServer.BaseRequestHandler):
  def handle(self):
    self.data = self.request.recv(1024).strip()
    logging.info("Connection from " % ( format(self.client_address[0]) ))
    print self.data
    self.request.sendall(self.data.upper())

""" MAIN SERVER """
class recserver:
  def __init__(self, host="localhost", port=9999):
    self.host = host
    self.port = port
    
  def start(self):
    self.server = SocketServer.TCPServer((self.host, self.port), ConnHandler)
    logging.info("Server ready to serve forever.")
    self.server.serve_forever()     


def loadall():

  # Testing DB
  db = RecDB()

  a = Rec(name="Mimmo1",starttime="ora",endtime="fine")
  b = Rec(name="Mimmo2",starttime="ora",endtime="fine")
  c = Rec(name="Mimmo3",starttime="ora",endtime="fine")
  
  db.add( a )
  db.add( b )
  db.add( c )
  
  db.printall()

  db.search( Rec(name="Mimmo1") )


  sys.exit()
  
  # Loading Server TODO: make thread
  r = recserver() 
  r.start()


# Loading Server
if __name__ == "__main__":
  loadall()
  