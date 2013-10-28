from django.test import TestCase
from django.contrib.auth.models import User
from signalbox.models import UserProfile

class TestUserProfiles(TestCase):
    """Check functionality related to UserProfile model."""


    def test_user_profile_created(self):
        """Check the signal to create a user profile has fired."""

        user = User(**{'username': "TEST", 'email':"TEST@TEST.COM"})
        user.save()
        assert type(user.get_profile()) == UserProfile
