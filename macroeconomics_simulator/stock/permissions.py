from rest_framework import permissions
from rest_framework.exceptions import AuthenticationFailed, PermissionDenied, NotFound
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import AccessToken

from stock.models import Player


class IsAuthor(permissions.BasePermission):
    """used to check whether the user who sent the request is the author of this page"""

    def has_permission(self, request, view):
        user_id = view.kwargs.get('user_id')
        if not user_id: # perhaps this condition will never be triggered
            raise AuthenticationFailed('Account UUID is required in URL.')

        auth_header = request.headers.get('Authorization')

        if auth_header:
            try:
                token_type, access_token = auth_header.split()

                if token_type.lower() != 'token':
                    raise AuthenticationFailed('Invalid token type. Expected "Token".')

                token = AccessToken(access_token)
                token_user_id = token['user_id']

                if user_id != token_user_id:
                    raise PermissionDenied('Forbidden')

                if not Player.objects.filter(id=user_id).exists(): # perhaps this condition will never be triggered
                    raise NotFound(f'There is no user with id {user_id}')

            except TokenError as e:
                raise AuthenticationFailed(f'Token error: {str(e)}')
            else:
                return True
        return False
