from dateutil.relativedelta import *
import re
from datetime import timedelta, datetime
import django
from django.core import mail
from django.conf import settings
from django.test import TestCase
import itertools as it
from helpers import make_user
from signalbox.utils import send_reminders_due_now
from signalbox.models.observation_timing_functions import observations_due_in_window
from signalbox.models import Script, ScriptType, Study, Membership, Reminder, ReminderInstance, Observation
from signalbox.allocation import allocate


class TestSchedule(TestCase):
    """Test that we can access the DB and some key parameters are set."""

    fixtures = ['test.json', ]

    def test_natural_date_specification(self):

        script = Script.objects.get(reference='test-email')
        times = script.datetimes()
        assert len(times) == 3

        # first is (just) before present moment (i.e., syntax is 'now')
        assert times[0] < datetime.now()

        # others are later than now
        [self.assertTrue(i > datetime.now()) for i in times[1:]]

        # each is later than the last
        [self.assertTrue(j < k) for j, k in it.combinations(times, 2)]

        # all gaps divisble by 10
        [self.assertTrue(abs(relativedelta(j, k).minutes) in [10, 20])
            for j, k in it.combinations(times, 2)]

    def test_calculate_start_datetime(self):

        script = Script.objects.get(reference='test-email-survey')
        script.delay_in_whole_days_only = False
        script.save()
        date = datetime(2012, 07, 01, 23, 59, 0)

        # Test calculate_start_datetime
        start = script.calculate_start_datetime(date)
        assert str(start) == "2012-07-01 23:58:00"

        # Test delay_by_minutes
        script.delay_by_minutes = 1
        start = script.calculate_start_datetime(date)
        assert str(start) == "2012-07-02 00:00:00"

        # Test delay_by_hours
        script.delay_by_hours = 1
        start = script.calculate_start_datetime(date)
        assert str(start) == "2012-07-02 01:00:00"

        # Test delay_by_days
        script.delay_by_days = 1
        start = script.calculate_start_datetime(date)
        assert str(start) == "2012-07-03 01:00:00"

        # Test delay_by_weeks
        script.delay_by_weeks = 1
        start = script.calculate_start_datetime(date)
        assert str(start) == "2012-07-10 01:00:00"

        # Test delay_in_whole_days_only (hh:mm:ss set to zero)
        script.delay_in_whole_days_only = True
        start = script.calculate_start_datetime(date)
        assert str(start) == "2012-07-10 00:00:00"

    def test_delay(self):

        script = Script.objects.get(reference='test-email-survey')

        script.delay_by_minutes = 9
        d = script.delay()
        assert str(d) == "0:09:00"

        script.delay_by_hours = 8
        d = script.delay()
        assert str(d) == "8:09:00"

        script.delay_by_days = 7
        d = script.delay()
        assert str(d) == "7 days, 8:09:00"

        script.delay_by_weeks = 6
        d = script.delay()
        assert str(d) == "49 days, 8:09:00"

        script.delay_by_weeks = 52
        d = script.delay()
        assert str(d) == "371 days, 8:09:00"


class TestScheduling(TestCase):
    """Check that Observations are created correctly and can be sent."""

    fixtures = ['test.json', ]

    def test_observation_timings(self):
        """Check that observation timings are as we expect -> None"""

        study = Study.objects.get(slug='test-schedule-study')

        user = make_user({'username': "TEST2", 'email': "TEST@TEST.COM", 'password': "TEST"})
        membership = Membership(study=study, user=user)
        membership.save()

        assert membership.observation_set.all().count() is 4

        first = membership.observation_set.all()[0]
        last = membership.observation_set.all()[3]
        assert first.due < last.due
        assert first.ready_to_send() is True
        assert last.ready_to_send() is False

        return membership

    def test_observation_due_selection(self):
        """Test the function which selects Observations in the time window."""

        membership = self.test_observation_timings()
        assert len(observations_due_in_window()) is 1

        first = observations_due_in_window()[0]
        first.due = datetime.now() + timedelta(days=100)
        first.save()
        assert len(observations_due_in_window()) is 0

    def test_reminders_get_added(self):
        """Check that ReminderInstances are added for each Observation -> (Observation, Reminder)."""
        membership = self.test_observation_timings()
        assert ReminderInstance.objects.all().count() is 1  # added to email surveys
        first = membership.observations().filter(created_by_script__reference="test-email-survey")[0]
        reminder = first.reminderinstance_set.all()[0]
        assert reminder.due - first.due == timedelta(days=2)  # 48 hours later

        return (first, reminder)

    def test_reminder_is_sent(self):

        first, reminder = self.test_reminders_get_added()

        send_reminders_due_now()
        assert len(mail.outbox) == 0  # nothing sent

        reminder.due = datetime.now()  # fiddle the time
        reminder.save()
        send_reminders_due_now()
        assert len(mail.outbox) == 1  # has been sent now

        send_reminders_due_now()
        assert len(mail.outbox) == 1  # not resent again
        
        # it comes from the right address
        assert mail.outbox[0].from_email == "jondoe@example.com"
        
    def test_reminder_from_emails(self):
        """"Test the logic that determines the return address for emails."""
        first, reminder = self.test_reminders_get_added()
        reminder.due = datetime.now()
        reminder.reminder.from_address = ""
        reminder.save()
        reminder.reminder.save()
        send_reminders_due_now()
            
        # expect it to come from the studyadmin because nothing set for the reminder
        assert mail.outbox[0].from_email == "studyadmin@example.com"
        
    def test_sending_observation(self):
        """ -> Observation """

        membership = self.test_observation_timings()
        first_observation = membership.observations().filter(created_by_script__reference="test-email-survey")[0]

        # test the email gets sent
        assert len(mail.outbox) == 0
        success, message = first_observation.do()
        assert success is True
        assert len(mail.outbox) == 1

        return first_observation

    def test_pausing_study(self):

        membership = self.test_observation_timings()
        first_observation = membership.observations()[0]

        assert first_observation.ready_to_send() is True
        first_observation.dyad.study.paused = True
        assert first_observation.ready_to_send() is False

    def test_deactivating_membership(self):
        """-> None """

        membership = self.test_observation_timings()
        first = membership.observations()[0]

        assert first.ready_to_send() is True
        first.dyad.active = False
        assert first.ready_to_send() is False

    def test_not_resending_observation(self):
        """Once an Observation has been sent, it shouldn't be resent immediately."""
        observation = self.test_sending_observation()
        observation.do()
        assert observation.ready_to_send() is False

    def test_no_sending_after_multiple_attempts(self):
        membership = self.test_observation_timings()
        first = membership.observation_set.all()[0]
        assert first.ready_to_send() is True
        first.attempt_count = 50
        assert first.ready_to_send() is False

    def test_emailsurvey_email_contains_url(self):
        "Check that we can see an access a url in the first line of the email."
        
        observation = self.test_sending_observation()
        urlre = 'http://[\w+\d+-/?.]+(?P<reply_token>[\w]{8}(-[\w]{4}){3}-[\w]{12})'
        email = mail.outbox[-1]
        assert re.search(urlre, email.body)
        url = re.search(urlre, email.body).group(0)
        questionnaire = self.client.get(url, follow=True)
        assert len(questionnaire.redirect_chain) == 1  # we get redirected
        assert questionnaire.status_code == 200  # we get a page
