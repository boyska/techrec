  import logging
logging.basicConfig(level=logging.DEBUG)

from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

"""
This class describe a single Record (Rec() class) and the 
records manager (RecDB() class) 
"""

Base = declarative_base()

""" ************ 
RECORD ABSTRACTION
************ """

class Rec(Base):
  
  __tablename__ = 'rec'
  id = Column(Integer, primary_key=True)
  name = Column(String)
  endtime = Column(String)
  starttime = Column(String)
  
  def __init__(self, name="", starttime="", endtime=""):
    self.name = name
    self.starttime = starttime
    self.endtime = endtime
    self.id = None

  def __repr__(self):
    return "<Rec('%s','%s','%s', '%s')>" % (self.id, self.name, self.starttime, self.endtime)
    

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
    logging.info("DB")
    allrecords = self.session.query(Rec).all()

    for record in allrecords:
      logging.info("R: %s " % record)
      
  def execsql(self,sql):
    records = self.conn.execute( sql )
    
  def search(self, name="", starttime="", endtime=""):
    
    logging.info("Looking for %s" % recfilter)
    
    self.session.query( Rec ).filter( Rec.name=name ).first()
    
    for row in records:
      print "Found:", row
