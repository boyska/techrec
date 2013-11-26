TECHREC
=======

A Python2 web application that assist radio speakers in recording their shows.
At the moment, it relies on some details that are specific of our radio (like
the directory/format of the continous recording).



Implementation details
======================

It is based on bottle, to get a minimal framework. Rest APIs are offered
through it, and the static site uses them.

Create
--------

    JSON = {
            'starttime-rec-1385231288390': '2013/11/23 19:32:49',
            'endtime-rec-1385231288390': '2013/11/23 19:32:49',
            'recid': 'rec-1385231288390',
            'name-rec-1385231288390': 'adasd',
            'op': 'new'
            }

Update
-------

    JSON = {
            'starttime-rec-1385231288390': '2013/11/23 19:32:49',
            'endtime-rec-1385231288390': '2013/11/23 19:32:49',
            'recid': 'rec-1385231288390', ### VALID REC ID
            'name-rec-1385231288390': 'adasd',
            'op': 'update'
            }

Delete
------
    JSON = {
            'recid': 'rec-1385231288390', ### VALID REC ID
            'op': 'delete'
            }
