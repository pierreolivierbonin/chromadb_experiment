import chromadb
from chromadb.utils import embedding_functions
import pandas as pd

# create client
client = chromadb.PersistentClient(path="../chromadb_directory")

# load embedding model
sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="multi-qa-mpnet-base-dot-v1")

# fetch or create collection
collection = client.get_or_create_collection("Labour_Program_Feb132025_augmented", 
                                             embedding_function=sentence_transformer_ef,
                                             metadata={
                                                 "hnsw:space":"cosine",
                                             })

# Load the data to be embedded
df1 = pd.read_csv(r"outputs/clc.csv", encoding='utf-8')
df1.fillna(value="N/A", inplace=True)
df2 = pd.read_csv(r"outputs/clsr.csv", encoding='utf-8')
df2.fillna(value="N/A", inplace=True)
df3 = pd.read_csv(r"outputs/ipgs.csv", encoding='utf-8')
df3.fillna(value="N/A", inplace=True)
df4 = pd.read_csv(r"outputs/pages.csv", encoding='utf-8')
df4.fillna(value="N/A", inplace=True)

augmented_passages_df1 = [str({id:[title, section, hl, text]}) for id, title, section, hl, text in zip(
    df1["id"].values, 
    df1["title"].values,
    df1["section_number"].values, 
    df1["hyperlink"].values, 
    df1["text"].values,)]
augmented_passages_df2 = [str({id:[title, section, hl, text]}) for id, title, section, hl, text in zip(
    df2["id"].values, 
    df2["title"].values,
    df2["section_number"].values, 
    df2["hyperlink"].values, 
    df2["text"].values,)]
augmented_passages_df3 = [str({id:[title, hl, text]}) for id, title, hl, text in zip(
    df3["id"].values, 
    df3["title"].values,
    df3["hyperlink"].values, 
    df3["text"].values,)]
augmented_passages_df4 = [str({id:[title, hl, text]}) for id, title, hl, text in zip(
    df4["id"].values, 
    df4["title"].values,
    df4["hyperlink"].values, 
    df4["text"].values,)]

# adding documents to the collection (prints the documents added once done)
collection.upsert(
    documents=augmented_passages_df1,
    ids=df1["id"].values.tolist(),
    metadatas=[{ttl:str([sect, hrchy, hlink])} for # this is an unresolved issue with chromadb (we have to convert the list to str currently)
               ttl, sect, hrchy, hlink in 
               zip(df1.title.values, df1.section_number.values, df1.hierarchy.values, df1.hyperlink.values)]
)

collection.upsert(
    documents=augmented_passages_df2,
    ids=df2["id"].values.tolist(),
    metadatas=[{ttl:str([sect, hrchy, hlink])} for
               ttl, sect, hrchy, hlink in 
               zip(df2.title.values, df2.section_number.values, df2.hierarchy.values, df2.hyperlink.values)]
)

collection.upsert(
    documents=augmented_passages_df3,
    ids=df3["id"].values.tolist(),
    metadatas=[{k:v} for k,v in zip(df3.title.values, df3.hyperlink.values)]
)

collection.upsert(
    documents=augmented_passages_df4,
    ids=df4["id"].values.tolist(),
    metadatas=[{k:v} for k,v in zip(df4.title.values, df4.hyperlink.values)]
)

# quick check if the output makes sense
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

