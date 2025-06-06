from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams
import os

QDRANT_URL = os.environ.get('QDRANT_URL')
QDRANT_API_KEY = os.environ.get('QDRANT_API_KEY')


def get_vector_store(collection_name,embeddings):
    url=QDRANT_URL 
    api_key=QDRANT_API_KEY
    client = QdrantClient(url=url,api_key=api_key)
    collection_exist = client.collection_exists(collection_name=collection_name)
    if not collection_exist:
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=3072, distance=Distance.COSINE),
        )
    vector_store = QdrantVectorStore(
        client=client,
        collection_name=collection_name,
        embedding=embeddings,
    )
    return vector_store