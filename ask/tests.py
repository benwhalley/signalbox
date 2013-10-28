from signalbox.models import Answer
from ask.models import Asker
from django.core.urlresolvers import reverse
from django.test import TestCase



class Test_Asker(TestCase):
    """Basic tests on starting and submitting data for a questionnaire."""

    fixtures = ['ask_test.json', ]
    # to refresh fixture:
    # app/manage.py dumpdata --indent 2 ask signalbox.ScoreSheet > app/ask/fixtures/ask_test.json

    def test_anonymous_survey(self):

        asker = Asker.objects.get(slug="demonstration_questionnaire")
        url = reverse('start_anonymous_survey', args=(asker.id,))
        response = self.client.get(url)
        reply_url = response['Location']

        self.assertEqual(response.status_code, 302)

        questionnirepage = self.client.get(reply_url)
        self.assertContains(questionnirepage, '<form class="form" id="questionnaire_form"')
        return reply_url, questionnirepage

    def test_saving_answers(self):

        reply_url, questionnirepage = self.test_anonymous_survey()

        # Check the form won't submit without providing an answer
        errorpage = self.client.post(reply_url, {'page_id': 0}, follow=True)
        self.assertFormError(errorpage, "form", "demo1", ["An answer to this question is needed."])
        self.assertEqual(Answer.objects.all().count(), 0)

        # post an answer to the required question and check the Answers have been saved
        nextpage = self.client.post(reply_url,
            {'page_id': 0, 'demo1': 1, 'instrument_question_1': "2013-05-29"}, follow=True)
        self.assertTrue(Answer.objects.all().count() > 0)
        self.assertEqual(Answer.objects.get(question__variable_name="demo1").answer, "1")
        self.assertEqual(Answer.objects.get(question__variable_name="demo2").answer, "")
        self.assertEqual(Answer.objects.get(question__variable_name="instrument_question_1").answer, "2013-05-29")



# def test_submitting_questionnaire_bad_data(self):
#         """By design, nothing is saved until the form validates

#         Whether this is a good design or not is an open question, however when
#         using the django form machinery, this is the default way, and it there
#         would be a fair amount of work in making sure fields were saved
#         individually after validating."""

#         nexturl = self.get_questionnaire_page()
#         assert [i.answer for i in Answer.objects.all()] == []
#                                                      # nothing saved yet
#         incorrect_data = {'demo_list': "999", 'demo_date':
#                           "2001-19-19", 'demo_integer': "notanumber"}
#         data_to_post = dict(
#             helpers.QUESTIONNAIRE_POST_DATA.items() + incorrect_data.items())
#         formsubmission = self.client.post(nexturl, data_to_post, follow=True)
#         assert "9 is not one of the available choices." in formsubmission.content
#         assert "This question needs an answer in whole numbers." in formsubmission.content
#         assert "Enter a valid date" in formsubmission.content
#         assert Answer.objects.all().count() == 0  # still nothing saved
