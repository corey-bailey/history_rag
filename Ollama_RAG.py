import os
import argparse
from typing import List, Callable

# LangChain imports
from langchain_community.document_loaders import Docx2txtLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_ollama import OllamaLLM
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

class DocxRAGSystem:
    def __init__(self, 
                 folder_path: str, 
                 model_name: str = "llama3.2", 
                 chunk_size: int = 500, 
                 chunk_overlap: int = 100):
        """
        Initialize the RAG system with document loading and processing configurations
        """
        self.folder_path = folder_path
        self.model_name = model_name
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        # Initialize Ollama components
        self.embeddings = OllamaEmbeddings(model=model_name)
        self.llm = OllamaLLM(model=model_name)
        
        # Process documents
        self.documents = self._load_docx_documents()
        
        # Fallback vector storage options
        try:
            from langchain_community.vectorstores import Chroma
            self.vector_store = self._create_vector_store(Chroma)
            self.retriever = self.vector_store.as_retriever()
        except ImportError:
            print("Chroma not available. Falling back to in-memory storage.")
            self.vector_store = None
            self.retriever = None
        
        # Create retrieval chain
        self.chain = self.create_retrieval_chain()
    
    def _load_docx_documents(self) -> List:
        """
        Load all DOCX files from the specified folder
        """
        documents = []
        for root, _, files in os.walk(self.folder_path):
            for filename in files:
                if filename.endswith(".docx"):
                    file_path = os.path.join(root, filename)
                    loader = Docx2txtLoader(file_path)
                    docs = loader.load()
                    documents.extend(docs)
        
        if not documents:
            raise ValueError(f"No DOCX files found in {self.folder_path}")
        
        print(f"Loaded {len(documents)} documents")
        return documents
    
    def _create_vector_store(self, vector_store_class):
        """
        Create a vector store from loaded documents
        """
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size, 
            chunk_overlap=self.chunk_overlap
        )
        
        splits = text_splitter.split_documents(self.documents)
        vector_store = vector_store_class.from_documents(
            documents=splits, 
            embedding=self.embeddings
        )
        
        return vector_store
    
    def create_retrieval_chain(self, template: str = None):
        """
        Create a retrieval-augmented generation chain
        """
        if template is None:
            template = """Use the following pieces of context to answer the question. 
            If you don't know the answer, just say that you don't know, don't try to make up an answer.
            
            Context: {context}
            Question: {question}
            
            Helpful Answer:"""
        
        prompt = PromptTemplate.from_template(template)
        
        def format_docs(docs):
            return "\n\n".join(doc.page_content for doc in docs)
        
        # Fallback if no retriever
        if self.retriever is None:
            print("No retriever available. Using direct document context.")
            context = "\n\n".join([doc.page_content for doc in self.documents])
            
            def simple_chain(question):
                filled_template = template.format(context=context, question=question)
                result = self.llm.invoke(filled_template)  # This might already be a string
                return result
            
            return simple_chain
        
        retrieval_chain = (
            {"context": self.retriever | format_docs, "question": RunnablePassthrough()}
            | prompt
            | self.llm
            | StrOutputParser()
        )
        
        return retrieval_chain
    
    def query(self, question: str):
        """
        Query the document corpus
        """
        return self.chain(question)

def main():
    parser = argparse.ArgumentParser(description="DOCX RAG System with Ollama")
    parser.add_argument("folder_path", help="Path to folder containing DOCX files")
    parser.add_argument("--model", default="llama3.2", help="Ollama model to use")
    
    args = parser.parse_args()
    
    try:
        rag_system = DocxRAGSystem(
            folder_path=args.folder_path, 
            model_name="llama3.2"
        )
        
        # Interactive query loop
        while True:
            query = input("\n🤖 Enter your question (or 'quit' to exit): ")
            if query.lower() == 'quit':
                break
            
            try:
                response = rag_system.query(query)
                print("\n📄 Response:", response)
            except Exception as e:
                print(f"Error processing query: {e}")
    
    except Exception as e:
        print(f"Error initializing RAG system: {e}")

if __name__ == "__main__":
    main()