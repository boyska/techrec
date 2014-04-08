import sys
import logging

from sqlalchemy import inspect

from config_manager import get_config
from techrec import RecDB

def cleanold_cmd(options):
    log = logging.getLogger('cleanold')
    log.debug("starting cleanold[%d]" % options.minage)
    db = RecDB(get_config()['DB_URI'])
    res = db.get_not_completed(options.minage*3600*24)
    count = len(res)
    if options.pretend:
        for rec in res:
            print rec
    else:
        for rec in res:
            logging.info("Deleting " + str(rec))
            s = inspect(rec).session
            s.delete(rec)
            s.commit()
        logging.info("Cleanold complete: %d deleted" % count)
    sys.exit(0)

# vim: set ai ts=4 sw=4 et:
