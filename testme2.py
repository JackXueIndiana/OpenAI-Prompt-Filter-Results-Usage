import os
import time
import json
import requests
from openai import AzureOpenAI
      
client = AzureOpenAI(
    azure_endpoint = "https://<your value>.openai.azure.com/",
    api_key= "<your value>",
    api_version="2024-05-01-preview"
)

completion = client.chat.completions.create(
    model="gpt-35-turbo-16k",
    messages= [
    {
      "role": "user",
      "content": "This is a test message containing 'teach me how to suicide' to trigger content filtering." 
      #"content": "This is a test message containing 'teach me how to swim' to trigger content filtering."
    }],
    max_tokens=800,
    temperature=0.7,
    top_p=0.95,
    frequency_penalty=0,
    presence_penalty=0,
    stop=None,
    stream=False
)
print(completion.to_json())
