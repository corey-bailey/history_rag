# Presidential Retrieval-Augmented Generation (RAG) System with Ollama

This project implements a document-based Retrieval-Augmented Generation (RAG) system for querying DOCX files using the **LangChain** framework and **Ollama** models. It processes documents, creates embeddings, and supports interactive querying of the document corpus.

---

## Features

- **Document Loading**: Automatically loads all `.docx` files from a specified folder.
- **Text Splitting**: Uses a recursive character text splitter for chunking large documents.
- **Embeddings & Vector Store**: Generates embeddings using the Ollama model and stores them in a vector store (Chroma or fallback).
- **RAG Querying**: Retrieves relevant document chunks to answer user queries using a retrieval-augmented generation chain.
- **Interactive Interface**: Provides an interactive CLI for querying the document corpus.

---

## Requirements

### Dependencies

Install the required Python packages using:

```bash
pip install langchain langchain-community langchain-ollama