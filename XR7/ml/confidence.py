"""
Bayesian confidence score updater for XR7 Engine 2.

When a claim is resolved (ACCEPTED / CLOSED with recovered amount), we learn
whether the original anomaly detection was correct.  This module maintains a
lightweight Beta-distribution prior per (category, subtype) pair and updates
it from historical outcomes.

The updated posterior mean is used as the refined confidence score for future
anomalies of the same type, replacing the static hand-coded scores in the rule
files.

Design
------
We model the probability P(anomaly is valid | category, subtype) with a
Beta(α, β) prior.

- Each confirmed true-positive increments α.
- Each confirmed false-positive increments β.
- The posterior mean is α / (α + β).

Priors start at Beta(2, 1) (slight positive bias) to reflect that rules were
designed conservatively.
"""

from __future__ import annotations

from dataclasses import dataclass

# ---------------------------------------------------------------------------
# Default prior (slightly optimistic)
# ---------------------------------------------------------------------------

# Default prior: Beta(2, 1).
# Chosen to reflect that our detection rules are designed conservatively —
# we expect more true-positives than false-positives.  The prior mean is
# 2/(2+1) ≈ 0.667, which is deliberately more optimistic than a flat Beta(1,1)
# prior (mean 0.5) but still shrinks towards 1.0 as evidence accumulates.
_PRIOR_ALPHA = 2.0  # pseudo-counts: confirmed true-positives
_PRIOR_BETA = 1.0  # pseudo-counts: confirmed false-positives


# ---------------------------------------------------------------------------
# Beta distribution helpers
# ---------------------------------------------------------------------------


def _beta_mean(alpha: float, beta: float) -> float:
    return alpha / (alpha + beta)


def _beta_std(alpha: float, beta: float) -> float:
    n = alpha + beta
    return (alpha * beta / (n * n * (n + 1))) ** 0.5


# ---------------------------------------------------------------------------
# Outcome type
# ---------------------------------------------------------------------------


class AnomalyOutcome:
    TRUE_POSITIVE = "TRUE_POSITIVE"  # claim accepted / recovered amount > 0
    FALSE_POSITIVE = "FALSE_POSITIVE"  # claim closed with no recovery


# ---------------------------------------------------------------------------
# Updater class
# ---------------------------------------------------------------------------


@dataclass
class _Prior:
    alpha: float = _PRIOR_ALPHA
    beta: float = _PRIOR_BETA


class ConfidenceUpdater:
    """
    Maintains a Beta-distribution prior for each anomaly type and updates it
    from claim resolution outcomes.

    Usage::

        updater = ConfidenceUpdater()

        # At claim resolution time:
        updater.record_outcome("ROYALTY", "MISSING_PAYMENT", AnomalyOutcome.TRUE_POSITIVE)

        # When scoring a new anomaly of the same type:
        score = updater.refined_confidence("ROYALTY", "MISSING_PAYMENT", raw_score=0.85)
    """

    def __init__(self) -> None:
        # Map (category, subtype) → Beta prior
        self._priors: dict[tuple[str, str], _Prior] = {}

    def _get_prior(self, category: str, subtype: str) -> _Prior:
        key = (category, subtype)
        if key not in self._priors:
            self._priors[key] = _Prior()
        return self._priors[key]

    def record_outcome(
        self,
        category: str,
        subtype: str,
        outcome: str,
    ) -> None:
        """
        Update the Beta prior for *(category, subtype)* from a resolved claim.

        Parameters
        ----------
        category:
            Anomaly category string (e.g. ``"ROYALTY"``).
        subtype:
            Anomaly subtype string (e.g. ``"MISSING_PAYMENT"``).
        outcome:
            One of :attr:`AnomalyOutcome.TRUE_POSITIVE` or
            :attr:`AnomalyOutcome.FALSE_POSITIVE`.
        """
        prior = self._get_prior(category, subtype)
        if outcome == AnomalyOutcome.TRUE_POSITIVE:
            prior.alpha += 1.0
        elif outcome == AnomalyOutcome.FALSE_POSITIVE:
            prior.beta += 1.0

    def refined_confidence(
        self,
        category: str,
        subtype: str,
        raw_score: float,
        blend_weight: float = 0.5,
    ) -> float:
        """
        Return a refined confidence score that blends the rule's raw score with
        the Beta posterior mean.

        Parameters
        ----------
        category:
            Anomaly category.
        subtype:
            Anomaly subtype.
        raw_score:
            The static confidence score emitted by the rule or ML model.
        blend_weight:
            Weight given to the posterior mean.  ``0.5`` gives equal weight to
            the raw rule score and the learned posterior.  Range [0, 1].

        Returns
        -------
        Float in [0, 1].
        """
        prior = self._get_prior(category, subtype)
        posterior_mean = _beta_mean(prior.alpha, prior.beta)
        blended = blend_weight * posterior_mean + (1.0 - blend_weight) * float(raw_score)
        return round(min(max(blended, 0.0), 1.0), 4)

    def precision_stats(self, category: str, subtype: str) -> dict:
        """
        Return statistics about the Beta posterior for a given anomaly type.

        Returns
        -------
        Dict with ``posterior_mean``, ``posterior_std``, ``alpha``, ``beta``,
        and ``sample_count``.
        """
        prior = self._get_prior(category, subtype)
        return {
            "category": category,
            "subtype": subtype,
            "alpha": prior.alpha,
            "beta": prior.beta,
            "posterior_mean": round(_beta_mean(prior.alpha, prior.beta), 4),
            "posterior_std": round(_beta_std(prior.alpha, prior.beta), 4),
            "sample_count": int(prior.alpha + prior.beta - _PRIOR_ALPHA - _PRIOR_BETA),
        }

    def all_stats(self) -> list[dict]:
        """Return precision stats for every (category, subtype) that has been updated."""
        return [self.precision_stats(cat, sub) for cat, sub in self._priors]

    def bulk_record_from_claims(self, claims: list[dict]) -> None:
        """
        Convenience method to update priors from a list of claim dicts.

        Each dict is expected to contain:
        - ``category`` and ``subtype`` (from the linked anomaly)
        - ``status``: ``"PAID"`` or ``"CLOSED"`` to trigger an update
        - ``recovered_amount``: float; > 0 means true-positive

        Parameters
        ----------
        claims:
            List of claim dicts.
        """
        for claim in claims:
            status = claim.get("status", "")
            if status not in ("PAID", "CLOSED"):
                continue
            category = claim.get("category", "")
            subtype = claim.get("subtype", "")
            if not category or not subtype:
                continue
            recovered = float(claim.get("recovered_amount", 0.0) or 0.0)
            outcome = (
                AnomalyOutcome.TRUE_POSITIVE if recovered > 0.0 else AnomalyOutcome.FALSE_POSITIVE
            )
            self.record_outcome(category, subtype, outcome)
