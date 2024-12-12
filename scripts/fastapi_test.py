from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import chromadb

app = FastAPI()
client = chromadb.PersistentClient(path="./chroma")
collection = client.get_collection("first_collection")


@app.post("/vectors/")
async def add_document(document: str):
    try:
        collection.add(ids, embeddings, metadatas, documents)
        return {"message": "Vector added successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/vectors/{doc_id}")
async def get_document(doc_id: str):
    try:
        vector = collection.query(query_texts)
        if vector:
            return {"id": vector_id, "vector": vector}
        else:
            raise HTTPException(status_code=404, detail="Vector not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/vectors/")
async def get_all_embeddings():
    try:
        vectors = collection.get()
        return {"vectors": vectors}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
