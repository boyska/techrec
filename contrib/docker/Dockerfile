FROM saucy

RUN DEBIAN_FRONTEND=noninteractive apt-get update
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends
python python3 python-virtualenv
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends
python-pip
# e virtualenv3?? a me virtualenvwrapper fa un po' schifo...
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends
virtualenvwrapper

RUN git clone https://github.com/boyska/techrec.git /opt/techrec
RUN virtualenv --python=python2 /opt/virtualenv
RUN /opt/virtualenv/bin/pip install -r /opt/techrec/server/requirements.txt
RUN mkdir /opt/db
RUN chown nobody /opt/db

ENV TECHREC_CONFIG /opt/techrec/conf.py
USER nobody
WORKDIR /opt/techrec/server

ADD conf.py /opt/techrec/
