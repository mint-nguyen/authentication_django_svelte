import jwt
import datetime


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
