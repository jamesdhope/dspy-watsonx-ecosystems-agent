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

from watsonxModel import Watson, generate_access_token

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
        prediction = self.generate_answer(context=context, question=question, max_tokens=500)
        return dspy.Prediction(context=context, answer=prediction.answer) 

# Uncompiled module prediction
answer = dspy.Predict(GenerateAnswer)(context="", question="How do I go about designing an ecosystems architecture?")
print(answer)

# Validation logic: check that the predicted answer is correct.
# Also check that the retrieved context does actually contain that answer.
def validate_context_and_answer(example, pred, trace=None):
    answer_EM = dspy.evaluate.answer_exact_match(example, pred)
    answer_PM = dspy.evaluate.answer_passage_match(example, pred)
    return answer_EM and answer_PM

# Set up a basic teleprompter, which will compile our RAG program.
teleprompter = BootstrapFewShot(metric=validate_context_and_answer)

dataset = HotPotQA(train_seed=1, train_size=20, eval_seed=2023, dev_size=50, test_size=0)
# Tell DSPy that the 'question' field is the input. Any other fields are labels and/or metadata.
trainset = [x.with_inputs('question') for x in dataset.train]
devset = [x.with_inputs('question') for x in dataset.dev]
len(trainset), len(devset)

# 2. Recompile the RAG program
compiled_rag = teleprompter.compile(student=RAG(), trainset=trainset)

# Compiled module prediction
answer = dspy.Predict(GenerateAnswer)(context="", question="How do I go about designing an ecosystems architecture?")
print(answer)

#watsonx.inspect_history(n=3)

#dspy.candidate_programs

