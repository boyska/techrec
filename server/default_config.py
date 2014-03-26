HOST = 'localhost'
PORT = '8000'
WSGI_SERVER = 'wsgiref'
WSGI_SERVER_OPTIONS = {}
#WSGI_SERVER = 'gunicorn'
#WSGI_SERVER_OPTIONS = {'workers': 4, 'worker_class': 'eventlet'}

DEBUG = True
DB_URI = 'sqlite:///techrec.db'
AUDIO_OUTPUT = 'output/'
AUDIO_INPUT = 'rec/'
AUDIO_INPUT_FORMAT = '%Y-%m/%d/rec-%Y-%m-%d-%H-%M-%S.mp3'
AUDIO_OUTPUT_FORMAT = 'techrec-%(time)s-%(name)s.mp3'
FORGE_TIMEOUT = 20
FORGE_MAX_DURATION = 3600*5
FFMPEG_OPTIONS = ['-loglevel', 'warning', '-n']
