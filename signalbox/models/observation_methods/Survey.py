from django.core.urlresolvers import reverse
from signalbox.models.observation_helpers import *


def link(self):
    return reverse('start_data_entry', kwargs={'observation_token':self.token})

def update(self, success_status):
    self.status = -3
    self.save()

def do(self):
    self.update(1)
    return (1, "Ready to be completed")
