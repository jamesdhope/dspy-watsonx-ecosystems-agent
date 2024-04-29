import dspy
from dsp.utils import deduplicate
from dspy.datasets import HotPotQA
from dspy.predict.retry import Retry
from dspy.teleprompt import BootstrapFewShot, BootstrapFewShotWithRandomSearch
from dspy.evaluate.evaluate import Evaluate
from dspy.primitives.assertions import assert_transform_module, backtrack_handler

import os
import requests
from dsp import LM
import dspy

class Watson(LM):
    def __init__(self,model,api_key):
        self.kwargs = {
            "decoding_method": "sample",
            #"model": model,
            "temperature": 0.7,
            "max_new_tokens": 100,
            "max_tokens": 100,
            "temperature": 0.4,
            "top_k": 50,
		    "top_p": 1,
		    "repetition_penalty": 1
        }
        self.model = model
        self.api_key = api_key
        self.provider = "default"
        self.history = []
        
        self.base_url = os.environ['WATSONX_URL']
        self.project_id = os.environ['WATSONX_PROJECTID']

    def basic_request(self, prompt: str, **kwargs):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json",
            "content-type": "application/json"
        }

        data = {
            "parameters": self.kwargs,
            "model_id": self.model,
            "input": prompt,
            "project_id": self.project_id
        }

        #print("payload:",self.base_url, headers, data)

        response = requests.post(self.base_url, headers=headers, json=data)
        response = response.json()

        self.history.append({
            "prompt": prompt,
            "response": response,
            "kwargs": kwargs,
        })
        return response

    def __call__(self, prompt, only_completed=True, return_sorted=False, **kwargs):
        
        response = self.request(prompt, **kwargs)

        #print(response)

        completions = [result["generated_text"] for result in response["results"]]

        return completions
    
import requests

def generate_access_token(api_key):
    headers={}
    headers["Content-Type"] = "application/x-www-form-urlencoded"
    headers["Accept"] = "application/json"
    data = {
        "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
        "apikey": api_key
    }
    response = requests.post('https://iam.cloud.ibm.com/identity/token', data=data, headers=headers)
    json_data = response.json()
    iam_access_token = json_data['access_token']
    return iam_access_token