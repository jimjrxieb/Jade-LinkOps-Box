#!/usr/bin/env python3
"""
RAG Search Engine
================

Core search functionality for retrieval-augmented generation.
"""

import logging
import pickle
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

import numpy as np

# Import schemas
from schemas.query_schema import SearchResult

# LangChain imports for LLM integration
try:
    from langchain.chains import RetrievalQA
    from langchain.embeddings import HuggingFaceEmbeddings
    from langchain.llms import LlamaCpp
    from langchain.retrievers.multi_query import MultiQueryRetriever
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    from langchain.vectorstores import FAISS

    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("LangChain not available. LLM features will be disabled.")

logger = logging.getLogger(__name__)


class RAGSearchEngine:
    """
    RAG search engine using FAISS for vector similarity search.
    """

    def __init__(
        self,
        vectorstore_path: str = "vectorstore/index.pkl",
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
        use_llm: bool = True,
        llm_model_path: str = "llm_weights/mistral.gguf",
    ):
        """
        Initialize the RAG search engine.

        Args:
            vectorstore_path: Path to the vector store file
            model_name: Name of the embedding model to use
            use_llm: Whether to enable LLM integration for answer generation
            llm_model: HuggingFace model ID for LLM
        """
        self.vectorstore_path = Path(vectorstore_path)
        self.model_name = model_name
        self.embedding_dimension = 384  # Default for all-MiniLM-L6-v2
        self.use_llm = use_llm and LANGCHAIN_AVAILABLE
        self.llm_model_path = llm_model_path

        # Initialize components
        self.index = None
        self.documents = []
        self.document_metadata = {}
        self.model = None
        self.langchain_vectorstore = None
        self.qa_chain = None
        self.multi_query_retriever = None
        self.use_multi_query = True  # Enable MultiQueryRetriever by default

        # Create vectorstore directory
        self.vectorstore_path.parent.mkdir(parents=True, exist_ok=True)

        # Load or initialize the index
        self._load_or_initialize_index()

        # Initialize LangChain components if available
        if self.use_llm:
            self._initialize_langchain()

        # Initialize MultiQueryRetriever if enabled
        if self.use_multi_query and self.use_llm:
            self._initialize_multi_query_retriever()

        logger.info("🔍 RAG search engine initialized")
        logger.info(f"   Model: {self.model_name}")
        logger.info(f"   Vector store: {self.vectorstore_path}")
        logger.info(f"   Documents loaded: {len(self.documents)}")
        logger.info(f"   LLM enabled: {self.use_llm}")
        if self.use_llm:
            logger.info(f"   LLM model: {self.llm_model_path}")
        logger.info(f"   MultiQuery enabled: {self.use_multi_query}")

    def _initialize_langchain(self):
        """Initialize LangChain components for LLM integration."""
        try:
            if not LANGCHAIN_AVAILABLE:
                logger.warning("LangChain not available, skipping LLM initialization")
                return

            # Initialize embeddings
            embeddings = HuggingFaceEmbeddings(model_name=self.model_name)

            # Create or load LangChain vectorstore
            langchain_index_path = self.vectorstore_path.parent / "langchain_index"
            if langchain_index_path.exists() and len(self.documents) > 0:
                self.langchain_vectorstore = FAISS.load_local(
                    str(langchain_index_path), embeddings
                )
                logger.info("📂 Loaded existing LangChain vectorstore")
            else:
                # Create empty vectorstore
                self.langchain_vectorstore = FAISS.from_texts(
                    ["Initial document"], embeddings
                )
                logger.info("🆕 Created new LangChain vectorstore")

            # Initialize QA chain
            try:
                # Check if model file exists
                model_path = Path(self.llm_model_path)
                if not model_path.exists():
                    logger.warning(f"LLM model file not found: {self.llm_model_path}")
                    self.use_llm = False
                    return

                llm = LlamaCpp(
                    model_path=str(model_path),
                    temperature=0.1,
                    max_tokens=512,
                    n_ctx=2048,
                    verbose=False,
                    n_gpu_layers=0,  # Set to 1 or higher if GPU available
                )
                retriever = self.langchain_vectorstore.as_retriever(
                    search_type="similarity", search_kwargs={"k": 3}
                )
                self.qa_chain = RetrievalQA.from_chain_type(
                    llm=llm, retriever=retriever, return_source_documents=True
                )
                logger.info("🧠 Local LLM QA chain initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize local LLM: {e}")
                self.use_llm = False

        except Exception as e:
            logger.error(f"Failed to initialize LangChain: {e}")
            self.use_llm = False

    def _initialize_multi_query_retriever(self):
        """Initialize MultiQueryRetriever for smarter search."""
        try:
            if not self.use_llm or self.langchain_vectorstore is None:
                logger.warning(
                    "LangChain not available, skipping MultiQueryRetriever initialization"
                )
                return

            # Check if LLM model exists
            model_path = Path(self.llm_model_path)
            if not model_path.exists():
                logger.warning(f"LLM model file not found: {self.llm_model_path}")
                self.use_multi_query = False
                return

            # Initialize LLM for query generation
            llm = LlamaCpp(
                model_path=str(model_path),
                temperature=0.1,
                max_tokens=256,
                n_ctx=2048,
                verbose=False,
                n_gpu_layers=0,  # Set to 1 or higher if GPU available
            )

            # Create base retriever
            base_retriever = self.langchain_vectorstore.as_retriever(
                search_type="mmr",  # Maximum Marginal Relevance for diversity
                search_kwargs={
                    "k": 6,  # Number of documents to retrieve
                    "fetch_k": 10,  # Number of documents to fetch before filtering
                    "lambda_mult": 0.7,  # Diversity parameter
                },
            )

            # Create MultiQueryRetriever
            self.multi_query_retriever = MultiQueryRetriever.from_llm(
                retriever=base_retriever,
                llm=llm,
                parser_key="text",  # Use text parser for query generation
            )

            logger.info("🧠 MultiQueryRetriever initialized successfully")
            logger.info("   - Generates multiple semantically similar queries")
            logger.info("   - Uses MMR search for diverse results")
            logger.info("   - Improves accuracy for vague or varied questions")

        except Exception as e:
            logger.error(f"Failed to initialize MultiQueryRetriever: {e}")
            self.use_multi_query = False

    def _load_or_initialize_index(self):
        """Load existing index or initialize a new one."""
        try:
            if self.vectorstore_path.exists():
                self._load_index()
                logger.info(
                    f"📂 Loaded existing vector store: {len(self.documents)} documents"
                )
            else:
                self._initialize_index()
                logger.info("🆕 Initialized new vector store")
        except Exception as e:
            logger.error(f"Failed to load/initialize index: {e}")
            self._initialize_index()

    def _initialize_index(self):
        """Initialize a new FAISS index."""
        try:
            import faiss

            # Create FAISS index
            self.index = faiss.IndexFlatL2(self.embedding_dimension)
            self.documents = []
            self.document_metadata = {}

            # Save empty index
            self._save_index()

        except ImportError:
            logger.warning("FAISS not available, using placeholder index")
            self.index = None
            self.documents = []
            self.document_metadata = {}

    def _load_index(self):
        """Load existing FAISS index and documents."""
        try:
            with open(self.vectorstore_path, "rb") as f:
                data = pickle.load(f)

            if isinstance(data, tuple) and len(data) >= 3:
                self.index, self.documents, self.document_metadata = data
            elif isinstance(data, tuple) and len(data) == 2:
                # Backward compatibility
                self.index, self.documents = data
                self.document_metadata = {}
            else:
                raise ValueError("Invalid vector store format")

        except Exception as e:
            logger.error(f"Failed to load index: {e}")
            self._initialize_index()

    def _save_index(self):
        """Save FAISS index and documents."""
        try:
            with open(self.vectorstore_path, "wb") as f:
                pickle.dump((self.index, self.documents, self.document_metadata), f)
        except Exception as e:
            logger.error(f"Failed to save index: {e}")

    def _load_model(self):
        """Load the embedding model."""
        if self.model is None:
            try:
                from sentence_transformers import SentenceTransformer

                self.model = SentenceTransformer(self.model_name)
                logger.info(f"🤖 Loaded embedding model: {self.model_name}")
            except ImportError:
                logger.error("sentence-transformers not available")
                raise ImportError("sentence-transformers is required for embedding")
            except Exception as e:
                logger.error(f"Failed to load model: {e}")
                raise

    def search(
        self,
        query: str,
        top_k: int = 5,
        similarity_threshold: float = 0.5,
        include_metadata: bool = True,
    ) -> list[SearchResult]:
        """
        Search for similar documents.

        Args:
            query: Search query
            top_k: Number of results to return
            similarity_threshold: Minimum similarity threshold
            include_metadata: Include document metadata in results

        Returns:
            List of search results
        """
        if not self.documents:
            logger.warning("No documents in vector store")
            return []

        if self.index is None:
            logger.error("FAISS index not available")
            return []

        try:
            # Load model if needed
            self._load_model()

            # Encode query
            query_embedding = self.model.encode([query])

            # Search in FAISS index
            distances, indices = self.index.search(
                query_embedding, min(top_k, len(self.documents))
            )

            # Convert distances to similarity scores (1 - normalized distance)
            max_distance = np.max(distances) if np.max(distances) > 0 else 1.0
            similarity_scores = 1.0 - (distances[0] / max_distance)

            # Prepare results
            results = []
            for i, (_distance, idx) in enumerate(zip(distances[0], indices[0])):
                if idx < len(self.documents):
                    similarity_score = similarity_scores[i]

                    # Apply similarity threshold
                    if similarity_score >= similarity_threshold:
                        # Get document info
                        doc_id = self._get_document_id(idx)
                        metadata = (
                            self.document_metadata.get(doc_id, {})
                            if include_metadata
                            else None
                        )

                        result = SearchResult(
                            content=self.documents[idx],
                            similarity_score=float(similarity_score),
                            document_id=doc_id,
                            chunk_index=idx,
                            metadata=metadata,
                        )
                        results.append(result)

            logger.info(
                f"🔍 Search completed: {len(results)} results (threshold: {similarity_threshold})"
            )
            return results

        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []

    def search_with_multi_query(
        self,
        query: str,
        top_k: int = 5,
        similarity_threshold: float = 0.5,
        include_metadata: bool = True,
    ) -> list[SearchResult]:
        """
        Search using MultiQueryRetriever for smarter results.

        This method generates multiple semantically similar queries from the original query,
        then retrieves documents using all generated queries for better coverage.

        Args:
            query: Search query
            top_k: Number of results to return
            similarity_threshold: Minimum similarity threshold
            include_metadata: Include document metadata in results

        Returns:
            List of search results with enhanced relevance
        """
        if not self.use_multi_query or self.multi_query_retriever is None:
            logger.info(
                "MultiQueryRetriever not available, falling back to regular search"
            )
            return self.search(query, top_k, similarity_threshold, include_metadata)

        try:
            logger.info(f"🔍 MultiQuery search for: {query[:50]}...")

            # Use MultiQueryRetriever to get relevant documents
            documents = self.multi_query_retriever.get_relevant_documents(query)

            # Convert to SearchResult format
            results = []
            for i, doc in enumerate(documents):
                if i >= top_k:
                    break

                # Calculate approximate similarity score (higher for earlier results)
                similarity_score = max(0.5, 1.0 - (i * 0.1))

                if similarity_score >= similarity_threshold:
                    metadata = doc.metadata if include_metadata else None

                    result = SearchResult(
                        content=doc.page_content,
                        similarity_score=float(similarity_score),
                        document_id=(
                            metadata.get("source", f"doc_{i}")
                            if metadata
                            else f"doc_{i}"
                        ),
                        chunk_index=i,
                        metadata=metadata,
                    )
                    results.append(result)

            logger.info(f"🧠 MultiQuery search completed: {len(results)} results")
            return results

        except Exception as e:
            logger.error(f"MultiQuery search failed: {e}")
            logger.info("Falling back to regular search")
            return self.search(query, top_k, similarity_threshold, include_metadata)

    def _get_document_id(self, chunk_index: int) -> str:
        """Get document ID for a chunk index."""
        # This is a simplified implementation
        # In a real system, you'd maintain a mapping from chunk indices to document IDs
        return f"doc_{chunk_index // 10}"  # Assume 10 chunks per document

    def add_documents(
        self, documents: list[str], metadata: Optional[dict[str, Any]] = None
    ):
        """
        Add documents to the vector store.

        Args:
            documents: List of document texts
            metadata: Optional metadata for the documents
        """
        if not documents:
            return

        try:
            # Load model if needed
            self._load_model()

            # Encode documents
            embeddings = self.model.encode(documents)

            # Add to FAISS index
            if self.index is not None:
                self.index.add(embeddings)

            # Add to documents list
            len(self.documents)
            self.documents.extend(documents)

            # Add metadata
            if metadata:
                doc_id = f"doc_{len(self.document_metadata)}"
                self.document_metadata[doc_id] = metadata

            # Save updated index
            self._save_index()

            logger.info(f"📄 Added {len(documents)} documents to vector store")

        except Exception as e:
            logger.error(f"Failed to add documents: {e}")

    def reload_index(self):
        """Reload the index from disk."""
        self._load_or_initialize_index()
        logger.info("🔄 Index reloaded")

    def clear_index(self):
        """Clear all documents from the index."""
        self._initialize_index()
        logger.info("🗑️ Index cleared")

    def get_status(self) -> dict[str, Any]:
        """Get search engine status."""
        return {
            "index_loaded": self.index is not None,
            "document_count": len(self.documents),
            "chunk_count": len(self.documents),
            "model_name": self.model_name,
            "embedding_dimension": self.embedding_dimension,
            "vectorstore_path": str(self.vectorstore_path),
            "last_updated": self._get_last_updated(),
        }

    def _get_last_updated(self) -> str:
        """Get the last updated timestamp of the vectorstore."""
        try:
            if self.vectorstore_path.exists():
                timestamp = datetime.fromtimestamp(self.vectorstore_path.stat().st_mtime)
                return timestamp.isoformat()
            return datetime.now().isoformat()
        except Exception:
            return datetime.now().isoformat()

    def get_document_count(self) -> int:
        """Get number of documents in the index."""
        return len(self.documents)

    def get_chunk_count(self) -> int:
        """Get number of chunks in the index."""
        return len(self.documents)

    def get_vectorstore_size(self) -> float:
        """Get vector store size in MB."""
        try:
            if self.vectorstore_path.exists():
                size_bytes = self.vectorstore_path.stat().st_size
                return size_bytes / (1024 * 1024)
            return 0.0
        except Exception:
            return 0.0

    def get_model_name(self) -> str:
        """Get the name of the embedding model."""
        return self.model_name

    def get_embedding_dimension(self) -> int:
        """Get the embedding dimension."""
        return self.embedding_dimension

    def get_index_type(self) -> str:
        """Get the type of vector index."""
        if self.index is not None:
            try:
                import faiss

                if isinstance(self.index, faiss.IndexFlatL2):
                    return "FAISS-FlatL2"
                else:
                    return "FAISS-Other"
            except ImportError:
                return "Unknown"
        return "None"

    def get_last_updated(self) -> str:
        """Get the last update timestamp."""
        try:
            if self.vectorstore_path.exists():
                timestamp = datetime.fromtimestamp(
                    self.vectorstore_path.stat().st_mtime
                )
                return timestamp.isoformat()
        except Exception:
            pass
        return datetime.now().isoformat()

    def list_documents(self) -> list[dict[str, Any]]:
        """List all documents in the index."""
        documents = []

        # Group chunks by document (simplified)
        doc_chunks = {}
        for i, chunk in enumerate(self.documents):
            doc_id = self._get_document_id(i)
            if doc_id not in doc_chunks:
                doc_chunks[doc_id] = []
            doc_chunks[doc_id].append(chunk)

        # Create document info
        for doc_id, chunks in doc_chunks.items():
            doc_info = {
                "document_id": doc_id,
                "filename": f"{doc_id}.txt",
                "file_path": f"/path/to/{doc_id}.txt",
                "file_size_bytes": sum(len(chunk.encode()) for chunk in chunks),
                "chunks_count": len(chunks),
                "embedding_model": self.model_name,
                "created_at": self.get_last_updated(),
                "metadata": self.document_metadata.get(doc_id, {}),
            }
            documents.append(doc_info)

        return documents

    def get_document(self, doc_id: str) -> Optional[dict[str, Any]]:
        """Get a specific document by ID."""
        documents = self.list_documents()
        for doc in documents:
            if doc["document_id"] == doc_id:
                return doc
        return None

    def delete_document(self, doc_id: str) -> bool:
        """Delete a document from the index."""
        # This is a simplified implementation
        # In a real system, you'd need to rebuild the index without the document
        logger.warning(f"Document deletion not fully implemented for {doc_id}")
        return False

    def search_with_llm(
        self,
        query: str,
        top_k: int = 3,
        similarity_threshold: float = 0.5,
    ) -> dict[str, Any]:
        """
        Search with LLM-generated answer using RetrievalQA chain.

        Args:
            query: Search query
            top_k: Number of top results to retrieve
            similarity_threshold: Minimum similarity threshold

        Returns:
            Dictionary with answer, sources, citations, and metadata
        """
        if not self.use_llm or self.qa_chain is None:
            # Fallback to regular search
            results = self.search(query, top_k, similarity_threshold)
            return {
                "answer": "LLM not available. Here are the most relevant document chunks:\n\n"
                + "\n\n".join([f"• {r.content}" for r in results]),
                "sources": results,
                "citations": [r.content for r in results],
                "llm_used": False,
                "model": "fallback",
            }

        try:
            # Use LangChain QA chain
            result = self.qa_chain({"query": query})

            # Extract answer and sources
            answer = result.get("result", "No answer generated")
            source_documents = result.get("source_documents", [])

            # Convert source documents to SearchResult format
            sources = []
            citations = []
            for i, doc in enumerate(source_documents):
                sources.append(
                    SearchResult(
                        content=doc.page_content,
                        score=1.0 - (i * 0.1),  # Approximate score
                        metadata={
                            "source": f"Document {i + 1}",
                            "chunk_id": i,
                            "llm_source": True,
                        },
                    )
                )
                citations.append(doc.page_content)

            # Save to memory log
            self._save_to_memory(query, answer, citations)

            return {
                "answer": answer,
                "sources": sources,
                "citations": citations,
                "llm_used": True,
                "model": "local-mistral-7b",
                "query": query,
            }

        except Exception as e:
            logger.error(f"LLM search failed: {e}")
            # Fallback to regular search
            results = self.search(query, top_k, similarity_threshold)
            return {
                "answer": f"LLM search failed: {str(e)}. Here are the most relevant document chunks:\n\n"
                + "\n\n".join([f"• {r.content}" for r in results]),
                "sources": results,
                "citations": [r.content for r in results],
                "llm_used": False,
                "model": "fallback",
                "error": str(e),
            }

    def _save_to_memory(self, query: str, answer: str, citations: list[str]):
        """
        Save query, answer, and citations to JSON log file.

        Args:
            query: The user's question
            answer: The LLM-generated answer
            citations: List of source document chunks
        """
        try:
            import json
            from datetime import datetime

            record = {
                "timestamp": datetime.utcnow().isoformat(),
                "query": query,
                "answer": answer,
                "citations": citations,
                "model": "local-mistral-7b",
                "llm_used": True,
            }

            # Create db directory if it doesn't exist
            db_path = Path("db")
            db_path.mkdir(exist_ok=True)

            log_path = db_path / "query_log.json"

            # Append to log file
            with open(log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(record, ensure_ascii=False) + "\n")

            logger.info(f"💾 Saved query to memory log: {log_path}")

        except Exception as e:
            logger.error(f"Failed to save to memory log: {e}")

    def update_langchain_vectorstore(
        self, documents: list[str], metadata: Optional[dict[str, Any]] = None
    ):
        """
        Update the LangChain vectorstore with new documents.

        Args:
            documents: List of document chunks
            metadata: Optional metadata for the documents
        """
        if not self.use_llm or not LANGCHAIN_AVAILABLE:
            logger.warning("LangChain not available, skipping vectorstore update")
            return

        try:
            # Initialize embeddings if not already done
            embeddings = HuggingFaceEmbeddings(model_name=self.model_name)

            # Create new vectorstore with documents
            self.langchain_vectorstore = FAISS.from_texts(documents, embeddings)

            # Save the vectorstore
            langchain_index_path = self.vectorstore_path.parent / "langchain_index"
            self.langchain_vectorstore.save_local(str(langchain_index_path))

            # Reinitialize QA chain
            if self.qa_chain is None:
                self._initialize_langchain()

            logger.info(
                f"✅ Updated LangChain vectorstore with {len(documents)} documents"
            )

        except Exception as e:
            logger.error(f"Failed to update LangChain vectorstore: {e}")


def search_query(query: str) -> str:
    """
    Convenience function for simple query search.

    Args:
        query: Search query

    Returns:
        Best matching document chunk
    """
    search_engine = RAGSearchEngine()
    results = search_engine.search(query, top_k=1)

    if results:
        return results[0].content
    else:
        return "No relevant documents found."


def retrieve_chunks(query: str, use_multi_query: bool = True) -> list[SearchResult]:
    """
    Convenience function for retrieving document chunks with optional MultiQueryRetriever.

    Args:
        query: Search query
        use_multi_query: Whether to use MultiQueryRetriever for smarter search

    Returns:
        List of search results
    """
    search_engine = RAGSearchEngine()

    if use_multi_query and search_engine.use_multi_query:
        return search_engine.search_with_multi_query(
            query, top_k=5, similarity_threshold=0.5
        )
    else:
        return search_engine.search(query, top_k=5, similarity_threshold=0.5)


if __name__ == "__main__":
    # Example usage
    print("🔍 RAG Search Engine Demo")
    print("=" * 30)

    # Initialize search engine
    search_engine = RAGSearchEngine()

    # Add some example documents
    example_docs = [
        "The zero trust model is a security framework that requires all users to be authenticated and authorized before accessing any resources.",
        "Machine learning is a subset of artificial intelligence that enables computers to learn without being explicitly programmed.",
        "Docker is a platform for developing, shipping, and running applications in containers.",
        "Kubernetes is an open-source container orchestration platform for automating deployment, scaling, and management of containerized applications.",
    ]

    search_engine.add_documents(example_docs)

    # Test search
    query = "What is zero trust?"
    results = search_engine.search(query, top_k=2)

    print(f"🔍 Query: {query}")
    print(f"📊 Found {len(results)} results:")

    for i, result in enumerate(results, 1):
        print(f"\n{i}. Score: {result.similarity_score:.3f}")
        print(f"   Content: {result.content}")

    # Show status
    status = search_engine.get_status()
    print(
        f"\n📈 Status: {status['document_count']} documents, {status['chunk_count']} chunks"
    )

    print("🎉 RAG search engine demo completed!")
