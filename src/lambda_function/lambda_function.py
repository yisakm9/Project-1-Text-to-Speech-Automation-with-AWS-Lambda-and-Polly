import boto3
import os
import json
import urllib.parse
import logging

# Initialize AWS clients
s3 = boto3.client('s3')
polly = boto3.client('polly')

# Retrieve the destination bucket name from environment variables
AUDIO_BUCKET = os.environ.get('AUDIO_BUCKET', 'default-audio-bucket')

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def synthesize_and_upload(text, output_key):
    """
    Converts text to speech using AWS Polly, saves it as an MP3, 
    and uploads it to the designated S3 audio bucket.
    """
    try:
        # Generate speech using Polly
        response = polly.synthesize_speech(
            Text=text,
            OutputFormat='mp3',
            VoiceId='Joanna'  # You can choose other voices
        )

        # Write the audio stream to a temporary file
        audio_file_path = '/tmp/output.mp3'
        with open(audio_file_path, 'wb') as f:
            f.write(response['AudioStream'].read())

        # Upload the temporary file to the audio S3 bucket
        s3.upload_file(audio_file_path, AUDIO_BUCKET, output_key)
        logger.info(f"Successfully uploaded audio to s3://{AUDIO_BUCKET}/{output_key}")
        
        return output_key

    except Exception as e:
        logger.error(f"Error during synthesis or upload: {e}")
        raise

def lambda_handler(event, context):
    """
    Main handler function. Determines the invocation source (API Gateway or S3)
    and processes the event accordingly.
    """
    logger.info("Event received: %s", json.dumps(event))

    # --- Case 1: Invoked by API Gateway ---
    # API Gateway events contain a 'body' key.
    if "body" in event and event["body"] is not None:
        try:
            body = json.loads(event["body"])
            text = body.get("text", "")

            if not text.strip():
                logger.warning("API Gateway request is missing 'text' field.")
                return {
                    "statusCode": 400,
                    "headers": {"Content-Type": "application/json"},
                    "body": json.dumps({"error": "Missing 'text' in request"})
                }

            output_key = "api-generated-speech.mp3"
            synthesize_and_upload(text, output_key)

            return {
                "statusCode": 200,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({
                    "message": "Audio generated successfully from API request.",
                    "audio_file": f"s3://{AUDIO_BUCKET}/{output_key}"
                })
            }
        except json.JSONDecodeError:
            logger.error("Invalid JSON received in API Gateway request body.")
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "Invalid JSON format in request body."})
            }

    # --- Case 2: Triggered by S3 upload ---
    # S3 trigger events contain a 'Records' key.
    if "Records" in event:
        try:
            record = event['Records'][0]
            source_bucket = record['s3']['bucket']['name']
            # Decode the object key to handle spaces and other special characters
            source_key = urllib.parse.unquote_plus(record['s3']['object']['key'])

            logger.info(f"Processing file '{source_key}' from bucket '{source_bucket}'.")

            # Download the source text file to a temporary location
            tmp_file_path = f'/tmp/{os.path.basename(source_key)}'
            s3.download_file(source_bucket, source_key, tmp_file_path)

            with open(tmp_file_path, 'r', encoding='utf-8') as f:
                text = f.read()

            # Create the output key by replacing the file extension
            output_key = os.path.splitext(source_key)[0] + '.mp3'
            synthesize_and_upload(text, output_key)

            return {
                "statusCode": 200,
                "body": json.dumps({
                    "message": "Audio generated successfully from S3 upload.",
                    "input_file": f"s3://{source_bucket}/{source_key}",
                    "audio_file": f"s3://{AUDIO_BUCKET}/{output_key}"
                })
            }
        except Exception as e:
            logger.error(f"Error processing S3 event: {e}")
            # Optionally, you can implement a dead-letter queue (DLQ) for failed events.
            raise

    # Fallback for unknown event sources
    logger.error("Handler invoked by an unknown event source.")
    return {
        "statusCode": 500,
        "body": json.dumps({"error": "Unknown invocation trigger"})
    }