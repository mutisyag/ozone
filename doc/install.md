# Installing the application

## Docker

XXX TODO update this for prod/local instalations

1. Get the source code:

       git clone https://github.com/eaudeweb/ozone
       cd ozone
       
Optionally clone the translations as well in `translations` folder inside the ozone folder.
        
       git clone https://github.com/eaudeweb/ozone-translations.git translations
   
2. Customize the Docker environment files:

       cp docker/app.env.example docker/demo.env
       cp docker/weblate.env.example docker/weblate.env
       cp frontend/.env.example frontend/.env.local
   
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

1. Install prerequisites: Python 3.6, PostgreSQL 9, virtualenvwrapper, direnv, tusd. Installation instructions may vary according to host OS.

2. Get the source code:

       git clone https://github.com/eaudeweb/ozone
       cd ozone
       
Optionally clone the translations as well in `translations` folder inside the ozone folder.
        
       git clone https://github.com/eaudeweb/ozone-translations.git translations

3. Customize the environment files

        cp .envrc.example .envrc
        
   Edit as necessary, replacing <LAN IP> with relevant value, then run:
   
        direnv allow
        
   to load the environment variables.
   
4. Create the virtual environment for the application:
   
        mkvirtualenv ozone 
        
   To activate the virtual environment, use:
        
        workon ozone
        
5. Install requirements:

        pip install -r requirements/local.txt
        
6. Using PgAdmin (or from psql), create database `ozone` for user `ozone`.

   You can then run the migrations, load the fixtures and start the server:
   
        python manage.py migrate
        python manage.py load_inital_fixtures
        python manage.py createsuperuser
        python manage.py runserver 0.0.0.0:8000
        
7. See `frontend/README.md` for instructions on starting the frontend application.

8. (optional) Installing tusd locally:

        wget https://github.com/tus/tusd/releases/download/0.11.0/tusd_linux_amd64.tar.gz 
        tar -xzvf tusd_linux_amd64.tar.gz 
        install tusd_linux_amd64/tusd /usr/local/bin/
        
9. (optional) Start tusd (make sure to configure these variable in your .envrc and load them)

       tusd -dir $TUSD_UPLOADS_DIR -hooks-http http://$BACKEND_HOST:$BACKEND_PORT/api/uploads/
