FROM python:3.5

RUN useradd registr

RUN apt-get update && \
    apt-get install -y nodejs

RUN mkdir /data/
COPY . /data/

WORKDIR /data/
RUN pip3 install --upgrade pip setuptools && \
    pip3 install -r /data/requirements.txt && \
    pip3 install gunicorn gevent


RUN touch /data/registration-2016-fall.db && \
    chown registr /data/registration-2016-fall.db

RUN mkdir -p /data/pics && \
    chown -R registr /data/pics

RUN chown -R registr /data/translations

USER registr

RUN /data/i18n compile

CMD gunicorn --worker-class=gevent --workers=10 --bind 0.0.0.0 --access-logfile - app:app
