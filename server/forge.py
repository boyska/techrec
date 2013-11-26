from datetime import datetime, timedelta


def get_timefile_exact(time):
    '''
    time is of type `datetime`; it is not "rounded" to match the real file;
    that work is done in get_timefile(time)
    '''
    return time.strftime('%Y-%m/%d/rec-%Y-%m-%d-%H-%M-%S-ror.mp3')


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
    print '%s < %s' % (start, end)
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


def mp3_join(named_intervals):
    '''
    Note that these are NOT the intervals returned by get_files_and_intervals,
    as they do not supply a filename, but only a datetime.
    What we want in input is basically the same thing, but with get_timefile()
    applied on the first element
    '''
    for (filename, start_cut, end_cut) in named_intervals:
        pass
    raise NotImplementedError()
