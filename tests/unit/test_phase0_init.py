import pytest
from sqlalchemy import create_engine, text
from ui.main_window import MainWindow

def test_pyside6_app_initialization(qapp):
    """
    Verify that the PySide6 application (MainWindow) can instantiate without crashing.
    """
    window = MainWindow()
    assert window is not None
    assert window.windowTitle() == "MediAssist Pro"

def test_database_engine_in_memory():
    """
    Verify that the database engine can connect to a test in-memory SQLite DB.
    """
    engine = create_engine("sqlite:///:memory:", echo=False)
    
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1")).scalar()
            assert result == 1
    except Exception as e:
        pytest.fail(f"Database connection to in-memory SQLite failed: {e}")
