from __future__ import print_function

import json
import urllib
import boto3
import tempfile
import subprocess
import os
import stat
import re
from shutil import copyfile


s3 = boto3.client('s3')

def lambda_handler(event, context):
    """
        The AWS Lambda handler

        @param dict event The event data
        @param LambdaContext context The runtime information
    """
    # Ensure convert and ffmpeg are executable
    copyfile("./convert", "/tmp/convert")
    st = os.stat('/tmp/convert')
    os.chmod('/tmp/convert', st.st_mode | stat.S_IEXEC)

    copyfile("./ffmpeg", "/tmp/ffmpeg")
    st = os.stat('/tmp/ffmpeg')
    os.chmod('/tmp/ffmpeg', st.st_mode | stat.S_IEXEC)

    # Grab the file details
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.unquote_plus(event['Records'][0]['s3']['object']['key']).decode('utf8')
    key_name, key_ext = os.path.splitext(key)

    # Extract the resize instructions json from the `image` file metadata
    image = s3.get_object(Bucket=bucket, Key=key)
    instructions = json.loads(image['Metadata']['instructions'])

    # Download the file
    image_original = tempfile.NamedTemporaryFile(suffix='.' + key_ext, delete=False)
    s3.download_file(bucket, key, image_original.name)

    for payload in instructions:
        if payload['suffix'] == 'display' and key_ext == '.gif':
            image_thumb = tempfile.NamedTemporaryFile(suffix='.webm', delete=False)

            # Convert the display version of the .gif to a .webm
            args=["/tmp/ffmpeg", "-y", "-i", image_original.name, "-c:v", "libvpx", "-crf", "10", "-b:v", "1M", "-c:a", "libvorbis", image_thumb.name]
            with open(os.devnull, 'w') as devnull:
                subprocess.check_call(args, stdout=devnull, stderr=devnull)

            thumbnail_ext = 'webm'
        else:
            # Create a .jpg thumbnail
            image_thumb = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)

            image_name = image_original.name
            if key_ext == '.gif':
                # If it's a .gif, only grab the first frame
                image_name = image_name + '[0]'

            args=["/tmp/convert", image_name, "-thumbnail", "%sx%s" % (payload['width'], payload['height']), "-quality", "%s" % payload['quality'], image_thumb.name]
            with open(os.devnull, 'w') as devnull:
                subprocess.check_call(args, stdout=devnull, stderr=devnull)

            thumbnail_ext = 'jpg'

        # Upload the thumbnail to s3
        thumbnail_key = key_name + '_' + payload['suffix'] + '.' + thumbnail_ext;
        s3.upload_file(image_thumb.name, bucket, thumbnail_key, ExtraArgs={'ACL': 'public-read', 'StorageClass': 'REDUCED_REDUNDANCY' })

        # Cleanup the local thumbnail file
        os.unlink(image_thumb.name)

    # Cleanup the downloaded original file
    os.unlink(image_original.name)
