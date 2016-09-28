import json

import mock
import pytest
from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from django.db import DatabaseError
from django.test.utils import override_settings

from marketing_site.apps.core.constants import Status

User = get_user_model()


@pytest.mark.django_db
class TestHealthView:
    def test_all_services_available(self, client):
        """Test that the endpoint reports when all services are healthy."""
        self._assert_health(client, 200, Status.OK, Status.OK)

    def test_database_outage(self, client, settings):
        """Test that the endpoint reports when the database is unavailable."""
        #  Wagtail's SiteMiddleware should be disabled for our database outage test since the middleware
        # requires database access.
        TEST_FRIENDLY_MIDDLEWARE_CLASSES = [mc for mc in settings.MIDDLEWARE_CLASSES if
                                            mc != 'wagtail.wagtailcore.middleware.SiteMiddleware']
        settings.MIDDLEWARE_CLASSES = TEST_FRIENDLY_MIDDLEWARE_CLASSES
        with mock.patch('django.db.backends.base.base.BaseDatabaseWrapper.cursor', side_effect=DatabaseError):
            self._assert_health(client, 503, Status.UNAVAILABLE, Status.UNAVAILABLE)

    def _assert_health(self, client, status_code, overall_status, database_status):
        """Verify that the response matches expectations."""
        response = client.get(reverse('health'))
        assert response.status_code == status_code
        assert response['content-type'] == 'application/json'

        expected_data = {
            'overall_status': overall_status,
            'detailed_status': {
                'database_status': database_status
            }
        }

        assert json.loads(response.content.decode('utf8')) == expected_data


@pytest.mark.django_db
class TestAutoAuthView:
    AUTO_AUTH_PATH = reverse('auto_auth')

    @override_settings(ENABLE_AUTO_AUTH=False)
    def test_setting_disabled(self, client, settings):
        settings.ENABLE_AUTO_AUTH = False
        response = client.get(self.AUTO_AUTH_PATH)
        assert response.status_code == 404

    @override_settings(ENABLE_AUTO_AUTH=True)
    def test_setting_enabled(self, client, settings):
        """
        When ENABLE_AUTO_AUTH is set to True, the view should create and authenticate
        a new User with superuser permissions.
        """
        settings.ENABLE_AUTO_AUTH = True
        original_user_count = User.objects.count()
        response = client.get(self.AUTO_AUTH_PATH)

        # Verify that a redirect has occured and that a new user has been created
        assert response.status_code == 302
        assert User.objects.count() == original_user_count + 1

        # Get the latest user
        user = User.objects.latest()

        # Verify that the user is logged in and that their username has the expected prefix
        assert int(client.session['_auth_user_id']) == user.pk
        assert user.username.startswith(settings.AUTO_AUTH_USERNAME_PREFIX)
        assert user.is_superuser
