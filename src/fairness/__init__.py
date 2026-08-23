"""Fairness and demographic impact analysis."""
from src.fairness.metrics import (
    compute_population_baselines,
    evaluate_demographic_fairness,
    generate_fairness_markdown_report,
    DEFAULT_DEMOGRAPHIC_DIMENSIONS,
)

__all__ = [
    "compute_population_baselines",
    "evaluate_demographic_fairness",
    "generate_fairness_markdown_report",
    "DEFAULT_DEMOGRAPHIC_DIMENSIONS",
]

