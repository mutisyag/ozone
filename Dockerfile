FROM python:3.6-slim

# Can be overriden by compose
ARG REQUIREMENTS_FILE=requirements/local.txt

ARG BACKEND_HOST=ozone.eaudeweb.ro
ARG BACKEND_PORT=80
ARG TUSD_HOST=ozone.eaudeweb.ro
ARG TUSD_PORT=8080

ENV BACKEND_HOST=$BACKEND_HOST
ENV BACKEND_PORT=$BACKEND_PORT
ENV TUSD_HOST=$TUSD_HOST
ENV TUSD_PORT=$TUSD_PORT

ENV PYTHONUNBUFFERED=1

ENV APP_HOME=/var/local/ozone/
ENV MEDIA_ROOT=/var/local/uploads/
ENV PROTECTED_ROOT = /var/local/protected_uploads
ENV DOWNLOAD_STAGING_ROOT = /var/local/download_staging

RUN apt-get update -y \
  && apt-get install -y --no-install-recommends apt-utils curl bzip2 netcat-traditional lsb-release ca-certificates gnupg \
  && sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt/ $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list' \
  && curl -sS https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add - \
  && curl -sL https://deb.nodesource.com/setup_8.x | bash - \
  && curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | apt-key add - \
  && echo "deb https://dl.yarnpkg.com/debian/ stable main" | tee /etc/apt/sources.list.d/yarn.list

RUN runDeps="gcc postgresql-client-10 libxml2-dev libxslt-dev libsasl2-dev python-dev libldap2-dev libssl-dev git" \
 && apt-get update -y \
 && apt-get install -y --no-install-recommends $runDeps \
 && apt-get clean \
 && rm -vrf /var/lib/apt/lists/*

RUN mkdir -p $APP_HOME $MEDIA_ROOT $PROTECTED_ROOT $DOWNLOAD_STAGING_ROOT

COPY requirements $APP_HOME/requirements
WORKDIR $APP_HOME

RUN pip install --no-cache-dir -r $REQUIREMENTS_FILE

COPY . $APP_HOME

ENTRYPOINT ["./docker-entrypoint.sh"]
CMD ["run"]
