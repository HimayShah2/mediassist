from typing import List, Dict, Iterable


class RedFlagDetector:
    """Scans questionnaire answers for emergency / warning clinical markers.

    Two mechanisms:
    1. Structured: any selected MCQ option the LLM marked is_red_flag / is_amber_flag.
    2. Keyword fallback: free-text answers containing emergency phrases.
    """

    EMERGENCY_KEYWORDS = [
        "chest pain", "shortness of breath", "difficulty breathing",
        "loss of consciousness", "unconscious", "facial droop", "slurred speech",
        "severe bleeding", "uncontrolled bleeding", "suicidal", "self harm",
        "meningitis", "stiff neck", "fetal distress", "no fetal movement",
        "blue lips", "seizure", "anaphylaxis", "worst headache",
    ]

    def check_answers(self, answers: Dict, round_number: int,
                      questions: Iterable = None) -> List[str]:
        flags: List[str] = []

        # --- 1. Structured option flags ---
        if questions:
            q_by_id = {getattr(q, "question_id", None): q for q in questions}
            for q_id, answer in answers.items():
                q = q_by_id.get(q_id)
                if not q or not getattr(q, "options", None):
                    continue
                selected_ids = answer if isinstance(answer, list) else [answer]
                selected_ids = {str(s) for s in selected_ids}
                for opt in q.options:
                    if str(opt.id) in selected_ids or opt.label in selected_ids:
                        if getattr(opt, "is_red_flag", False):
                            flags.append(f"RED FLAG: '{opt.label}' (Q: {q.text})")
                        elif getattr(opt, "is_amber_flag", False):
                            flags.append(f"AMBER: '{opt.label}' (Q: {q.text})")

        # --- 2. Keyword fallback on free text ---
        for q_id, answer in answers.items():
            texts = answer if isinstance(answer, list) else [answer]
            for t in texts:
                if isinstance(t, str):
                    low = t.lower()
                    for kw in self.EMERGENCY_KEYWORDS:
                        if kw in low:
                            flags.append(f"RED FLAG: emergency keyword '{kw}' in {q_id}")

        # de-dup, preserve order
        seen = set()
        out = []
        for f in flags:
            if f not in seen:
                seen.add(f)
                out.append(f)
        return out
