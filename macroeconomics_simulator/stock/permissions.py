from rest_framework import permissions
from rest_framework.exceptions import AuthenticationFailed, PermissionDenied
from rest_framework.generics import get_object_or_404
from rest_framework_simplejwt.exceptions import TokenError

from stock.models import PlayerCompanies, Company


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


class IsHeadOfSelectedCompany(permissions.BasePermission): # use with IsAuthenticated
    """used to check whether the user is the owner of the company (but only with the data sent in the request data)"""

    def has_permission(self, request, view):
        ticker = request.data.get('ticker')

        if not ticker:
            raise AuthenticationFailed(f"Company with ticker '{ticker}' doesn't exist")

        auth_header = request.headers.get('Authorization')

        if auth_header:
            try:
                token_user_id = request.user.id

                company = get_object_or_404(Company, ticker=ticker,)

                if not PlayerCompanies.objects.filter(company=company, player_id=token_user_id, isHead=True).exists():
                    raise PermissionDenied(f'You are not the head of company with ticker {ticker}')

            except TokenError as e:
                raise AuthenticationFailed(f'Token error: {str(e)}')
            else:
                return True
        return False
