==========================================
    techrec
==========================================


--------
 Client
--------

The Client is a JS script that exchange data with server via JSON

--------
 Server
--------

The Server is a python software and uses the bottle library to implements a web 
services 


Data Format
===================================

--------
 Create 
--------
JSON = {
        'starttime-rec-1385231288390': '2013/11/23 19:32:49', 
        'endtime-rec-1385231288390': '2013/11/23 19:32:49', 
        'recid': 'rec-1385231288390', 
        'name-rec-1385231288390': 'adasd',
        'op': 'new'
        }

--------
Retrieve
--------


--------
 Update
-------- 

JSON = {
        'starttime-rec-1385231288390': '2013/11/23 19:32:49', 
        'endtime-rec-1385231288390': '2013/11/23 19:32:49', 
        'recid': 'rec-1385231288390', ### VALID REC ID 
        'name-rec-1385231288390': 'adasd',
        'op': 'update'
        }
        
--------
 Delete
--------
JSON = {
        'recid': 'rec-1385231288390', ### VALID REC ID 
        'op': 'delete'
        }

BUG
Da Salva button lo stato non va. Per il resto sembra funzionare.

