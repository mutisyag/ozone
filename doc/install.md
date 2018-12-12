# Installing the application

## Docker

1. Get the source code:

       git clone https://github.com/eaudeweb/ozone
       cd ozone
   
2. Customize the Docker environment files:

       cp docker/demo.env.example docker/demo.env
       cp docker/smtp.env.example docker/smtp.env
       cp docker/postgres.env.example docker/postgres.env
   
   Depending on the installation mode, create the docker-compose.override.yml file:
   
       cp docker-compose.override.[local|edw].yml docker-compose.override.yml
   
   (when installing on a development machine, docker-compose.override.local.yml should be used)
   
3. Start the application stack:

        docker-compose up -d
        docker-compose logs
        
   If not starting for the first time, rebuild the relevant images:
   
        docker-compose build app

4. Attach to the app service:

        docker-compose exec app bash
        
   In the app console, create superuser if needed:
   
        python manage.py createsuperuser
        
## Install directly on development machine

1. Install prerequisites: Python 3.6, PostgreSQL 9, virtualenvwrapper, direnv. Installation instructions may vary according to host OS.

2. Get the source code:

       git clone https://github.com/eaudeweb/ozone
       cd ozone

3. Customize the environment files

        cp .envrc.example .envrc
        
   Edit as necessary, replacing <LAN IP> with relevant value, then run:
   
        direnv allow
        
   to load the environment variables.
   
4. Create the virtual environment for the application:
   
        mkvirtualenv ozone 
        
   To activate the virtual environment, use:
        
        workon ozone
        
5. Using PgAdmin (or from psql), create database `ozone` for user `ozone`.

   You can then run the migrations, load the fixtures and start the server:
   
        python manage.py migrate
        python manage.py load_inital_fixtures
        python manage.py createsuperuser
        python manage.py runserver 0.0.0.0:8000