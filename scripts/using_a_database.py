import chromadb
import yaml

client = chromadb.PersistentClient()

collection = client.get_collection(name="first_collection")

print(
    collection.query(
        query_texts=[
            "This is a query document about hawaii"
        ],  # Chroma will embed this for you
        n_results=2,  # how many results to return
    )
)
