from datetime import datetime, timedelta

from nose.tools import raises, eq_

from .forge import get_files_and_intervals, get_timefile_exact, round_timefile,\
    get_timefile, mp3_join
from .config_manager import get_config

eight = datetime(2014, 5, 30, 20)
nine = datetime(2014, 5, 30, 21)
ten = datetime(2014, 5, 30, 22)

get_config()['AUDIO_INPUT'] = ''
get_config()['AUDIO_INPUT_FORMAT'] = '%Y-%m/%d/%Y-%m-%d-%H-%M-%S.mp3'
get_config()['FFMPEG_PATH'] = 'ffmpeg'
get_config()['FFMPEG_OUT_CODEC'] = ['-acodec', 'copy']


def minutes(n):
    return timedelta(minutes=n)


def seconds(n):
    return timedelta(seconds=n)

# timefile


def test_timefile_exact():
    eq_(get_timefile_exact(eight),
        '2014-05/30/2014-05-30-20-00-00.mp3')

# Rounding


def test_rounding_similarity():
    eq_(round_timefile(eight), round_timefile(eight+minutes(20)))
    assert round_timefile(eight) != round_timefile(nine)


def test_rounding_value():
    eq_(round_timefile(eight), eight)
    eq_(round_timefile(eight + minutes(20)), eight)


# Rounding + timefile


def test_timefile_alreadyround():
    eq_(get_timefile(eight),
        '2014-05/30/2014-05-30-20-00-00.mp3')


def test_timefile_toround():
    eq_(get_timefile(eight + minutes(20)),
        '2014-05/30/2014-05-30-20-00-00.mp3')

# Intervals


@raises(ValueError)
def test_intervals_same():
    tuple(get_files_and_intervals(eight, eight))


@raises(ValueError)
def test_intervals_before():
    tuple(get_files_and_intervals(nine, eight))


def test_intervals_full_1():
    res = list(get_files_and_intervals(eight, nine-seconds(1)))
    eq_(len(res), 1)
    eq_(res[0][1], 0)
    eq_(res[0][2], 0)


def test_intervals_partial_1():
    res = list(get_files_and_intervals(eight, nine-minutes(10)))
    eq_(len(res), 1)
    eq_(res[0][1], 0)
    eq_(res[0][2], 10*60 - 1)


def test_intervals_exact_2():
    res = list(get_files_and_intervals(eight, nine))
    eq_(len(res), 2)
    eq_(res[0][1], 0)
    eq_(res[0][2], 0)
    eq_(res[1][1], 0)
    eq_(res[1][2], 3599)


def test_intervals_partial_2():
    res = list(get_files_and_intervals(eight, nine + minutes(50)))
    eq_(len(res), 2)
    eq_(res[0][1], 0)
    eq_(res[0][2], 0)
    eq_(res[1][1], 0)
    eq_(res[1][2], 599)


def test_intervals_full_2():
    res = list(get_files_and_intervals(eight,
                                       nine + minutes(59) + seconds(59)))
    eq_(len(res), 2)
    eq_(res[0][1], 0)
    eq_(res[0][2], 0)
    eq_(res[1][1], 0)
    eq_(res[1][2], 0)


def test_intervals_exact_3():
    res = list(get_files_and_intervals(eight, ten))
    eq_(len(res), 3)
    eq_(res[0][1], 0)
    eq_(res[0][2], 0)
    eq_(res[1][1], 0)
    eq_(res[1][2], 0)
    eq_(res[2][1], 0)
    eq_(res[2][2], 3599)


def test_intervals_partial_3():
    res = list(get_files_and_intervals(eight, ten+minutes(50)))
    eq_(len(res), 3)
    eq_(res[0][1], 0)
    eq_(res[0][2], 0)
    eq_(res[1][1], 0)
    eq_(res[1][2], 0)
    eq_(res[2][1], 0)
    eq_(res[2][2], 599)


def test_intervals_full_3():
    res = list(get_files_and_intervals(eight, ten+minutes(59) + seconds(59)))
    eq_(len(res), 3)
    eq_(res[0][1], 0)
    eq_(res[0][2], 0)
    eq_(res[1][1], 0)
    eq_(res[1][2], 0)
    eq_(res[2][1], 0)
    eq_(res[2][2], 0)


def test_intervals_middle_1():
    res = list(get_files_and_intervals(eight + minutes(20),
                                       nine - minutes(20)))
    eq_(len(res), 1)
    eq_(res[0][1], 20*60)
    eq_(res[0][2], 20*60-1)


def test_intervals_left_2():
    res = list(get_files_and_intervals(eight+minutes(30), nine))
    eq_(len(res), 2)
    eq_(res[0][1], 30*60)
    eq_(res[0][2], 0)
    eq_(res[1][1], 0)
    eq_(res[1][2], 3599)

# MP3 Join


def test_mp3_1():
    eq_(' '.join(mp3_join((('a', 0, 0),))),
        'ffmpeg -i concat:a -acodec copy')


def test_mp3_1_left():
    eq_(' '.join(mp3_join((('a', 160, 0),))),
        'ffmpeg -i concat:a -acodec copy -ss 160')


def test_mp3_1_right():
    eq_(' '.join(mp3_join((('a', 0, 1600),))),
        'ffmpeg -i concat:a -acodec copy -t 2000')


def test_mp3_1_leftright():
    eq_(' '.join(mp3_join((('a', 160, 1600),))),
        'ffmpeg -i concat:a -acodec copy -ss 160 -t 1840')


def test_mp3_2():
    eq_(' '.join(mp3_join((('a', 0, 0), ('b', 0, 0)))),
        'ffmpeg -i concat:a|b -acodec copy')


def test_mp3_2_leftright():
    eq_(' '.join(mp3_join((('a', 1000, 0), ('b', 0, 1600)))),
        'ffmpeg -i concat:a|b -acodec copy -ss 1000 -t 4600')
