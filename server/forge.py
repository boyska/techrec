from datetime import datetime, timedelta
from time import sleep
import os
from subprocess import Popen

from config_manager import get_config


def get_timefile_exact(time):
    '''
    time is of type `datetime`; it is not "rounded" to match the real file;
    that work is done in get_timefile(time)
    '''
    return os.path.join(
        get_config()['AUDIO_INPUT'],
        time.strftime('%Y-%m/%d/rec-%Y-%m-%d-%H-%M-%S-ror.mp3')
        )


def round_timefile(exact):
    '''
    This will round the datetime, so to match the file organization structure
    '''
    return datetime(exact.year, exact.month, exact.day, exact.hour)


def get_timefile(exact):
    return get_timefile_exact(round_timefile(exact))


def get_files_and_intervals(start, end, rounder=round_timefile):
    '''
    both arguments are datetime objects
    returns an iterator whose elements are (filename, start_cut, end_cut)
    Cuts are expressed in seconds
    '''
    if end <= start:
        raise ValueError("end < start!")

    while start <= end:
        begin = rounder(start)
        start_cut = (start - begin).total_seconds()
        if end < begin + timedelta(seconds=3599):
            end_cut = (begin + timedelta(seconds=3599) - end).total_seconds()
        else:
            end_cut = 0
        yield (begin, start_cut, end_cut)
        start = begin + timedelta(hours=1)


def mp3_join(named_intervals, target):
    '''
    Note that these are NOT the intervals returned by get_files_and_intervals,
    as they do not supply a filename, but only a datetime.
    What we want in input is basically the same thing, but with get_timefile()
    applied on the first element

    This function make the (quite usual) assumption that the only start_cut (if
    any) is at the first file, and the last one is at the last file
    '''
    ffmpeg = 'ffmpeg'  # binary name
    startskip = None
    endskip = None
    files = []
    for (filename, start_cut, end_cut) in named_intervals:
        # this happens only one time, and only at the first iteration
        if start_cut:
            assert startskip is None
            startskip = start_cut
        # this happens only one time, and only at the first iteration
        if end_cut:
            assert endskip is None
            endskip = end_cut
        assert '|' not in filename
        files.append(filename)

    cmdline = [ffmpeg, '-i', 'concat:%s' % '|'.join(files), '-acodec',
               'copy']
    if startskip is not None:
        cmdline += ['-ss', str(startskip)]
    if endskip is not None:
        cmdline += ['-t', str(len(files)*3600 - (startskip + endskip))]
    cmdline += [target]
    cmdline += ['-loglevel', 'warning']
    return cmdline


def create_mp3(start, end, outfile, options={}, **kwargs):
    p = Popen(mp3_join([(get_timefile(begin), start_cut, end_cut)
                        for begin, start_cut, end_cut
                        in get_files_and_intervals(start, end)],
                       outfile))
    if get_config()['FORGE_TIMEOUT'] == 0:
        p.wait()
    else:
        start = datetime.now()
        while (datetime.now() - start).total_seconds() < \
               get_config()['FORGE_TIMEOUT']:
            p.poll()
            if p.returncode is None:
                sleep(1)
            else:
                break
    if p.returncode is None:
        os.kill(p.pid, 15)
        try:
            os.remove(outfile)
        except:
            pass
        raise Exception('timeout')  # TODO: make a specific TimeoutError
    if p.returncode != 0:
        raise OSError("return code was %d" % p.returncode)
    return True

def main_cmd(options):
    create_mp3(options.starttime, options.endtime, options.outfile)
