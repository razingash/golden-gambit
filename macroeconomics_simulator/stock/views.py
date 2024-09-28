from django.shortcuts import get_object_or_404 # проверить отличия с drf
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken
from rest_framework_simplejwt.tokens import RefreshToken, UntypedToken
from rest_framework_simplejwt.views import TokenVerifyView

from stock.models import Company, StateLaw, GlobalEvent
from stock.serializers import RegisterSerializer, CompanyCreateSerializer, CompanySerializer, PlayerSerializer, \
    PlayerCompaniesSerializer, CompanyUpdateSerializer, EventsSerializer, LawsSerializer
from stock.services import create_new_company, get_player, get_user_companies, get_paginated_objects
from stock.utils import custom_exception


class RegisterView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            player = serializer.save()

            refresh = RefreshToken.for_user(player)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)

            return Response({'refresh': refresh_token, 'access': access_token})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    permission_classes = (IsAuthenticated, )

    def post(self, request):
        try:
            refresh_token = request.data['refresh_token']
            token = RefreshToken(refresh_token)

            if token.payload['user_id'] != request.user.id: #
                return Response({"INFO": "Invalid token during logout"}, status=status.HTTP_403_FORBIDDEN)

            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except (TokenError, InvalidToken):
            return Response({"detail": "Invalid token during logout."}, status=status.HTTP_400_BAD_REQUEST)
        except KeyError:
            return Response({"detail": "Refresh token is required."}, status=status.HTTP_400_BAD_REQUEST)


class TokenVerifyWithBlacklistView(TokenVerifyView):
    def post(self, request, *args, **kwargs):
        try:
            token = UntypedToken(request.data['token'])

            if BlacklistedToken.objects.filter(token__jti=token.payload['jti']).exists():
                raise InvalidToken({"detail": "This token has been canceled"})

            return super().post(request, *args, **kwargs)
        except TokenError as e:
            raise InvalidToken(e.args[0])


class UserApiView(APIView):
    #add some permissions
    def get(self, request, user_id):
        player = get_player(user_id)

        return Response(PlayerSerializer(player, many=False).data)


class UserCompaniesView(APIView):
    #permission_classes = (IsAuthenticated, )

    def get(self, request, user_id):
        companies = get_user_companies(user_id)

        return Response(PlayerCompaniesSerializer(companies, many=True).data)

    @custom_exception
    def post(self, request, user_id):
        serializer = CompanyCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        company = create_new_company(user_id=user_id, request_data=request.data)

        return Response(CompanySerializer(company, many=False).data)


class CompanyListView(APIView):
    def get(self, request):
        companies, has_next = get_paginated_objects(model=Company, query_params=request.query_params)
        serializer = CompanySerializer(companies, many=True)

        return Response({'data': serializer.data, 'has_next': has_next})


class CompanyApiView(APIView):
    def get(self, request, ticker):
        company = get_object_or_404(Company, ticker=ticker)

        return Response(CompanySerializer(company, many=False).data)

    def patch(self, request, ticker):
        company = get_object_or_404(Company, ticker=ticker)
        serializer = CompanyUpdateSerializer(company, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        serializer.save()

        return Response(serializer.data)


class LawsApiView(APIView):
    def get(self, request):
        laws, has_next = get_paginated_objects(model=StateLaw, query_params=request.query_params)
        serializer = LawsSerializer(laws, many=True)

        return Response({'data': serializer.data, 'has_next': has_next})

class EventsApiView(APIView):
    def get(self, request):
        events, has_next = get_paginated_objects(model=GlobalEvent, query_params=request.query_params)
        serializer = EventsSerializer(events, many=True)

        return Response({'data': serializer.data, 'has_next': has_next})
