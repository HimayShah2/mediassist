from pydantic import BaseModel, Field
from typing import Optional, Literal, List
from enum import Enum

class OptionType(str, Enum):
    RADIO    = "radio"       # Single select
    CHECKBOX = "checkbox"    # Multi-select
    SCALE    = "scale"       # 0-10 slider
    BODY_MAP = "body_map"    # SVG anatomical location picker
    TEXT     = "text"        # Free nurse note (short)
    DATE     = "date"        # Date picker
    DURATION = "duration"    # Duration selector (hours/days/weeks/months)

class MCQOption(BaseModel):
    id:        str
    label:     str
    is_red_flag:   bool = False   # If selected -> RED clinical flag
    is_amber_flag: bool = False   # If selected -> AMBER flag
    differential_indicator: Optional[str] = None  # Which differential this supports

class Question(BaseModel):
    question_id:      str
    round:            int  # 1-4
    text:             str
    type:             OptionType
    options:          Optional[List[MCQOption]] = None
    nurse_explanation: Optional[str] = None  # Plain-language explanation shown via info button
    is_mandatory:     bool = True
    body_map_region:  Optional[str] = None   # Which SVG body region to pre-highlight
    triggers_followup: Optional[str] = None  # question_id of conditional follow-up

class QuestionnaireRound(BaseModel):
    round_number:       int
    visit_type:         str
    specialty:          str
    questions:          List[Question]
    rag_context_used:   List[str]   # Source document titles cited
    rag_chunk_ids:      List[str]   # Raw chunk IDs for physician raw data access
    model_used:         str
    generation_time_ms: int
    working_differentials: Optional[List[str]] = None  # Rounds 3-4 only
    scoring_tool_id: Optional[str] = None  # e.g., "phq9", "gcs", "apgar"
    
    model_config = {"protected_namespaces": ()}

class SessionAnswers(BaseModel):
    """Accumulated answers across all rounds — passed as context to each subsequent round."""
    round_1: Optional[dict] = None
    round_2: Optional[dict] = None
    round_3: Optional[dict] = None
    round_4: Optional[dict] = None
    vital_signs: Optional[dict] = None
    flags_raised: List[str] = []
