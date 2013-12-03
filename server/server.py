from datetime import datetime
import logging
from functools import partial

from bottle import Bottle, request, static_file, redirect, abort

from techrec import Rec, RecDB
from processqueue import get_process_queue
from forge import create_mp3
from config_manager import get_config


class RecServer:
    def __init__(self):
        self._app = Bottle()
        self._route()

        self.db = RecDB()

    def _route(self):
        ### This is the API part of the app
        # TODO: move to namespace /api/
        # TODO: create a "sub-application"
        self._app.route('/api/help', callback=self.help)

        self._app.route('/api/create', method="POST", callback=self.create)

        self._app.route('/api/update', method="POST", callback=self.update)
        self._app.route('/api/search', callback=self.search)
        self._app.route('/api/delete', method="POST", callback=self.delete)
        self._app.route('/api/jobs', callback=self.running_jobs)
        self._app.route('/api/jobs/<job_id:int>', callback=self.check_job)

        ## Static part of the site
        self._app.route('/output/<filepath:path>',
                        callback=lambda filepath:
                        static_file(filepath, root=get_config()['OUTPUT_DIR']))
        self._app.route('/static/<filepath:path>',
                        callback=lambda filepath: static_file(filepath,
                                                              root='static/'))
        self._app.route('/', callback=lambda: redirect('/new.html'))
        self._app.route('/new.html',
                        callback=partial(static_file, 'new.html',
                                         root='pages/'))
        self._app.route('/tempo.html',
                        callback=partial(static_file, 'tempo.html',
                                         root='pages/'))

    def create(self):
        req = dict(request.POST.allitems())
        ret = {}
        print "Server:: Create request %s " % req

        starttime = datetime.now()
        recid = starttime.strftime('%s')  # unix timestamp
        name = ""
        endtime = datetime.now()

        print "RECID %s Starttime %s EndTime %s" %\
              (recid, starttime, endtime)
        rec = Rec(name=name,
                  recid=recid,
                  starttime=starttime,
                  endtime=endtime)
        ret = self.db.add(rec)

        return self.rec_msg("Nuova registrazione creata! (id:%d)" % ret.id,
                            rec=rec.serialize())

    def delete(self, recid=None):
        req = dict(request.POST.allitems())
        logging.info("Server: request delete %s " % (req))
        if 'recid' not in req:
            return self.rec_err("No valid ID")

        if self.db.delete(req["recid"]):
            return self.rec_msg("DELETE OK")
        else:
            return self.rec_err("DELETE error: %s" % (self.db.get_err()))

    def update(self):
        req = dict(request.POST.allitems())

        newrec = {}
        if 'starttime' not in req:
            newrec['starttime'] = int(datetime.now().strftime('%s'))
        else:
            newrec['starttime'] = int(req['starttime'])
        if "endtime" not in req:
            newrec['endtime'] = int(datetime.now().strftime('%s'))
        else:
            newrec['endtime'] = int(req['endtime'])

        newrec["name"] = req["name"] if 'name' in req else ''

        # TODO: il filename va dentro al db!
        if not self.db.update(req["recid"], newrec):
            return self.rec_err("Errore Aggiornamento")
        req['filename'] = 'ror-%s-%s' % (req['recid'], newrec['name'])

        # TODO: real ffmpeg job!
        job_id = get_process_queue().submit(
            create_mp3,
            start=datetime.fromtimestamp(newrec['starttime']),
            end=datetime.fromtimestamp(newrec['endtime']),
            outfile=req['filename'])
        print "SUBMITTED: %d" % job_id
        return self.rec_msg("Aggiornamento completato!", job_id=job_id,
                            result='/output/' + req['filename'])

    def check_job(self, job_id):
        try:
            job = get_process_queue().check_job(job_id)
        except ValueError:
            abort(400, 'job_id not valid')

        def ret(status):
            return {'job_status': status, 'job_id': job_id}
        if job is True:
            return ret('DONE')
        if job is False:
            abort(404, 'No such job has ever been spawned')
        else:
            if job.ready():
                try:
                    res = job.get()
                    return res
                except Exception as exc:
                    r = ret('FAILED')
                    r['exception'] = str(exc)
                    return r
            return ret('WIP')

    def running_jobs(self):
        res = {}
        res['last_job_id'] = get_process_queue().last_job_id
        res['running'] = get_process_queue().jobs.keys()
        return res

    def search(self, args=None):
        req = dict()
        req.update(request.GET.allitems())
        print "Search request: %s" % (req)

        values = self.db._search(**req)
        from pprint import pprint
        print "Returned Values %s" % pprint([r.serialize() for r in values])

        ret = {}
        for rec in values:
            ret[rec.recid] = rec.serialize()

        logging.info("Return: %s" % ret)
        return ret

    # @route('/help')
    def help(self):
        return "<h1>help</h1><hr/>\
        <h2>/get, /get/, /get/<recid> </h2>\
        <h3>Get Info about rec identified by RECID </h3>\
        \
        <h2>/search, /search/, /search/<key>/<value></h2>\
        <h3>Search rec that match key/value (or get all)</h3>\
        \
        <h2>/delete/<recid> </h2>\
        <h3>Delete rec identified by RECID </h3>\
        <h2>/update </h2>\
        <h3>Not implemented.</h3>"

    # JSON UTILS
    def rec_msg(self, msg, **kwargs):
        d = {"message": msg, "status": True}
        d.update(kwargs)
        return d

    def rec_err(self, msg):
        return {"error": msg, "status": False}


if __name__ == "__main__":
    get_config().from_pyfile("default_config.py")
    c = RecServer()
    c._app.run(host="localhost", port="8000", debug=True, reloader=True)
