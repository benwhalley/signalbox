import os
from django.shortcuts import *
from django import http
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import *
from django.core.files.storage import FileSystemStorage
from django.conf import settings
import mimetypes


PRIVATE_UPLOAD_STORAGE_BACKEND = FileSystemStorage(
    location=os.path.join(settings.PROJECT_PATH, "../files/private"),
    base_url="/admin/signalbox/private/")


def get_from_id_or_filename(id, klass):
    try:
        obj = get_object_or_404(klass, id=id)
    except:
        obj = get_object_or_404(klass, document__endswith=id)
    return obj

