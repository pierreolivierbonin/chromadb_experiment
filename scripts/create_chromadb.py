import chromadb

client = chromadb.PersistentClient(path="chroma")
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
