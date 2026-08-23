"""Repository and store for investigator feedback records."""
from typing import Dict, List, Optional
import pandas as pd
from pathlib import Path
from src.feedback.models import InvestigatorFeedback, ReviewOutcome, FeedbackAction, FeedbackCategory


class FeedbackStore:
    """Modular in-memory and persistent store for investigator review feedback."""

    def __init__(self, feedback_path: Optional[Path] = None):
        self._records: Dict[str, InvestigatorFeedback] = {}
        self.load_csv(feedback_path or Path(__file__).resolve().parents[2] / "data" / "investigator_feedback.csv")

    def load_csv(self, feedback_path: Path) -> None:
        """Load human feedback records from a structured CSV input."""
        if not feedback_path.exists():
            return
        feedback_df = pd.read_csv(feedback_path).fillna("")
        for row in feedback_df.to_dict(orient="records"):
            self.add_feedback(
                InvestigatorFeedback(
                    case_id=str(row["case_id"]),
                    review_outcome=ReviewOutcome(str(row["review_outcome"])),
                    action=FeedbackAction(str(row["action"])),
                    category=FeedbackCategory(str(row["category"])),
                    reason=str(row["reason"]),
                    evidence_context=str(row["evidence_context"]),
                    feedback_date=str(row.get("feedback_date", "")),
                    investigator_id=str(row.get("investigator_id", "")),
                )
            )


    def add_feedback(self, feedback: InvestigatorFeedback):
        """Add or update an investigator feedback record."""
        self._records[feedback.case_id] = feedback

    def get_feedback(self, case_id: str) -> Optional[InvestigatorFeedback]:
        """Retrieve feedback for a specific case."""
        return self._records.get(case_id)

    def get_all_feedback(self) -> List[InvestigatorFeedback]:
        """Return all recorded feedback objects."""
        return list(self._records.values())

    def to_dataframe(self) -> pd.DataFrame:
        """Export feedback records to DataFrame."""
        if not self._records:
            return pd.DataFrame(columns=[
                "case_id", "review_outcome", "action", "category",
                "reason", "evidence_context", "feedback_date", "investigator_id"
            ])
        return pd.DataFrame([f.to_dict() for f in self._records.values()])

    def is_case_excluded(self, case_id: str) -> bool:
        """Check if case should be excluded based on investigator review."""
        fb = self.get_feedback(case_id)
        if fb and fb.action == FeedbackAction.EXCLUDE_FROM_WORKLIST:
            return True
        return False
