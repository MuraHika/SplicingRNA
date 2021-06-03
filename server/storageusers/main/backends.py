import jwt

from django.conf import settings

from rest_framework import authentication, exceptions

from .models import MyUser


class JWTAuthentication(authentication.BaseAuthentication):
    authentication_header_prefix = 'Token'

    def authenticate(self, request):
        request.user = None
        token = self.get_token_from_headers(request)
        if token == None:
            token = self.get_token_from_cookie(request)
        if token == None:
            return None
        return self._authenticate_credentials(request, token)

    def get_token_from_headers(self, request):
        auth_header = authentication.get_authorization_header(request).split()
        auth_header_prefix = self.authentication_header_prefix.lower()

        if not auth_header or len(auth_header) != 2:
            return None

        prefix = auth_header[0].decode('utf-8')
        token = auth_header[1].decode('utf-8')

        if prefix.lower() != auth_header_prefix:
            return None
        return token


    def get_token_from_cookie(self, request):
        token = None
        if self.authentication_header_prefix in request.COOKIES:
            token = request.COOKIES[self.authentication_header_prefix]
        return token

    def _authenticate_credentials(self, request, token):
        try:
            payload = jwt.decode(token, settings.SECRET_KEY)
        except:
            msg = 'Invalid authentication. Could not decode token.'
            raise exceptions.AuthenticationFailed(msg)

        try:
            user = MyUser.objects.get(pk=payload['id'])
        except MyUser.DoesNotExist:
            msg = 'No user matching this token was found.'
            raise exceptions.AuthenticationFailed(msg)

        if not user.is_active:
            msg = 'This user has been deactivated.'
            raise exceptions.AuthenticationFailed(msg)
            
        return (user, token)