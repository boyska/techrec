import multiprocessing


class JobQueue(object):
    def __init__(self):
        self.pool = multiprocessing.Pool(processes=1)
        self.last_job_id = 0
        self.jobs = {}  # job_id: AsyncResult

    def submit(self, function, *args, **kwargs):
        self.last_job_id += 1
        job_id = self.last_job_id

        def clean_jobs(res):
            '''this callback will remove the job from the queue'''
            del self.jobs[job_id]
        self.jobs[job_id] = self.pool.apply_async(function, args, kwargs,
                                                  clean_jobs)
        return job_id

    def check_job(self, job_id):
        '''
        If the job is running, return the asyncResult.
        If it has already completed, returns True.
        If no such job_id exists at all, returns False
        '''
        if job_id <= 0:
            raise ValueError("non-valid job_id")
        if self.last_job_id < job_id:
            return False
        if job_id in self.jobs:
            return self.jobs[job_id]
        return True

    def join(self):
        self.pool.close()
        self.pool.join()
        self.pool = None


def simulate_long_job(recid=None, starttime=None, endtime=None, name='', filename=None):
    from time import sleep
    print "evviva " + name
    sleep(2)
    print "lavoro su " + name
    sleep(2)
    print "done su " + name
_queue = None


def get_process_queue():
    global _queue
    if _queue is None:
        _queue = JobQueue()
    return _queue

if __name__ == '__main__':
    from datetime import datetime
    n = datetime.now()

    def sleep(n):
        import time
        print "Inizio %d" % n
        time.sleep(n)
        print "Finisco %d" % n
        return n

    get_process_queue().submit(sleep, 3)
    get_process_queue().submit(sleep, 3)
    get_process_queue().join()
    print get_process_queue().jobs
    delta = (datetime.now() - n).total_seconds()
    print delta
    assert 5 < delta < 7
