from social_core.backends.oauth import BaseOAuth2


class OzoneOAuth2(BaseOAuth2):
    """Ozone OAuth authentication backend"""
    name = 'ozone'
    ACCESS_TOKEN_METHOD = 'POST'
    SCOPE_SEPARATOR = ','

    def authorization_url(self):
        return 'http://%s/o/authorize/' % self.setting("SOCIAL_AUTH_OZONE_HOST")

    def access_token_url(self):
        return 'http://%s/o/token/' % self.setting("SOCIAL_AUTH_OZONE_API_HOST")

    def auth_allowed(self, response, details):
        """Only allow secretariat with write access."""
        # XXX It might be better to have a separate permission for this.
        if not response.get('is_secretariat') or response.get('is_read_only'):
            return False
        return super().auth_allowed(response, details)

    def get_user_details(self, response):
        return {
            'id': response.get('id'),
            'username': response.get('username'),
            'email': response.get('email'),
            'first_name': response.get('first_name'),
            'last_name': response.get('last_name'),
            'social': self,
        }

    def user_data(self, access_token, *args, **kwargs):
        """Loads user data from service"""
        url = 'http://%s/api/current-user/' % self.setting("SOCIAL_AUTH_OZONE_API_HOST")
        return self.get_json(url, headers={"Authorization": "Bearer %s" % access_token})[0]
