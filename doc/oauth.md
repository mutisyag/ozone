### ORS OAuth2 provider

New applications can be added via the admin panel from 
the Django OAuth Toolkit/Applications. An automatic random
client ID and secret will be generated in the process. 

Note that you can also skip the authorization step if required.

See Django OAuth Toolkit [documentation](https://django-oauth-toolkit.readthedocs.io) for more details


### OAuth client workflow (authorization code + secret)

A OAuth consumer should:
 - redirect the user to the following url 
 ```
 /o/authorize?response_type=code&client_id=CLIENT_ID&state=RANDOM_STRING
 ```
 - the user logs in and authorizes the application if needed.
 - the application redirects to the configured with the authorization `code` and the same state string
 - the authorization code needs to be exchanged for a access token by issuing a POST
   request (server-side) to `/o/token`, that also has the client secret, with the following values:
    - "code": CODE
    - "grant_type": "authorization_code",
    - "client_id": CLIENT_ID,
    - "client_secret": CLIENT_SECRET,
    - "redirect_uri": REDIRECT_URI,
 - the resulting token can then be used to access the API, for example to retrieve the user details:
 
```bash
curl -H "Authorization: Bearer <acces-token>" http://localhost:8000/api/current-user/
[{"username":"party","is_secretariat":false,"is_read_only":false,"party":80}]
```