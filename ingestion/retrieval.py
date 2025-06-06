from .embeddings import get_embedding_model
from .vector_store import get_vector_store
def retrieve_data(query,user_id):
    collection_name = f'{user_id}_collection'
    embeddings = get_embedding_model()
    vector_store = get_vector_store(collection_name=collection_name,embeddings=embeddings)
    results = vector_store.similarity_search(
        query, k=2
    )
    context = "\n\n".join(
        [
            f'Page Content: {res.page_content}\n\n Metadata: {res.metadata}' for res in results
        ]
    )
    return context