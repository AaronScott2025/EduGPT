import os.path

from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain_community.llms import Ollama
from langchain.chains import RetrievalQA

def loadRAG(file,query):
    PDF_PATH = file #File
    VECTORSTORE_DIR = f"faiss_index_{query}" #Directory
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2", model_kwargs={"device": "cpu"}) #Embedding Model

    if not os.path.exists(VECTORSTORE_DIR): #If vectors aren't locally stored
        print(f"{VECTORSTORE_DIR}  Doesnt Exist. Generating Vectorstore")
        document = PyPDFLoader(PDF_PATH).load() #Load PDF as text
        splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=30, separator="\n") #Split text into chunks
        docs = splitter.split_documents(document)
        vectorstore = FAISS.from_documents(docs, embeddings)
        vectorstore.save_local(VECTORSTORE_DIR) #Save Machine-readable Data
        return 1
    return 0


def LLM(query,instruction):
    query = query.replace(" ", "") #No Spaces
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2",model_kwargs={"device": "cpu"}) #Embedding Model (Realtime currently, but normally should be done in batches. Handled this way to allow for the future addition of a webscraper
    VECTORSTORE_DIR = f"faiss_index_{query}" #Directory of machine-language-translated PDF
    vectorstore = FAISS.load_local(VECTORSTORE_DIR, embeddings, allow_dangerous_deserialization=True) #Load FAISS (facebook ai similarity search) index. Designed for efficient similarity search and clustering
    retriever = vectorstore.as_retriever() #Enables searching
    llm = Ollama(model="llama3") #LLM in use (can theoretically be anything, but llama3 was in my testing, the strongest model on ollama)
    qa_chain = RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", retriever=retriever) #Creates QA-chain using LLM and Searching retriever.
    return qa_chain.run(instruction) #Run instruction
