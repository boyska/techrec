import os
import sys
from argparse import ArgumentParser, Action
from datetime import datetime
import logging
logger = logging.getLogger('cli')
CWD = os.getcwd()

import forge
from config_manager import get_config
import server


def pre_check_permissions():

    def is_writable(d):
        return os.access(d, os.W_OK)

    if is_writable(get_config()['AUDIO_INPUT']):
        yield "Audio input '%s' writable" % get_config()['AUDIO_INPUT']
    if not os.access(get_config()['AUDIO_INPUT'], os.R_OK):
        yield "Audio input '%s' unreadable" % get_config()['AUDIO_INPUT']
        sys.exit(10)
    if is_writable(os.getcwd()):
        yield "Code writable"
    if not is_writable(get_config()['AUDIO_OUTPUT']):
        yield "Audio output '%s' not writable" % get_config()['AUDIO_OUTPUT']
        sys.exit(10)


def pre_check_user():
    if os.geteuid() == 0:
        yield "You're running as root; this is dangerous"


class DateTimeAction(Action):
    def __call__(self, parser, namespace, values, option_string=None):
        if len(values) == 15:
            parsed_val = datetime.strptime(values, '%Y%m%d-%H%M%S')
        elif len(values) == 13:
            parsed_val = datetime.strptime(values, '%Y%m%d-%H%M%S')
        else:
            raise ValueError("'%s' is not a valid datetime" % values)
        setattr(namespace, self.dest, parsed_val)


def common_pre():
    prechecks = [pre_check_user, pre_check_permissions]
    configs = ['default_config.py']
    if 'TECHREC_CONFIG' in os.environ:
        for conf in os.environ['TECHREC_CONFIG'].split(':'):
            if not conf:
                continue
            path = os.path.realpath(conf)
            if not os.path.exists(path):
                logger.warn("Configuration file '%s' does not exist; skipping"
                            % path)
                continue
            configs.append(path)
    os.chdir(os.path.dirname(os.path.realpath(__file__)))
    for conf in configs:
        get_config().from_pyfile(conf)

    for check in prechecks:
        for warn in check():
            logging.warn(warn)

if __name__ == "__main__":
    parser = ArgumentParser(description='creates mp3 from live recordings')
    parser.add_argument('--verbose', '-v', action='count',
                        help='Increase verbosity; can be used multiple times')
    sub = parser.add_subparsers(title='subcommands',
                                description='valid subcommands',
                                help='additional help')
    serve_p = sub.add_parser('serve')
    serve_p.set_defaults(func=server.main_cmd)
    forge_p = sub.add_parser('forge')
    forge_p.add_argument('starttime', metavar='FROM', action=DateTimeAction)
    forge_p.add_argument('endtime', metavar='TO', action=DateTimeAction)
    forge_p.add_argument('-o', metavar='OUTFILE', dest='outfile',
                         default='out.mp3', help='Path of the output mp3')
    forge_p.set_defaults(func=forge.main_cmd)

    options = parser.parse_args()
    options.cwd = CWD
    if options.verbose < 1:
        logging.basicConfig(level=logging.WARNING)
    elif options.verbose == 1:
        logging.basicConfig(level=logging.INFO)
    elif options.verbose >= 2:
        logging.basicConfig(level=logging.DEBUG)
    common_pre()
    options.func(options)
