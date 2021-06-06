from ecommerce_api.settings import blackListedTokens
from rest_framework.response import Response


def check_blacklist_token(function):
    def wrap(request, *args, **kwargs):
        authorization_header = request.headers.get('Authorization')
        if authorization_header:
            try:
                access_token = authorization_header.split(' ')[1]
                if access_token in blackListedTokens:
                    return Response({'response': 'Misuse of deactivated token is not allowed!', 'status': False})
            except IndexError:
                pass
        if request.method == 'POST':
            refresh_token = request.COOKIES.get('refreshtoken')
            if refresh_token in blackListedTokens:
                return Response({'response': 'Misuse of deactivated token is not allowed!', 'status': False})
        return function(request, *args, **kwargs)
    return wrap
