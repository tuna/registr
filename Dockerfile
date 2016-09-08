FROM python:3.5

RUN apt-get update && \
    apt-get install -y nodejs

RUN mkdir /data/
COPY . /data/

WORKDIR /data/
RUN pip3 install --upgrade pip setuptools && \
    pip3 install -r /data/requirements.txt && \
    pip3 install gunicorn gevent

RUN /data/i18n compile

CMD gunicorn --worker-class=gevent --workers=10 --bind 0.0.0.0 --access-logfile - app:app
