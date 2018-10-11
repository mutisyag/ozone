FROM python:3.6-slim as npm_builder

# Can be overriden by compose
ARG REQUIREMENTS_FILE=requirements/local.txt

ARG BACKEND_HOST=ozone.eaudeweb.ro
ARG BACKEND_PORT=80
ARG TUSD_HOST=ozone.eaudeweb.ro
ARG TUSD_PORT=8080

# Overriden in compose as needed
ENV BACKEND_HOST=$BACKEND_HOST

ENV APP_HOME=/var/local/ozone
RUN apt-get update -y \
    && apt-get install -y --no-install-recommends apt-utils curl software-properties-common gnupg \
    && curl -sL https://deb.nodesource.com/setup_8.x | bash - \
    && curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | apt-key add - \
    && echo "deb https://dl.yarnpkg.com/debian/ stable main" | tee /etc/apt/sources.list.d/yarn.list
RUN runDeps="nodejs yarn" \
    && apt-get update -y \
    && apt-get install -y --no-install-recommends $runDeps
RUN mkdir -p $APP_HOME/frontend
COPY frontend $APP_HOME/frontend/
RUN rm -rf frontend/dist
COPY package.json postcss.config.js yarn.lock $APP_HOME/
WORKDIR $APP_HOME
RUN npm_config_tmp=$APP_HOME yarn
RUN npm run build

FROM python:3.6-slim
RUN runDeps="netcat libpq-dev" \
    && apt-get update -y \
    && apt-get install -y --no-install-recommends $runDeps \
    && apt-get clean \
    && rm -vrf /var/lib/apt/lists/*
RUN mkdir -p $APP_HOME
COPY $REQUIREMENTS_FILE $APP_HOME/
WORKDIR $APP_HOME
RUN buildDeps="build-essential gcc" \
    && apt-get update -y \
    && apt-get install -y --no-install-recommends $buildDeps \
    && apt-get -y remove --purge --auto-remove $buildDeps
RUN pip install --no-cache-dir -r $REQUIREMENTS_FILE \
COPY . $APP_HOME
RUN rm -rf frontend package.json postcss.config.js yarn.lock \
    && mkdir -p $APP_HOME/frontend/dist \
    && mkdir $APP_HOME/static
COPY --from=npm_builder $APP_HOME/frontend/dist/build/ $APP_HOME/static/
COPY --from=npm_builder $APP_HOME/frontend/dist/stats.json $APP_HOME/frontend/dist/stats.json

ENTRYPOINT ["./docker-entrypoint.sh"]
CMD ["run"]
