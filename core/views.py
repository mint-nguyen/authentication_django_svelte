from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import exceptions
from core.serializers import UserSerializer
from .models import User
from .auth_token import create_auth_token, create_refresh_token, decode_auth_token
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
    def get(self, request):
        auth = get_authorization_header(request).split()

        if auth and len(auth) == 2:
            token = auth[1].decode('utf-8')
            id = decode_auth_token(token)
            user = User.objects.filter(id=id).first()

            if user:
                serializer = UserSerializer(user)
                return Response(serializer.data)

        raise Exception('Authentication credentials were not provided.')
