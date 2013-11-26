# from bottle import hook, response, route, run, static_file, request
import datetime
import logging

from bottle import Bottle, hook, response, request,static_file

from techrec import Rec, RecDB

class RecServer:
    def __init__(self,host="127.0.0.1", port=8000):
        self._host = host
        self._port = port

        self._app = Bottle()
        self._route()

        self.db = RecDB()

    def start(self):
        self._app.run(host=self._host, port=self._port, debug=True)

    @hook('after_request')
    def enable_cors(self):
        #These lines are needed for avoiding the "Access-Control-Allow-Origin" errors
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'PUT, GET, POST, DELETE, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token'

    def _route(self):
        self._app.route('/favicon.ico', callback=self.favicon)
        self._app.route('/help', callback=self.help)
        self._app.route('/help/', callback=self.help)

        self._app.route('/create', method="POST", callback=self.create)
        # self._app.post('/create', callback=self.create)

        self._app.route('/update', method="POST", callback=self.update)
        self._app.route('/search', method="POST", callback=self.search)
        self._app.route('/delete', method="POST", callback=self.delete)
        self._app.route('/static/<filepath:path>',
                        callback= lambda filepath: static_file(filepath, root='static/'))
        self._app.route('/js/<f>',
                        callback= lambda f: static_file(f, root='static/js/'))
        self._app.route('/css/<f>',
                        callback= lambda f: static_file(f, root='static/css/'))
        self._app.route('/img/<f>',
                        callback= lambda f: static_file(f, root='static/img/'))
        self._app.route('/', callback=lambda: static_file('index.html',
            root='pages/'))
        self._app.route('/tempo', callback=lambda: static_file('tempo.html',
            root='pages/'))

    def extsearch( self, args ):
        print "ARG", args
        return self.rec_err("EXT")

    """
        CREATE HANDLER
    """
    # @route('/create', method=['OPTIONS','POST'])
    def create(self):
        self.enable_cors()
        req = dict( request.POST.allitems() )
        ret = {}
        print "Server:: Create request %s " % req

        starttime = ""
        if req["starttime-"+req["recid"]] != "":
            starttime = datetime.datetime.strptime( req["starttime-"+req["recid"]] , "%Y/%m/%d %H:%M:%S")

        endtime =  datetime.datetime.now()
        if req["endtime-"+req["recid"]] != "":
            endtime = datetime.datetime.strptime( req["endtime-"+req["recid"]] , "%Y/%m/%d %H:%M:%S")


        print "Name %s RECID %s Starttime %s EndTime %s" %(req["name-"+req["recid"]],req["recid"], starttime,endtime )
        ret = self.db.add( Rec(name=req["name-"+req["recid"]],
                        recid=req["recid"],
                        starttime=starttime,
                        endtime=endtime )
                    )

        return { "msg": "Nuova registrazione aggiunta", }
        return self.rec_msg("Nuova registrazione creata! (id:" + ret.id *")")

    # @route('/active')
    def getactive(self):
        print "GetActive"

    """
        DELETE HANDLER
    """
    # @route('/delete/<recid>') # @route('/delete/<recid>/')
    def delete( self, recid = None ):
        self.enable_cors()
        req = dict( request.POST.allitems() )
        logging.info("Server: request delete %s " % ( req ) )
        if not req.has_key( "recid" ):
            return self.rec_err("No valid ID")

        if self.db.delete( req["recid"] ):
            return self.rec_msg("DELETE OK")
        else:
            return self.rec_err("DELETE error: %s" % (self.db.get_err()))

    """
        UPDATE HANDLER
    """
    # @route('/delete/<recid>') # @route('/delete/<recid>/')
    def update( self ):
        self.enable_cors()
        req  = dict( request.POST.allitems() )

        ret={}
        ret["starttime"]    = req ["starttime-"+req["recid"]]
        ret["endtime"]      = req["endtime-"+req["recid"]]
        ret["name"]         = req["name-"+req["recid"]]

        if self.db.update( req["recid"], ret ):
            return self.rec_msg("Aggiornamento completato!");
        else:
            return self.rec_err("Errore Aggiornamento");

    """
        JSON' RESPONDER
    """
    def rec_msg(self, msg): return self.rec_xerr("message", msg)
    def rec_err(self, msg): return self.rec_xerr("error", msg)
    def rec_xerr(self,_type,_msg): return { _type : _msg }


    """
     @route('/search') # @route('/search/')  # @route('/search/<key>/<value>')
    """
    def search( self, args=None):
        self.enable_cors()

        req  = dict( request.POST.allitems() )
        print "Search request: %s" % (req)

        name = "%s" % req["name"]
        if req["name"] == "": name = None

        starttime = req["starttime"]
        if req["starttime"] == "": starttime = None

        endtime = req["endtime"]
        if req["endtime"] == "": endtime = None

        recid = req["recid"]
        if req["recid"]== "": recid = None

        active = True

        values =  self.db._search(recid=recid,name=name, starttime=starttime, endtime=endtime,active=active)
        print "Returned Values %s" % values
        ret = {}
        for rec in values:
            recid = "rec-" + str(rec.id)

            ret [recid] = {}
            ret [recid]["name"] = rec.name
            ret [recid]["id"] = rec.id
            ret [recid]["recid"] = rec.recid
            ret [recid]["starttime"] = rec.starttime.strftime("%Y-%m-%d-%H-%H-%s")
            if rec.endtime != None:
                ret [recid]["endtime"] = rec.endtime.strftime("%Y-%m-%d-%H-%H-%s")

            ret [recid]["active"] =  rec.active

        logging.info("Return: %s" % ret);
        return ret

    # @route('/favicon.ico')
    def favicon(self):
        return static_file('icon.ico', root="/static/img/", mimetype="image/ico")

    # @route('/help')
    def help(self):
        return " <h1>help</h1><hr/>\
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

"""
    TESTs
"""
if __name__ == "__main__":
    c = RecServer(host="localhost")
    c.start()
