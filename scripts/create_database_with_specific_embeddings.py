# inspiration: https://huggingface.co/nvidia/NV-Embed-v2
import chromadb
from chromadb.utils import embedding_functions
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer

client = chromadb.PersistentClient(path="./chroma/")
sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="multi-qa-mpnet-base-dot-v1")
collection = client.get_or_create_collection("first_collection", embedding_function=sentence_transformer_ef)

# Each query needs to be accompanied by an corresponding instruction describing the task.
task_name_to_instruct = {
    "example": "Given a question, retrieve passages that answer the question",
}

query_prefix = "Instruct: " + task_name_to_instruct["example"] + "\nQuery: "
queries = [
    "What are the rules applying to maternity leave?",
    "What does the notion of averaging of hours mean for federally regulated employers?",
]

# No instruction needed for retrieval passages
df = pd.read_csv(r"data\LS_IPGs_clean.csv")
# passages = [
#     "Since you're reading this, you are probably someone from a judo background or someone who is just wondering how judo techniques can be applied under wrestling rules. So without further ado, let's get to the question. Are Judo throws allowed in wrestling? Yes, judo throws are allowed in freestyle and folkstyle wrestling. You only need to be careful to follow the slam rules when executing judo throws. In wrestling, a slam is lifting and returning an opponent to the mat with unnecessary force.",
#     "Below are the basic steps to becoming a radiologic technologist in Michigan:Earn a high school diploma. As with most careers in health care, a high school education is the first step to finding entry-level employment. Taking classes in math and science, such as anatomy, biology, chemistry, physiology, and physics, can help prepare students for their college studies and future careers.Earn an associate degree. Entry-level radiologic positions typically require at least an Associate of Applied Science. Before enrolling in one of these degree programs, students should make sure it has been properly accredited by the Joint Review Committee on Education in Radiologic Technology (JRCERT).Get licensed or certified in the state of Michigan.",
# ]

passages = [str(i) for i in df["text"].values]

# load model with tokenizer
model = SentenceTransformer("multi-qa-mpnet-base-dot-v1", trust_remote_code=False)
model.tokenizer.padding_side = "right"
model.tokenizer.pad_token = model.tokenizer.eos_token
print("EOS token: ", model.tokenizer.pad_token)


def add_eos(input_examples, model):
    input_examples = [
        input_example + model.tokenizer.eos_token for input_example in input_examples
    ]
    return input_examples


# get the embeddings
batch_size = 1
query_embeddings = model.encode(
    add_eos(queries, model),
    batch_size=batch_size,
    prompt=query_prefix,
    normalize_embeddings=True,
)
passage_embeddings = model.encode(
    add_eos(passages, model), batch_size=batch_size, normalize_embeddings=True
)

scores = (query_embeddings @ passage_embeddings.T)
print(scores)

for i in scores:
    print(f"Index of max score found: {np.argmax(i)}")
    print(f"This matches the following IPG: {df.loc[np.argmax(i),:]}")
print("Passage embeddings shape", passage_embeddings.shape)
print("Query embeddings shape", query_embeddings.shape)


collection.add(
    documents=df["text"].values,
    ids=df["id"].values,
)

queries = [
    "What are the rules applying to maternity leave?",
    "What does the notion of averaging of hours mean for federally regulated employers?",
]
results = collection.query(
    query_texts=queries,        # Chroma will embed this for you
    n_results=3,                # how many results to return
)
print(results)
