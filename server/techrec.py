import logging


import sys
import datetime
import json
import yaml

try:
  from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean
  from sqlalchemy.orm import sessionmaker
  from sqlalchemy.ext.declarative import declarative_base
except:
  sys.exit("No SQLAlchemy.")


logging.basicConfig(level=logging.INFO)

STATE_ACTIVE    = 0 
STATE_RUN       = 1 
STATE_DOWN      = 2 

PAGESIZE = 10

"""
This class describe a single Record (Rec() class) and the 
records manager (RecDB() class) 
"""
Base = declarative_base()

"""
 Rec entry
"""    
class Rec(Base):
  
    __tablename__ = 'rec'
    id          = Column(Integer, primary_key=True)
    recid       = Column(String)
    name        = Column(String, nullable = True)
    starttime   = Column(DateTime, nullable = True)
    endtime     = Column(DateTime, nullable = True)
    active      = Column(Boolean, default = True)

    def __init__(self, recid="", name="", starttime=None, endtime=None, asjson=""):
        self.error = 0 
        self.job = None    
    
        if len(asjson) == 0:
          self.name = name
          self.starttime = starttime
          self.endtime = endtime
          self.recid = recid
        else:
            #try:
                # dec = json.loads( unicode(asjson) )
            # dec = yaml.load( asjson )
            dec = json.dumps( asjson ) 
            # except:
            #  self.error = 0
            print("dec %s %s" % (dec,type(dec))) 
            print("asjson %s %s" % (asjson,type(asjson))) 
          
            self.recid = asjson[0]['recid']
            self.name = asjson[0]['name'] 
            self.starttime = asjson[0]['starttime']
            self.endtime = asjson[0]['endtime']
    
        self.state = STATE_ACTIVE


    # launch the job for processing files
    def start(self):
        self.job = RecJob( self )

    """
    def getvalues(self,val=None):
        return { "id":self.id,
                "recid":self.recid,
                "name":self.name,
                "starttime":self.starttime, 
                "endtime":self.endtime,
                "active": self.active
                }
    """
    def err(self): 
        return self.error

    def set_run(self):
        self.active = STATE_RUN

    def set_done(self):
        self.active = STATE_DOWN

    def __repr__(self):
        return "<Rec(id:'%s',recid:'%s',name:'%s',Start: '%s',End: '%s',Active: '%s')>" \
                % (self.id, self.recid, self.name, self.starttime, self.endtime, self.active)

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

        self.err = ""
        self.recordtimeformat = "%Y/%m/%d %H:%M:%S"
        
    def add(self, simplerecord):
        print self.session.add( simplerecord )
        self.commit()
        logging.info("New Record: %s" % simplerecord)
        return ( simplerecord )


    """" 
        UPDATE RECORD 
    """
    def update(self, recid, rec):

        _rlist = self._search(recid=recid)
        if not len(_rlist) == 1:
            return False

        logging.info("DB:: Update request %s:%s " % (recid, rec))
        logging.info("DB:: Update: data before %s" % _rlist[0])

        # 2013-11-24 22:22:42
        _rlist[0].starttime = datetime.datetime.strptime(rec["starttime"], self.recordtimeformat)
        _rlist[0].endtime = datetime.datetime.strptime(rec["endtime"], self.recordtimeformat)
        _rlist[0].name = rec["name"]
        logging.info("DB:: Update: data AFTER %s" % _rlist[0])

        self.commit()
        logging.info("DB:: Update complete")
        return True

    """" 
        DELETE RECORD 
    """
    def delete(self,_id):
        
        _rlist = self._search(_id=_id)
        
        if len(_rlist) == 0: 
            logging.info("DB: Delete: no record found!")
            self.err = "No rec found"
            return False
            
        if len(_rlist) > 1: 
            logging.info("DB: Delete: multilpe records found!")
            self.err = "multiple ID Found %s" % (_rlist)
            return False

        self.session.delete( _rlist[0] )
        logging.info("DB: Delete: delete complete")
        self.commit()
        return True
        
    def commit(self):
        logging.info("DB: Commit!!")
        self.session.commit()

    def get_all(self, page=0, page_size=PAGESIZE):
        return self._search(page=page, page_size=page_size)
    
    def _search(self, _id=None, name=None, recid=None, starttime=None, endtime=None, active=None, page=0, page_size=PAGESIZE):
    
        logging.info("DB: Search => id:%s recid:%s name:%s starttime:%s endtime=%s active=%s" % (_id,recid,name,starttime,endtime,active))
        
        query = self.session.query(Rec)
        
        if not _id == None:         query = query.filter_by(id=_id)
        if not recid == None:       query = query.filter_by(recid=recid)
        if not name == None:        query = query.filter(Rec.name.like("%"+name+"%"))
        try:
            if not starttime == None:   
                _st = datetime.datetime.strptime(starttime, self.recordtimeformat)
                query = query.filter(Rec.starttime > _st )
        except:
                logging.info("DB: search : no valid starttime")    
        try:
            if not endtime == None:     
                _et = datetime.datetime.strptime(endtime, self.recordtimeformat)
                query = query.filter(Rec.endtime < _et )
        except ValueError:
            logging.info("DB: search : no valid endtime")    

        if not active == None:      query = query.filter(Rec.active==active)
        
        if page_size:   query = query.limit(page_size)
        if page:        query = query.offset(page*page_size)
        print query
        ret = query.all()
        # print "Sending: %s" % ret
        return ret
        
    def get_err(self): 
        print "DB error: %s" % (self.err)
        t = self.err
        self.err = ""
        return t
        
    """def get_by_id(self,id):
        try:
            return self._search( _id=id )[0]
        except:
            return None
    """  
    
# Just for debug
def printall( queryres ):
    for record in queryres: print "Record: %s" % record


# Job in thread
class RecJob():
    def __init__(self, rec):
        print "Estraggo %s Start:%s, End:%s" % (rec.name, rec.starttime, rec.endtime)
        self.fdir = "/rec/ror/"
        self.fnameformat = "ror-%Y-%m-%d-%H-00-00.mp3"
        self.name = rec.name
        self.starttime = rec.starttime
        self.endtime = rec.endtime
        
    def extract(self):

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
    # j.extract()
    printall( db._search() )
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
    
