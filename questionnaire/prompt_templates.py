class PromptTemplates:
    """Central store for all LLM prompt templates."""

    @staticmethod
    def get_round_prompt(round_number: int, visit_type: str, specialty: str, 
                         patient_ctx: dict, session_answers: dict, rag_context: str) -> str:
        """Generates the prompt for a specific questionnaire round."""
        
        # Determine if history is missing
        history = patient_ctx.get('chronic_conditions', [])
        history_instruction = ""
        if round_number == 1 and (not history or patient_ctx.get('no_history_toggle')):
            history_instruction = "\n- Since NO patient history is available, you MUST ask foundational medical history questions (e.g., major past illnesses, ongoing medications, allergies) in this first round alongside the chief complaint."

        # Citation requirement for rounds 2-4
        citation_instruction = ""
        if round_number >= 2:
            citation_instruction = "\n- You MUST cite exactly 3 prominent medical sources from the provided RAG context to justify your question choices. Include these source titles in the 'rag_context_used' array in your JSON output."

        base_prompt = f"""
You are an expert clinical intake assistant in a humanitarian setting.
Your goal is to generate Round {round_number} of a 4-round adaptive questionnaire.

CONTEXT:
- Visit Type: {visit_type}
- Specialty: {specialty}
- Patient Demographics: {patient_ctx.get('demographics', {})}
- Known History: {history}
- RAG Knowledge Base Context: {rag_context}
- Previous Answers: {session_answers}

INSTRUCTIONS:
- Generate 6-8 MCQ questions for Round {round_number}.
- Round 1: Focus on Triage & Chief Complaint.{history_instruction}
- Round 2: Focus on Symptom Characterization (OPQRST).{citation_instruction}
- Round 3: Focus on History, Meds, Allergies, Risk Factors.{citation_instruction}
- Round 4: Focus on Differential Refinement.{citation_instruction}
- Use simple language for patients, but maintain clinical rigor.
- Provide a 'nurse_explanation' for complex terms.
- Mark critical findings as 'is_red_flag' or 'is_amber_flag'.
- If appropriate for the specialty (e.g., Psychiatry, Emergency, Pediatrics), you can choose to conduct a standardized assessment by setting 'scoring_tool_id' to one of: ["phq9", "gcs", "apgar", "sofa"]. If you do this, ensure the questions you generate exactly match the standard scale parameters.

OUTPUT FORMAT:
Respond ONLY with a JSON object matching the QuestionnaireRound schema.
"""
        return base_prompt

    @staticmethod
    def get_brief_prompt(case_number: str, session_answers: dict, 
                         patient_ctx: dict, vital_signs: dict, 
                         rag_context: str, specialty: str) -> str:
        """Generates the prompt for the final physician brief."""
        
        prompt = f"""
You are a senior physician. Generate a structured clinical brief based on the intake data.

PATIENT: {case_number}
SPECIALTY: {specialty}
DATA:
- Questionnaire Responses: {session_answers}
- Patient History: {patient_ctx}
- Vital Signs: {vital_signs}
- RAG Evidence: {rag_context}

REQUIREMENTS:
- Identify Clinical Flags (RED/AMBER/GREEN).
- Provide Top 3-5 Differential Diagnoses with reasoning.
- Suggest physical examination plan.
- Recommend investigations.
- Cite RAG sources.

OUTPUT FORMAT:
Respond ONLY with a JSON object matching the PhysicianBrief schema.
"""
        return prompt
