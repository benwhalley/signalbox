from django.conf import settings
from django.test import TestCase
from django.contrib.auth.models import User
from signalbox.models import Study



class TestConfig(TestCase):
    """Test that we can access the DB and some key parameters are set."""

    fixtures = ['test.json',]

    def test_key_parameters_exist(self):
        """Without these, things would probably break."""

        assert len(settings.SECRET_KEY) > 0
        assert type(settings.SITE_ID) == int


    def test_loading_fixtures(self):
        users = User.objects.all()
        assert users.count() > 1



