import logging
logging.basicConfig(level=logging.DEBUG)
import sys
import datetime
try:
  from sqlalchemy import create_engine, Column, Integer, String, DateTime
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
    # TODO: timestamp
    endtime = Column(DateTime)
    starttime = Column(DateTime)
    state   = Column(Integer)

    def __init__(self, name="", starttime=None, endtime=None, asjson=""):
        self.error = 0 
        self.values = {"name":"","starttime":"", "endtime":""}
    
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
          
            self.name = asjson[0]['name'] 
            self.starttime = asjson[0]['starttime']
            selfendtime = asjson[0]['endtime']
    
        self.state = QUEUE
        logging.info("New REC: ", self.values)

    # launch the job for processing files
    def start(self):
        # calcola file da splittare
        pass
                  
    def getvalue(self,val=None):
        if val != None:
            if self.values.has_key(val):
                return self.values[val]
        return self.values
      
    def err(self): 
        return self.error

    def set_run(self):
        self.state = RUN

    def set_done(self):
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
    print(" ---- DB ---- ")
    allrecords = self.session.query(Rec).all()

    print [ "R: %s" % record for record in allrecords ]
      
      
  def execsql(self,sql):
    records = self.conn.execute( sql )
    
  def search(self, name="", starttime="", endtime=""):
    
    logging.debug("Looking for %s - %s - %s" % (name, starttime, endtime) )
    
    ret = self.session.query(Rec).filter_by(name='Mimmo1').all()
    print "[SEARCH] RET (",type(ret),")" , ret
    for row in ret:
      print "[SEARCH] Found:", row

if __name__ == "__main__":
    # text
    db = RecDB()
      
    _mytime = datetime.datetime(2014,05,24,15,16,17)
    a = Rec(name="Mimmo1", starttime=_mytime, endtime=None)
    
    db.add( a )
    
    raw_input()
    
    db.printall()

    raw_input()
    # db.search( Rec(name="Mimmo1") )
    db.search( name="Mimmo1" )
    