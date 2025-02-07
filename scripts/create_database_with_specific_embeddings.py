# initial inspiration: https://huggingface.co/nvidia/NV-Embed-v2
import chromadb
from chromadb.utils import embedding_functions
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer

client = chromadb.PersistentClient(path="../chromadb_directory")
sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="multi-qa-mpnet-base-dot-v1")
collection = client.get_or_create_collection("Labour_Program_Feb072025", 
                                             embedding_function=sentence_transformer_ef,
                                             metadata={
                                                 "hnsw:space":"cosine",
                                             })

# Each query needs to be accompanied by an corresponding instruction describing the task. Below is an example:
task_name_to_instruct = {
    "example": "Given a question, retrieve passages that answer the question",
}

query_prefix = "Instruct: " + task_name_to_instruct["example"] + "\nQuery: "
queries = [
    "What are the rules applying to maternity leave?",
    "What does the notion of averaging of hours mean for federally regulated employers?",
]

# Load the data
df1 = pd.read_csv(r"outputs/clc.csv")
df2 = pd.read_csv(r"outputs\clsr.csv")
df3 = pd.read_csv(r"outputs\IPGs_Labour_standards.csv")
df4 = pd.read_csv(r"outputs\LS_Occupational_Health_and_Safety.csv")

passages_df1 = [str(i) for i in df1["text"].values]
passages_df2 = [str(i) for i in df2["text"].values]
passages_df3 = [str(i) for i in df3["text"].values]
passages_df4 = [str(i) for i in df4["text"].values]

# load model with tokenizer
model = SentenceTransformer("multi-qa-mpnet-base-dot-v1", trust_remote_code=False)
model.tokenizer.padding_side = "right"
model.tokenizer.pad_token = model.tokenizer.eos_token

def add_eos(input_examples, model):
    input_examples = [
        input_example + model.tokenizer.eos_token for input_example in input_examples
    ]
    return input_examples


# get the embeddings for the query + the documents
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

# adding documents to the collection (prints the documents added once done)
collection.upsert(
    documents=df1["text"].values.tolist(),
    ids=df1["id"].values.tolist(),
    metadatas=[{ttl:str([sect, hrchy, hlink])} for # this is an unresolved issue with chromadb (we have to convert the list to str currently)
               ttl, sect, hrchy, hlink in 
               zip(df1.title.values, df1.section_number.values, df1.hierarchy.values, df1.hyperlink.values)]
)

collection.upsert(
    documents=df2["text"].values.tolist(),
    ids=df2["id"].values.tolist(),
    metadatas=[{ttl:str([sect, hrchy, hlink])} for
               ttl, sect, hrchy, hlink in 
               zip(df2.title.values, df2.section_number.values, df2.hierarchy.values, df2.hyperlink.values)]
)

collection.upsert(
    documents=df3["text"].values.tolist(),
    ids=df3["id"].values.tolist(),
    metadatas=[{k:v} for k,v in zip(df3.title.values, df3.hyperlink.values)]
)

collection.upsert(
    documents=df4["text"].values.tolist(),
    ids=df4["id"].values.tolist(),
    metadatas=[{k:v} for k,v in zip(df4.title.values, df4.hyperlink.values)]
)

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
    include=["metadatas", "distances", "documents", "embeddings"]
)

print(results.items()) # this works well
print("hello")

