import logging


import sys

try:
    from sqlalchemy import create_engine, Column, Integer, String, DateTime
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy.ext.declarative import declarative_base
except:
    sys.exit("No SQLAlchemy.")


logging.basicConfig(level=logging.INFO)

PAGESIZE = 10

"""
This class describe a single Record (Rec() class) and the
records manager (RecDB() class)
"""
Base = declarative_base()


class Rec(Base):
    '''Entry on the DB'''
    __tablename__ = 'rec'
    id = Column(Integer, primary_key=True)
    recid = Column(String)
    name = Column(String, nullable=True)
    starttime = Column(DateTime, nullable=True)
    endtime = Column(DateTime, nullable=True)
    filename = Column(String, nullable=True)

    def __init__(self, recid="", name="", starttime=None, endtime=None,
                 filename=None):
        self.name = name
        self.starttime = starttime
        self.endtime = endtime
        self.recid = recid
        self.filename = filename

    def serialize(self):
        '''json-friendly encoding'''
        return {'name': self.name,
                'starttime': self.starttime,
                'endtime': self.endtime,
                'recid': self.recid,
                'filename': self.filename
                }

    def __repr__(self):
        contents = "id:'%s',recid:'%s',name:'%s',Start: '%s',End: '%s'" % \
            (self.id, self.recid, self.name, self.starttime, self.endtime)
        if self.filename is not None:
            contents += ",Filename: '%s'" % self.filename
        return "<Rec(%s)>" % contents


class RecDB:
    def __init__(self, uri):
        self.engine = create_engine(uri, echo=False)
        self.conn = self.engine.connect()

        logging.getLogger('sqlalchemy.engine').setLevel(logging.FATAL)
        logging.getLogger('sqlalchemy.engine.base.Engine')\
            .setLevel(logging.FATAL)
        logging.getLogger('sqlalchemy.dialects').setLevel(logging.FATAL)
        logging.getLogger('sqlalchemy.pool').setLevel(logging.FATAL)
        logging.getLogger('sqlalchemy.orm').setLevel(logging.FATAL)

        Base.metadata.create_all(self.engine) # create Database

        Session = sessionmaker(bind=self.engine)
        self.session = Session()

        self.err = ""

    def add(self, simplerecord):
        print self.session.add( simplerecord )
        self.commit()
        logging.info("New Record: %s" % simplerecord)
        return ( simplerecord )

    def update(self, recid, rec):

        ## TODO: rlist = results list
        _rlist = self._search(recid=recid)
        if not len(_rlist) == 1:
            raise ValueError('Too many recs with id=%s' % recid)

        logging.info("DB:: Update request %s:%s " % (recid, rec))
        logging.info("DB:: Update: data before %s" % _rlist[0])

        # 2013-11-24 22:22:42
        _rlist[0].starttime = rec["starttime"]
        _rlist[0].endtime = rec["endtime"]
        if 'name' in rec:
            _rlist[0].name = rec["name"]
        logging.info("DB:: Update: data AFTER %s" % _rlist[0])

        self.commit()
        logging.info("DB:: Update complete")
        return _rlist[0]

    def delete(self,recid):

        _rlist = self._search(recid=recid)

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

    def _search(self, _id=None, name=None, recid=None, starttime=None,
                endtime=None, page=0, page_size=PAGESIZE):

        logging.info("DB: Search => id:%s recid:%s name:%s starttime:%s endtime=%s" % (_id,recid,name,starttime,endtime))

        query = self.session.query(Rec)

        if _id is not None:
            query = query.filter_by(id=_id)
        if recid is not None:
            query = query.filter_by(recid=recid)
        if name is not None:
            query = query.filter(Rec.name.like("%"+name+"%"))
        try:
            if starttime is not None:
                _st = starttime
                query = query.filter(Rec.starttime > _st)
        except:
                logging.info("DB: search : no valid starttime")
                raise ValueError('starttime not valid')

        try:
            if endtime is not None:
                _et = endtime
                query = query.filter(Rec.endtime < _et)
        except ValueError:
            logging.info("DB: search : no valid endtime")

        if page_size:
            page_size = int(page_size)
            query = query.limit(page_size)
        if page:
            query = query.offset(page*page_size)
        print query
        ret = query.all()
        # print "Sending: %s" % ret
        return ret

    def get_err(self):
        print "DB error: %s" % (self.err)
        t = self.err
        self.err = ""
        return t


if __name__ == "__main__":
    from datetime import datetime

    def printall(queryres):
        for record in queryres:
            print "Record: %s" % record

    db = RecDB()
    _mytime = datetime(2014,05,23,15,12,17)
    _endtime = datetime(2014,05,24,17,45,17)

    a = Rec(name="Mimmo1", starttime=_mytime, endtime=_endtime)
    printall( db._search() )
    sys.exit("End test job")

    # a = Rec(name="Mimmo1", starttime=_mytime, endtime=None)
    print "Aggiunto", db.add( a )
    printall( db.get_all(page_size=5,page=0) )

    print "Mimmo "
    printall( db._search(name="Mimmo1"))
    print "Search"
    printall( db._search(name="Mimmo1",starttime=datetime(2014,05,24,15,16,1) ))
    a = db.get_by_id(5)
    a.start()
    db.delete(1)
    db.delete(2)
    db.delete(4)
    db.delete(1)
    printall( db._search() )
