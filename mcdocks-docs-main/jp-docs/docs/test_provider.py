from google.ai.generativelanguage import GenerativeServiceClient
from google.api_core.client_options import ClientOptions

import os
from dotenv import load_dotenv, find_dotenv


# these expect to find a .env file at the directory above the lesson.                                                                                                                     # the format for that file is (without the comment)                                                                                                                                       #API_KEYNAME=AStringThatIsTheLongAPIKeyFromSomeService                                                                                                                                     
def load_env():
    _ = load_dotenv(find_dotenv())


def get_gemini_api_key():
    load_env()
    gemini_api_key = os.getenv("AIzaSyC2pbBSTd_5UwINjE_9_0vPyXKXWuXLVnk")
    return gemini_api_key


GENERATIVE_SERVICE_ENDPOINT = "https://generativelanguage.googleapis.com"


# Create a client with the appropriate settings
client_options = ClientOptions(api_endpoint=GENERATIVE_SERVICE_ENDPOINT)
client = GenerativeServiceClient(client_options=client_options)

api_key = get_gemini_api_key()
# Check the key here
print("AIzaSyC2pbBSTd_5UwINjE_9_0vPyXKXWuXL:", api_key)

# Set the API key in client headers, if required, and test a sample call
client._transport._credentials = api_key  