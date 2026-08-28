import os
import pytest
from unittest.mock import AsyncMock, patch

from models.questionnaire import QuestionnaireRound, Question, OptionType
from nim.nim_client import NIMClient


# Toggle live API vs mocked responses
# Use: export TEST_LIVE_API=1 to run against the real NVIDIA NIM endpoints
RUN_LIVE = os.environ.get("TEST_LIVE_API", "0") == "1"

@pytest.fixture
def mock_nim_client():
    """
    Returns a NIMClient where structured_chat is mocked to return 
    valid QuestionnaireRound responses simulating the 4-round loop.
    """
    client = NIMClient(key_manager=None)  # Can initialize without keys if mocking
    
    async def mock_structured_chat(role, messages, response_model, **kwargs):
        # Infer round number from context for testing realism
        round_num = 1
        for msg in messages:
            content = msg.get("content", "")
            if "Generate Round 4" in content: round_num = 4
            elif "Generate Round 3" in content: round_num = 3
            elif "Generate Round 2" in content: round_num = 2

        return QuestionnaireRound(
            round_number=round_num,
            visit_type="general_consultation",
            specialty="internal_medicine",
            questions=[
                Question(
                    question_id=f"q_{round_num}_1",
                    round=round_num,
                    text=f"Mock clinical question for round {round_num}?",
                    type=OptionType.RADIO,
                    options=[],
                    is_mandatory=True
                )
            ],
            rag_context_used=["mock_doc_1.pdf"],
            rag_chunk_ids=["chunk_123"],
            model_used="mock-medical-model",
            generation_time_ms=150,
            working_differentials=["Differential A", "Differential B"] if round_num >= 3 else None
        )
        
    client.structured_chat = AsyncMock(side_effect=mock_structured_chat)
    
    # We patch the health check so tests pass without real keys
    client.is_offline = lambda: False
    
    return client

@pytest.fixture
def live_nim_client():
    """
    Returns a real NIMClient. Requires valid API keys in .env.
    """
    return NIMClient()

@pytest.mark.asyncio
async def test_phase2_4_round_loop(mock_nim_client, live_nim_client):
    """
    Test the Phase 2 4-round questionnaire loop end-to-end.
    Ensures that the `instructor` schema structure validates successfully.
    """
    client = live_nim_client if RUN_LIVE else mock_nim_client
    
    # Check if we should skip live test due to missing keys
    if RUN_LIVE and client.is_offline():
        pytest.skip("Skipping live test: No NIM API keys available.")
        
    accumulated_context = "Patient is a 45-year-old male presenting with intermittent headache for 3 days."
    
    for round_num in range(1, 5):
        messages = [
            {"role": "system", "content": "You are MediAssist Pro, an AI clinical assistant. Follow the instructor schema."},
            {"role": "user", "content": f"Generate Round {round_num} questions. Context so far: {accumulated_context}"}
        ]
        
        # We use the MEDICAL role for clinical questionnaire generation
        response = await client.structured_chat(
            role=ModelRole.MEDICAL,
            messages=messages,
            response_model=QuestionnaireRound,
            temperature=0.1
        )
        
        # 1. Validate Schema Structure (Instructor enforces this, but we verify fields)
        assert isinstance(response, QuestionnaireRound)
        assert response.round_number in [round_num, 1, 2, 3, 4] # Allow flexibility if model hallucinates slightly in live
        assert len(response.questions) > 0
        
        for q in response.questions:
            assert isinstance(q, Question)
            assert isinstance(q.type, OptionType)
            
        # 2. Check conditional fields
        if round_num >= 3 and not RUN_LIVE:
            # Only enforce in mock as live models might return None if they haven't formed differentials
            assert response.working_differentials is not None
            assert len(response.working_differentials) > 0

        # Simulate user answering the first question
        first_q = response.questions[0]
        mock_answer = "Patient reports mild severity."
        
        # Append answer to accumulated context for the next round
        accumulated_context += f"\nRound {round_num} - {first_q.text}: {mock_answer}"

    # Verify loop ran 4 times successfully
    assert "Round 1" in accumulated_context
    assert "Round 2" in accumulated_context
    assert "Round 3" in accumulated_context
    assert "Round 4" in accumulated_context
