#!/usr/bin/env python
# -*- coding: utf-8 -*-

from storages.backends.s3boto import S3BotoStorage
from django.utils.functional import SimpleLazyObject
from django.core.files.storage import get_storage_class



class CustomS3BotoStorage(S3BotoStorage):  # pragma: no cover
    """
    S3 storage backend that saves the files locally, too.
    """
    def __init__(self, *args, **kwargs):
        super(CustomS3BotoStorage, self).__init__(*args, **kwargs)
        self.local_storage = get_storage_class(
            "compressor.storage.CompressorFileStorage")()


    # XXX Temporary hack to fix https://bitbucket.org/david/django-storages/issue/121/s3boto-admin-prefix-issue-with-django-14
    def url(self, name):
        url = super(CustomS3BotoStorage, self).url(name)
        if name.endswith('/') and not url.endswith('/'):
            url += '/'
        return url


    def save(self, name, content):
        name = super(CustomS3BotoStorage, self).save(name, content)
        self.local_storage._save(name, content)
        return name

StaticRootS3BotoStorage = lambda: CustomS3BotoStorage(location='static/') # pragma: no cover
MediaRootS3BotoStorage = lambda: CustomS3BotoStorage(location='media/') # pragma: no cover
PrivateRootS3BotoStorage = lambda: CustomS3BotoStorage(location='private/') # pragma: no cover
