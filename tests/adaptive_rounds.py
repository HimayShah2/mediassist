"""Verify the questionnaire runs the 4 mandatory rounds, then adaptive follow-up
rounds until the engine says it's sufficient — driven through the real UI widget."""
import os, sys, time
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
os.environ.setdefault("LLM_BASE_URL", "http://127.0.0.1:59999/v1")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

FAIL = []


def main():
    import PySide6.QtWidgets as W
    for m in ("information", "warning", "critical", "question"):
        setattr(W.QMessageBox, m, staticmethod(lambda *a, **k: None))
    W.QMessageBox.exec = lambda self, *a, **k: 0
    app = W.QApplication(sys.argv)

    from app_controller import AppController
    from models.questionnaire import QuestionnaireRound, Question, MCQOption, OptionType
    c = AppController(); c.initialize()
    eng = c.questionnaire_engine

    generated_rounds = []
    focuses = []

    async def fake_gen(round_number, visit_type, patient_ctx, specialty, focus=None):
        generated_rounds.append(round_number)
        focuses.append(focus)
        qs = [Question(question_id=f"r{round_number}q{i}", round=round_number, text=f"Q{i}",
                       type=OptionType.RADIO,
                       options=[MCQOption(id="y", label="Yes"), MCQOption(id="n", label="No")])
              for i in range(3)]
        r = QuestionnaireRound(round_number=round_number, visit_type=visit_type,
                               specialty=specialty, questions=qs)
        eng._round_questions[round_number] = r.questions
        return r
    eng.generate_round = fake_gen

    # Not sufficient after round 4 or 5; sufficient after round 6.
    async def fake_next_step(round_number, *a):
        if round_number < 4:
            return {"action": "round", "round": round_number + 1, "focus": None}
        if round_number < 6:
            return {"action": "round", "round": round_number + 1,
                    "focus": {"focus_areas": ["clarify chest pain character"],
                              "unresolved_flags": ["dyspnoea"], "leading_differentials": ["ACS", "PE"]}}
        return {"action": "complete", "assessment": {"sufficient_for_brief": True}}
    eng.next_step = fake_next_step

    from ui.main_window import MainWindow
    win = MainWindow(controller=c)
    win._on_login_success("t", "ADMIN")
    complete_fired = []
    win.questionnaire_view.session_complete.connect(lambda: complete_fired.append(True))
    win._start_questionnaire("Specific Complaint / Acute Visit",
                             {"case_number": "ADAPT-1", "chief_complaint_summary": "chest pain"},
                             "Cardiology")
    q = win.questionnaire_view

    def answer_and_submit():
        for _ in range(400):
            app.processEvents(); time.sleep(0.01)
            if q.current_round_data is not None and q.btn_submit.isEnabled():
                break
        assert q.current_round_data is not None, f"round {generated_rounds[-1:]} did not load"
        for w in q.widgets.values():
            rbs = w.findChildren(W.QRadioButton)
            if rbs:
                rbs[0].setChecked(True)
        q.current_round_data = None if False else q.current_round_data
        prev = q.current_round_data.round_number
        q.submit_round()
        # wait until either a new round loads or completion fires
        for _ in range(600):
            app.processEvents(); time.sleep(0.01)
            if complete_fired or (q.current_round_data is not None
                                  and q.current_round_data.round_number != prev
                                  and q.btn_submit.isEnabled()):
                break

    for _ in range(8):
        if complete_fired:
            break
        answer_and_submit()

    print("rounds generated:", generated_rounds)
    print("completion fired:", bool(complete_fired))
    print("focus passed to round 5:", focuses[4] if len(focuses) > 4 else None)

    assert generated_rounds[:4] == [1, 2, 3, 4], "mandatory rounds wrong"
    assert 5 in generated_rounds and 6 in generated_rounds, "adaptive follow-up rounds did not run"
    assert 7 not in generated_rounds, "did not stop when sufficient"
    assert complete_fired, "session never completed"
    assert isinstance(focuses[4], dict) and focuses[4].get("focus_areas"), "focus not passed to follow-up"
    print("ADAPTIVE ROUNDS OK")


if __name__ == "__main__":
    main()
