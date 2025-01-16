import chromadb
import streamlit as st
from streamlit_chromadb_connection.chromadb_connection import ChromadbConnection

client = chromadb.PersistentClient(path="./chroma/")
collection = client.get_or_create_collection("first_collection")

collection.add(
    documents=[
        "This is a document about pineapple",
        "This is a document about oranges",
    ],
    ids=["id1", "id2"],
)

results = collection.query(
    query_texts=[
        "This is a query document about hawaii"
    ],  # Chroma will embed this for you
    n_results=2,  # how many results to return
)
print(results)


configuration = {
    "client": "PersistentClient",
    "path": "./chroma"
}

collection_name = "first_collection"

conn = st.connection("chromadb",
                     type=ChromadbConnection,
                     **configuration)
documents_collection_df = conn.get_collection_data(collection_name)
st.dataframe(documents_collection_df)