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
            task_line = (
                f"\nThis is FOCUSED FOLLOW-UP round {round_number}. The 4 mandatory rounds are done "
                "but the picture is not yet clear enough for a safe physician brief.\n"
                f"- Still to clarify: {focus.get('focus_areas', [])}\n"
                f"- Flags not yet characterised: {focus.get('unresolved_flags', [])}\n"
                f"- Leading differentials to separate: {focus.get('leading_differentials', [])}\n\n"
                "The 'Previous Answers' section above lists every question already asked and its "
                "answer. You MUST NOT ask any question that is the same as, or a rephrasing of, one "
                "already there — the patient has answered it. Instead ask NEW, more specific "
                "questions (2-5) that move the above items forward, e.g. timing/onset details, "
                "associated features, response to interventions, or a discriminating exam-history "
                "point. If a flag genuinely cannot be characterised further by questioning, do not "
                "ask about it again."
            )
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
    def get_sufficiency_prompt(rounds_done: int, questions_asked: int, patient_ctx: dict,
                               flags_raised: list, specialty: str,
                               answer_digest: str = "") -> str:
        flags = "; ".join(str(f) for f in flags_raised[:20]) or "none"
        return f"""
You are a senior physician reviewing a completed intake questionnaire before a clinical brief.
Decide if there is enough information for a SAFE brief, or if ONE more focused round is needed.

SPECIALTY: {specialty}
PATIENT: {patient_ctx.get('demographics', '')} — {patient_ctx.get('chief_complaint_summary', '')}
ROUNDS COMPLETED: {rounds_done} ({questions_asked} questions answered)
FLAGS RAISED DURING INTAKE:
{flags}
KEY ANSWERS: {answer_digest or 'see flags above'}

Be conservative: NOT sufficient if a red/amber flag is uncharacterised, if 2+ serious
differentials remain roughly equally likely, or if a key discriminating feature is unknown.

Respond ONLY with JSON matching the SufficiencyAssessment schema. Keep EVERY list entry
under 10 words. At most 5 entries per list.
- sufficient_for_brief: true only if a doctor could act safely now
- reason: one short sentence
- focus_areas: what a follow-up round should ask (empty if sufficient)
- unresolved_flags: short labels of flags still lacking detail
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
