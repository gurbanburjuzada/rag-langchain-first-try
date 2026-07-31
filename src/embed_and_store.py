import json
import chromadb
from sentence_transformers import SentenceTransformer
from src.config import path_to_data, EMBEDDING_MODEL_NAME

# Loads data/chunks.json
with open(path_to_data / "chunks.json", encoding="utf-8") as file:
    deserialised_content = json.load(file)

# Loading model
model = SentenceTransformer(EMBEDDING_MODEL_NAME)

# Building three parallel lists from chunks
texts, metadatas, ids = [], [], []

for item in deserialised_content:
    source = item["source"]
    chunk_index = item["chunk_index"]
    texts.append(item["text"])
    metadatas.append({"source": source, "chunk_index": chunk_index})
    ids.append(f"{source}_{chunk_index}")
embeddings = model.encode(texts)

client = chromadb.PersistentClient(path=str(path_to_data / "chroma_db"))
collection = client.get_or_create_collection(name="physics_papers")

collection.add(
    ids=ids,
    embeddings=embeddings.tolist(),
    documents=texts,
    metadatas=metadatas
)

print(f"Added {len(ids)} chunks. Collection now has {collection.count()} total.")
print(f"Added {collection.count()} chunks to collection '{collection.name}'")
