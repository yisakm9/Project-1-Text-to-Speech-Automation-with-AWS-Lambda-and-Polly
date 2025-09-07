import pytest
import boto3
import json
import os
from moto import mock_aws

# Import the handler function from your lambda code
# This assumes the test file is in the root and the lambda is in src/lambda_function/
from src.lambda_function.lambda_function import lambda_handler

# --- Pytest Fixtures: Reusable Setup Code ---

@pytest.fixture(scope='function')
def aws_credentials():
    """Mocked AWS Credentials for moto."""
    os.environ['AWS_ACCESS_KEY_ID'] = 'testing'
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'
    os.environ['AWS_SECURITY_TOKEN'] = 'testing'
    os.environ['AWS_SESSION_TOKEN'] = 'testing'
    os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'

@pytest.fixture(scope='function')
def mock_environment(aws_credentials):
    """Set up the mocked AWS environment with S3 and Polly."""
    audio_bucket_name = 'test-voicevault-audio'
    os.environ['AUDIO_BUCKET'] = audio_bucket_name

    with mock_aws():
        s3 = boto3.client('s3', region_name='us-east-1')
        # No setup needed for Polly with moto, it's mocked automatically
        polly = boto3.client('polly', region_name='us-east-1')

        # Create the buckets the lambda function will interact with
        s3.create_bucket(Bucket=audio_bucket_name)
        s3.create_bucket(Bucket='test-voicevault-notes')

        yield s3, polly

# --- Test Cases ---

def test_s3_trigger_success(mock_environment):
    """
    Tests the successful execution of the Lambda when triggered by an S3 file upload.
    """
    s3_client, _ = mock_environment
    notes_bucket = 'test-voicevault-notes'
    audio_bucket = os.environ['AUDIO_BUCKET']
    note_key = 'mynote.txt'
    expected_audio_key = 'mynote.mp3'
    note_content = 'This is a test note for Polly.'

    # 1. SETUP: Upload a sample file to the mock notes S3 bucket
    s3_client.put_object(Bucket=notes_bucket, Key=note_key, Body=note_content)

    # 2. CREATE EVENT: Build a mock S3 event payload
    s3_event = {
        "Records": [{"s3": {"bucket": {"name": notes_bucket}, "object": {"key": note_key}}}]
    }

    # 3. INVOKE: Call the lambda handler with the mock event
    response = lambda_handler(s3_event, {})

    # 4. ASSERT: Verify the outcome
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert "Audio generated successfully from S3 upload" in body['message']
    assert body['audio_file'] == f"s3://{audio_bucket}/{expected_audio_key}"

    # Verify that the mp3 file was actually created in the audio bucket
    s3_objects = s3_client.list_objects_v2(Bucket=audio_bucket)
    assert s3_objects['KeyCount'] == 1
    assert s3_objects['Contents'][0]['Key'] == expected_audio_key

def test_api_gateway_trigger_success(mock_environment):
    """
    Tests the successful execution of the Lambda when triggered by API Gateway.
    """
    s3_client, _ = mock_environment
    audio_bucket = os.environ['AUDIO_BUCKET']
    expected_audio_key = "api-generated-speech.mp3"
    text_to_synthesize = "Hello from the API."

    # 1. CREATE EVENT: Build a mock API Gateway event payload
    api_event = {"body": json.dumps({"text": text_to_synthesize})}

    # 2. INVOKE: Call the handler
    response = lambda_handler(api_event, {})

    # 3. ASSERT: Verify the HTTP response
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert "Audio generated successfully from API request" in body['message']
    assert body['audio_file'] == f"s3://{audio_bucket}/{expected_audio_key}"

    # Verify the file was created in S3
    s3_objects = s3_client.list_objects_v2(Bucket=audio_bucket)
    assert s3_objects['KeyCount'] == 1
    assert s3_objects['Contents'][0]['Key'] == expected_audio_key

def test_api_gateway_missing_text_error(mock_environment):
    """
    Tests the error handling when the 'text' field is missing in an API Gateway request.
    """
    # 1. CREATE EVENT: Build a bad request payload
    api_event = {"body": json.dumps({"note": "This is not the right key"})}

    # 2. INVOKE: Call the handler
    response = lambda_handler(api_event, {})

    # 3. ASSERT: Verify the error response
    assert response['statusCode'] == 400
    body = json.loads(response['body'])
    assert body["error"] == "Missing 'text' in request"

def test_s3_trigger_with_spaces_in_key(mock_environment):
    """
    Tests that the handler correctly decodes an S3 object key with spaces.
    """
    s3_client, _ = mock_environment
    notes_bucket = 'test-voicevault-notes'
    audio_bucket = os.environ['AUDIO_BUCKET']
    note_key_encoded = 'my+test+file.txt' # S3 event sends the key URL-encoded
    note_key_decoded = 'my test file.txt'
    expected_audio_key = 'my test file.mp3'

    # 1. SETUP: Upload file with its decoded name
    s3_client.put_object(Bucket=notes_bucket, Key=note_key_decoded, Body="Testing spaces.")

    # 2. CREATE EVENT: Mimic the S3 event with the encoded key
    s3_event = {
        "Records": [{"s3": {"bucket": {"name": notes_bucket}, "object": {"key": note_key_encoded}}}]
    }

    # 3. INVOKE
    response = lambda_handler(s3_event, {})

    # 4. ASSERT
    assert response['statusCode'] == 200
    # Check that the output file has the correct, decoded name
    s3_objects = s3_client.list_objects_v2(Bucket=audio_bucket)
    assert s3_objects['Contents'][0]['Key'] == expected_audio_key