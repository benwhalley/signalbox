from contracts import contract, new_contract
from django.db.models.loading import get_model
import signalbox
import ask
import django
from twilio import twiml

# Twiliobox
is_twiml_response = lambda s: isinstance(s, twiml.Response)
new_contract('is_twiml_response', is_twiml_response)


# Signalbox
model_instance = lambda s: isinstance(s, django.db.models.model)
new_contract('model_instance', model_instance)

is_answer = lambda s: isinstance(s, signalbox.models.Answer)
new_contract('is_answer', is_answer)

is_observation = lambda s: isinstance(s, signalbox.models.Observation)
new_contract('is_observation', is_observation)

is_reply = lambda s: isinstance(s, signalbox.models.Reply)
new_contract('is_reply', is_reply)


# Ask
is_question = lambda s: isinstance(s, ask.models.Question)
new_contract('is_question', is_question)
