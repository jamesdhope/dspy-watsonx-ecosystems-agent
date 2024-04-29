#def metric(example: dspy.Example, prediction, trace=None):
#        
#    transcript, answer, summary = example.transcript, example.summary, prediction.summary
#    
#    with dspy.context(lm=watsonx):
#        # This next line is the one that results in the error when called from the optimizer.
#        content_eval = dspy.Predict(Assess)(summary=summary, assessment_question=\
#                            f"Is the assessed text a good summary of this transcript, capturing all the important details?\n\n{transcript}?")
#    return content_eval.to_lower().endswith('yes')

# Define the signature for automatic assessments.
#class Assess(dspy.Signature):
#    """Assess the quality of a tweet along the specified dimension."""

#    assessed_text = dspy.InputField()
#    assessment_question = dspy.InputField()
#    assessment_answer = dspy.OutputField(desc="Yes or No")

#def metric(example, pred, trace=None):

#    engaging = "Does the assessed text make for a self-contained, engaging tweet?"
#    correct = f"The text should answer `{example.question}` with `{pred}`. Does the assessed text contain this answer?"
    
#    print("correct",correct)

#    with dspy.context(lm=watsonx):
#        correct =  dspy.Predict(Assess)(assessed_text=pred, assessment_question=correct)
#        engaging = dspy.Predict(Assess)(assessed_text=pred, assessment_question=engaging)

#    correct, engaging = [m.assessment_answer.lower() == 'yes' for m in [correct, engaging]]
#    score = (correct + engaging) if correct and (len(example.question) <= 280) else 0

#    if trace is not None: return score >= 2
#    return score / 2.0