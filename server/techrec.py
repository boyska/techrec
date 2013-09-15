import logging


import sys
import datetime
import json
import yaml

try:
  from sqlalchemy import create_engine, Column, Integer, String, DateTime
  from sqlalchemy.orm import sessionmaker
  from sqlalchemy.ext.declarative import declarative_base
except:
  sys.exit("No SQLAlchemy.")


logging.basicConfig(level=logging.INFO)


"""
This class describe a single Record (Rec() class) and the 
records manager (RecDB() class) 
"""

Base = declarative_base()

""" ************ 
RECORD STATE FLAGS
************ """
QUEUE = 0 
RUN   = 2
DONE  = 4

PAGESIZE = 10

    
class Rec(Base):
  
    __tablename__ = 'rec'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    endtime = Column(DateTime)
    starttime = Column(DateTime)
    state   = Column(Integer)

    def __init__(self, name="", starttime=None, endtime=None, asjson=""):
        self.error = 0 
        self.job = None    
    
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


    # launch the job for processing files
    def start(self):
        self.job = RecJob( self )

    def getvalues(self,val=None):
        return { "id":self.id,
                "name":self.name,
                "starttime":self.starttime, 
                "endtime":self.endtime,
                "state": self.state
                }
      
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
  
        self.engine = create_engine('sqlite:///techrec.db', echo=False)
        self.conn = self.engine.connect()

        logging.getLogger('sqlalchemy.engine').setLevel(logging.FATAL)
        logging.getLogger('sqlalchemy.engine.base.Engine').setLevel(logging.FATAL)
        logging.getLogger('sqlalchemy.dialects').setLevel(logging.FATAL)
        logging.getLogger('sqlalchemy.pool').setLevel(logging.FATAL)
        logging.getLogger('sqlalchemy.orm').setLevel(logging.FATAL)
        
        Base.metadata.create_all(self.engine) # create Database
        
        Session = sessionmaker(bind=self.engine)
        self.session = Session()    
        
    def add(self, simplerecord):
        logging.debug("New Record: %s" % simplerecord)
        self.session.add( simplerecord )
        self.commit()
        return ( simplerecord )

    def delete(self,id):
        _r = self.get_by_id(id)
        
        if _r:
            self.session.delete( _r )
            self.commit()
            return
        logging.info("Delete error: ID %s not found!", id)
        
    def commit(self):
        self.session.commit()

    def get_all(self,page=0, page_size=PAGESIZE):
        return self._search(page=page, page_size=page_size)
    
    def _search(self, _id=None, name=None, starttime=None, endtime=None, page=0, page_size=PAGESIZE):
        query = self.session.query(Rec)
        if _id:         query = query.filter_by(id=_id)
        if name:        query = query.filter_by(name=name)
        if starttime:   query = query.filter(Rec.starttime>starttime)
        if endtime:     query = query.filter(Rec.endtime<endtime)
        if page_size:   query = query.limit(page_size)
        if page:        query = query.offset(page*page_size)

        return query.all()
        
    def get_by_id(self,id):
        try:
            return self._search( _id=id )[0]
        except:
            return None
        
# Just for debug
def printall( queryres ):
    for record in queryres:
        print "R: %s" % record


# Job in thread
class RecJob():
    def __init__(self, rec):
        print "Estraggo %s Start:%s, End:%s" % (rec.name, rec.starttime, rec.endtime)
        self.fdir = "/rec/ror/"
        self.fnameformat = "ror-%Y-%m-%d-%H-00-00.mp3"
        self.name = rec.name
        self.starttime = rec.starttime
        self.endtime = rec.endtime
        
    def run(self):

        if type(self.starttime) != type(datetime.datetime.now()):
            logging.info("Starttime format error")
            return
        
        if type(self.endtime) != type(datetime.datetime.now()):
            logging.info("Endtime format error")
            return
            
        if self.starttime >= self.endtime:
            logging.info("Starttime > Endtime (%s > %s)" % (self.starttime,self.endtime) )
            return

        start = self.starttime
        end  = self.endtime
        app = self.starttime
        
        while True:
            print
            print "**** From file %s take:" % ( self._get_recfile(start) )
            nexth = self._truncate(start) + datetime.timedelta(minutes=60)
             
            if start > self._truncate(start):
                print "FROM: %s for %s seconds" % (start - self._truncate(start), nexth - start )
            
            if end < self._truncate(nexth):
                print "FROM: %s for %s seconds" % (0, end - self._truncate(start) )
            else:
                print "FROM: %s for 0 to 60." % (self._get_recfile(start))
            if nexth >= end:
                print "FINITO"
                print "Start ", start, " end: ", end
                break;
            start = nexth
            
    def _truncate(self, mytime):
        return datetime.datetime(mytime.year,mytime.month,mytime.day,mytime.hour)

    def _get_recfile(self, mytime):
        return "%s/%s" % (self.fdir,mytime.strftime(self.fnameformat))
 
    def __repr__(self):
        return "%s: %s (%s) => %s (%s)" % ( self.name, self.starttime, type(self.starttime) ,self.endtime, type(self.endtime))
            
        
"""
    TEST
"""
if __name__ == "__main__":
    db = RecDB()
    _mytime = datetime.datetime(2014,05,24,15,12,17)
    _endtime = datetime.datetime(2014,05,24,17,45,17)

    a = Rec(name="Mimmo1", starttime=_mytime, endtime=_endtime)
    j = RecJob( a )
    # print (j)
    j.run()
    
    sys.exit("End test job")
      
    # a = Rec(name="Mimmo1", starttime=_mytime, endtime=None)
    print "Aggiunto", db.add( a )
    printall( db.get_all(page_size=5,page=0) )
    
    print "Mimmo "
    printall( db._search(name="Mimmo1"))
    print "Search"
    printall( db._search(name="Mimmo1",starttime=datetime.datetime(2014,05,24,15,16,1) ))
    a = db.get_by_id(5)
    a.start()
    db.delete(1)
    db.delete(2)
    db.delete(4)
    db.delete(1)
    printall( db._search() )
    
