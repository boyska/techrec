import logging
logging.basicConfig(level=logging.DEBUG)
import sys

try:
  from sqlalchemy import create_engine, Column, Integer, String
  from sqlalchemy.orm import sessionmaker
  from sqlalchemy.ext.declarative import declarative_base
except:
  sys.exit("No SQLAlchemy.")


import json

import yaml

"""
This class describe a single Record (Rec() class) and the 
records manager (RecDB() class) 
"""

Base = declarative_base()

""" ************ 
RECORD ABSTRACTION
************ """
QUEUE = 0 
RUN   = 2
DONE  = 4

class Rec(Base):
  
  __tablename__ = 'rec'
  id = Column(Integer, primary_key=True)
  name = Column(String)
  endtime = Column(String)
  starttime = Column(String)
  state   = Column(Integer)

  def __init__(self, name="", starttime="", endtime="",asjson=""):
    self.error = 0 

    if len(asjson) == 0:
      self.name = name
      self.starttime = starttime
      self.endtime = endtime
    else:
      #try:
        # dec = json.loads( unicode(asjson) )
      # dec = yaml.load( asjson )
      dec = json.dumps( asjson ) 
      # except:
      #  self.error = 0
      print("dec %s %s" % (dec,type(dec))) 
      print("asjson %s %s" % (asjson,type(asjson))) 
      
      # self.name = dec[0]['name'] 
      # self.starttime = dec[0]['starttime']
      # self.endtime = dec[0]['endtime']
      self.name = asjson[0]['name'] 
      self.starttime = asjson[0]['starttime']
      self.endtime = asjson[0]['endtime']
    # self.id = None
    self.state = QUEUE
    print "DECC" , dec
    print "NAME", self.name
    print "Sstart", self.starttime
    print "END", self.endtime
      
  def err(self): return self.error

  def setrun(self):
    self.state = RUN

  def setdone(self):
    self.state = DONE

  def __repr__(self):
    return "<Rec('%s','%s','%s', '%s', '%s')>" % (self.id, self.name, self.starttime, self.endtime, self.state)
    

""" ************ 
RecDB
************ """

class RecDB:
  def __init__(self):
  
    self.engine = create_engine('sqlite:///techrec.db', echo=True)
    self.conn = self.engine.connect()
    
    Base.metadata.create_all(self.engine) # create Database

    Session = sessionmaker(bind=self.engine)
    self.session = Session()    
        
  def add(self, simplerecord):
    logging.debug("New Record: %s" % simplerecord)
    self.session.add( simplerecord )
    self.session.commit()

  # print all records
  def printall(self):
    print("DB")
    allrecords = self.session.query(Rec).all()

    for record in allrecords:
      print("R: %s" % record)
      
  def execsql(self,sql):
    records = self.conn.execute( sql )
    
  def search(self, name="", starttime="", endtime=""):
    
    logging.debug("Looking for %s" % recfilter)
    
    # self.session.query( Rec ).filter( Rec.name=name ).first()
    
    for row in records:
      print "Found:", row
