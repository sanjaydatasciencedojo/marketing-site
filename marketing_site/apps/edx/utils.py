import datetime

from dateutil import parser
from django.conf import settings
from django.core.cache import cache
from edx_rest_api_client.client import EdxRestApiClient


def get_access_token():
    """ Returns an access token for this site's service user.

    The access token is retrieved using the current site's OAuth credentials and the client credentials grant.
    The token is cached for the lifetime of the token, as specified by the OAuth provider's response. The token
    type is JWT.

    Returns:
        str: JWT access token
    """
    oauth_endpoint = settings.SOCIAL_AUTH_EDX_OIDC_URL_ROOT
    oauth_client_id = settings.SOCIAL_AUTH_EDX_OIDC_KEY
    key = 'api_access_token_{endpoint}_{client_id}'.format(endpoint=oauth_endpoint, client_id=oauth_client_id)
    access_token = cache.get(key)

    if not access_token:
        access_token, expiration_datetime = EdxRestApiClient.get_oauth_access_token(
            '{}/access_token'.format(oauth_endpoint),
            oauth_client_id,
            settings.SOCIAL_AUTH_EDX_OIDC_SECRET,
            token_type='jwt'
        )

        expires = (expiration_datetime - datetime.datetime.utcnow()).seconds
        cache.set(key, access_token, expires)

    return access_token


def discovery_api_client():
    return EdxRestApiClient(settings.DISCOVERY_API_URL, jwt=get_access_token())


def parse_datetime(s):
    if s:
        return parser.parse(s)

    return None
