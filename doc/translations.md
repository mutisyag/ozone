## Continuous translation

### Overview
 
 1. PO translation files are kept in a separate repository [ozone-translations](https://github.com/eaudeweb/ozone-translations)
 2. Every Travis build on the `develop` branch will extract strings marked for translations
 update the PO files and push the changes back to the `ozone-translations` repo
 3. The weblate server is notified via a webhook whenever new changes are committed to the 
 `ozone-translations`
 4. Translators use the weblate interface to add new translations and commits the updated PO files
 5. When Jenkins updates the staging environment, changes are pulled from both repositories
 6. The docker-entrypoint compiles the translations to be used by the application
 
### Configuring the integration

 1. Add webhook from github to `https://<weblate-instance>/hooks/github/`
 2. Generate a SSH key from the weblate admin interface
 3. Add the SSH key as deploy key in GitHub with write access
 4. Create a personal access token with access to the translation repository
 5. Encrypt the token using travis-cli and add it to the environment
 6. Configure travis to push changes to the translations repo.
 
### Configure the project in Weblate

 1. Add new  project (+ "Add new translation project")
 2. Add new component to the project for the backend/frontend translations
 3. Configure Source code repository and push URL (using SSH)
 4. Enable push on commit
 5. Disable adding new languages
 
### Configuring Weblate OAuth

 1. Make sure that the Django site is correctly configured in Weblate Django admin
 2. Add a new OAuth App from ORS Django admin with:
   - Client Type: public
   - Redirect URI: `https://<weblate host>/accounts/complete/ozone/`
   - Authorization grant type: `Authorization code`
   - Name: 'weblate'
   - Skip authorization checked (*optional)
 3. Configure the `SOCIAL_AUTH_OZONE_*` variables in `docker/weblate.env` with the key and secret
 configured at step (2) and ensure that the hosts are correctly set. 
 4. Rebuild/restart Weblate if needed.
 5. Link admin from Django ORS with the one from Weblate, other users are created automatically. 
