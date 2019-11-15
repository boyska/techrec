'''
This module contains DB logic
'''
from __future__ import print_function
import logging
from datetime import datetime, timedelta


import sys

from sqlalchemy import create_engine, Column, Integer, String, DateTime, inspect
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from .config_manager import get_config

PAGESIZE = 10

Base = declarative_base()


class Rec(Base):
    '''Entry on the DB'''
    __tablename__ = 'rec'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=True)
    starttime = Column(DateTime, nullable=True)
    endtime = Column(DateTime, nullable=True)
    filename = Column(String, nullable=True)

    def __init__(self, name="", starttime=None, endtime=None,
                 filename=None):
        self.name = name
        self.starttime = starttime
        self.endtime = endtime
        self.filename = filename

    def serialize(self):
        '''json-friendly encoding'''
        return {'id': self.id,
                'name': self.name,
                'starttime': self.starttime,
                'endtime': self.endtime,
                'filename': self.filename
                }

    def __repr__(self):
        contents = "id:'%s',name:'%s',Start: '%s',End: '%s'" % \
            (self.id, self.name, self.starttime, self.endtime)
        if self.filename is not None:
            contents += ",Filename: '%s'" % self.filename
        return "<Rec(%s)>" % contents


class RecDB:
    def __init__(self, uri):
        self.engine = create_engine(uri, echo=False)
        self.conn = self.engine.connect()
        self.log = logging.getLogger(name=self.__class__.__name__)

        logging.getLogger('sqlalchemy.engine').setLevel(logging.FATAL)
        logging.getLogger('sqlalchemy.engine.base.Engine')\
            .setLevel(logging.FATAL)
        logging.getLogger('sqlalchemy.dialects').setLevel(logging.FATAL)
        logging.getLogger('sqlalchemy.pool').setLevel(logging.FATAL)
        logging.getLogger('sqlalchemy.orm').setLevel(logging.FATAL)

        Base.metadata.create_all(self.engine)  # create Database

        Session = sessionmaker(bind=self.engine)
        self.session = Session()

        self.err = ""

    def add(self, simplerecord):
        s = self.get_session()
        s.add( simplerecord )
        s.commit()
        self.log.info("New Record: %s" % simplerecord)
        return ( simplerecord )

    def update(self, id, rec):

        # TODO: rlist = results list
        _rlist = self._search(_id=id)
        if not len(_rlist) == 1:
            raise ValueError('Too many recs with id=%s' % id)

        self.log.debug("DB:: Update request %s:%s " % (id, rec))
        self.log.debug("DB:: Update: data before %s" % _rlist[0])

        # 2013-11-24 22:22:42
        _rlist[0].starttime = rec["starttime"]
        _rlist[0].endtime = rec["endtime"]
        if 'name' in rec:
            _rlist[0].name = rec["name"]
        self.log.debug("DB:: Update: data AFTER %s" % _rlist[0])

        self.get_session(_rlist[0]).commit()
        self.log.debug("DB:: Update complete")
        return _rlist[0]

    def delete(self, recid):

        _rlist = self._search(id=recid)

        if len(_rlist) == 0:
            self.log.info("DB: Delete: no record found!")
            self.err = "No rec found"
            return False

        if len(_rlist) > 1:
            self.log.warning("DB: Delete: multiple records found!")
            self.err = "multiple ID Found %s" % (_rlist)
            return False

        s = self.get_session()
        s.delete(_rlist[0])
        self.log.info("Delete: delete complete")
        s.commit()
        return True

    def commit(self):
        self.log.info("Commit!!")
        self.session.commit()

    def get_session(self, rec=None):
        if rec is None:
            Session = sessionmaker(bind=self.engine)
            return Session()
        else:
            return inspect(rec).session

    def get_all(self, page=0, page_size=PAGESIZE):
        return self._search(page=page, page_size=page_size)

    def get_ongoing(self, page=0, page_size=PAGESIZE):
        query = self._query_page(self._query_ongoing(), page, page_size)
        return query.all()

    def get_not_completed(self, minseconds=36000):
        query = self._query_ongoing()
        query = self._query_older(timedelta(seconds=minseconds), query)
        return query.all()

    def get_archive_recent(self):
        query = self._query_saved()
        query = self._query_newer(timedelta(days=15), query)
        query = query.order_by(Rec.starttime.desc())
        return query.all()

    def _query_ongoing(self, query=None):
        '''
        Not terminated AND recent.

        The meaning is "a query that makes sense to stop"
        '''
        delta = timedelta(seconds=get_config()['FORGE_MAX_DURATION'])
        return self._query_newer(delta, self._query_not_saved(query))

    def _query_not_saved(self, query=None):
        '''Still not saved'''
        if query is None:
            query = self.get_session().query(Rec)
        return query.filter(Rec.filename == None)

    def _query_saved(self, query=None):
        '''Still not saved'''
        if query is None:
            query = self.get_session().query(Rec)
        return query.filter(Rec.filename != None)

    def _query_newer(self, delta, query=None):
        '''Get Rec older than delta seconds'''
        if query is None:
            query = self.get_session().query(Rec)
        return query.filter(Rec.starttime > datetime.now() - delta)

    def _query_older(self, delta, query=None):
        '''Get Rec older than delta seconds'''
        if query is None:
            query = self.get_session().query(Rec)
        return query.filter(Rec.starttime < datetime.now() - delta)

    def _query_page(self, query, page=0, page_size=PAGESIZE):
        if page_size:
            page_size = int(page_size)
            query = query.limit(page_size)
        if page:
            query = query.offset(page*page_size)
        return query

    def _query_generic(self, query, _id=None, name=None, starttime=None,
                       endtime=None):
        if _id is not None:
            query = query.filter_by(id=_id)
        if name is not None:
            query = query.filter(Rec.name.like("%"+name+"%"))
        if starttime is not None:
            _st = starttime
            query = query.filter(Rec.starttime > _st)
        if endtime is not None:
            _et = endtime
            query = query.filter(Rec.endtime < _et)
        return query

    def _search(self, _id=None, name=None, starttime=None,
                endtime=None, page=0, page_size=PAGESIZE):
        self.log.debug(
            "DB: Search => id:%s name:%s starttime:%s endtime=%s" %
            (_id, name, starttime, endtime))

        query = self.get_session().query(Rec)
        query = self._query_generic(query, _id, name, starttime,
                                    endtime)
        query = self._query_page(query, page, page_size)
        self.log.debug("Searching: %s" % str(query))
        ret = query.all()
        return ret

    def get_err(self):
        print("DB error: %s" % (self.err))
        t = self.err
        self.err = ""
        return t


if __name__ == "__main__":
    def printall(queryres):
        for record in queryres:
            print("Record: %s" % record)

    db = RecDB()
    _mytime = datetime(2014, 5, 23, 15, 12, 17)
    _endtime = datetime(2014, 5, 24, 17, 45, 17)

    a = Rec(name="Mimmo1", starttime=_mytime, endtime=_endtime)
    printall(db._search())
    sys.exit("End test job")

    # a = Rec(name="Mimmo1", starttime=_mytime, endtime=None)
    print("Aggiunto", db.add(a))
    printall(db.get_all(page_size=5, page=0))

    print("Mimmo ")
    printall(db._search(name="Mimmo1"))
    print("Search")
    printall(db._search(name="Mimmo1",
                        starttime=datetime(2014, 5, 24, 15, 16, 1) ))
    a = db.get_by_id(5)
    a.start()
    db.delete(1)
    db.delete(2)
    db.delete(4)
    db.delete(1)
    printall( db._search() )
