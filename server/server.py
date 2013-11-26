import datetime
import logging

from bottle import Bottle, request, static_file, redirect

from techrec import Rec, RecDB

class RecServer:
    def __init__(self):
        self._app = Bottle()
        self._route()

        self.db = RecDB()


    def _route(self):
        ### This is the API part of the app
        # TODO: move to namespace /api/
        # TODO: create a "sub-application"
        self._app.route('/help', callback=self.help)
        self._app.route('/help/', callback=self.help)

        self._app.route('/create', method="POST", callback=self.create)
        # self._app.post('/create', callback=self.create)

        self._app.route('/update', method="POST", callback=self.update)
        self._app.route('/search', method=["GET", "POST"], callback=self.search)
        self._app.route('/delete', method="POST", callback=self.delete)

        ## Static part of the site
        self._app.route('/static/<filepath:path>',
                        callback= lambda filepath: static_file(filepath, root='static/'))
        self._app.route('/', callback=lambda: redirect('/new.html'))
        self._app.route('/new.html', callback=lambda: static_file('new.html',
            root='pages/'))
        self._app.route('/tempo.html', callback=lambda: static_file('tempo.html',
            root='pages/'))

    def extsearch( self, args ):
        print "ARG", args
        return self.rec_err("EXT")

    """
        CREATE HANDLER
    """
    # @route('/create', method=['OPTIONS','POST'])
    def create(self):
        req = dict( request.POST.allitems() )
        ret = {}
        print "Server:: Create request %s " % req

        starttime = ""
        if req["starttime-" + req["recid"]] != "":
            starttime = datetime.datetime.strptime( req["starttime-"+req["recid"]] , "%Y/%m/%d %H:%M:%S")

        endtime =  datetime.datetime.now()
        if req["endtime-" + req["recid"]] != "":
            endtime = datetime.datetime.strptime( req["endtime-"+req["recid"]] , "%Y/%m/%d %H:%M:%S")


        print "Name %s RECID %s Starttime %s EndTime %s" %(req["name-"+req["recid"]],req["recid"], starttime,endtime )
        ret = self.db.add( Rec(name=req["name-"+req["recid"]],
                        recid=req["recid"],
                        starttime=starttime,
                        endtime=endtime )
                    )

        return self.rec_msg("Nuova registrazione creata! (id:%d)" % ret.id,
                id=ret.id)

    # @route('/active')
    def getactive(self):
        print "GetActive"

    """
        DELETE HANDLER
    """
    # @route('/delete/<recid>') # @route('/delete/<recid>/')
    def delete( self, recid = None ):
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
    def rec_msg(self, msg, **kwargs):
        d = {"message": msg, "status": True}
        d.update(kwargs)
        return d
    def rec_err(self, msg):
        return {"error": msg, "status": False}


    """
     @route('/search') # @route('/search/')  # @route('/search/<key>/<value>')
    """
    def search( self, args=None):
        if request.method == 'GET':
            req  = dict( request.GET.allitems() )
        else:
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

if __name__ == "__main__":
    c = RecServer()
    c._app.run(host="localhost", port="8000", debug=True, reloader=True)
