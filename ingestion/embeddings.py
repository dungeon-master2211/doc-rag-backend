from langchain_openai import OpenAIEmbeddings
def get_embedding_model():
    embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
    return embeddings