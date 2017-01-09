from django.conf import settings
from django.contrib.auth.middleware import RemoteUserMiddleware
from django.contrib import auth


class GeoAxisMiddleware(RemoteUserMiddleware):
    """
    Middleware for utilizing GEOAXIS provided authentication. This is a
    subclass of the RemoteUserMiddleware. The header value is configurable
    by setting a django setting of GEOAXIS_HEADER.
    """
    header = getattr(settings, 'GEOAXIS_HEADER', 'OAM_REMOTE_USER')
    force_logout_if_no_header = False

    def clean_username(self, username, request):
        """
        Allows the backend to clean the username, if the backend defines a
        clean_username method.
        """
        backend_str = request.session[auth.BACKEND_SESSION_KEY]
        backend = auth.load_backend(backend_str)
        try:
            username = backend.clean_username(username)
        except AttributeError:
            pass
        return username.lower()
