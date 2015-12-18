import json
import envoy
import os
import shortuuid
from boto.s3.connection import S3Connection


def make_secret_key():
    print(shortuuid.uuid())

def make_s3_bucket():
    print("Creating a new amazon bucket to save static files to")
    required, optional = _get_settings()
    s3conn = S3Connection(required['AWS_ACCESS_KEY_ID'], required['AWS_SECRET_ACCESS_KEY'])
    bucket = s3conn.create_bucket(required['AWS_STORAGE_BUCKET_NAME'])
    print("New bucket created.")
    bucket.set_acl('public-read')
