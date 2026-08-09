from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
import os
import glob

# Drop any PDF(s) you want the bot to answer from into this folder -
# a student handbook, admissions brochure, fee circular, whatever you have.
# All PDFs in here get loaded, so this also works if you have several files.
DOCUMENTS_DIR = "documents"

embeddings = OllamaEmbeddings(model="nomic-embed-text")

db_location = "./chrome_langchain_db"
add_documents = not os.path.exists(db_location)

if add_documents:
    pdf_paths = glob.glob(os.path.join(DOCUMENTS_DIR, "*.pdf"))

    if not pdf_paths:
        raise FileNotFoundError(
            f"No PDFs found in '{DOCUMENTS_DIR}/'. Put at least one PDF in "
            f"that folder, then run this again."
        )

    # PyPDFLoader turns each PDF into one Document per page.
    raw_pages = []
    for path in pdf_paths:
        raw_pages.extend(PyPDFLoader(path).load())

    # A whole page is usually too big and too unfocused to embed well (and a
    # short page is sometimes barely anything), so we re-cut everything into
    # ~1000 character chunks with a bit of overlap so a sentence that gets
    # cut off at a chunk boundary still shows up whole in the next chunk too.
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
    documents = splitter.split_documents(raw_pages)
    ids = [str(i) for i in range(len(documents))]

vector_store = Chroma(
    collection_name="cu_shah_sahayak_docs",
    persist_directory=db_location,
    embedding_function=embeddings
)

if add_documents:
    vector_store.add_documents(documents=documents, ids=ids)

# Each chunk is smaller than a full review used to be, so k=5 gives the model
# a handful of relevant paragraphs to work with - bump this up if answers
# feel like they're missing context, or down if they feel unfocused.
retriever = vector_store.as_retriever(
    search_kwargs={"k":1}
)
