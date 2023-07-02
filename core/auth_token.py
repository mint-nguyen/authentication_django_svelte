import jwt
import datetime
from rest_framework.authentication import BaseAuthentication, get_authorization_header
from rest_framework.exceptions import AuthenticationFailed
from core.models import User


class JWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth_data = get_authorization_header(request).split()
        if not auth_data or len(auth_data) != 2:
            return None
        try:
            payload = jwt.decode(
                auth_data[1], 'auth_secret', algorithms=["HS256"]
            )
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Token Expired")
        except:
            raise AuthenticationFailed("Token Invalid")
        user = User.objects.get(id=payload["user_id"])
        return (user, None)

    def authentication_header(request):
        auth_data = request.META.get("HTTP_AUTHORIZATION", None)
        if auth_data:
            auth_data = auth_data.split(" ")
            if len(auth_data) == 2:
                return auth_data[1]
        return None


def create_auth_token(id):
    return jwt.encode({
        'user_id': id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=30),
        'iat': datetime.datetime.utcnow()
    }, 'auth_secret', algorithm='HS256')


def decode_auth_token(token):
    try:
        payload = jwt.decode(token, 'auth_secret', algorithms=[
                             'HS256'])
        return payload['user_id']
    except Exception as e:
        return 'Signature expired. Please log in again.'


def create_refresh_token(id):
    return jwt.encode({
        'user_id': id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7),
        'iat': datetime.datetime.utcnow()
    }, 'refresh_secret', algorithm='HS256')
