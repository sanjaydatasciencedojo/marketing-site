from django.test import RequestFactory

from marketing_site.apps.core.context_processors import core


def test_core(settings):
    settings.PLATFORM_NAME = 'Test Platform'
    request = RequestFactory().get('/')
    assert core(request) == {'platform_name': settings.PLATFORM_NAME}
