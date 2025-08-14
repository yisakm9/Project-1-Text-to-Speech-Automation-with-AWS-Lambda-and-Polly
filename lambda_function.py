import boto3
import os
import json
import urllib.parse
import logging

s3 = boto3.client('s3')
polly = boto3.client('polly')

AUDIO_BUCKET = os.environ['AUDIO_BUCKET']

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def synthesize_and_upload(text, output_key):
    """Convert text to audio using Polly and upload to AUDIO_BUCKET"""
    # Generate speech
    response = polly.synthesize_speech(
        Text=text,
        OutputFormat='mp3',
        VoiceId='Joanna'
    )

    audio_file = '/tmp/output.mp3'
    with open(audio_file, 'wb') as f:
        f.write(response['AudioStream'].read())

    # Upload to audio bucket
    s3.upload_file(audio_file, AUDIO_BUCKET, output_key)
    logger.info(f"Uploaded audio to {AUDIO_BUCKET}/{output_key}")
    return output_key

def lambda_handler(event, context):
    logger.info("Event: %s", json.dumps(event))

    # Case 1: Invoked by API Gateway
    if "body" in event:
        body = json.loads(event["body"])
        text = body.get("text", "")

        if not text.strip():
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Missing 'text' in request"})
            }

        output_key = "api_request.mp3"
        synthesize_and_upload(text, output_key)

        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "Audio generated from API",
                "audio_file": f"s3://{AUDIO_BUCKET}/{output_key}"
            })
        }

    # Case 2: Triggered by S3 upload
    record = event['Records'][0]
    bucket = record['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(record['s3']['object']['key'])

    tmp_file = '/tmp/input.txt'
    s3.download_file(bucket, key, tmp_file)

    with open(tmp_file, 'r', encoding='utf-8') as f:
        text = f.read()

    # Use same key but with .mp3 extension
    output_key = key.rsplit('.', 1)[0] + '.mp3'
    synthesize_and_upload(text, output_key)

    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "Audio generated from S3 upload",
            "audio_file": f"s3://{AUDIO_BUCKET}/{output_key}"
        })
    }
