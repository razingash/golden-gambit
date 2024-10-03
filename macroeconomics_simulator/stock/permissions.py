from rest_framework import permissions
from rest_framework.exceptions import AuthenticationFailed, PermissionDenied
from rest_framework.generics import get_object_or_404
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import AccessToken

from stock.models import PlayerCompanies, Company


class IsAuthor(permissions.BasePermission): # use with IsAuthenticated
    """used to check whether the user who sent the request is the author of this page"""

    def has_permission(self, request, view):
        auth_header = request.headers.get('Authorization')

        if auth_header:
            user_id = view.kwargs.get('user_id')
            token_user_id = request.user.id

            if int(user_id) != token_user_id:
                raise PermissionDenied('Forbidden for you')

            return True
        return False


class IsHeadOfCompany(permissions.BasePermission): # use with IsAuthenticated
    """used to check whether the user is the head of the company"""

    def has_permission(self, request, view):
        ticker = view.kwargs.get('ticker')

        if not ticker: # remove this check later. It will only work if you use permission inappropriately
            raise AuthenticationFailed('Incorrect permission application, but company ticker is required in URL.')

        auth_header = request.headers.get('Authorization')

        if auth_header:
            try:
                token_user_id = request.user.id

                company = get_object_or_404(Company, ticker=ticker)

                if not PlayerCompanies.objects.filter(company=company, player_id=token_user_id, isHead=True).exists():
                    raise PermissionDenied('You are not the head of this company')

            except TokenError as e:
                raise AuthenticationFailed(f'Token error: {str(e)}')
            else:
                return True
        return False

