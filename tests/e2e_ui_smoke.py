"""
Offscreen end-to-end UI smoke test with a MOCK LLM (fast, no server needed).

Exercises: login (all roles) -> patient intake -> every questionnaire widget type
-> submit each round -> vitals -> report generation -> report viewer ->
physician dashboard -> documents / settings / audit views -> logout.

Run:  QT_QPA_PLATFORM=offscreen .venv/Scripts/python.exe tests/e2e_ui_smoke.py
Exit code 0 = clean, 1 = at least one failure (details printed).
"""
import os
import sys
import traceback

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

FAILURES = []


def check(name, fn):
    try:
        fn()
        print(f"  PASS  {name}")
    except Exception as e:
        FAILURES.append((name, e, traceback.format_exc()))
        print(f"  FAIL  {name}: {e}")


def build_round(round_number):
    from models.questionnaire import QuestionnaireRound, Question, MCQOption, OptionType
    qs = [
        Question(question_id=f"r{round_number}_radio", round=round_number,
                 text="Do you have a fever?", type=OptionType.RADIO,
                 options=[MCQOption(id="yes", label="Yes", is_red_flag=(round_number == 1)),
                          MCQOption(id="no", label="No")]),
        Question(question_id=f"r{round_number}_check", round=round_number,
                 text="Select any that apply", type=OptionType.CHECKBOX,
                 options=[MCQOption(id="a", label="Cough"), MCQOption(id="b", label="Headache")]),
        Question(question_id=f"r{round_number}_scale", round=round_number,
                 text="Rate pain 0-10", type=OptionType.SCALE,
                 options=[MCQOption(id=str(i), label=str(i), value=i) for i in range(11)]),
        Question(question_id=f"r{round_number}_date", round=round_number,
                 text="When did it start (date)?", type=OptionType.DATE),
        Question(question_id=f"r{round_number}_dur", round=round_number,
                 text="For how long?", type=OptionType.DURATION),
        Question(question_id=f"r{round_number}_text", round=round_number,
                 text="Anything else?", type=OptionType.TEXT, is_mandatory=False),
    ]
    return QuestionnaireRound(round_number=round_number, visit_type="Specific Complaint / Acute Visit",
                              specialty="General Medicine", questions=qs)


def build_brief():
    from models.report_output import PhysicianBrief, DifferentialDiagnosis, ClinicalFlag
    return PhysicianBrief(
        case_number="SMOKE-1",
        flags=[ClinicalFlag(level="AMBER", reason="fever", category="triage")],
        differentials=[DifferentialDiagnosis(condition_name="Acute bronchitis", confidence_score=0.6,
                                             reasoning_summary="cough + fever")],
        examination_plan=["chest auscultation"],
        recommended_investigations=["CXR if not improving"],
        rag_sources=[],
    )


def main():
    import PySide6.QtWidgets as W
    # neutralise blocking dialogs
    for m in ("information", "warning", "critical", "question"):
        setattr(W.QMessageBox, m, staticmethod(lambda *a, **k: W.QMessageBox.StandardButton.Yes))

    app = W.QApplication(sys.argv)

    from app_controller import AppController
    controller = AppController()
    controller.initialize()

    # --- mock the engine + report generator (no LLM) ---
    eng = controller.questionnaire_engine

    async def fake_generate_round(round_number, visit_type, patient_ctx, specialty):
        r = build_round(round_number)
        eng._round_questions[round_number] = r.questions
        return r
    eng.generate_round = fake_generate_round

    async def fake_report(**kw):
        return build_brief()
    controller.report_generator.generate = fake_report

    from ui.main_window import MainWindow
    win = MainWindow(controller=controller)

    check("construct MainWindow", lambda: win)

    for role in ("NURSE", "DOCTOR", "ADMIN"):
        check(f"login as {role}", lambda role=role: win._on_login_success("tester", role))
        for view in ("dashboard", "patients", "questionnaire", "vitals",
                     "physician", "documents", "settings", "audit"):
            check(f"  nav {role} -> {view}", lambda v=view: win.navigate_to(v))

    # --- intake ---
    win._on_login_success("tester", "ADMIN")
    pv = win.patient_view
    pv.input_first_name.setText("Test")
    pv.input_last_name.setText("Patient")
    pv.input_complaint.setText("cough and fever")
    check("patient: click Start Intake", pv._on_start_clicked)

    q = win.questionnaire_view

    def run_round():
        # wait for the (mocked, sync-ish) worker
        for _ in range(200):
            app.processEvents()
            if q.current_round_data is not None and q.btn_submit.isEnabled():
                break
        assert q.current_round_data is not None, "round did not load"
        # answer every widget
        for qid, widget in q.widgets.items():
            _answer_widget(widget)
        q.submit_round()
        app.processEvents()

    def _answer_widget(widget):
        from PySide6.QtWidgets import QRadioButton, QCheckBox, QSlider, QTextEdit
        rbs = widget.findChildren(QRadioButton)
        if rbs:
            rbs[0].setChecked(True)
        for cb in widget.findChildren(QCheckBox):
            cb.setChecked(True)
        for sl in widget.findChildren(QSlider):
            sl.setValue(sl.maximum())
        for te in widget.findChildren(QTextEdit):
            te.setPlainText("n/a")

    for rnd in range(1, 5):
        check(f"questionnaire round {rnd}", run_round)

    # After round 4 the UI emits session_complete -> navigate to vitals
    app.processEvents()
    check("nav to vitals present", lambda: win.navigate_to("vitals"))

    vs = win.vital_signs_view
    vs.vitals_form.hr_input.setText("88")
    vs.vitals_form.bp_input.setText("120/80")
    vs.vitals_form.temp_input.setText("38.1")
    vs.vitals_form.rr_input.setText("18")
    case_no = win.active_case["case_number"]
    brief_path = os.path.join("data", "cases", case_no, "physician_brief.json")
    if os.path.exists(brief_path):
        os.remove(brief_path)
    check("vitals: click Generate Brief", vs._on_generate_clicked)

    import time as _t
    for _ in range(400):
        app.processEvents()
        _t.sleep(0.02)
        if os.path.exists(brief_path):
            break
    check("physician_brief.json written",
          lambda: (_ for _ in ()).throw(AssertionError(f"not written at {brief_path}"))
          if not os.path.exists(brief_path) else None)

    check("report viewer populated",
          lambda: win.report_viewer.load_brief(build_brief().model_dump(mode="json")))
    check("physician dashboard refresh", win.physician_view.refresh_data)
    check("open saved report", lambda: win._open_saved_report(case_no))
    check("logout", win._on_logout)

    print()
    if FAILURES:
        print(f"{len(FAILURES)} FAILURE(S):\n")
        for name, err, tb in FAILURES:
            print(f"### {name}\n{tb}")
        sys.exit(1)
    print("ALL UI SMOKE CHECKS PASSED")


if __name__ == "__main__":
    main()
