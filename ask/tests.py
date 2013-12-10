from signalbox.models import Answer
from ask.models import Asker
from django.core.urlresolvers import reverse
from django.test import TestCase
from ask.views.asker_text_editing import TextEditForm
import os
from django.conf import settings
from ask.views.parse_definitions import *

class Test_Asker(TestCase):
    """Basic tests on starting and submitting data for a questionnaire."""

    def test_load_markdown_asker(self, markdown="demonstration_asker.markdown"):

        markdown = os.path.join("/Users/ben/dev/signalbox/ask/fixtures/", markdown)
        asker = Asker(slug="demonstration_asker")
        asker.save()
        form = TextEditForm({'text':open(markdown).read()}, asker=asker)
        form.is_valid()
        form.save()
        assert len(form.asker.questions()) == 12, "Not the right number of questions found"


