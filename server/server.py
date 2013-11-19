# from bottle import hook, response, route, run, static_file, request
from bottle import Bottle, hook, template, response, request,static_file
import json
import socket

from techrec import * 

class RecServer:
    def __init__(self,host="127.0.0.1", port=8000):
        self._host = host
        self._port = port

        self._app = Bottle()
        self._route()

        self.db = RecDB()

    def start(self):
        self._app.run(host=self._host, port=self._port)

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
        self._app.post('/create', callback=self.create)        
                
        # self._app.route('/get', method="GET", callback=self.getrec)        
        # self._app.route('/get/', method="GET", callback=self.getrec)        
        # self._app.route('/get/<recid>', method="GET", callback=self.getrec)        
        
        self._app.route('/search', method="POST", callback=self.search)        
        # self._app.route('/search/', method="POST", callback=self.search)        
        # self._app.route('/search/<recid>', method="POST", callback=self.search)        
        # self._app.route('/oldsearch/<key>/<value>', method="POST", callback=self.search)        
        # self._app.route('/search/<args:path>', method="POST", callback=self.search)

        self._app.route('/delete/<recid>', method="GET", callback=self.delete)
        self._app.route('/delete/<recid>/', method="GET", callback=self.delete)
        
    def extsearch( self, args ):
        print "ARG", args
        return self.rec_err("EXT")
        
    # @route('/create', method=['OPTIONS','POST'])
    def create(self):
        self.enable_cors()
        req = dict( request.POST.allitems() )
        ret = {}
        print "REQ", req
        if req["starttime-"+req["recid"]] != "":
            starttime = datetime.datetime.strptime( req["starttime-"+req["recid"]] , "%Y/%m/%d %H:%M:%S")
        else:
            starttime = ""

        if req["endtime-"+req["recid"]] != "":
            endtime = datetime.datetime.strptime( req["endtime-"+req["recid"]] , "%Y/%m/%d %H:%M:%S")
        else:
            endtime = ""
            
        self.db.add( Rec(name=req["name-"+req["recid"]], 
            starttime=starttime,
            endtime=endtime ) 
            )

        return { "msg": "Nuova registrazione aggiunta" }
   
    # @route('/active')
    def getactive(self):
        print "GetActive"

    # @route('/delete/<recid>') # @route('/delete/<recid>/')
    def delete( self, recid = None ):
        if not recid:
            self.rec_err("No recid!")
        self.rec_err("Delete")
        
    def rec_err(self, msg):
        return { "error": msg }


    """
     @route('/search') # @route('/search/')  # @route('/search/<key>/<value>')
    """
    def search( self, args=None):
        self.enable_cors()

        req  = dict( request.POST.allitems() )

        name = req["name"]
        if req["name"] == "": name = None
        starttime = req["starttime"]
        if req["starttime"] == "": name = None
        endtime = req["endtime"]
        if req["endtime"] == "": endtime = None
            
        values =  self.db._search(name=name, starttime=starttime, endtime=endtime)
        ret = {}
        for rec in values:
            recid = "rec-" + str(rec.id) 
            
            ret [recid] = {}
            ret [recid]["name"] = rec.name
            ret [recid]["starttime"] = rec.starttime.strftime("%Y-%m-%d-%H-%H-%s")
            if rec.endtime != None:
                ret [recid]["endtime"] = rec.endtime.strftime("%Y-%m-%d-%H-%H-%s")
            else:
                rec.endtime = ""
                
            ret [recid]["state"] =  rec.state
            
        # print "RET ", ret 
        """
        print "VALUES ", values
        print type(self.rec_err("sdiaso")), " - " , type(values)
        print "ERR" , self.rec_err("sdiaso")"""
        logging.info("Return: %s" % ret);
        return ret
                
    # @route('/favicon.ico')
    def favicon(self):
        return static_file('icon.ico', root="./img/", mimetype="image/ico")

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
    c = RecServer(host="0.0.0.0")
    c.start()
