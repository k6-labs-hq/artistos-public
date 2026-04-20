"""Billing and revenue integrity detector."""

from datetime import datetime, timedelta, timezone

from sqlalchemy import and_, func, select

from intelligence.monitor.detector import Detector
from intelligence.monitor.types import Finding, FindingSeverity, PlatformState
from XR7.models.artist import Artist
from XR7.models.claim import Claim, ClaimStatus


class BillingDetector(Detector):
    """Monitors billing integrity, disbursement health, and fee calculation accuracy."""

    @property
    def name(self) -> str:
        return "billing-integrity-detector"

    @property
    def domain(self) -> str:
        return "billing"

    def detect(self, state: PlatformState) -> list[Finding]:
        findings = []

        findings.extend(self._check_trolley_failure_rate(state))
        findings.extend(self._check_fee_calculation_drift(state))
        findings.extend(self._check_founders_circle_capacity(state))

        return findings

    def _check_trolley_failure_rate(self, state: PlatformState) -> list[Finding]:
        """Check for elevated Trolley disbursement failure rate."""
        # Look at last 7 days of disbursement attempts
        week_ago = datetime.now(timezone.utc) - timedelta(days=7)

        stmt = select(
            func.count(Claim.id).label("total"),
            func.sum((Claim.trolley_payment_status == "failed").cast(int)).label("failed"),
        ).where(
            and_(
                Claim.trolley_payment_id.isnot(None),
                Claim.updated_at >= week_ago,
            )
        )

        result = state.db_session.execute(stmt).first()

        if result and result.total > 0:
            total, failed = result.total, result.failed or 0
            failure_rate = failed / total

            # Alert if failure rate exceeds 5%
            if failure_rate > 0.05:
                return [
                    Finding(
                        detector=self.name,
                        severity=FindingSeverity.P1,
                        domain=self.domain,
                        title=f"trolley disbursement failure rate elevated ({failure_rate:.1%})",
                        description=f"Last 7 days: {failed} of {total} Trolley disbursements failed. Normal failure rate is <5%. This delays artist payouts and degrades platform trust.",
                        expected_behavior="Trolley disbursement failure rate should remain below 5%. Failures should be investigated and resolved within 48 hours.",
                        investigation_path=[
                            f"Query failed disbursements: SELECT id, artist_id, trolley_payment_id, payout_failure_reason FROM claims WHERE trolley_payment_status = 'failed' AND updated_at >= '{week_ago.isoformat()}'",
                            "Check Trolley API health and rate limit status",
                            "Review payout_failure_reason patterns for systemic issues",
                            "Verify artist payout recipient details are current",
                        ],
                        metadata={
                            "total_disbursements": total,
                            "failed_disbursements": failed,
                            "failure_rate": failure_rate,
                            "threshold": 0.05,
                            "period_days": 7,
                        },
                    )
                ]

        return []

    def _check_fee_calculation_drift(self, state: PlatformState) -> list[Finding]:
        """Check for fee calculation anomalies."""
        # Sample recent recovered claims and verify fee calculation
        stmt = (
            select(
                Claim.id,
                Claim.recovered_amount,
                Claim.contingency_fee,
                Artist.contingency_fee_percent,
            )
            .join(Artist, Artist.id == Claim.artist_id)
            .where(
                and_(
                    Claim.status == ClaimStatus.RESOLVED,
                    Claim.recovered_amount.isnot(None),
                    Claim.contingency_fee.isnot(None),
                )
            )
            .order_by(Claim.updated_at.desc())
            .limit(100)
        )

        results = state.db_session.execute(stmt).all()

        drift_cases = []
        for claim_id, recovered, fee, artist_rate in results:
            expected_fee = recovered * (artist_rate / 100)
            # Allow 1 cent tolerance for floating point
            if abs(fee - expected_fee) > 0.01:
                drift_cases.append(
                    {
                        "claim_id": claim_id,
                        "recovered_amount": recovered,
                        "recorded_fee": fee,
                        "expected_fee": expected_fee,
                        "drift": fee - expected_fee,
                        "artist_rate": artist_rate,
                    }
                )

        if drift_cases:
            total_drift = sum(case["drift"] for case in drift_cases)
            return [
                Finding(
                    detector=self.name,
                    severity=FindingSeverity.P0,
                    domain=self.domain,
                    title=f"fee calculation drift detected ({len(drift_cases)} claims, ${abs(total_drift):.2f})",
                    description=f"Found {len(drift_cases)} claims where recorded contingency_fee does not match artist_rate × recovered_amount. Total drift: ${total_drift:.2f}. This indicates fee calculation logic error or data corruption.",
                    expected_behavior="contingency_fee must exactly equal (recovered_amount × artist_contingency_fee_percent / 100) for all resolved claims.",
                    investigation_path=[
                        "Review BillingEngine.calculate_contingency_fee() logic",
                        "Check for race conditions in fee updates",
                        "Verify no manual database modifications bypassed fee calculation",
                        "Audit affected claims for revenue reconciliation",
                    ],
                    metadata={
                        "affected_claims": len(drift_cases),
                        "total_drift_usd": total_drift,
                        "sample_size": len(results),
                        "drift_cases": drift_cases[:10],  # First 10 for issue body
                    },
                )
            ]

        return []

    def _check_founders_circle_capacity(self, state: PlatformState) -> list[Finding]:
        """Alert when Founders Circle approaching capacity."""
        FOUNDERS_CIRCLE_LIMIT = 2500

        # Count artists with founders_circle_member = True
        stmt = select(func.count(Artist.id)).where(Artist.founders_circle_member.is_(True))

        enrolled = state.db_session.execute(stmt).scalar()

        # Alert at 90% capacity (2250 seats)
        utilization = enrolled / FOUNDERS_CIRCLE_LIMIT
        if utilization >= 0.90:
            remaining = FOUNDERS_CIRCLE_LIMIT - enrolled
            severity = FindingSeverity.P0 if remaining < 100 else FindingSeverity.P1

            return [
                Finding(
                    detector=self.name,
                    severity=severity,
                    domain=self.domain,
                    title=f"founders circle approaching capacity ({enrolled}/{FOUNDERS_CIRCLE_LIMIT}, {remaining} seats remaining)",
                    description=f"Founders Circle enrollment at {utilization:.1%} capacity. Once cap reached, no new lifetime-rate-locked enrollments possible. This is a revenue and market positioning decision point.",
                    expected_behavior="Founders Circle cap should be monitored starting at 90% capacity. At 95%, founder should decide: increase cap, close program, or launch tiered pricing.",
                    investigation_path=[
                        "Calculate daily enrollment velocity over last 30 days",
                        "Project days until cap reached at current velocity",
                        "Prepare founder decision: increase cap to 5K, close program, or launch Artist Pro tier",
                        "If closing program: update marketing site, onboarding flow, and API validation",
                    ],
                    metadata={
                        "enrolled_count": enrolled,
                        "capacity": FOUNDERS_CIRCLE_LIMIT,
                        "remaining_seats": remaining,
                        "utilization_percent": utilization * 100,
                    },
                )
            ]

        return []
