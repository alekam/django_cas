"""CAS authentication backend"""

from django.conf import settings
from django.contrib.auth.backends import ModelBackend
from django.core.urlresolvers import get_callable
from django_cas.models import User
from urllib import urlencode, urlopen
from urlparse import urljoin


__all__ = ['CASBackend']


def get_response(ticket, service):
    """Make request to CAS and get response"""
    params = {'ticket': ticket, 'service': service}
    if settings.CAS_VERSION == '1':
        validate = 'validate'
    else:
        validate = 'serviceValidate'
    url = (urljoin(settings.CAS_SERVER_URL, validate) + '?' +
           urlencode(params))
    page = urlopen(url)
    response = None
    try:
        response = page.read().strip()
    finally:
        page.close()
    return response


def _verify_cas1(response):
    """Verifies CAS 1.0 authentication ticket.

    Returns user instance on success and None on failure.
    """
    if response is not None:
        try:
            verified, username = response.strip().split()
            if verified == 'yes':
                return get_user(username)
        except:
            pass
    return None


def _verify_cas2(response):
    """Verifies CAS 2.0+ XML-based authentication ticket.

    Returns user instance on success and None on failure.
    """
    try:
        from xml.etree import ElementTree
    except ImportError:
        from elementtree import ElementTree

    try:
        tree = ElementTree.fromstring(response)
        if tree[0].tag.endswith('authenticationSuccess'):
            user = get_user(tree[0][0].text)
            if user is not None:
                attr_filler = get_callable(settings.CAS_ATTRIBUTES_PROCESSOR)
                if attr_filler:
                    user = attr_filler(user, tree)
                return user
    except:
        return None


_PROTOCOLS = {'1': _verify_cas1, '2': _verify_cas2}

if settings.CAS_VERSION not in _PROTOCOLS:
    raise ValueError('Unsupported CAS_VERSION %r' % settings.CAS_VERSION)

_verify = _PROTOCOLS[settings.CAS_VERSION]


def get_user(username):
    """Returns user instance"""
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        # user will have an "unusable" password
        user = User.objects.create_user(username, '')
        user.save()
    return user


class CASBackend(ModelBackend):
    """CAS authentication backend"""

    def authenticate(self, ticket, service):
        """Verifies CAS ticket and gets or creates User object"""
        return _verify(get_response(ticket, service))
