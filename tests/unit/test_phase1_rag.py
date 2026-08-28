import os
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch

from reportlab.pdfgen import canvas
import chromadb

from llm.server_client import ServerLLMClient
from rag.document_manager import DocumentManager

@pytest.fixture
def mock_keys():
    manager = MagicMock(spec=ServerLLMClient)
    
    # Mock get_key_for_role
    key_mock = MagicMock()
    key_mock.value = "fake-nim-key"
    manager.get_key_for_role.return_value = key_mock
    
    # Mock get_model_for_role
    manager.get_model_for_role.side_effect = lambda role: {
        str.EMBED: "nvidia/nv-embed-v1",
        str.RERANK: "nvidia/nv-rerank-qa-mistral-4b:1"
    }.get(role, "unknown")
    
    return manager

@pytest.fixture
def temp_workspace(tmp_path):
    # Create test txt
    txt_path = tmp_path / "test_doc.txt"
    txt_path.write_text("This is a test medical document about hypertension.\n\nHypertension is high blood pressure.")
    
    # Create test pdf
    pdf_path = tmp_path / "test_doc.pdf"
    c = canvas.Canvas(str(pdf_path))
    c.drawString(100, 750, "Patient medical history indicates diabetes mellitus.")
    c.save()
    
    return {
        "txt_path": str(txt_path),
        "pdf_path": str(pdf_path),
        "db_path": str(tmp_path / "chromadb")
    }

@patch("rag.document_manager.OpenAIEmbeddings")
@patch("rag.document_manager.requests.post")
def test_rag_pipeline(mock_post, MockEmbeddings, temp_workspace, mock_keys):
    # 1. Setup mocks
    # Mock Embedder Proxy
    mock_embedder_instance = MagicMock()
    mock_embedder_instance.embed_documents.side_effect = lambda texts: [[0.1] * 4096 for _ in texts]
    mock_embedder_instance.embed_query.return_value = [0.1] * 4096
    MockEmbeddings.return_value = mock_embedder_instance
    
    # Mock Reranker logic
    mock_response = MagicMock()
    # Assume 2 chunks retrieved, we rerank them
    mock_response.json.return_value = {
        "rankings": [
            {"index": 0, "logit": 0.95},
            {"index": 1, "logit": 0.85}
        ]
    }
    mock_post.return_value = mock_response

    # 2. Initialize DocumentManager
    doc_mgr = DocumentManager(llm_client=mock_keys, db_path=temp_workspace["db_path"])
    # Modify min similarity so our dummy zero distance (perfect match) doesn't get filtered out.
    # Default distance from chromadb for zero vectors is 0, so similarity = 1.0. 
    # But wait, we mocked embed_documents to return vectors. ChromaDB will calculate distance.
    doc_mgr.MIN_SIMILARITY = -100.0 # Make sure everything passes similarity filter in tests

    # 3. Test Ingest TXT
    res_txt = doc_mgr.ingest_document(
        file_path=temp_workspace["txt_path"], 
        collection="test_collection",
        document_type="text_doc"
    )
    assert res_txt["collection"] == "test_collection"
    assert res_txt["chunks_added"] > 0
    
    # 4. Test Ingest PDF
    res_pdf = doc_mgr.ingest_document(
        file_path=temp_workspace["pdf_path"], 
        collection="test_collection",
        document_type="pdf_doc"
    )
    assert res_pdf["chunks_added"] > 0
    
    # Verify storing chunks in ChromaDB
    stats = doc_mgr.get_stats()
    assert "test_collection" in stats
    total_chunks = res_txt["chunks_added"] + res_pdf["chunks_added"]
    assert stats["test_collection"] == total_chunks

    # Verify that it correctly contacted the embedder proxy (OpenAIEmbeddings was used)
    # Actually, langchain's OpenAIEmbeddings contacts the proxy, but here we mocked the class.
    assert MockEmbeddings.called
    assert mock_embedder_instance.embed_documents.called

    # 5. Test Retrieval using Reranker Logic
    results = doc_mgr.retrieve("What is hypertension?", ["test_collection"], n_results=5)
    
    # Assert reranker was called
    assert mock_post.called
    call_kwargs = mock_post.call_args.kwargs
    assert "nvidia/nv-rerank-qa-mistral-4b:1" in str(call_kwargs.get("json"))
    assert call_kwargs.get("headers")["Authorization"] == "Bearer fake-nim-key"
    
    # Verify results are sorted by reranker score
    assert len(results) > 0
    if len(results) >= 2:
        assert results[0]["similarity"] >= results[1]["similarity"]
        
    # Verify metadata is retained
    for r in results:
        assert "document_type" in r["metadata"]
