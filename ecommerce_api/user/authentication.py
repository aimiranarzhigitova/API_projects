from rest_framework.authentication import BaseAuthentication
from django.middleware.csrf import CsrfViewMiddleware
from rest_framework import exceptions
from django.conf import settings
from django.contrib.auth import get_user_model
import jwt


class CSRFCheck(CsrfViewMiddleware):
    def _reject(self, request, reason):
        if reason == 'Referer checking failed - no Referer.':
            print("[+] No referer csrf failed error")
            return None
        print("[+] csrf verified!")
        return reason


class SafeJWTAuthentication(BaseAuthentication):

    def authenticate(self, request):
        User = get_user_model()
        authorization_header = request.headers.get('Authorization')
        xcsrf_token = request.headers.get('X-CSRFToken')
        print("[+] csrftoken : ",end='')
        print(xcsrf_token)
        if not authorization_header:
            return None
        try:
            access_token = authorization_header.split(' ')[1]
            payload = jwt.decode(
                access_token, settings.SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            if xcsrf_token:
                return None
            raise exceptions.AuthenticationFailed('access token expired!')
        except jwt.InvalidSignatureError:
            raise exceptions.AuthenticationFailed('invalid token!')
        except jwt.DecodeError:
            raise exceptions.AuthenticationFailed('invalid token!')
        except IndexError:
            raise exceptions.AuthenticationFailed('Token prefix missing')

        user = User.objects.filter(id=payload['user_id']).first()
        if user is None:
            raise exceptions.AuthenticationFailed('User not found!')
        if not user.is_active:
            raise exceptions.AuthenticationFailed('User is inactive!')
        print("[+] Access token verified!")
        self.enforce_csrf(request)
        return user, None

    def enforce_csrf(self, request):
        check = CSRFCheck()
        check.process_request(request)
        reason = check.process_view(request, None, (), {})
        if reason:
            raise exceptions.AuthenticationFailed('CSRF Failed: %s' % reason)
