from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import exceptions
from core.serializers import UserSerializer
from .models import User
from .auth_token import create_auth_token, create_refresh_token, decode_auth_token, JWTAuthentication, decode_refresh_token
from rest_framework.authentication import get_authorization_header


class RegisterAPIView(APIView):

    def post(self, request):
        data = request.data

        if data['password'] != data['password_confirm']:
            raise exceptions.APIException('Passwords do not match!')

        serializer = UserSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)


class LoginAPIView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        user = User.objects.filter(email=email).first()

        if user is None:
            raise exceptions.AuthenticationFailed('User not found!')

        if not user.check_password(password):
            raise exceptions.AuthenticationFailed('Incorrect password!')

        auth_token = create_auth_token(user.id)
        refresh_token = create_refresh_token(user.id)

        response = Response()
        response.set_cookie(key='refresh_token',
                            value=refresh_token, httponly=True)
        response.data = {
            'token': auth_token
        }

        return response


class UserAPIView(APIView):
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        return Response(UserSerializer(request.user).data)


class RefreshAPIView(APIView):
    def post(self, request):
        refresh_token = request.COOKIES['refresh_token']
        id = decode_refresh_token(refresh_token)
        access_token = create_auth_token(id)
        return Response({
            'token': access_token
        })
