# coding: utf-8
import StringIO
import csv
from signalbox.views.data import export_dataframe
import zipfile
from django.utils.html import escape
from django.core.urlresolvers import reverse
from django.test import TestCase
from signalbox.models import Study, Answer
from signalbox.views.data import *
from reversion.models import Version
from signalbox.allocation import allocate
from signalbox.tests.helpers import LONG_YUCKY_UNICODE, make_user
from django.conf import settings


class TestUnicode(TestCase):
    """"""


    def test_displaying_models(self):
        """Check that unicode weirdness doesn't foul model printing."""
        _ = Answer(answer=LONG_YUCKY_UNICODE)
        _ = Answer(answer=LONG_YUCKY_UNICODE).__repr__()
        _ = Answer(answer=LONG_YUCKY_UNICODE).__str__()
        _ = Answer(answer=LONG_YUCKY_UNICODE).__unicode__()
        _ = Answer(answer=223.000).__str__()



class TestDataHandling(TestCase):
    """Test that we can save and export data.

    Test that data is exported to CSV/Stata correctly. Some cases we should handle:

    - Simplest - single row per membership

    TODO
    - Longitudinal - multiple responses per user to different obs
    - Complex longitudinal - mutliple responses to different obs from different scripts
    - Conflicting - multiple replies to a single observation

    """

    fixtures = ['test.json', ]

    def test_making_membership(self):
        """"Can we add a dummy user to the demo study?"""

        study = Study.objects.get(slug='demo-study')
        user = make_user({'username': "TEST2", 'email': "TEST@TEST.COM", 'password': "TEST"})
        membership = Membership(study=study, user=user)
        membership.save()
        assert membership.condition is None  # has not auto-randomised
        allocate(membership)
        membership.add_observations()
        return membership

    def test_autorandomisation(self):

        study = Study.objects.get(slug='demo-study')
        study.auto_randomise = False
        study.save()

        user = make_user({'username': "TEST2", 'email': "TEST@TEST.COM", 'password': "TEST"})
        membership = Membership(study=study, user=user)
        membership.save()

        assert membership.condition is None

        allocate(membership)
        assert membership.condition is not None

    def test_auto_add_observations(self):
        study = Study.objects.get(slug='demo-study')
        study.auto_add_observations = False
        study.save()

        user = make_user({'username': "TEST2", 'email': "TEST@TEST.COM", 'password': "TEST"})
        membership = Membership(study=study, user=user)
        membership.save()
        assert membership.condition is None

        allocate(membership)
        assert membership.condition is not None
        assert membership.observation_set.all().count() is 0

        membership.add_observations()
        assert membership.observation_set.all().count() is 1

    def test_initial_reply(self):
        """"Can we make a reply to the first questionnaire in the demo study?"""
        membership = self.test_making_membership()
        observation = membership.observation_set.all()[0]
        url = observation.link()

        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

        reply_url = response['Location']

        return reply_url

    def test_responsive_mode_observations(self):
        """Can we create new observations in response to user input?

        The demo study defines several additional observations if the user
        responds in the right way to the first questionnaire."""

        url = self.test_initial_reply()
        reply = Reply.objects.get(token__iendswith=url[-20:-1])  # lookup the reply for this url to use in a moment

        questionnaire = self.client.get(url)
        self.assertContains(questionnaire, 'Would you like us to demonstrate the SignalBox system by sending')

        # note, we add ?finish=1 to make sure the questionnaire is finished and the reply checked for observationcreators
        nextpage = self.client.post(url + "?finish=1", {'agree_demonstrate_signalbox': "1", 'page_id': "0"}, follow=True)

        observations = reply.observation.dyad.observation_set.all()
        self.assertTrue(observations.count() == 4)

        return reply.observation.dyad

    def test_sending_scripts(self):
        from signalbox.cron import send, remind
        membership = self.test_responsive_mode_observations()
        sms_observation = membership.observation_set.get(created_by_script__reference="test-sms")
        send_results = send()
        remind_results = remind()
        assert str(sms_observation.id) in send_results
        assert "[]" in remind_results

    def test_responding_to_demo_questionnaire(self):

        membership = self.test_responsive_mode_observations()
        observation = membership.observation_set.get(created_by_script__asker__slug="demonstration_questionnaire")
        url = observation.link()
        questionnaire_url = self.client.get(url)['Location']
        missing_answers = self.client.post(questionnaire_url, {'page_id': 0}, follow=True)
        self.assertContains(missing_answers, "There were problems with a number of the questions below")
        self.assertContains(missing_answers, "An answer to this question is needed")

        # note we skip the middle page because it does not contain a required question
        last_page = self.client.post(questionnaire_url + "?page=2", {'page_id': 0, 'demo_longtext': LONG_YUCKY_UNICODE}, follow=True)

        # need to escape the YUCK because django does in the front end
        assert LONG_YUCKY_UNICODE not in last_page.content.decode('utf-8')
        assert escape(LONG_YUCKY_UNICODE) in last_page.content.decode('utf-8')

        return observation

    def test_demo_questionnaire_saves_answers(self):

        observation = self.test_responding_to_demo_questionnaire()
        assert observation.reply_set.all().count() == 1

        reply = observation.reply_set.all()[0]
        asker = reply.asker
        answers = reply.answer_set.all()

        # check we have as many answers as questions on the first page
        assert answers.count() == len(reply[0].get_questions()) + 1  # extra 1 for page_id which is saved
        assert answers.get(question__variable_name="demo_longtext").answer == LONG_YUCKY_UNICODE

    def test_demo_questionnaire_completes_observation(self):

        observation = self.test_responding_to_demo_questionnaire()
        reply = observation.reply_set.all()[0]
        url = reverse('show_page', args=(reply.token, ))

        finished = self.client.post(url + "?finish=1", {'page_id': 2})
        assert reply.redirect_url() in finished['Location']
        profile_page = self.client.get(finished['Location'], follow=True)

        # need to requery the database to see changes to reply behind the scenes
        reply = Reply.objects.get(token=reply.token)
        assert reply.complete is True
        assert reply.observation.status is 1

        return reply

    def test_export_answers(self):
        reply = self.test_demo_questionnaire_completes_observation()
        study = reply.observation.dyad.study
        answers = reply.answer_set.all()

        csvstring = build_csv_data_as_string(answers, study)
        questions = Question.objects.filter(id__in=answers.values('question__id'))
        syntax = generate_syntax('admin/ask/stata_syntax.html', questions)

        f = StringIO.StringIO(csvstring)
        dicts = list(csv.DictReader(f))

        headings = dicts[0].keys()

        expected_cols = ['n_in_sequence', 'observation.id', 'membership.id']
        [self.assertTrue(i in headings) for i in expected_cols]

        # check our horrible unicode was saved into the CSV file correctly
        assert LONG_YUCKY_UNICODE == dicts[0]['demo_longtext__0'].decode('utf-8')

        # and also that the zipfile is created correctly
        download = export_dataframe(answers, study)
        self.assertTrue(download.status_code == 200)
        zipped = StringIO.StringIO(download.content)
        pzipped = zipfile.ZipFile(zipped)
        assert set(pzipped.namelist()) == set(['syntax.do', 'data.csv', 'make.do'])
        assert LONG_YUCKY_UNICODE in pzipped.open('data.csv').read().decode('utf-8')
