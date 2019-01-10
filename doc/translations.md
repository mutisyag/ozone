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
 
### Configure the project in weblate

 1. Add new  project (+ "Add new translation project")
 2. Add new component to the project for the backend/frontend translations
 3. Configure Source code repository and push URL (using SSH)
 4. Enable push on commit
 5. Disable adding new languages
 
 