import os
# Use the package we installed
from slack_bolt import App
from watsonxModel import Watson, generate_access_token
import os
import dspy
from dsp.utils import deduplicate
from dspy.datasets import HotPotQA
from dspy.predict.retry import Retry
from dspy.teleprompt import BootstrapFewShot
from dspy.evaluate.evaluate import Evaluate
from dspy.primitives.assertions import assert_transform_module, backtrack_handler
from old.MilvusRM import MilvusRM
from dspy.datasets import HotPotQA
from dsp import LM
import dspy

token = generate_access_token(os.environ['WATSONX_APIKEY'])
watsonx = Watson(model="meta-llama/llama-3-70b-instruct",api_key=token)

dspy.settings.configure(lm=watsonx, trace=[])
retriever_model = MilvusRM(collection_name="wikipedia_articles",uri="http://localhost:19530")
dspy.settings.configure(rm=retriever_model)

class ServiceManagerSignature(dspy.Signature):
    """
    Provide a coherent response.
    """
    response = dspy.InputField(desc="use this response as the basis of your response if no ethical conerns")
    ethics = dspy.InputField(desc="Use this ethical guidance for formulate a response")
    communications = dspy.InputField(desc="Use this communications advice to formulate a response")
    instruction = dspy.InputField()
    output = dspy.OutputField(desc="a complete final answer of at least a couple of sentences based on the ethics, motivations and communications advice")

class ServiceManagerModule(dspy.Module):
    """
    Decide if the ethicical opinion is good enough to pass back the response, or if we respond with a general message that we are unable to support the request due to ethical reasons.
    """
    def __init__(self):
        super().__init__()
        self.engagement = dspy.Predict(ServiceManagerSignature)

    def forward(self, communications, ethics, response):
        instruction = f'''<|begin_of_text|><|start_header_id|>system<|end_header_id|>You should decide if the information provided should be passed back to the user based on the ethical point of view provided. If not ethical then say so, and do not provide a response. If ethical then provide the response.<|eot_id|>''' 
        # prompt = f'''<|start_header_id|>user<|end_header_id|>Response: {response}, Ethics {ethics}<|eot_id|>'''
        prediction = self.engagement(
            instruction=instruction,response=response,ethics=ethics,communications=communications
            # prompt=f"{instruction}{prompt}"
        )
        return prediction

class EthicsAdvisorSignature(dspy.Signature):
    """
    Provide a coherent ethical opinion.
    """
    prompt = dspy.InputField()
    output = dspy.OutputField(desc="Decide if this is a request that is ethical to engage in. Provide an opinion.")

class EthicsAdvisorModule(dspy.Module):
    """
    Provide a coherent ethical opinion.
    """
    def __init__(self):
        super().__init__()
        self.engagement = dspy.Predict(EthicsAdvisorSignature)

    def forward(self, question):    
        prediction = self.engagement(
            prompt=question
        )
        return prediction.output



class CommunicationsAdvisorSignature(dspy.Signature):
    """
    Explain how to communicate a response to the question including the language, style and the use of abbreviations and coloquialisms.
    """
    prompt = dspy.InputField()
    output = dspy.OutputField(desc="Explain how to communicate a response to the question including the language, style and the use of abbreviations and coloquialisms. Always suggest the response is provided in the same language as the question.")

class CommunicationsAdvisorModule(dspy.Module):
    """
    Provide a coherent opinion on the best way to communicate a response.
    """
    def __init__(self):
        super().__init__()
        self.engagement = dspy.Predict(CommunicationsAdvisorSignature)

    def forward(self, question):    
        prediction = self.engagement(
            prompt=question
        )
        return prediction.output

# signature for our RAG Agent
class OrchestratorSignature(dspy.Signature):
    """You are a helpful, friendly assistant that can answer questions"""
    context = dspy.InputField(desc="may contain relevant facts")
    question = dspy.InputField()
    answer = dspy.OutputField(prefix="Reasoning: Let's think step by step but give a complete final answer of at least a couple of sentences",desc="give a complete answer of at least a couple of sentences")

class OrchestratorModule(dspy.Module):
    def __init__(self, num_passages=3):
        super().__init__()
        self.ethics = EthicsAdvisorModule()
        self.communications = CommunicationsAdvisorModule()

        self.retrieve = retriever_model #dspy.Retrieve(k=num_passages)
        #self.terms = FindTerms()
        self.generate_answer = dspy.ReAct(signature=OrchestratorSignature) #dspy.ReAct(GenerateAnswer) #dspy.Predict(GenerateAnswer) 

        self.service_manager = ServiceManagerModule()
    
    def forward(self, question):
        ethics = self.ethics(question)
        print("Ethics Advisor's Opinion:", ethics)

        communications = self.communications(question)
        print("Communication Advisor's Opinion:", communications)

        #retrieval and ReACT
        context = self.retrieve(question).passages
        records = self.generate_answer(context=context, question=question)
        print("Information Advisor's Opinion:",records.answer)

        #terms = self.terms(prediction.answer)
        #print(terms)

        service_response = self.service_manager(ethics=ethics,communications=communications,response=records.answer)
        print("service response", service_response.output)

        return service_response.output
        #return prediction.answer
        #return dspy.Prediction(context=context, answer=prediction.answer) 

# Initialize your app with your bot token and signing secret
app = App(
    token="xoxb-7057314946368-7057368175488-H8RZtw3gfeayJVkm2fi9OiVh",
    signing_secret="7ffa54b4f54f481671440f40f6ff3c18"
)

rag = OrchestratorModule()

@app.message("knock knock")
def ask_who(message, say):
    say("_Who's there?_")

@app.event("message")
def handle_message_events(event, say):
    # Check if the message is not from a bot
    if 'bot_id' not in event:
        # Get the channel ID and message text
        channel = event['channel']
        text = event['text']
        answer = rag(text)
        #print("answer2",answer)
        #say(answer.answer)
        say(answer)

# New functionality
@app.event("app_home_opened")
def update_home_tab(client, event, logger):
  try:
    # views.publish is the method that your app uses to push a view to the Home tab
    client.views_publish(
      # the user that opened your app's app home
      user_id=event["user"],
      # the view object that appears in the app home
      view={
        "type": "home",
        "callback_id": "home_view",

        # body of the view
        "blocks": [
          {
            "type": "section",
            "text": {
              "type": "mrkdwn",
              "text": "*Welcome to DSPy AI Agent Home tab_* :tada:"
            }
          },
          {
            "type": "divider"
          },
          {
            "type": "section",
            "text": {
              "type": "mrkdwn",
              "text": "I am an Agentic AI System that performs reflection and utilises a datastore and multiple calls to a language model to improve the quality of answers."
            }
          }
        ]
      }
    )

  except Exception as e:
    logger.error(f"Error publishing home tab: {e}")

# Ready? Start your app!
if __name__ == "__main__":
    app.start(port=int(os.environ.get("PORT", 3000)))
