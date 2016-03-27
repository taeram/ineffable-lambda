from __future__ import print_function

import json
import urllib
import boto3
import tempfile
import os
import re
from PIL import Image

s3 = boto3.client('s3')

def lambda_handler(event, context):
    """
        The AWS Lambda handler

        @param dict event The event data
        @param LambdaContext context The runtime information
    """
    # Grab the file details
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.unquote_plus(event['Records'][0]['s3']['object']['key']).decode('utf8')
    key_name, key_ext = os.path.splitext(key)

    # Extract the resize instructions json from the image file metadata
    image = s3.get_object(Bucket=bucket, Key=key)
    instructions = json.loads(image['Metadata']['instructions'])

    # Download the file
    image_original = tempfile.NamedTemporaryFile(suffix='.' + key_ext, delete=False)
    s3.download_file(bucket, key, image_original.name)

    for payload in instructions:
        # Create a temp file
        image_thumb = tempfile.NamedTemporaryFile(delete=False)

        # Resize the image
        img = Image.open(image_original.name)
        img.thumbnail((payload['width'], payload['height']))
        img.save(image_thumb.name, 'JPEG')

        # Upload the thumbnail to s3
        thumbnail_key = key_name + '_' + payload['suffix'] + '.jpg';
        s3.upload_file(image_thumb.name, bucket, thumbnail_key, ExtraArgs={'ACL': 'public-read', 'StorageClass': 'REDUCED_REDUNDANCY' })

        # Cleanup the local thumbnail file
        os.unlink(image_thumb.name)

    # Cleanup the downloaded original file
    os.unlink(image_original.name)
