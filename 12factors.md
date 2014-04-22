techrec tries to follow [The Twelve Factors](http://12factor.net/), but it's
still not perfect

 * **Codebase**: YES
 * **Dependencies**: YES, ffmpeg must be done manually
 * **Config**: ALMOST: the environment contains the path for the config file
 * **Backing services**: there are none, so YES
 * **Build, release, run**: YES
 * **Processes**: ALMOST; the process are not completely stateless, as the job
dispatcher is in them
 * **Port binding**: YES
 * **Concurrency**: NO; as in Processes, the job dispatcher is a violation
 * **Disposability**: YES
 * **Dev/prod parity**: YES
 * **Logs**: YES; but accesslog is written to stderr
 * **Admin processes**: YES, using cli.py


vim: set ft=markdown:
