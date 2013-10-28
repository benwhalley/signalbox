"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase


class TestConfiguration(TestCase):
    def test_credentials(self):
        """
        Tests that we can create a client using credentials from the ENV
        """            
        from twilio.rest import TwilioRestClient
        client = TwilioRestClient()

        
