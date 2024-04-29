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
from MilvusRM import MilvusRM
from dspy.datasets import HotPotQA
from dsp import LM
import dspy

token = generate_access_token(os.environ['WATSONX_APIKEY'])
watsonx = Watson(model="meta-llama/llama-3-70b-instruct",api_key=token)

dspy.settings.configure(lm=watsonx, trace=[])
retriever_model = MilvusRM(collection_name="wikipedia_articles",uri="http://localhost:19530")
dspy.settings.configure(rm=retriever_model)

# signature for our RAG Agent
class GenerateAnswer(dspy.Signature):
    """You are a helpful, friendly assistant that can answer questions"""

    context = dspy.InputField(desc="may contain relevant facts")
    question = dspy.InputField()
    answer = dspy.OutputField(prefix="Reasoning: Let's think step by step but give a complete final answer of at least a couple of sentences",desc="give a complete answer of at least a couple of sentences")

class RAG(dspy.Module):
    def __init__(self, num_passages=3):
        super().__init__()

        self.retrieve = retriever_model #dspy.Retrieve(k=num_passages)
        self.generate_answer = dspy.ReAct(signature=GenerateAnswer) #dspy.ReAct(GenerateAnswer) #dspy.Predict(GenerateAnswer) 
    
    def forward(self, question):
        context = self.retrieve(question).passages
        prediction = self.generate_answer(context=context, question=question)
        return dspy.Prediction(context=context, answer=prediction.answer) 

# Initialize your app with your bot token and signing secret
app = App(
    token="xoxb-7057314946368-7057368175488-H8RZtw3gfeayJVkm2fi9OiVh",
    signing_secret="7ffa54b4f54f481671440f40f6ff3c18"
)

rag = RAG()

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
        say(answer.answer)

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
