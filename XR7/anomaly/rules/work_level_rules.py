"""Work-level royalty-shortfall detectors.

Unlike the artist-level rules in ``transparent_rules``, these look at *individual works*
across payers and over time, so a finding names the specific song to chase.

Pure functions over event dicts (``work_title``, ``platform``, ``territory``, ``timestamp``,
``quantity``, ``unit_value`` and optionally ``share_pct``). No ORM, no network.

Design rules (credibility budget):
* Every finding is a lead. ``estimated_recoverable`` is 0.0 so these never double-count the
  artist-level ``PROBABLE_UNCLAIMED_MECHANICALS`` dollars they itemize; the dollars at stake
  live in ``evidence``.
* Every detector needs a *control*: proof the payer's data for this artist is present and
  healthy (e.g. MLC paid other works that period), otherwise a gap may just be a statement
  that was never uploaded.
* Payer lag gates keep recent periods out; PROs pay late.
"""

from __future__ import annotations

import re
from collections import defaultdict
from datetime import date, datetime, timedelta, timezone
from difflib import SequenceMatcher
import os


def work_level_rules_enabled() -> bool:
    """Off by default: false-positive rate on real statements is not yet measured.
    Set XR7_WORK_LEVEL_RULES=1 to include these findings in detection runs."""
    return os.environ.get("XR7_WORK_LEVEL_RULES", "").strip().lower() in {"1", "true", "yes"}

PRO_FAMILIES = {"BMI", "ASCAP", "SESAC", "GMR"}
MECHANICAL_FAMILY = "MLC"
SOUND_RECORDING_FAMILY = "SOUNDEXCHANGE"
_KNOWN_FAMILIES = PRO_FAMILIES | {MECHANICAL_FAMILY, SOUND_RECORDING_FAMILY}

# Days after a period ends before income is normally paid. Conservative on purpose.
LAG_DAYS = {"PRO": 270, "MLC": 120, SOUND_RECORDING_FAMILY: 150}

MIN_WORK_AMOUNT = 25.0  # coverage findings below this aren't worth a claim
MIN_DROPOUT_QUARTERLY_MEAN = 10.0
MECH_TO_PERF_RATIO = 1.5  # same floor used by PROBABLE_UNCLAIMED_MECHANICALS
TITLE_MATCH = 0.88  # >= treated as the same work across payers
SHARE_TOLERANCE_PTS = 0.5
MAX_FINDINGS_PER_RULE = 25

# Mirrors the MLC-eligible DSP keywords in transparent_rules (interactive streaming only).
_INTERACTIVE_KEYWORDS = (
    "spotify", "apple", "amazon", "pandora premium", "pandora plus", "tidal", "deezer",
    "youtube", "soundcloud", "napster", "internet", "digital media",
)


# ── helpers ──────────────────────────────────────────────────────────────────


def payer_family(platform: str | None) -> str | None:
    head = re.split(r"\s*/\s*", str(platform or "").upper().strip())[0]
    for fam in _KNOWN_FAMILIES:
        if head.startswith(fam):
            return fam
    return None


def normalize_work_title(title: str | None) -> str:
    t = str(title or "").upper()
    t = re.sub(r"\([^)]*\)|\[[^\]]*\]", " ", t)  # (feat. X), [Remix]
    t = re.sub(r"\s-\s.*$", " ", t)  # " - Remastered 2011"
    t = re.sub(r"[^A-Z0-9 ]", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def _dt(value) -> datetime | None:
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
    if isinstance(value, date):
        return datetime(value.year, value.month, value.day, tzinfo=timezone.utc)
    if isinstance(value, str):
        try:
            p = datetime.fromisoformat(value)
        except ValueError:
            return None
        return p if p.tzinfo else p.replace(tzinfo=timezone.utc)
    return None


def _q_index(d: datetime) -> int:
    return d.year * 4 + (d.month - 1) // 3


def _q_label(q: int) -> str:
    return f"{q // 4}-Q{q % 4 + 1}"


def _q_end(q: int) -> datetime:
    y, qq = divmod(q, 4)
    m = qq * 3 + 3
    nxt = datetime(y + (m == 12), 1 if m == 12 else m + 1, 1, tzinfo=timezone.utc)
    return nxt - timedelta(days=1)


def _lag(family: str) -> int:
    return LAG_DAYS["PRO"] if family in PRO_FAMILIES else LAG_DAYS[family]


def _amount(e: dict) -> float:
    return float(e.get("quantity") or 0.0) * float(e.get("unit_value") or 0.0)


def _similar(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b).ratio() if a and b else 0.0


def _best_match(key: str, candidates) -> tuple[str | None, float]:
    best, score = None, 0.0
    for c in candidates:
        s = 1.0 if c == key else _similar(key, c)
        if s > score:
            best, score = c, s
    return best, score


def _is_interactive_us(e: dict) -> bool:
    terr = str(e.get("territory") or "").upper()
    if terr not in ("", "US", "USA"):
        return False
    plat = str(e.get("platform") or "").lower()
    return any(k in plat for k in _INTERACTIVE_KEYWORDS)


def _finding(artist_id, subtype, severity, confidence, key, description, amount, evidence) -> dict:
    return {
        "artist_id": artist_id,
        "category": "ROYALTY",
        "subtype": subtype,
        "severity": severity,
        "expected_amount": 0.0,
        "actual_amount": round(amount, 2),
        "estimated_recoverable": 0.0,
        "confidence_score": confidence,
        "status": "OPEN",
        "description": description,
        "rule_id": subtype,
        "rule_name": subtype.replace("_", " ").title(),
        "identity_key": f"{subtype}:{key}",
        "evidence": {
            **evidence,
            "note": (
                "Lead from statement data, not proof of underpayment. Confirm against the "
                "payer's work registration before filing a claim."
            ),
        },
    }


def _top(findings: list[dict]) -> list[dict]:
    findings.sort(key=lambda f: f["evidence"].get("amount_basis", 0.0), reverse=True)
    return findings[:MAX_FINDINGS_PER_RULE]


# ── 1. coverage matrix ───────────────────────────────────────────────────────


def detect_coverage_gaps(artist_id: str, events: list[dict], now: datetime) -> list[dict]:
    """A work paid by the PRO but absent from the MLC (and vice versa).

    Control: the other side must have paid this artist *something*, proving those
    statements were uploaded and the artist is registered there.
    """
    pro_cut = now - timedelta(days=LAG_DAYS["MLC"])  # PRO usage old enough that MLC should have paid
    mlc_cut = now - timedelta(days=LAG_DAYS["PRO"])  # MLC usage old enough that PRO should have paid

    pro_work: dict[str, float] = defaultdict(float)  # eligible interactive US PRO income, aged
    pro_all: dict[str, float] = defaultdict(float)  # any PRO income (for the reverse check)
    mlc_work: dict[str, float] = defaultdict(float)
    mlc_aged: dict[str, float] = defaultdict(float)
    titles: dict[str, str] = {}
    sources: dict[str, set] = defaultdict(set)

    for e in events:
        fam, ts, amt = payer_family(e.get("platform")), _dt(e.get("timestamp")), _amount(e)
        key = normalize_work_title(e.get("work_title"))
        if not fam or ts is None or amt <= 0 or not key or key == "UNKNOWN":
            continue
        titles.setdefault(key, str(e.get("work_title")))
        if fam in PRO_FAMILIES:
            pro_all[key] += amt
            if _is_interactive_us(e) and ts <= pro_cut:
                pro_work[key] += amt
                sources[key].add(str(e.get("platform")))
        elif fam == MECHANICAL_FAMILY:
            mlc_work[key] += amt
            if ts <= mlc_cut:
                mlc_aged[key] += amt

    findings: list[dict] = []

    if mlc_work:  # control for PRO -> MLC
        for key, perf in pro_work.items():
            if perf < MIN_WORK_AMOUNT:
                continue
            match, score = _best_match(key, mlc_work)
            if score >= TITLE_MATCH:
                continue
            est = perf * MECH_TO_PERF_RATIO
            findings.append(
                _finding(
                    artist_id, "WORK_MISSING_MECHANICAL",
                    "HIGH" if est >= 100 else "MEDIUM", 0.55 if score >= 0.6 else 0.65, key,
                    (
                        f"'{titles[key]}' earned ${perf:,.2f} in interactive-streaming performance "
                        "income but has no mechanical income at The MLC, although the MLC paid "
                        "other works in this catalog. Either the work is unmatched/unregistered at "
                        "the MLC or it is listed under a different title."
                    ),
                    perf,
                    {
                        "work_title": titles[key],
                        "pro_interactive_income": round(perf, 2),
                        "estimated_mechanical_floor": round(est, 2),
                        "mech_to_perf_ratio": MECH_TO_PERF_RATIO,
                        "closest_mlc_title": match if score >= 0.6 else None,
                        "closest_mlc_title_similarity": round(score, 2) if match else None,
                        "payer_sources": sorted(sources[key]),
                        "amount_basis": est,
                        "itemizes": "PROBABLE_UNCLAIMED_MECHANICALS",
                    },
                )
            )

    if pro_all:  # control for MLC -> PRO
        for key, mech in mlc_aged.items():
            if mech < MIN_WORK_AMOUNT:
                continue
            match, score = _best_match(key, pro_all)
            if score >= TITLE_MATCH:
                continue
            est = mech / MECH_TO_PERF_RATIO
            findings.append(
                _finding(
                    artist_id, "WORK_MISSING_PERFORMANCE",
                    "HIGH" if est >= 100 else "MEDIUM", 0.5, key,
                    (
                        f"'{titles[key]}' earned ${mech:,.2f} in mechanical income at the MLC but "
                        "has no performance income from any PRO, although PROs paid other works "
                        "in this catalog. The work may be unregistered with the writer's PRO."
                    ),
                    mech,
                    {
                        "work_title": titles[key],
                        "mlc_income": round(mech, 2),
                        "estimated_performance_floor": round(est, 2),
                        "closest_pro_title": match if score >= 0.6 else None,
                        "closest_pro_title_similarity": round(score, 2) if match else None,
                        "amount_basis": est,
                    },
                )
            )
    return _top(findings)


# ── 2. dropout ───────────────────────────────────────────────────────────────


def detect_work_dropouts(artist_id: str, events: list[dict], now: datetime) -> list[dict]:
    """A work that paid steadily, then stopped while its payer kept paying the artist."""
    fam_q: dict[str, dict[int, float]] = defaultdict(lambda: defaultdict(float))
    work_q: dict[tuple[str, str], dict[int, float]] = defaultdict(lambda: defaultdict(float))
    titles: dict[str, str] = {}

    for e in events:
        fam, ts, amt = payer_family(e.get("platform")), _dt(e.get("timestamp")), _amount(e)
        key = normalize_work_title(e.get("work_title"))
        if not fam or ts is None or amt <= 0 or not key or key == "UNKNOWN":
            continue
        q = _q_index(ts)
        fam_q[fam][q] += amt
        work_q[(fam, key)][q] += amt
        titles.setdefault(key, str(e.get("work_title")))

    findings: list[dict] = []
    for (fam, key), series in work_q.items():
        quarters = fam_q[fam]
        eligible = max(
            (q for q in quarters if _q_end(q) <= now - timedelta(days=_lag(fam))), default=None
        )
        if eligible is None:
            continue
        horizon = min(eligible, max(quarters))
        last = max(series)
        gap = list(range(last + 1, horizon + 1))
        if len(gap) < 2:
            continue

        history = [q for q in sorted(series) if last - 5 <= q <= last]
        if len(history) < 3:
            continue
        mean = sum(series[q] for q in history) / len(history)
        if mean < MIN_DROPOUT_QUARTERLY_MEAN:
            continue

        # Control: the payer kept paying this artist through the gap at a healthy level.
        trailing = [quarters[q] for q in range(last - 3, last + 1) if q in quarters]
        if not trailing:
            continue
        fam_mean = sum(trailing) / len(trailing)
        if any(quarters.get(q, 0.0) < 0.5 * fam_mean for q in gap):
            continue

        # Not a rename: a near-identical title must not be earning in the gap.
        renamed = any(
            k2 != key and f2 == fam and _similar(key, k2) >= TITLE_MATCH and any(q in s2 for q in gap)
            for (f2, k2), s2 in work_q.items()
        )
        if renamed:
            continue

        missed = mean * len(gap)
        findings.append(
            _finding(
                artist_id, "WORK_INCOME_DROPOUT", "MEDIUM", 0.5, f"{fam}:{key}",
                (
                    f"'{titles[key]}' paid about ${mean:,.2f} per quarter through "
                    f"{_q_label(last)} via {fam}, then nothing for {len(gap)} quarters "
                    f"({_q_label(gap[0])} to {_q_label(gap[-1])}) while {fam} kept paying other works. "
                    "Common causes: lapsed or merged registration, a share or publisher change, "
                    "or a title/ID mismatch."
                ),
                missed,
                {
                    "work_title": titles[key],
                    "payer": fam,
                    "last_paid_quarter": _q_label(last),
                    "quarters_without_income": [_q_label(q) for q in gap],
                    "prior_quarterly_mean": round(mean, 2),
                    "income_if_unchanged": round(missed, 2),
                    "payer_total_in_gap": round(sum(quarters.get(q, 0.0) for q in gap), 2),
                    "amount_basis": missed,
                },
            )
        )
    return _top(findings)


# ── 3. share drift ───────────────────────────────────────────────────────────


def detect_share_drift(artist_id: str, events: list[dict], now: datetime) -> list[dict]:
    """The writer share a payer reports for the same work drops between periods.

    Needs ``share_pct`` on events (captured today for SESAC and MLC; ASCAP/BMI parsers do not
    persist it yet, so those payers are silently skipped).
    """
    series: dict[tuple[str, str], dict[int, dict[float, float]]] = defaultdict(
        lambda: defaultdict(lambda: defaultdict(float))
    )
    titles: dict[str, str] = {}
    for e in events:
        fam, ts, amt = payer_family(e.get("platform")), _dt(e.get("timestamp")), _amount(e)
        share = e.get("share_pct")
        key = normalize_work_title(e.get("work_title"))
        if not fam or ts is None or share is None or not key:
            continue
        share = round(float(share), 2)
        if not 0 < share <= 100:
            continue
        series[(fam, key)][_q_index(ts)][share] += max(amt, 0.0) or 0.0001
        titles.setdefault(key, str(e.get("work_title")))

    amounts: dict[tuple[str, str], dict[int, float]] = defaultdict(lambda: defaultdict(float))
    for e in events:
        fam, ts, key = payer_family(e.get("platform")), _dt(e.get("timestamp")), normalize_work_title(e.get("work_title"))
        if fam and ts and key and e.get("share_pct") is not None:
            amounts[(fam, key)][_q_index(ts)] += max(_amount(e), 0.0)

    findings: list[dict] = []
    for (fam, key), by_q in series.items():
        modal = {q: max(shares.items(), key=lambda kv: kv[1])[0] for q, shares in by_q.items()}
        qs = sorted(modal)
        drop = None
        for prev, cur in zip(qs, qs[1:]):
            if modal[cur] < modal[prev] - SHARE_TOLERANCE_PTS:
                drop = (prev, cur)
        if drop is None:
            continue
        prev, cur = drop
        before, after = modal[prev], modal[cur]
        if any(modal[q] >= before - SHARE_TOLERANCE_PTS for q in qs if q > cur):
            continue  # share was restored
        affected = [q for q in qs if q >= cur and modal[q] <= after + SHARE_TOLERANCE_PTS]
        paid_at_lower = sum(amounts[(fam, key)].get(q, 0.0) for q in affected)
        impact = paid_at_lower * (before / after - 1.0)
        findings.append(
            _finding(
                artist_id, "WORK_SHARE_DRIFT", "HIGH" if impact >= 100 else "MEDIUM", 0.7,
                f"{fam}:{key}",
                (
                    f"{fam} reported a {before:g}% writer share for '{titles[key]}' through "
                    f"{_q_label(prev)}, then {after:g}% from {_q_label(cur)}. If the registered "
                    "split did not change, income is being paid at the wrong share."
                ),
                paid_at_lower,
                {
                    "work_title": titles[key],
                    "payer": fam,
                    "share_before_pct": before,
                    "share_after_pct": after,
                    "drop_quarter": _q_label(cur),
                    "income_at_lower_share": round(paid_at_lower, 2),
                    "income_if_prior_share_correct": round(impact, 2),
                    "amount_basis": impact,
                },
            )
        )
    return _top(findings)


# ── entry point ──────────────────────────────────────────────────────────────


def run_work_level_rules(
    artist_id: str, events: list[dict], now: datetime | None = None
) -> list[dict]:
    now = now or datetime.now(timezone.utc)
    return (
        detect_coverage_gaps(artist_id, events, now)
        + detect_work_dropouts(artist_id, events, now)
        + detect_share_drift(artist_id, events, now)
    )
