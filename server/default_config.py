import logging
HOST = 'localhost'
PORT = '8000'
# pastelog is just "paste", but customized to accept logging options
WSGI_SERVER = 'pastelog'
# these are pastelog-specific options for logging engine
TRANSLOGGER_OPTS = {
        'logger_name': 'accesslog',
        'set_logger_level': logging.WARNING,
        'setup_console_handler': False }
WSGI_SERVER_OPTIONS = {}

DEBUG = True
DB_URI = 'sqlite:///techrec.db'
AUDIO_OUTPUT = 'output/'
AUDIO_INPUT = 'rec/'
AUDIO_INPUT_FORMAT = '%Y-%m/%d/rec-%Y-%m-%d-%H-%M-%S.mp3'
AUDIO_OUTPUT_FORMAT = 'techrec-%(startdt)s-%(endtime)s-%(name)s.mp3'
FORGE_TIMEOUT = 20
FORGE_MAX_DURATION = 3600*5
FFMPEG_OUT_CODEC = ['-acodec', 'copy']
FFMPEG_OPTIONS = ['-loglevel', 'warning', '-n']
FFMPEG_PATH = 'ffmpeg'
# tag:value pairs
TAG_EXTRA = {}
# LICENSE URI is special because date need to be added
TAG_LICENSE_URI = None

STATIC_FILES='static/'
STATIC_PAGES='pages/'
try:
    from pkg_resources import resource_filename, resource_isdir
    if resource_isdir('techrec', 'pages'):
        STATIC_PAGES = resource_filename('techrec', 'pages')
        STATIC_FILES = resource_filename('techrec', 'static')
    else:
        print "invece dice", resource_filename('techrec', 'static')
except ImportError:
    logging.exception("Error loading resources from installed part")
