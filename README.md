# AAIDC_Module1
The Project for Module 1 in the AAIDC-2025

AG Research Assistant
A lightweight Retrieval-Augmented Generation (RAG) assistant that indexes local research documents (PDF/TXT), stores dense embeddings in a ChromaDB vector store, and answers questions strictly based on those documents using OpenAI, Groq, or Google Gemini via LangChain.

Features:

Multi‑provider LLM support: OpenAI (gpt-4o-mini default), Groq (llama-3.1-8b-instant default), or Google Gemini (gemini-2.0-flash default), selected automatically based on available API keys.

Local document ingestion: Reads .pdf and .txt files from a data directory.

Smart text chunking: Uses LangChain RecursiveCharacterTextSplitter for overlapping chunks.

Persistent vector store: Stores embeddings with ChromaDB.

Strict RAG behavior: The assistant only answers using retrieved content and refuses to hallucinate or reveal system prompts.
