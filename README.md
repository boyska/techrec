TechRec
=======

A Python2 web application that assist radio speakers in recording their shows.
Meant to be simple to install and to maintain.

It basically takes a directory with the continuous recording and create new
files "cutting/pasting" with ffmpeg.

Features
=========

* The interface is extremely simple to use
* You can have nested recording (ie: to record an interview inside of a whole
  show)
* There is no user system: any user opening the website will see the complete
  status of the applications. There is, also, nothing stored in cookie or
  similar mechanisms. This means that recording a session does not require a
  browser to remain open, or any kind of persistence client-side: server-side
  does it all. It also means that authorization must be done on another layer
  (for example, your webserver could add a Basic Auth)

Implementation details
======================

It is based on bottle, to get a minimal framework. Simple APIs are offered
through it, and the static site uses them.

Jobs are not dispatched using stuff like celery, but with a thin wrapper over
`multiprocessing.Pool`; this is just to keep the installation as simple as
possible.

The encoding part is delegated to `ffmpeg`, but the code is really modular so
changing this is a breeze.
