class PromptTemplates:
    """Central store for all LLM prompt templates."""

    MANDATORY_ROUNDS = 4

    @staticmethod
    def get_round_prompt(round_number: int, visit_type: str, specialty: str,
                         patient_ctx: dict, session_answers: dict, rag_context: str,
                         focus: dict = None) -> str:
        """Generates the prompt for a specific questionnaire round.

        Rounds 1-4 are the mandatory adaptive intake. Rounds 5+ are FOCUSED
        follow-ups driven by `focus` (a SufficiencyAssessment dict) — they exist
        to resolve specific flags and separate the leading differentials so the
        physician brief is well supported.
        """
        is_followup = round_number > PromptTemplates.MANDATORY_ROUNDS

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

        if is_followup:
            focus = focus or {}
            focus_block = (
                f"\nThis is FOCUSED FOLLOW-UP round {round_number}. The mandatory 4-round intake is "
                "complete but the picture is not yet clear enough for a safe physician brief.\n"
                f"- Still to clarify: {focus.get('focus_areas', [])}\n"
                f"- Flags not yet characterised: {focus.get('unresolved_flags', [])}\n"
                f"- Leading differentials to separate: {focus.get('leading_differentials', [])}\n"
                "- Ask 3-6 highly targeted questions that directly resolve the above. "
                "Do NOT repeat questions already answered. Prioritise anything that changes "
                "urgency or the top diagnosis."
            )
            task_line = focus_block
        else:
            task_line = f"""- Generate 6-10 thorough questions for Round {round_number}. Be comprehensive — a doctor
  will rely on this; missing a key question is worse than asking one extra.
- Round 1: Triage & Chief Complaint.{history_instruction}
- Round 2: Symptom Characterization (full OPQRST).{citation_instruction}
- Round 3: Past history, medications, allergies, risk factors, relevant family/social history.{citation_instruction}
- Round 4: Differential refinement — questions that discriminate between the plausible diagnoses.{citation_instruction}"""

        base_prompt = f"""
You are an expert clinical intake assistant in a humanitarian setting.
Your goal is to generate Round {round_number} of an adaptive clinical questionnaire
(4 mandatory rounds, then focused follow-up rounds until the case is clear).

CONTEXT:
- Visit Type: {visit_type}
- Specialty: {specialty}
- Patient Demographics: {patient_ctx.get('demographics', {})}
- Known History: {history}
- RAG Knowledge Base Context: {rag_context}
- Previous Answers: {session_answers}

INSTRUCTIONS:
{task_line}
- Use simple language for patients, but maintain clinical rigor.
- Provide a 'nurse_explanation' for complex terms.
- EVERY 'radio' and 'checkbox' question MUST include an 'options' array; each option needs a
  short 'id' (e.g. "a","b") and a patient-friendly 'label'.
- On any option that indicates a clinical emergency, set "is_red_flag": true. On a concerning
  but non-emergency finding, set "is_amber_flag": true.
- If a standardized assessment is warranted, set 'scoring_tool_id' to one of
  ["phq9","gcs","apgar","sofa"], make the questions match that scale exactly, and set the
  integer "value" on every option (e.g. PHQ-9 options carry value 0,1,2,3).

OUTPUT FORMAT:
Respond ONLY with a JSON object matching the QuestionnaireRound schema.
"""
        return base_prompt

    @staticmethod
    def get_sufficiency_prompt(session_answers: dict, patient_ctx: dict,
                               flags_raised: list, specialty: str) -> str:
        return f"""
You are a senior physician reviewing a completed 4-round intake questionnaire before
writing a clinical brief. Decide whether enough information has been gathered to hand a
SAFE brief to the attending doctor, or whether one more focused round of questions is needed.

SPECIALTY: {specialty}
PATIENT: {patient_ctx.get('demographics', '')} — {patient_ctx.get('chief_complaint_summary', '')}
ALL ANSWERS SO FAR: {session_answers}
FLAGS RAISED DURING INTAKE: {flags_raised}

Be conservative: if a red/amber flag has NOT been fully characterised, or if two or more
serious differentials remain roughly equally likely, or if a key discriminating feature is
still unknown, then it is NOT sufficient.

Respond ONLY with JSON matching the SufficiencyAssessment schema:
- sufficient_for_brief: true only if a doctor could act safely on what is known
- reason: one sentence
- focus_areas: specific things a follow-up round should ask about (empty if sufficient)
- unresolved_flags: raised flags still lacking detail
- leading_differentials: the 2-4 diagnoses still in contention
"""

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
