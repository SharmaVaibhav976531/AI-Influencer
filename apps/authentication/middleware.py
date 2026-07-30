# apps/authentication/middleware.py
import time
from django.contrib.sessions.middleware import SessionMiddleware
from django.conf import settings
from django.utils.cache import patch_vary_headers
from django.utils.http import http_date
from django.contrib.sessions.backends.base import UpdateError
from django.contrib.sessions.exceptions import SessionInterrupted

class IsolatedSessionMiddleware(SessionMiddleware):
    """
    Custom Session Middleware to completely isolate session cookies 
    between the Django Admin Panel ('/admin/') and the Custom Application.
    """

    def process_request(self, request):
        if request.path_info.startswith('/admin'):
            cookie_name = getattr(settings, 'ADMIN_SESSION_COOKIE_NAME', 'admin_sessionid')
        else:
            cookie_name = settings.SESSION_COOKIE_NAME

        session_key = request.COOKIES.get(cookie_name)
        request.session = self.SessionStore(session_key)
        request._session_cookie_name = cookie_name


    def process_response(self, request, response):
        """
        Save the session data and set/delete the session cookie.
        Preserves all behaviors of Django's native SessionMiddleware while using
        the isolated cookie name for Admin vs Application paths.
        """
        try:
            accessed = request.session.accessed
            modified = request.session.modified
            empty = request.session.is_empty()
        except AttributeError:
            return response

        cookie_name = getattr(request, '_session_cookie_name', settings.SESSION_COOKIE_NAME)

        # First check if we need to delete this cookie.
        if cookie_name in request.COOKIES and empty:
            response.delete_cookie(
                cookie_name,
                path=settings.SESSION_COOKIE_PATH,
                domain=settings.SESSION_COOKIE_DOMAIN,
                samesite=settings.SESSION_COOKIE_SAMESITE,
            )
            need_vary_cookie = True
        else:
            need_vary_cookie = accessed
            if (modified or settings.SESSION_SAVE_EVERY_REQUEST) and not empty:
                if request.session.get_expire_at_browser_close():
                    max_age = None
                    expires = None
                else:
                    max_age = request.session.get_expiry_age()
                    expires_time = time.time() + max_age
                    expires = http_date(expires_time)

                # Save the session data to database / backend storage
                if response.status_code < 500:
                    try:
                        request.session.save()
                    except UpdateError:
                        raise SessionInterrupted(
                            "The request's session was deleted before the "
                            "request completed. The user may have logged "
                            "out in a concurrent request, for example."
                        )
                    response.set_cookie(
                        cookie_name,
                        request.session.session_key,
                        max_age=max_age,
                        expires=expires,
                        domain=settings.SESSION_COOKIE_DOMAIN,
                        path=settings.SESSION_COOKIE_PATH,
                        secure=settings.SESSION_COOKIE_SECURE or None,
                        httponly=settings.SESSION_COOKIE_HTTPONLY or None,
                        samesite=settings.SESSION_COOKIE_SAMESITE,
                    )
                    need_vary_cookie = True

        if need_vary_cookie:
            patch_vary_headers(response, ("Cookie",))

        return response