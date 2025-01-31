# initial inspiration: https://huggingface.co/nvidia/NV-Embed-v2
import chromadb
from chromadb.utils import embedding_functions
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer

client = chromadb.PersistentClient(path="./chromadb_example/")
sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="multi-qa-mpnet-base-dot-v1")
collection = client.get_or_create_collection("Labour_Standards_IPGs_Jan312025", embedding_function=sentence_transformer_ef)

# Each query needs to be accompanied by an corresponding instruction describing the task.
task_name_to_instruct = {
    "example": "Given a question, retrieve passages that answer the question",
}

query_prefix = "Instruct: " + task_name_to_instruct["example"] + "\nQuery: "
queries = [
    "What are the rules applying to maternity leave?",
    "What does the notion of averaging of hours mean for federally regulated employers?",
]

# Load the data;
df1 = pd.read_csv(r"data\IPGs_Labour_standards.csv")
df2 = pd.read_csv(r"data/LS_Occupational_Health_and_Safety.csv")

# # passages = [
# #     "Since you're reading this, you are probably someone from a judo background or someone who is just wondering how judo techniques can be applied under wrestling rules. So without further ado, let's get to the question. Are Judo throws allowed in wrestling? Yes, judo throws are allowed in freestyle and folkstyle wrestling. You only need to be careful to follow the slam rules when executing judo throws. In wrestling, a slam is lifting and returning an opponent to the mat with unnecessary force.",
# #     "Below are the basic steps to becoming a radiologic technologist in Michigan:Earn a high school diploma. As with most careers in health care, a high school education is the first step to finding entry-level employment. Taking classes in math and science, such as anatomy, biology, chemistry, physiology, and physics, can help prepare students for their college studies and future careers.Earn an associate degree. Entry-level radiologic positions typically require at least an Associate of Applied Science. Before enrolling in one of these degree programs, students should make sure it has been properly accredited by the Joint Review Committee on Education in Radiologic Technology (JRCERT).Get licensed or certified in the state of Michigan.",
# # ]


passages_df1 = [str(i) for i in df1["text"].values]
passages_df2 = [str(i) for i in df2["text"].values]

# load model with tokenizer
model = SentenceTransformer("multi-qa-mpnet-base-dot-v1", trust_remote_code=False)
model.tokenizer.padding_side = "right"
model.tokenizer.pad_token = model.tokenizer.eos_token

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

passage_embeddings_df1 = model.encode(
    add_eos(passages_df1, model), 
    batch_size=batch_size, 
    normalize_embeddings=True
)

scores = (query_embeddings @ passage_embeddings_df1.T)

for i in scores:
    print(f"\nIndex of max score found: {np.argmax(i)}")
    print(f"\nThis matches the following IPG: \n{df1.loc[np.argmax(i),:]}")
print("\nPassage embeddings shape", passage_embeddings_df1.shape)
print("\nQuery embeddings shape", query_embeddings.shape)

# # adding documents to the collection (prints the documents added once done)
# collection.upsert(
#     documents=df1["text"].values.tolist(),
#     ids=df1["id"].values.tolist(),
#     metadatas=[{k:v} for k,v in zip(df1.title.values, df1.hyperlink.values)]
# )

# collection.upsert(
#     documents=df2["text"].values.tolist(),
#     ids=df2["id"].values.tolist(),
#     metadatas=[{k:v} for k,v in zip(df2.title.values, df2.hyperlink.values)]
# )

queries = [
    "What are the rules applying to maternity leave?",
    "What does the notion of averaging of hours mean for federally regulated employers?",
    "What is constructive dismissal?",
    "What is the definition of danger?",
    "How to prevent harmful behaviour at work?"
]

results = collection.query(
    query_texts=queries,        # Chroma will embed this for you
    n_results=3,                # how many results to return
    include=["metadatas", "distances", "documents"]
)

print(results.items()) # this works well

