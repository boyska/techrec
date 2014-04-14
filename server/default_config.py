HOST = 'localhost'
PORT = '8000'
WSGI_SERVER = 'paste'
WSGI_SERVER_OPTIONS = {}

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
