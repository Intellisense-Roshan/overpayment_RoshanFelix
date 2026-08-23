"""Data models for human investigator feedback and two-tier status tracking."""
from dataclasses import dataclass
from enum import Enum
from typing import Optional, List, Dict, Any


class ReviewOutcome(str, Enum):
    INVESTIGATOR_CONFIRMED_LEGITIMATE = "INVESTIGATOR_CONFIRMED_LEGITIMATE"
    CONFIRMED_DISCREPANCY = "CONFIRMED_DISCREPANCY"
    DEPARTMENTAL_PROCESSING_ERROR = "DEPARTMENTAL_PROCESSING_ERROR"
    PENDING_INVESTIGATION = "PENDING_INVESTIGATION"


class AlgorithmicSignalStatus(str, Enum):
    NO_HARD_SIGNAL = "NO_HARD_SIGNAL"
    POST_CLOSURE_CONTINUATION = "POST_CLOSURE_CONTINUATION"
    IN_MONTH_DUPLICATE = "IN_MONTH_DUPLICATE"
    SEVERE_AWARD_SPIKE = "SEVERE_AWARD_SPIKE"


class FeedbackAction(str, Enum):
    EXCLUDE_FROM_WORKLIST = "EXCLUDE_FROM_WORKLIST"
    MAINTAIN_PRIORITY = "MAINTAIN_PRIORITY"
    DEPRIORITIZE = "DEPRIORITIZE"
    FLAG_FOR_RECHECK = "FLAG_FOR_RECHECK"


class FeedbackCategory(str, Enum):
    DOCUMENTED_INCOME_CHANGE = "DOCUMENTED_INCOME_CHANGE"
    DEPARTMENTAL_PROCESSING_CORRECTION = "DEPARTMENTAL_PROCESSING_CORRECTION"
    LANGUAGE_COMMUNICATION_ASSISTANCE = "LANGUAGE_COMMUNICATION_ASSISTANCE"
    UNTERMINATED_POST_CLOSURE = "UNTERMINATED_POST_CLOSURE"
    DUPLICATE_BATCH_DISBURSEMENT = "DUPLICATE_BATCH_DISBURSEMENT"
    SYSTEMIC_MULTIPLIER_ERROR = "SYSTEMIC_MULTIPLIER_ERROR"


@dataclass
class InvestigatorFeedback:
    case_id: str
    review_outcome: ReviewOutcome
    action: FeedbackAction
    category: FeedbackCategory
    reason: str
    evidence_context: str
    feedback_date: str = "2026-08-23"
    investigator_id: str = "INV-BRITE-06"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "case_id": self.case_id,
            "review_outcome": self.review_outcome.value,
            "action": self.action.value,
            "category": self.category.value,
            "reason": self.reason,
            "evidence_context": self.evidence_context,
            "feedback_date": self.feedback_date,
            "investigator_id": self.investigator_id,
        }

