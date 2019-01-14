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

    def get_user_details(self, response):
        if not response.get('is_secretariat') or response.get('is_read_only'):
            return None
        return {
            'id': response.get('id'),
            'username': response.get('username'),
            'email': response.get('email'),
            'first_name': response.get('first_name'),
            'social': self,
        }

    def user_data(self, access_token, *args, **kwargs):
        """Loads user data from service"""
        url = 'http://%s/api/current-user/' % self.setting("SOCIAL_AUTH_OZONE_API_HOST")
        return self.get_json(url, headers={"Authorization": "Bearer %s" % access_token})[0]
