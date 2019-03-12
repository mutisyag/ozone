FROM python:3.6-slim

# Can be overriden by compose
ARG REQUIREMENTS_FILE=requirements/local.txt

RUN runDeps="netcat libpq-dev gettext" \
    && apt-get update -y \
    && apt-get install -y --no-install-recommends $runDeps \
    && apt-get clean \
    && rm -vrf /var/lib/apt/lists/*
RUN buildDeps="build-essential gcc" \
    && apt-get update -y \
    && apt-get install -y --no-install-recommends $buildDeps

ENV APP_HOME=/var/local/ozone
RUN mkdir -p $APP_HOME
COPY requirements $APP_HOME/requirements
WORKDIR $APP_HOME
RUN pip install --no-cache-dir -r $REQUIREMENTS_FILE
COPY . $APP_HOME

ENTRYPOINT ["./docker-entrypoint.sh"]
CMD ["run"]
