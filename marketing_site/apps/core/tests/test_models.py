import pytest
from social_django.models import UserSocialAuth

from marketing_site.apps.core.tests.factories import UserFactory


@pytest.mark.django_db
class TestUser:
    def test_access_token(self):
        user = UserFactory()
        assert user.access_token is None

        social_auth = UserSocialAuth.objects.create(user=user, provider='test', uid=user.username)
        assert user.access_token is None

        access_token = 'My voice is my passport. Verify me.'
        social_auth.extra_data.update({'access_token': access_token})
        social_auth.save()
        assert user.access_token == access_token

    def test_get_full_name(self):
        full_name = 'George Costanza'
        user = UserFactory(full_name=full_name)
        assert user.get_full_name() == full_name

        first_name = 'Jerry'
        last_name = 'Seinfeld'
        user = UserFactory(full_name=None, first_name=first_name, last_name=last_name)
        expected = '{first_name} {last_name}'.format(first_name=first_name, last_name=last_name)
        assert user.get_full_name() == expected

        user = UserFactory(full_name=full_name, first_name=first_name, last_name=last_name)
        assert user.get_full_name() == full_name

    def test_str(self):
        user = UserFactory()
        assert str(user) == user.get_full_name()
