import chromadb
from sentence_transformers import SentenceTransformer
from src.config import path_to_data, RETRIEVAL_K
from src.config import EMBEDDING_MODEL_NAME


model = SentenceTransformer(EMBEDDING_MODEL_NAME)
client = chromadb.PersistentClient(path=str(path_to_data / "chroma_db"))
collection = client.get_or_create_collection(name="physics_papers")


def retrieve(query: str, k: int = RETRIEVAL_K):
    query_embeddings = model.encode(query)
    res = collection.query(
        query_embeddings=[query_embeddings.tolist()],   # must be a list of vectors even for one query
        n_results=k
    )
    return res


if __name__ == "__main_ _":
    query = "sloshing spiral"
    results = retrieve(query, k=5)

    for doc, meta, dist in zip(
        results["documents"][0], results["metadatas"][0], results["distances"][0]
    ):
        print(f"--- {meta['source']} (chunk {meta['chunk_index']}, distance {dist:.3f}) ---")
        print(doc[:300])
        print()
