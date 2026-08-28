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

        # Citation requirement for rounds 2-4 (only when RAG context is actually present)
        citation_instruction = ""
        if round_number >= 2:
            if rag_context and rag_context.strip():
                citation_instruction = ("\n- Cite up to 3 sources FROM THE PROVIDED RAG CONTEXT that justify your "
                                        "question choices, and list their titles in 'rag_context_used'. "
                                        "Do NOT invent sources that are not in the context.")
            else:
                citation_instruction = ("\n- No RAG context was retrieved. Base questions on well-established "
                                        "clinical guidelines from your training and leave 'rag_context_used' empty. "
                                        "Do NOT fabricate citations.")

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
- Generate 6-8 questions for Round {round_number}.
- Round 1: Focus on Triage & Chief Complaint.{history_instruction}
- Round 2: Focus on Symptom Characterization (OPQRST).{citation_instruction}
- Round 3: Focus on History, Meds, Allergies, Risk Factors.{citation_instruction}
- Round 4: Focus on Differential Refinement.{citation_instruction}
- Use simple language for patients, but maintain clinical rigor.
- Provide a 'nurse_explanation' for complex terms.
- EVERY 'radio' and 'checkbox' question MUST include an 'options' array; each option needs a
  short 'id' (e.g. "a","b") and a patient-friendly 'label'.
- On any option that indicates a clinical emergency, set "is_red_flag": true. On a concerning
  but non-emergency finding, set "is_amber_flag": true.
- If you choose a standardized assessment, set 'scoring_tool_id' to one of
  ["phq9","gcs","apgar","sofa"], make the questions match that scale exactly, and set the
  integer "value" on every option (e.g. PHQ-9 options carry value 0,1,2,3).

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
