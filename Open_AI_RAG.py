import os
from langchain_community.document_loaders import Docx2txtLoader
from langchain_ollama import OllamaLLM  # Updated import
from langchain_community.embeddings import OpenAIEmbeddings  # Or use OllamaEmbeddings if available
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_core.runnables import RunnablePassthrough
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

def load_docx_texts_from_folder(folder_path):
    all_text = ""
    for root, _, files in os.walk(folder_path):
        for filename in files:
            if filename.endswith(".docx"):
                file_path = os.path.join(root, filename)
                loader = Docx2txtLoader(file_path)
                documents = loader.load()
                all_text += " ".join(doc.page_content for doc in documents) + "\n"
    return all_text

# Set constants and API details
embed_model = OpenAIEmbeddings(openai_api_key="")
MODEL_NAME = "llama3.2"
BASE_URL = "http://127.0.0.1:11434"
TRANSCRIPT_FOLDER_PATH = "/Users/**/Documents/GitHub/history_rag/presidential_documents"  # Replace with your folder path

# Load text from all DOCX files in the folder
docx_text = load_docx_texts_from_folder(TRANSCRIPT_FOLDER_PATH)

# Initialize model and embeddings
llm = OllamaLLM(model=MODEL_NAME, base_url=BASE_URL)
embed_model = OpenAIEmbeddings()  # Ensure you have OpenAI API key, or use alternative embedding

# Split the combined DOCX text into chunks
text_splitter = RecursiveCharacterTextSplitter(chunk_size=512, chunk_overlap=128)
chunks = text_splitter.split_text(docx_text)

# Create the vector store and retriever
vector_store = Chroma.from_texts(chunks, embed_model)
retriever = vector_store.as_retriever()

# Create a prompt template
prompt_template = PromptTemplate.from_template(
    "Summarize the following context: {context}"
)

# Create a retrieval chain
def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

retrieval_chain = (
    {"context": retriever | format_docs}
    | prompt_template
    | llm
    | StrOutputParser()
)

# Get a response from the retrieval chain
response = retrieval_chain.invoke("CREATE A SUMMARY OF THE TEXT")
print(response)