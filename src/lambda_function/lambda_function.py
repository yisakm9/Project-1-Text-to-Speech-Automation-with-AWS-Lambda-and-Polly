import boto3
import os
import json
import urllib.parse
import logging

s3 = boto3.client('s3')
polly = boto3.client('polly')

# REMOVE the global variable from here.
# AUDIO_BUCKET = os.environ.get('AUDIO_BUCKET', 'default-audio-bucket')

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# MODIFY the function to accept the bucket name as a parameter.
def synthesize_and_upload(text, output_key, audio_bucket_name):
    """Convert text to audio using Polly and upload to the specified bucket"""
    try:
        response = polly.synthesize_speech(
            Text=text,
            OutputFormat='mp3',
            VoiceId='Joanna'
        )

        audio_file_path = '/tmp/output.mp3'
        with open(audio_file_path, 'wb') as f:
            f.write(response['AudioStream'].read())

        # Use the passed-in bucket name.
        s3.upload_file(audio_file_path, audio_bucket_name, output_key)
        logger.info(f"Successfully uploaded audio to s3://{audio_bucket_name}/{output_key}")
        
        return output_key
    except Exception as e:
        logger.error(f"Error during synthesis or upload: {e}")
        raise

def lambda_handler(event, context):
    """
    Main handler function. Fetches config from environment and routes the event.
    """
    # GET the environment variable at RUN-TIME.
    audio_bucket = os.environ.get('AUDIO_BUCKET')
    if not audio_bucket:
        logger.error("FATAL: AUDIO_BUCKET environment variable is not set.")
        # Fail hard if the configuration is missing.
        raise ValueError("AUDIO_BUCKET environment variable not configured.")

    logger.info("Event received: %s", json.dumps(event))

    # --- Case 1: Invoked by API Gateway ---
    if "body" in event and event["body"] is not None:
        try:
            body = json.loads(event["body"])
            text = body.get("text", "")

            if not text.strip():
                # ... (error handling)
                return { "statusCode": 400, "body": json.dumps({"error": "Missing 'text' in request"}) }

            output_key = "api-generated-speech.mp3"
            # PASS the bucket name to the function.
            synthesize_and_upload(text, output_key, audio_bucket)

            return {
                "statusCode": 200,
                "body": json.dumps({
                    "message": "Audio generated successfully from API request.",
                    "audio_file": f"s3://{audio_bucket}/{output_key}"
                })
            }
        except Exception as e:
            # ... (error handling)
            logger.error(f"Error processing API Gateway event: {e}")
            raise

    # --- Case 2: Triggered by S3 upload ---
    if "Records" in event:
        try:
            record = event['Records'][0]
            source_bucket = record['s3']['bucket']['name']
            source_key = urllib.parse.unquote_plus(record['s3']['object']['key'])

            # ... (download logic)
            tmp_file_path = f'/tmp/{os.path.basename(source_key)}'
            s3.download_file(source_bucket, source_key, tmp_file_path)
            with open(tmp_file_path, 'r', encoding='utf-8') as f:
                text = f.read()

            output_key = os.path.splitext(source_key)[0] + '.mp3'
            # PASS the bucket name to the function.
            synthesize_and_upload(text, output_key, audio_bucket)

            return {
                "statusCode": 200,
                "body": json.dumps({
                    "message": "Audio generated successfully from S3 upload.",
                    "input_file": f"s3://{source_bucket}/{source_key}",
                    "audio_file": f"s3://{audio_bucket}/{output_key}"
                })
            }
        except Exception as e:
            logger.error(f"Error processing S3 event: {e}")
            raise

    # Fallback for unknown event sources
    return { "statusCode": 500, "body": json.dumps({"error": "Unknown invocation trigger"}) }