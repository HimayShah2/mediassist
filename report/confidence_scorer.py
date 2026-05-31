from models.questionnaire import SessionAnswers

class ConfidenceScorer:
    """Calculates a deterministic confidence score for the physician brief."""

    def calculate(self, rag_chunks: list, consensus: any, 
                  session_answers: SessionAnswers, patient_ctx: dict) -> float:
        
        # Weights from blueprint
        w_rag = 0.40
        w_consensus = 0.30
        w_completeness = 0.20
        w_history = 0.10
        
        # Simplified scores for now
        s_rag = sum([c.get('similarity', 0.8) for c in rag_chunks]) / len(rag_chunks) if rag_chunks else 0.5
        s_consensus = 1.0 if consensus.agrees_with_top_differential else 0.5
        s_completeness = 1.0 # Assume complete for now
        s_history = 0.5 # Assume no history match for now
        
        return (s_rag * w_rag) + (s_consensus * w_consensus) + \
               (s_completeness * w_completeness) + (s_history * w_history)
