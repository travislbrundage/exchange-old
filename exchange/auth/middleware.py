from django.conf import settings
from django.contrib.auth.middleware import RemoteUserMiddleware
from social_django.middleware import SocialAuthExceptionMiddleware
from social_core.exceptions import AuthForbidden


class GeoAxisMiddleware(RemoteUserMiddleware):
    """
    Middleware for utilizing GEOAXIS provided authentication. This is a
    subclass of the RemoteUserMiddleware. The header value is configurable
    by setting a django setting of GEOAXIS_HEADER.
    """
    header = getattr(settings, 'GEOAXIS_HEADER', 'OAM_REMOTE_USER')
    force_logout_if_no_header = False


class RedirectOnForbiddenMiddleware(SocialAuthExceptionMiddleware):
    def get_redirect_uri(self, request, exception):
        if isinstance(exception, AuthForbidden):
            return '/'
        else:
            return super(RedirectOnForbiddenMiddleware,
                         self).get_redirect_uri(request, exception)

    def get_message(self, request, exception):
        if isinstance(exception, AuthForbidden):
            return 'You are not authorized to log ' \
                   'into this system with that account.'
        else:
            return super(RedirectOnForbiddenMiddleware,
                         self).get_message(request, exception)
