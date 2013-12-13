import os
from datetime import datetime
import logging
logger = logging.getLogger('server')
from functools import partial

from bottle import Bottle, request, static_file, redirect, abort, response

from techrec import Rec, RecDB
from processqueue import get_process_queue
from forge import create_mp3
from config_manager import get_config


def date_read(s):
    return datetime.fromtimestamp(int(s))


def date_write(dt):
    return dt.strftime('%s')


def rec_sanitize(rec):
    d = rec.serialize()
    d['starttime'] = date_write(d['starttime'])
    d['endtime'] = date_write(d['endtime'])
    return d


class DateApp(Bottle):
    '''
    This application will expose some date-related functions; it is intended to
    be used when you need to know the server's time on the browser
    '''
    def __init__(self):
        Bottle.__init__(self)
        self.route('/help', callback=self.help)
        self.route('/date', callback=self.date)
        self.route('/custom', callback=self.custom)

    def date(self):
        n = datetime.now()
        return {
            'unix': n.strftime('%s'),
            'isoformat': n.isoformat(),
            'ctime': n.ctime()
        }

    def custom(self):
        n = datetime.now()
        if 'strftime' not in request.query:
            abort(400, 'Need argument "strftime"')
        response.content_type = 'text/plain'
        return n.strftime(request.query['strftime'])

    def help(self):
        response.content_type = 'text/plain'
        return \
            '/date : get JSON dict containing multiple formats of now()\n' + \
            '/custom?strftime=FORMAT : get now().strftime(FORMAT)'


class RecAPI(Bottle):
    def __init__(self):
        Bottle.__init__(self)
        self._route()
        self.db = RecDB(get_config()['DB_URI'])

    def _route(self):
        self.post('/create', callback=self.create)
        self.post('/delete', callback=self.delete)
        self.post('/update/<recid:int>', callback=self.update)
        self.post('/generate', callback=self.generate)
        self.get('/help', callback=self.help)
        self.get('/', callback=self.help)
        self.get('/get/search', callback=self.search)
        self.get('/get/ongoing', callback=self.get_ongoing)
        self.get('/jobs', callback=self.running_jobs)
        self.get('/jobs/<job_id:int>', callback=self.check_job)

    def create(self):
        req = dict(request.POST.allitems())
        ret = {}
        print "Server:: Create request %s " % req

        starttime = datetime.now()
        name = ""
        endtime = datetime.now()

        print "Starttime %s EndTime %s" %\
              (starttime, endtime)
        rec = Rec(name=name,
                  starttime=starttime,
                  endtime=endtime)
        ret = self.db.add(rec)

        return self.rec_msg("Nuova registrazione creata! (id:%d)" % ret.id,
                            rec=rec_sanitize(rec))

    def delete(self):
        req = dict(request.POST.allitems())
        logging.info("Server: request delete %s " % (req))
        if 'id' not in req:
            return self.rec_err("No valid ID")

        if self.db.delete(req["id"]):
            return self.rec_msg("DELETE OK")
        else:
            return self.rec_err("DELETE error: %s" % (self.db.get_err()))

    def update(self, recid):
        req = dict(request.POST.allitems())

        newrec = {}
        now = datetime.now()
        if 'starttime' not in req:
            newrec['starttime'] = now
        else:
            newrec['starttime'] = date_read(req['starttime'])
        if "endtime" not in req:
            newrec['endtime'] = now
        else:
            newrec['endtime'] = date_read(req['endtime'])
        if 'name' in req:
            newrec["name"] = req["name"]

        try:
            logger.info("prima di update")
            result_rec = self.db.update(recid, newrec)
            logger.info("dopo update")
        except Exception as exc:
            return self.rec_err("Errore Aggiornamento", exception=exc)
        return self.rec_msg("Aggiornamento completato!",
                            rec=rec_sanitize(result_rec))

    def generate(self):
        # prendiamo la rec in causa
        recid = dict(request.POST.allitems())['id']
        rec = self.db._search(_id=recid)[0]
        if rec.filename is not None and os.path.filename.exists(rec.filename):
            return {'status': 'ready',
                    'message': 'The file has already been generated at %s' %
                    rec.filename,
                    'rec': rec
                    }
        rec.filename = 'ror-%s-%s.mp3' % \
                       (rec.starttime.strftime('%y%m%d_%H%M'),
                        filter(lambda c: c.isalpha(), rec.name))
        self.db.update(rec.id, rec.serialize())
        job_id = get_process_queue().submit(
            create_mp3,
            start=rec.starttime,
            end=rec.endtime,
            outfile=os.path.join(get_config()['AUDIO_OUTPUT'], rec.filename))
        print "SUBMITTED: %d" % job_id
        return self.rec_msg("Aggiornamento completato!",
                            job_id=job_id,
                            result='/output/' + rec.filename,
                            rec=rec_sanitize(rec))

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
        logger.debug("Returned Values %s" %
                     pprint([r.serialize() for r in values]))

        ret = {}
        for rec in values:
            ret[rec.id] = rec_sanitize(rec)

        logging.info("Return: %s" % ret)
        return ret

    def get_ongoing(self):
        return {rec.id: rec_sanitize(rec)
                for rec in self.db.get_ongoing()}

    # @route('/help')
    def help(self):
        return "<h1>help</h1><hr/>\
        <h2>/get, /get/, /get/<id> </h2>\
        <h3>Get Info about rec identified by ID </h3>\
        \
        <h2>/search, /search/, /search/<key>/<value></h2>\
        <h3>Search rec that match key/value (or get all)</h3>\
        \
        <h2>/delete/<id> </h2>\
        <h3>Delete rec identified by ID </h3>\
        <h2>/update </h2>\
        <h3>Not implemented.</h3>"

    # JSON UTILS

    def rec_msg(self, msg, status=True, **kwargs):
        d = {"message": msg, "status": status}
        d.update(kwargs)
        return d

    def rec_err(self, msg, **kwargs):
        return self.rec_msg(msg, status=False, **kwargs)


class RecServer:
    def __init__(self):
        self._app = Bottle()
        self._route()

        self.db = RecDB(get_config()['DB_URI'])

    def _route(self):
        ### This is the API part of the app
        # TODO: move to namespace /api/
        # TODO: create a "sub-application"

        ## Static part of the site
        self._app.route('/output/<filepath:path>',
                        callback=lambda filepath:
                        static_file(filepath,
                                    root=get_config()['AUDIO_OUTPUT']))
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

def pre_check_permissions():
    import sys

    def is_writable(d):
        return os.access(d, os.W_OK)

    if is_writable(get_config()['AUDIO_INPUT']):
        yield "Audio input '%s' writable" % get_config()['AUDIO_INPUT']
    if not os.access(get_config()['AUDIO_INPUT'], os.R_OK):
        yield "Audio input '%s' unreadable" % get_config()['AUDIO_INPUT']
        sys.exit(1)
    if is_writable(os.getcwd()):
        yield "Code writable"
    if not is_writable(get_config()['AUDIO_OUTPUT']):
        yield "Audio output '%s' not writable" % get_config()['AUDIO_OUTPUT']
        sys.exit(1)

def pre_check_user():
    if os.geteuid() == 0:
        yield "You're running as root; this is dangerous"

if __name__ == "__main__":
    prechecks=[pre_check_user, pre_check_permissions]
    configs = ['default_config.py']
    if 'TECHREC_CONFIG' in os.environ:
        for conf in os.environ['TECHREC_CONFIG'].split(':'):
            if not conf:
                continue
            path = os.path.realpath(conf)
            if not os.path.exists(path):
                logger.warn("Configuration file '%s' does not exist; skipping"
                            % path)
                continue
            configs.append(path)
    os.chdir(os.path.dirname(os.path.realpath(__file__)))
    for conf in configs:
        get_config().from_pyfile(conf)

    for check in prechecks:
        for warn in check():
            logging.warn(warn)
    c = RecServer()
    c._app.mount('/date', DateApp())
    c._app.mount('/api', RecAPI())
    c._app.run(host=get_config()['HOST'], port=get_config()['PORT'],
               debug=get_config()['DEBUG'])
