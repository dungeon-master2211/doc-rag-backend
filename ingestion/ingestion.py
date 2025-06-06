from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from .embeddings import get_embedding_model
from .vector_store import get_vector_store


def process_file(filename,user_id):
    collection_name = f'{user_id}_collection'
    cur_dir = Path(__file__).parent
    upload_dir = (cur_dir / ".."/ "uploads").resolve()
    filepath = (upload_dir/filename).resolve()
    print('File to ingest',filepath)
    print('Loading PDF file')
    # Load File
    loader = PyPDFLoader(filepath)
    docs = loader.load()
    print('PDF file loaded')
    # Split File into Documents
    print('Splitting PDF file')
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, chunk_overlap=200, add_start_index=True
    )
    all_splits = text_splitter.split_documents(docs)
    print('Chunks created')
    # Embed each Document

    embeddings = get_embedding_model()

    # Store in Vector DB
    print('Converting chunks to vector and Storing in Vector DB')
    vector_store = get_vector_store(collection_name,embeddings)
    ids = vector_store.add_documents(documents=all_splits)
    print('chunks stored')
    return 1