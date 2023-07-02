import datetime
import random
import string
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import exceptions
from core.serializers import UserSerializer
from .models import User, UserTokens, ForgotPassword
from .auth_token import create_auth_token, create_refresh_token, JWTAuthentication, decode_refresh_token
from django.core.mail import send_mail


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

        UserTokens.objects.create(user_id=user.id, token=refresh_token,
                                  expired_at=datetime.datetime.utcnow() + datetime.timedelta(days=7))

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

        if not UserTokens.objects.filter(user_id=id, token=refresh_token, expired_at__gt=datetime.datetime.now(tz=datetime.timezone.utc)).exists():
            raise exceptions.AuthenticationFailed('Refresh token expired!')
        access_token = create_auth_token(id)
        return Response({
            'token': access_token
        })


class LogoutAPIView(APIView):
    def post(self, request):
        refresh_token = request.COOKIES['refresh_token']
        UserTokens.objects.filter(token=refresh_token).delete()
        response = Response()
        response.delete_cookie(key='refresh_token')

        response.data = {
            'message': 'Log out successfully'
        }

        return response


class ForgotPasswordAPIView(APIView):
    def post(self, request):
        email = request.data.get('email')
        token = ''.join(random.choice(string.ascii_lowercase +
                        string.digits) for _ in range(10))
        ForgotPassword.objects.create(
            email=email, token=token)

        url = 'https://localhost:3000/reset/' + token

        send_mail(
            subject='Reset your password',
            message=f'Click <a href=${url}>here</a> to reset your password!',
            from_email='from@example.com',
            recipient_list=[email]
        )
        return Response({
            'message': 'Reset link sent successfully',
        })


class ResetAPIView(APIView):
    def post(self, request):
        data = request.data

        if data['password'] != data['password_confirm']:
            raise exceptions.APIException('Passwords do not match!')

        reset_pw = ForgotPassword.objects.filter(
            token=data['token']).first()

        if not reset_pw:
            raise exceptions.APIException('Invalid link!')

        user = User.objects.filter(email=reset_pw.email).first()

        if not user:
            raise exceptions.APIException('User not found!')

        user.set_password(data['password'])
        user.save()

        return Response({
            'message': 'Password reset',
        })
