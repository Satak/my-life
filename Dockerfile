FROM alpine:3.7

RUN apk add --no-cache build-base=0.5-r0 && \
    apk add --no-cache python3=3.6.3-r9 python3-dev=3.6.3-r9 postgresql-dev=10.3-r0 && \
    pip3 install --upgrade pip && pip3 install virtualenv==15.2.0 && \
    apk add --no-cache curl=7.59.0-r0

COPY ["requirements.txt", "src/", "/srv/"]
RUN virtualenv /srv/env && \
    /srv/env/bin/pip install -r /srv/requirements.txt

WORKDIR /srv
EXPOSE 8080
USER nobody

CMD ["/srv/env/bin/gunicorn", "-b", "0.0.0.0:8080", "-w", "10", "main:app"]