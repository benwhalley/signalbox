from pprint import pprint
from django.core import serializers
from ask.models import *
from signalbox.models import *
import itertools


asker = Asker.objects.select_related().get(slug="LINQ")


# This defines the relations to traverse when exporting questions
question_relations = {
        'relations': {
            'showif': { 'relations': {
                'summary_score': { 'relations': {
                    'variables': {},
                }}
            }},
            'choiceset': {'relations': 'choice_set'}
        }
}
# redefine this part so it's nested within itself...
question_relations['relations']['showif']['relations']['summary_score']['relations']['variables'] = question_relations


# defines all the other relations we need to fully export an asker
asker_relations = {
        'scoresheets': {},
        'askpage_set':{
            'relations': {
                'question_set': question_relations,
                'instrumentinaskpage_set': {
                    'relations': {
                        'instrument': {
                            'relations': {
                                'question_set': question_relations,
                            }
                        }
                    }
                },
            }
        },
    }


x = serializers.serialize( "json", [asker],  indent=4,
    relations=asker_relations)


with open('app/ask/fixtures/test_serialise_asker.json', 'w') as f:
    f.write(x)


# see for how to load this back in again later
# http://code.google.com/p/wadofstuff/issues/detail?id=7
