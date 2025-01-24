import os
import json
from pymongo import MongoClient
from datetime import datetime
from openai import OpenAI
import logging
import time
import sys
import boto3

sys.path.append(os.path.join(os.path.dirname(__file__), 'dist'))

ssm_client = boto3.client('ssm')

logger = logging.getLogger()
logger.setLevel(logging.INFO)
client = None

def get_secure_parameter(param_name):
    logger.info(f"Retrieving SSM parameter: {param_name}")
    response = ssm_client.get_parameter(Name=param_name, WithDecryption=True)
    return response['Parameter']['Value']

def get_mongo_client():
    global client
    if not client:
        # Retrieve the parameter name from the environment variable
        mongo_uri_param_name = os.environ.get('MONGO_URI_PARAM')
        if not mongo_uri_param_name:
            logger.error("MONGO_URI_PARAM environment variable is not set.")
            raise Exception("MONGO_URI_PARAM environment variable is missing.")
        
        # Pass the SSM parameter name to the get_secure_parameter function
        logger.info(f"Retrieving SSM parameter: {mongo_uri_param_name}")
        mongo_uri = get_secure_parameter(mongo_uri_param_name)
        
        # Log the sanitized URI (avoid logging sensitive credentials)
        logger.info(f"Successfully retrieved MongoDB URI. Connecting to cluster: {mongo_uri.split('@')[-1].split('/')[0]}")
        client = MongoClient(mongo_uri)
    return client



def call_openai_with_retries(client, url, retries=5, delay=1):
    """Call OpenAI with exponential backoff for retries."""
    for attempt in range(retries):
        try:
            completion = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a witty assistant that generates clever 404 error messages based on the content of the url."},
                    {"role": "user", "content": f"Generate a witty 404 error message for the URL: {url}"}
                ],
                max_tokens=50,
            )
            return completion.choices[0].message.content
        except Exception as e:
            if "429" in str(e):  # Handle rate-limiting errors
                logger.warning(f"Rate limit hit. Retrying in {delay} seconds... (Attempt {attempt + 1}/{retries})")
                time.sleep(delay)
                delay *= 2  # Exponential backoff
            else:
                logger.error(f"Unhandled OpenAI error: {str(e)}")
                raise
    raise Exception("Exceeded maximum retries for OpenAI API")

def lambda_handler(event, context):

    # Parse event (API Gateway input)
    try:
        body = json.loads(event.get("body", "{}"))
        url = body.get("url")
        if not url:
            return {"statusCode": 400, "body": json.dumps({"error": "Missing URL"})}
    except Exception as e:
        return {"statusCode": 400, "body": json.dumps({"error": str(e)})}
    logger.info(f"Parsed URL: {url}")
    
    

    # Connect to MongoDB
    logger.info(f"Connecting to MongoDB with URI: {os.getenv('MONGO_URI')}")
    try:
        db = get_mongo_client()["Witty404"]
        collection = db["cache"]
    except Exception as e:
        return {"statusCode": 500, "body": f"Error connecting to MongoDB: {str(e)}"}
    # Check if URL is cached
    cached = collection.find_one({"_id": url})
    if cached:
        return {"statusCode": 200, "body": json.dumps({"wittyText": cached["wittyText"]})}

    # Generate witty text using OpenAI
    try:
        # Fetch the OpenAI API key securely
        logger.info(f"Calling OpenAI API for URL: {url}")
        openai_api_key = get_secure_parameter(os.environ['OPENAI_API_KEY'])
        openai_client = OpenAI(api_key=openai_api_key)  # Pass the API key to OpenAI client
        witty_text = call_openai_with_retries(openai_client, url)
    except Exception as e:
        return {"statusCode": 500, "body": f"Error generating witty text: {str(e)}"}
    
    # Cache response in MongoDB
    collection.insert_one({"_id": url, "wittyText": witty_text, "createdAt": datetime.utcnow()})
    return {"statusCode": 200, "body": json.dumps({"wittyText": witty_text})}
