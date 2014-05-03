Target of this file is the system administrator that is upgrading techrec
Purpose of this file is making clear what changes need to be done to
configuration or deployment for techrec to work well

* Added `TAG_EXTRA` option
  suggested keys for TAG_EXTRA are `CREATOR`, `PUBLISHER`, `CONTACT`
* Added `TAG_LICENSE_URI` option
  It should be a link to a license. For example: 
  http://creativecommons.org/publicdomain/zero/1.0/
  Note that if you don't set TAG_LICENSE_URI, there will be no RIGHTS-DATE tag
* Added `TRANSLOGGER_OPTS` to configure `pastelog`.
* `WSGI_SERVER` default changed to `pastelog`. There should not be any issue
  with this change


vim: set ft=markdown tw=79:
