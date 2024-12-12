from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
)
import torch

# model loading and setup
model_name = "jhu-clsp/FollowIR-7B"
model = AutoModelForCausalLM.from_pretrained(model_name).cuda()
tokenizer = AutoTokenizer.from_pretrained(model_name, padding_side="left")
tokenizer.pad_token = tokenizer.eos_token
tokenizer.padding_side = "left"
token_false_id = tokenizer.get_vocab()["false"]
token_true_id = tokenizer.get_vocab()["true"]
template = """<s> [INST] You are an expert Google searcher, whose job is to determine if the following document is relevant to the query (true/false). Answer using only one word, one of those two choices.

Query: {query}
Document: {text}
Relevant (only output one word, either "true" or "false"): [/INST] """


## Lets define some example queries with instructions in the query and the passage
query1 = "What movies were written by James Cameron? A relevant document would describe a movie that was written by James Cameron only and not with anyone else"
query2 = "What movies were directed by James Cameron? A relevant document would describe any movie that was directed by James Cameron"
passages = [
    "Avatar: The Way of Water is a 2022 American epic science fiction film co-produced and directed by James Cameron, who co-wrote the screenplay with Rick Jaffa and Amanda Silver from a story the trio wrote with Josh Friedman and Shane Salerno. Distributed by 20th Century Studios, it is the sequel to Avatar (2009) and the second installment in the Avatar film series."
] * 2

prompts = [
    template.format(query=query, text=text)
    for (query, text) in zip([query1, query2], passages)
]
tokens = tokenizer(
    prompts,
    padding=True,
    truncation=True,
    return_tensors="pt",
    pad_to_multiple_of=None,
)

# move to cuda if desired
for key in tokens:
    tokens[key] = tokens[key].cuda()

# calculate the scores by comparing true and false tokens
batch_scores = model(**tokens).logits[:, -1, :]
true_vector = batch_scores[:, token_true_id]
false_vector = batch_scores[:, token_false_id]
batch_scores = torch.stack([false_vector, true_vector], dim=1)
batch_scores = torch.nn.functional.log_softmax(batch_scores, dim=1)
scores = batch_scores[:, 1].exp().tolist()
print(
    scores
)  # [0.0020704232156276703, 0.9999990463256836] first document is not relevant, as expected
