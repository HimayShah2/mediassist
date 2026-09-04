import asyncio
import time
import instructor
from openai import AsyncOpenAI
from loguru import logger

from models.questionnaire import QuestionnaireRound, SessionAnswers, SufficiencyAssessment
from llm.server_client import ServerLLMClient
from rag.document_manager import DocumentManager
from config.settings import VISIT_TYPE_RAG_MAP, VISIT_TYPE_ROLE_MAP
from .prompt_templates import PromptTemplates
from .red_flag_detector import RedFlagDetector

class QuestionnaireEngine:
    MAX_RETRIES = 2
    MANDATORY_ROUNDS = 4      # always asked, in full
    MAX_FOLLOWUPS = 2        # focused follow-up rounds after the mandatory 4
    MAX_ROUNDS = MANDATORY_ROUNDS + MAX_FOLLOWUPS   # absolute ceiling

    def __init__(self, llm_client: ServerLLMClient, doc_manager: DocumentManager):
        self.llm_client       = llm_client
        self.doc_manager      = doc_manager
        self.prompts          = PromptTemplates()
        self.flag_detector    = RedFlagDetector()
        self.session_answers  = SessionAnswers()
        self.raw_llm_log      = []    # Stored for physician raw data access
        self.raw_rag_log      = []    # Stored for physician raw data access
        self._round_questions = {}    # round_number -> [Question], for scoring/flag resolution
        self._assessment_fallback_used = False
        self._focus_history = []

    async def generate_round(self, round_number: int, visit_type: str,
                              patient_ctx: dict, specialty: str,
                              focus: dict = None) -> QuestionnaireRound:

        # Use blueprint mapping for role, default to STANDARD if missing
        role = VISIT_TYPE_ROLE_MAP.get(visit_type, "STANDARD")
        # Always use MEDICAL for the final refinement round and follow-ups
        if round_number >= 4:
            role = "MEDICAL"
            
        # DOMAIN RESTRICTION LOGIC
        # Standard domains map directly to collection names
        domain_slug = specialty.lower().replace(" ", "_").replace("(ent)", "ent")
        
        if patient_ctx.get("allow_all_domains"):
            # Use blueprint default map + current specialty
            collections = VISIT_TYPE_RAG_MAP.get(visit_type, ["core_medicine", "who_guidelines"])
            if domain_slug not in collections:
                collections.append(domain_slug)
        else:
            # STRICT MODE: Only [Selected Domain, Common Knowledge]
            collections = [domain_slug, "common_medicine"]
        
        # Retrieve RAG context
        query       = f"Patient presenting for {visit_type} in {specialty} domain. Context: {patient_ctx}"
        
        # Get trusted sites from settings
        from config.settings import settings
        trusted_sites = [s.strip() for s in settings.trusted_sites.split(",") if s.strip()]
        
        # DocumentManager.retrieve should now handle trusted_sites
        rag_chunks  = await self.doc_manager.retrieve(query, collections, n_results=15, trusted_sites=trusted_sites)
        self.raw_rag_log.extend(rag_chunks)
        rag_text    = "\n\n".join([f"SOURCE [{c.get('metadata', {}).get('source_file', 'unknown')}]: {c['text']}" for c in rag_chunks[:5]])

        # For follow-up rounds pass a readable Q->answer digest so the model can
        # SEE what has already been asked and not repeat itself.
        answers_ctx = (self._answer_digest() if round_number > self.MANDATORY_ROUNDS
                       else self.session_answers.dict())

        prompt      = self.prompts.get_round_prompt(
            round_number=round_number,
            visit_type=visit_type,
            specialty=specialty,
            patient_ctx=patient_ctx,
            session_answers=answers_ctx,
            rag_context=rag_text,
            focus=focus,
        )

        from config.settings import settings

        if rag_text.strip():
            grounding_prefix = """
CRITICAL GROUNDING RULES:
1. Prefer the provided RAG context below over your own recollection; if they conflict, follow the context.
2. If a source is a website (SOURCE [WEB: ...]), name the site in your reasoning (e.g. 'As per WHO...').
3. Cite the sources you used verbatim in the 'rag_context_used' array. Never cite a source not shown below.
"""
        else:
            grounding_prefix = """
GROUNDING RULES:
1. No knowledge-base context was retrieved for this case.
2. Base your questions on well-established clinical guidelines from your training.
3. Leave 'rag_context_used' as an empty array. Do NOT fabricate citations.
"""
        from models.questionnaire import CompactRound
        start = time.time()
        for attempt in range(self.MAX_RETRIES):
            try:
                # Mandatory rounds are comprehensive so give them room; follow-ups are short.
                round_tokens = 3072 if round_number <= self.MANDATORY_ROUNDS else 1536
                compact: CompactRound = await self.llm_client.generate_structured(
                    response_model=CompactRound,
                    messages=[{"role": "system", "content": grounding_prefix}, {"role": "user", "content": prompt}],
                    temperature=settings.ai_temperature,
                    max_tokens=max(round_tokens, settings.ai_max_tokens),
                )
                result = compact.to_round(round_number, visit_type, specialty)
                self._mark_red_flag_options(result)
                duration = int((time.time() - start) * 1000)
                result.generation_time_ms = duration
                result.model_used         = "local-model"
                result.rag_chunk_ids      = [c.get("metadata", {}).get("chunk_id", "") for c in rag_chunks[:5]]
                self.raw_llm_log.append({"round": round_number, "model": "local-model",
                                          "duration_ms": duration})
                logger.info(f"Round {round_number} generated: {len(result.questions)} questions in {duration}ms")
                if not hasattr(self, "_round_questions"):
                    self._round_questions = {}
                self._round_questions[round_number] = result.questions
                return result
            except Exception as e:
                logger.warning(f"Round {round_number} generation attempt {attempt+1} failed: {e}")
                if attempt == self.MAX_RETRIES - 1:
                    msg = str(e)
                    if "Connection" in msg or "connect" in msg.lower() or "refused" in msg.lower():
                        raise RuntimeError(
                            "Cannot reach the local AI server at "
                            f"{__import__('os').getenv('LLM_BASE_URL', 'http://127.0.0.1:1234/v1')}. "
                            "Start it with start_local_llm.bat (or Run_MediAssist_Dev.bat) and retry."
                        )
                    raise RuntimeError(
                        f"The AI returned an unusable response for round {round_number} "
                        f"after {self.MAX_RETRIES} attempts. Try again. ({msg[:150]})"
                    )

    def _answer_digest(self) -> str:
        """Compact 'question -> chosen label' list across all rounds (the raw
        session_answers dict is just opaque option ids)."""
        lines = []
        sa = self.session_answers.dict()
        for rn in range(1, self.MAX_ROUNDS + 1):
            answers = sa.get(f"round_{rn}")
            if not answers:
                continue
            q_by_id = {q.question_id: q for q in self._round_questions.get(rn, [])}
            for qid, val in answers.items():
                q = q_by_id.get(qid)
                if not q:
                    continue
                picked = val if isinstance(val, list) else [val]
                labels = []
                for opt in (q.options or []):
                    if str(opt.id) in {str(p) for p in picked} or opt.label in picked:
                        labels.append(opt.label)
                ans = ", ".join(labels) or (picked[0] if picked else "")
                lines.append(f"R{rn}: {q.text[:70]} -> {str(ans)[:60]}")
        return "\n".join(lines[:60])

    async def assess_sufficiency(self, patient_ctx: dict, specialty: str) -> SufficiencyAssessment:
        """After the mandatory rounds, judge whether the intake is complete enough
        for a safe physician brief."""
        rounds_done = sum(1 for rn in range(1, self.MAX_ROUNDS + 1)
                          if self.session_answers.dict().get(f"round_{rn}"))
        questions_asked = sum(len(v) for v in self.session_answers.dict().values()
                              if isinstance(v, dict))
        prompt = self.prompts.get_sufficiency_prompt(
            rounds_done=rounds_done,
            questions_asked=questions_asked,
            patient_ctx=patient_ctx,
            flags_raised=list(self.session_answers.flags_raised),
            specialty=specialty,
            answer_digest=self._answer_digest(),
        )
        for attempt in range(2):
            try:
                return await self.llm_client.generate_structured(
                    response_model=SufficiencyAssessment,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=1200, temperature=0.0,
                )
            except Exception as e:
                logger.warning(f"Sufficiency assessment attempt {attempt+1} failed ({str(e)[:200]})")
        # Conservative default when the model can't produce a clean assessment:
        # if flags were raised, ask one more focused round; otherwise proceed.
        flags = list(self.session_answers.flags_raised)
        if flags:
            return SufficiencyAssessment(
                sufficient_for_brief=False,
                reason="Automated review unavailable; flags were raised, so a follow-up round is warranted.",
                focus_areas=["characterise the raised red/amber flags"],
                unresolved_flags=[str(f)[:60] for f in flags[:5]],
            )
        return SufficiencyAssessment(sufficient_for_brief=True,
                                     reason="No flags raised; automated review unavailable.")

    async def next_step(self, round_number: int, visit_type: str,
                        patient_ctx: dict, specialty: str) -> dict:
        """Decide what happens after `round_number` was just submitted.

        Returns {"action": "round", "round": N, "focus": {...}}  or
                {"action": "complete", "assessment": {...}}
        """
        if round_number < self.MANDATORY_ROUNDS:
            return {"action": "round", "round": round_number + 1, "focus": None}

        followups_done = round_number - self.MANDATORY_ROUNDS

        # Absolute ceiling: 4 mandatory + MAX_FOLLOWUPS. Anything still unresolved is
        # carried into the brief as residual uncertainty for the physician — endless
        # rephrased questions help nobody.
        if followups_done >= self.MAX_FOLLOWUPS or round_number >= self.MAX_ROUNDS:
            note = ("Follow-up rounds exhausted; remaining uncertainty is noted for the physician."
                    if followups_done else f"reached the {self.MAX_ROUNDS}-round limit")
            return {"action": "complete",
                    "assessment": {"sufficient_for_brief": True, "reason": note}}

        assessment = await self.assess_sufficiency(patient_ctx, specialty)
        self.raw_llm_log.append({"round": round_number, "step": "sufficiency",
                                 "assessment": assessment.model_dump()})

        if "unavailable" in assessment.reason.lower():
            if getattr(self, "_assessment_fallback_used", False):
                return {"action": "complete", "assessment": assessment.model_dump()}
            self._assessment_fallback_used = True

        if assessment.sufficient_for_brief:
            return {"action": "complete", "assessment": assessment.model_dump()}

        return {"action": "round", "round": round_number + 1,
                "focus": assessment.model_dump()}

    def submit_round_answers(self, round_number: int, answers: dict, scoring_tool_id: str = None,
                             questions: list = None):
        """Store answers, calculate clinical scores if applicable, and check for red flags.

        `questions` is the list of Question objects for this round (from the generated
        QuestionnaireRound). It lets us resolve selected option metadata for red-flag
        detection and standardized scoring.
        """
        setattr(self.session_answers, f"round_{round_number}", answers)

        if questions is None:
            questions = list(getattr(self, "_round_questions", {}).get(round_number, []))

        # Clinical Scoring Integration
        if scoring_tool_id:
            from scoring import clinical_tools
            try:
                score_values = self._resolve_score_values(answers, questions)

                calculation = None
                if scoring_tool_id == "phq9":
                    calculation = clinical_tools.calculate_phq9(score_values)
                elif scoring_tool_id == "gcs":
                    # GCS requires eye, verbal, motor separately - simplified for skeleton
                    if len(score_values) >= 3:
                        calculation = clinical_tools.calculate_gcs(score_values[0], score_values[1], score_values[2])
                elif scoring_tool_id == "apgar":
                    if len(score_values) >= 5:
                        calculation = clinical_tools.calculate_apgar(*score_values[:5])
                elif scoring_tool_id == "sofa":
                    if len(score_values) >= 6:
                        calculation = clinical_tools.calculate_sofa(*score_values[:6])
                
                if calculation:
                    logger.info(f"Clinical score calculated [{scoring_tool_id}]: {calculation}")
                    self.session_answers.flags_raised.append(f"Score [{scoring_tool_id.upper()}]: {calculation['score']} - {calculation['interpretation']}")
            except Exception as e:
                logger.warning(f"Failed to calculate clinical score {scoring_tool_id}: {e}")

        flags = self.flag_detector.check_answers(answers, round_number, questions=questions)
        if flags:
            self.session_answers.flags_raised.extend(flags)
        # Only true RED flags escalate to an emergency stop; AMBER is recorded but not blocking.
        emergency = any("RED FLAG" in f.upper() for f in flags)
        return {"emergency": emergency, "flags": flags}

    # A SHORT list of unambiguous emergencies — used only as a light safety net on
    # top of the LLM's own flag_opts. Broad keyword matching over-flags badly.
    CRITICAL_PHRASES = (
        "crushing chest", "chest pain radiating", "tearing chest", "ripping",
        "unable to breathe", "can't breathe", "cannot breathe", "gasping",
        "unconscious", "passed out", "unresponsive", "not breathing",
        "blue lips", "bluish lips", "cyanosis", "coughing up blood",
        "heavy bleeding", "uncontrolled bleeding", "suicidal", "want to end my life",
        "worst headache of my life", "sudden severe headache", "seizure right now",
        "face droop", "slurred speech", "one-sided weakness", "anaphylaxis",
        "no fetal movement",
    )

    def _mark_red_flag_options(self, round_result):
        """Light safety net over the LLM's own flag_opts: flag an option ONLY when
        its own label unambiguously names an emergency. Never flag from question
        text (that flags every 'Yes' on a cardiac form)."""
        for q in round_result.questions:
            for opt in (q.options or []):
                label = opt.label.lower().strip()
                if any(neg in label for neg in ("no ", "none", "not ", "denies", "absent", "never", "n/a")):
                    continue
                if any(p in label for p in self.CRITICAL_PHRASES):
                    opt.is_red_flag = True

    @staticmethod
    def _resolve_score_values(answers: dict, questions: list) -> list:
        """Map selected option ids -> integer values (option.value, else trailing int in label,
        else the raw answer if it is already numeric). Preserves question order."""
        q_by_id = {getattr(q, "question_id", None): q for q in (questions or [])}
        ordered_ids = [getattr(q, "question_id", None) for q in (questions or [])] or list(answers.keys())
        values = []
        for q_id in ordered_ids:
            if q_id not in answers:
                continue
            ans = answers[q_id]
            q = q_by_id.get(q_id)
            picked = ans[0] if isinstance(ans, list) and ans else ans
            if q is not None and getattr(q, "options", None):
                opt = next((o for o in q.options if str(o.id) == str(picked) or o.label == picked), None)
                if opt is not None:
                    if opt.value is not None:
                        values.append(int(opt.value)); continue
                    import re
                    m = re.search(r"(\d+)", opt.label)
                    if m:
                        values.append(int(m.group(1))); continue
            if str(picked).lstrip("-").isdigit():
                values.append(int(picked))
        return values
