HOST = 'localhost'
PORT = '8000'
WSGI_SERVER = 'wsgiref'
WSGI_SERVER_OPTIONS = {}
### Beware: we use global objects (the processqueue); you can't use
### worker_class=sync in gunicorn, and probably other similar deployment won't
### work
### A dirty check is:
### * go to /old.html
### * create something
### * go to /api/jobs
### * refresh a lot and see if the result is always the same
#WSGI_SERVER = 'gunicorn'
#WSGI_SERVER_OPTIONS = {'workers': 4, 'worker_class': 'eventlet' }

DEBUG = True
DB_URI = 'sqlite:///techrec.db'
AUDIO_OUTPUT = 'output/'
AUDIO_INPUT = 'rec/'
AUDIO_INPUT_FORMAT = '%Y-%m/%d/rec-%Y-%m-%d-%H-%M-%S.mp3'
AUDIO_OUTPUT_FORMAT = 'techrec-%(time)s-%(name)s.mp3'
FORGE_TIMEOUT = 20
FORGE_MAX_DURATION = 3600*5
FFMPEG_OPTIONS = ['-loglevel', 'warning', '-n']
FFMPEG_PATH = 'ffmpeg'
