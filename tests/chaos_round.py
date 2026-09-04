"""Adversarial: feed weird QuestionnaireRound JSON and weird answers; nothing should crash."""
import os, sys, json, traceback
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

FAIL = []


def ck(name, fn):
    try:
        fn(); print("PASS", name)
    except Exception as e:
        FAIL.append(name); print("FAIL", name, "->", repr(e)); traceback.print_exc()


def main():
    import PySide6.QtWidgets as W
    for m in ("information", "warning", "critical", "question"):
        setattr(W.QMessageBox, m, staticmethod(lambda *a, **k: None))
    app = W.QApplication(sys.argv)

    from models.questionnaire import QuestionnaireRound
    from ui.questionnaire_ui import QuestionnaireUI

    class FakeCtl:
        class _E:
            _round_questions = {}
            session_answers = None
            def submit_round_answers(self, *a, **k): return {"emergency": False, "flags": []}
        questionnaire_engine = _E()
        current_user = None
        def log_activity(self, *a, **k): pass

    weird_rounds = [
        # radio/checkbox with null options
        {"round_number": 1, "visit_type": "v", "specialty": "s", "questions": [
            {"question_id": "q1", "round": 1, "text": "radio no opts", "type": "radio"},
            {"question_id": "q2", "round": 1, "text": "checkbox empty", "type": "checkbox", "options": []},
            {"question_id": "q3", "round": 1, "text": "rate 0 to 10 severity", "type": "radio"},
            {"question_id": "q4", "round": 1, "text": "scale no opts", "type": "scale"},
            {"question_id": "q5", "round": 1, "text": "body map", "type": "body_map"},
            {"question_id": "q6", "round": 1, "text": "dup ids", "type": "radio",
             "options": [{"id": "x", "label": "A"}, {"id": "x", "label": "B"}]},
        ]},
        # single option, and option missing id
        {"round_number": 2, "visit_type": "v", "specialty": "s", "questions": [
            {"question_id": "s1", "round": 2, "text": "one opt", "type": "radio",
             "options": [{"id": "only", "label": "Only"}]},
            {"question_id": "s2", "round": 2, "text": "blank id", "type": "checkbox",
             "options": [{"id": "", "label": "P"}, {"id": "", "label": "Q"}]},
        ]},
        # empty question list
        {"round_number": 3, "visit_type": "v", "specialty": "s", "questions": []},
    ]

    for i, raw in enumerate(weird_rounds):
        ck(f"validate weird round {i}", lambda raw=raw: QuestionnaireRound.model_validate(raw))

    for i, raw in enumerate(weird_rounds):
        r = QuestionnaireRound.model_validate(raw)
        for q in r.questions:
            from models.questionnaire import OptionType
            if q.type in (OptionType.RADIO, OptionType.CHECKBOX, OptionType.SCALE):
                assert q.options and len(q.options) >= 2, f"round{i} {q.question_id} still un-answerable: {q.options}"
        ck(f"render weird round {i}", lambda r=r: _render(QuestionnaireUI(FakeCtl()), r))

    # submit with mismatched / weird answers
    ui = QuestionnaireUI(FakeCtl())
    r = QuestionnaireRound.model_validate(weird_rounds[0])
    _render(ui, r)
    ck("submit with no answers (mandatory)", ui.submit_round)  # should warn, not crash
    for w in ui.widgets.values():
        _answer(w)
    ck("submit with answers", ui.submit_round)

    print()
    print("CHAOS FAILURES:", FAIL or "none")
    sys.exit(1 if FAIL else 0)


def _render(ui, r):
    ui.current_round_data = r
    ui.render_round(r)


def _answer(widget):
    from PySide6.QtWidgets import QRadioButton, QCheckBox, QSlider, QTextEdit
    for rb in widget.findChildren(QRadioButton):
        rb.setChecked(True); break
    for cb in widget.findChildren(QCheckBox):
        cb.setChecked(True)
    for sl in widget.findChildren(QSlider):
        sl.setValue(sl.maximum())
    for te in widget.findChildren(QTextEdit):
        te.setPlainText("x")


if __name__ == "__main__":
    main()
