from django.utils.translation import gettext_lazy as _
import rest_framework.authtoken.models
import rest_framework.exceptions

class TokenAuthMiddleware:
    """Token authorization middleware for Channels.

    Authenticate the connection by the header 'Authorization: Token...'
    using Django REST framework token-based authentication.
    """

    def __init__(self, inner):
        """Save given inner middleware to invoke in the `__call__`."""
        self._inner = inner

    def __call__(self, scope):
        """Add user to the scope by 'Authorization: Token...' header."""

        # This function carefully and creatively copied from Django REST
        # framework implementation `TokenAuthentication` class.

        # Only handle "Authorization" headers starting with "Token".
        headers = dict(scope["headers"])
        if b"authorization" not in headers:
            return self._inner(scope)
        auth_header = headers[b"authorization"].split()
        if not auth_header or auth_header[0].lower() != "token".encode():
            return self._inner(scope)

        # Check header correctness. Since we use Django REST framework
        # for token-based authentication, we raise its exceptions.
        AuthError = rest_framework.exceptions.AuthenticationFailed
        if len(auth_header) == 1:
            raise AuthError(_("Invalid token header: no credentials provided!"))
        if len(auth_header) > 2:
            raise AuthError(_("Invalid token header: token string contains spaces!"))
        try:
            auth_header_token = auth_header[1].decode()
        except UnicodeError:
            raise AuthError(_("Invalid token header: token contains invalid symbols!"))

        # According to the warning in the Channels authentication docs
        # we have to manually close old database connections to prevent
        # usage of timed out connections.
        django.db.close_old_connections()

        # Find a user by the token.
        Token = rest_framework.authtoken.models.Token
        try:
            token = Token.objects.select_related("user").get(key=auth_header_token)
        except Token.DoesNotExist:
            raise AuthError(_("Invalid token!"))
        if not token.user.is_active:
            raise AuthError(_("User is inactive!"))

        # Call inner middleware with a user in the scope.
        return self._inner(dict(scope, user=token.user))