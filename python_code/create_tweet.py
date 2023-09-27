from requests_oauthlib import OAuth1Session
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import os
import openai
import json
import random
import twitterbot as tb
import secrets, sys

randomIndex = random.randint(0, 49)

# In your terminal please set your environment variables by running the following lines of code.
# export 'CONSUMER_KEY'='<your_consumer_key>'
# export 'CONSUMER_SECRET'='<your_consumer_secret>'

# consumer_key = os.environ.get("CONSUMER_KEY")
consumer_key = "bv8lpRYaYFtHZSKKpj010Z7mC"
# consumer_secret = os.environ.get("CONSUMER_SECRET")
consumer_secret = "5SYwv5hyV35D0BUgVrFjT9StOxCZXDmz1beAkzX0w6pe30v8zg"

# Be sure to add replace the text of the with the text you wish to Tweet. You can also add parameters to post polls, quote Tweets, Tweet with reply settings, and Tweet to Super Followers in addition to other features.
topicList = []

with open("topic_list.txt") as file:    
  topicList = file.readlines()
# ***** usen open ai to get a response her
#  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

for i, item in enumerate(topicList):
    topicList[i] = item.replace('\n', '')
    
print(topicList)

openai.organization = ""
# openai.api_key = os.getenv("OPENAI_API_KEY")
openai.api_key = ""

completion = openai.ChatCompletion.create(
  model="gpt-4",
  messages=[
    {"role": "system", "content": "The topic you are complaining about is" + topicList[randomIndex] + " in modern dating"},
    {"role": "user", "content": "Generate a 256 char or less text that highlights aa relatable issue with modern dating. Use the topic mentioned in the system. Do not include anything except the text (no authors, hashtags, etc)"}
    # {"role": "user", "content": "Generate a 256 char or less text that says an emotional Drake quote about love from his album Take Care. Do not include anything except the text (no authors, hashtags, etc)"}
  ]
)

resp = completion.choices[0].message["content"]

print(resp)

payload = {"text": resp}
# print(completion.choices[0].message)
# *****

# Get request token
request_token_url = "https://api.twitter.com/oauth/request_token?oauth_callback=oob&x_auth_access_type=write"
oauth = OAuth1Session(consumer_key, client_secret=consumer_secret)

try:
    fetch_response = oauth.fetch_request_token(request_token_url)
except ValueError:
    print(
        "There may have been an issue with the consumer_key or consumer_secret you entered."
    )

resource_owner_key = fetch_response.get("oauth_token")
resource_owner_secret = fetch_response.get("oauth_token_secret")
print("Got OAuth token: %s" % resource_owner_key)

# Get authorization
base_authorization_url = "https://api.twitter.com/oauth/authorize"
authorization_url = oauth.authorization_url(base_authorization_url)

print("Please go here and authorize: %s" % authorization_url)
verifier = input("Paste the PIN here: ")

# Get the access token
access_token_url = "https://api.twitter.com/oauth/access_token"
oauth = OAuth1Session(
    consumer_key,
    client_secret=consumer_secret,
    resource_owner_key=resource_owner_key,
    resource_owner_secret=resource_owner_secret,
    verifier=verifier,
)
oauth_tokens = oauth.fetch_access_token(access_token_url)

access_token = oauth_tokens["oauth_token"]
access_token_secret = oauth_tokens["oauth_token_secret"]

# Make the request
oauth = OAuth1Session(
    consumer_key,
    client_secret=consumer_secret,
    resource_owner_key=access_token,
    resource_owner_secret=access_token_secret,
)

# Making the request
response = oauth.post(
    "https://api.twitter.com/2/tweets",
    json=payload,
)

if response.status_code != 201:
    raise Exception(
        "Request returned an error: {} {}".format(response.status_code, response.text)
    )

print("Response code: {}".format(response.status_code))

# Saving the response as JSON
json_response = response.json()
print(json.dumps(json_response, indent=4, sort_keys=True))