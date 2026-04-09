# XR7 AI-Augmentation Roadmap — Engine v2

**Version:** 1.0  
**Date:** 2026-04-09  
**Scope:** Complete roadmap for AI integration across XR7's ingestion, normalization, matching, and recovery pipeline  
**Horizon:** XR7 v2.0 (2026 Q3) → v2.5 (2027 Q1) → v3.0 (2027 Q4)  
**Philosophy:** AI augments human decision-making; it does not replace it. Every AI decision is explainable, auditable, and reversible by a human analyst.

---

## Table of Contents

1. [AI-Augmentation Overview](#1-ai-augmentation-overview)
2. [AI-Assisted Metadata Normalization](#2-ai-assisted-metadata-normalization)
3. [AI-Based Matching Heuristics](#3-ai-based-matching-heuristics)
4. [AI-Based Reconciliation Scoring](#4-ai-based-reconciliation-scoring)
5. [AI-Based Anomaly Detection (Foreign Society Leakage)](#5-ai-based-anomaly-detection-foreign-society-leakage)
6. [AI-Based Cue-Sheet Reconstruction](#6-ai-based-cue-sheet-reconstruction)
7. [AI-Based Recovery Opportunity Ranking](#7-ai-based-recovery-opportunity-ranking)
8. [AI-Based Claim-Packaging Automation](#8-ai-based-claim-packaging-automation)
9. [AI-Based Customer Insights & Reporting](#9-ai-based-customer-insights--reporting)
10. [Phased Roadmap: v2.0 → v2.5 → v3.0](#10-phased-roadmap-v20--v25--v30)
11. [Responsible AI Use Guide](#11-responsible-ai-use-guide)
12. [Human-in-the-Loop Review Framework](#12-human-in-the-loop-review-framework)
13. [Model Evaluation & Drift Monitoring Plan](#13-model-evaluation--drift-monitoring-plan)

---

## 1. AI-Augmentation Overview

### 1.1 Why AI is Necessary at Scale

The royalty recovery pipeline generates decision points that are tractable by rule-based logic for simple cases but quickly exceed human capacity at scale:

| Decision point | Rule-based (current) | AI-augmented (target) |
|---------------|---------------------|----------------------|
| Title normalization | Regex + stopword removal | LLM semantic equivalence |
| Recording-to-work matching | ISRC exact + title fuzzy | Multi-signal ML (ISRC + title + artist + fingerprint + context) |
| Rate anomaly detection | ±3σ statistical threshold | ML anomaly model trained on real outcomes |
| Foreign society leakage | Manual analyst review | Pattern recognition across society-specific leakage signatures |
| Cue sheet reconstruction | Manual | NLP extraction from PDF + structured prediction |
| Recovery prioritization | FIFO or manual | ML ranking by settlement probability × expected value |
| Claim packaging | Template-based | LLM-assisted narrative + evidence selection |
| Customer insights | Fixed dashboard metrics | Natural-language query interface + proactive insights |

### 1.2 AI Decision Confidence Tiers

Every AI output carries a confidence score that determines the required human review level:

| Confidence | Label | Required action |
|-----------|-------|----------------|
| ≥ 0.95 | HIGH | Auto-approve; logged; analyst notified batch-daily |
| 0.80–0.94 | MEDIUM | Queue for analyst sign-off within 48 hours |
| 0.60–0.79 | LOW | Mandatory analyst review before any action |
| < 0.60 | UNCERTAIN | No action; flag for manual investigation |

---

## 2. AI-Assisted Metadata Normalization

### 2.1 Problem

DSPs, PROs, and foreign societies report the same work with hundreds of variations:
- `"Shape Of You"` / `"Shape of You"` / `"SHAPE OF YOU"` / `"Shape of You (Radio Edit)"`
- `"Ed Sheeran"` / `"Edward Sheeran"` / `"Sheeran, E."` / `"Ed Sheeran feat. Khalid"`

Rule-based normalization (lowercase, strip punctuation) handles simple cases but fails on: featured artist variations, transliterated names (JASRAC), regional title differences, and OCR errors in scanned PDFs.

### 2.2 Solution: Semantic Title Equivalence Model

**Architecture:**
```
Input: work_title (raw from DSP)
       known_canonical_title (from catalog)

Model: fine-tuned sentence-transformer (all-MiniLM-L6-v2)
       trained on 500K labeled title-pairs (equivalent / not-equivalent)

Output:
  - equivalence_score: float [0, 1]
  - suggested_canonical: str
  - confidence: float
  - reasoning: str   ← explainability output
```

**Training data:**
- Labeled pairs from XR7's match history (matched titles where ISRC confirmed identity)
- Music-specific augmentation: known remix/edit patterns, featuring formats, transliterations

**Deployment:**
- Inference via `xr7-ml` service; gRPC endpoint
- Sub-10ms response for cached titles; 50ms for new titles
- Model updated quarterly on new labeled data

### 2.3 Party Name Deduplication

LLM-assisted deduplication for artist/party names across registries:

```python
# Uses OpenAI GPT-4o or local Llama 3 (privacy-preserving for enterprise)
async def are_same_party(name_a: str, name_b: str, context: dict) -> PartyEquivalenceResult:
    """Determine if two party names refer to the same person/org."""
    prompt = f"""
    Music rights context: Given these two party names, determine if they refer to the same person or organization.
    
    Name A: {name_a}
    Context A: IPI={context.get('ipi_a')}, Territories={context.get('territories_a')}
    
    Name B: {name_b}
    Context B: IPI={context.get('ipi_b')}, Territories={context.get('territories_b')}
    
    Respond JSON: {{"same_party": bool, "confidence": float, "reasoning": str}}
    """
    # ... call LLM, parse response, return typed result
```

**Human-in-the-loop:** Party deduplication always requires analyst confirmation before merging party records, regardless of confidence.

---

## 3. AI-Based Matching Heuristics

### 3.1 Current Matching Limitation

The current tiered matcher (ISRC → title → fingerprint) fails on:
- **Ambiguous ISRC:** A recording was released with two different ISRCs (common for regional pressings)
- **Missing ISRC:** DSP statement row has no ISRC (especially for older catalog or user-uploaded content)
- **Splitting vs. cover:** Different recording of the same work (same title, different artist)
- **Medley/mashup:** A statement row covers parts of 3 works; needs fractional attribution

### 3.2 Multi-Signal ML Matcher

**Model type:** Gradient Boosted Decision Tree (XGBoost) for speed; Neural ranking model for hard cases

**Features:**
```python
MATCH_FEATURES = [
    "isrc_exact_match",           # binary
    "title_similarity_score",     # float [0,1] from sentence-transformer
    "artist_similarity_score",    # float [0,1]
    "duration_delta_seconds",     # float (absolute difference)
    "release_date_delta_days",    # float (absolute difference, null-safe)
    "label_match",                # binary (exact label match)
    "dsp_id_match",               # binary (DSP-specific ID match)
    "fingerprint_similarity",     # float [0,1] from Chromaprint
    "prior_match_count",          # int (how many times has this pair matched before)
    "territory_overlap",          # float (fraction of territories in common)
]

TARGET: match_confirmed (binary; from analyst review outcomes)
```

**Output:**
- `match_confidence`: float [0, 1]
- `match_method`: enum [EXACT_ISRC, ML_HIGH, ML_MEDIUM, FINGERPRINT, UNMATCHED]
- `alternative_matches`: list of top-3 alternatives with confidence

### 3.3 Active Learning Loop

Every analyst correction (accepting or rejecting a match) feeds back into the training data:

```python
async def record_analyst_correction(
    statement_row_id: str,
    ml_suggested_work_id: str,
    correct_work_id: str | None,  # None = genuine unmatched
    analyst_id: str
):
    """Add a training example from analyst feedback."""
    await training_db.insert(MatchTrainingExample(
        features=await extract_features(statement_row_id, ml_suggested_work_id),
        label=1 if ml_suggested_work_id == correct_work_id else 0,
        source="analyst_correction",
        analyst_id=analyst_id,
        weight=2.0   # analyst corrections are up-weighted vs. auto-labeled examples
    ))
    # Model is retrained weekly if ≥ 1000 new corrections have accumulated
```

---

## 4. AI-Based Reconciliation Scoring

### 4.1 Problem

After matching, the reconciliation step compares:
- What was reported (DSP statement)
- What was expected (based on contract rates, statutory rates, historical averages)

The "expected" calculation is complex: different rate tiers apply by territory, subscription type, content type, label deal structure, and time period. Manual rate validation requires a royalty accountant.

### 4.2 Solution: Reconciliation Score Model

**What the model does:** Given a matched recording + statement row, predict the expected royalty amount and flag anomalies.

```python
class ReconciliationScorer:
    """
    Predicts expected royalty for a statement row given:
    - DSP × territory × subscription_type × content_type
    - Historical rate baseline for this combination
    - Known contractual adjustments
    
    Returns:
    - expected_amount: Decimal
    - expected_range: (Decimal, Decimal)  # 90% confidence interval
    - deviation_score: float  # how far from expected
    - anomaly: bool
    - explanation: str  # human-readable reason for flagging
    """
```

**Model type:** Gradient boosting (LightGBM) for tabular royalty data.

**Training data:**
- 24 months of confirmed-accurate statement rows (analyst-verified as correct)
- Labels: was the payment amount within expected range? (binary)

**Continuously updated:** Monthly retraining on last 3 months of verified outcomes.

---

## 5. AI-Based Anomaly Detection (Foreign Society Leakage)

### 5.1 The Foreign Society Leakage Problem

Foreign society leakage is systematic under-reporting by foreign collecting societies (BUMA/STEMRA, JASRAC, SACEM) for works registered by XR7 tenants. The leakage is difficult to detect because:
- Each society uses different identifiers
- Historical baselines are thin (less data than DSPs)
- Society-specific deductions are opaque
- Currency fluctuations mask rate changes

### 5.2 Society-Specific Anomaly Models

A separate anomaly model per society, because each society's leakage patterns are different:

```python
SOCIETY_MODELS = {
    "BUMA_STEMRA": {
        "model_type": "isolation_forest",
        "features": ["stream_count_delta", "rate_per_licensed_copy", "territory_coverage"],
        "threshold": 0.12,   # anomaly score above this = flag
    },
    "JASRAC": {
        "model_type": "lstm_sequence",  # temporal pattern model for quarterly seasonality
        "features": ["quarter_payout_normalized", "work_category_mix", "digital_vs_broadcast_ratio"],
        "threshold": 0.15,
    },
    # ... per society
}
```

### 5.3 Cross-Society Leakage Detection

A meta-model that compares a tenant's aggregate receipts across all societies against:
- Peer tenants with similar catalog genre/size
- Expected distribution based on streaming geography

```python
async def detect_cross_society_leakage(tenant_id: str) -> LeakageAssessment:
    """
    Compare this tenant's society receipt distribution to peer tenants.
    Flag societies where this tenant receives materially less than peers.
    """
    ...
```

---

## 6. AI-Based Cue-Sheet Reconstruction

### 6.1 Problem

Cue sheets (documents listing music used in TV/film) are often:
- Not filed at all (sync revenue lost)
- Filed with incorrect work metadata (ISRC missing, title misspelled)
- Only available as scanned PDFs from production companies

Without accurate cue sheets, performance royalties from broadcast and streaming (Netflix/Amazon licensed content) are never collected.

### 6.2 NLP Extraction from PDF Cue Sheets

```python
class CueSheetExtractor:
    """
    Use LLM to extract structured cue sheet data from unstructured PDF text.
    
    Input: raw text extracted from cue sheet PDF (via pdfplumber)
    Output: structured CueSheet object
    """
    
    EXTRACTION_PROMPT = """
    Extract all music cues from this television/film cue sheet.
    For each cue, extract: sequence number, timecode, work title, artist, usage type, duration.
    If a field is not present, use null.
    Return as JSON array of cue objects.
    
    Cue sheet text:
    {text}
    """
    
    async def extract(self, pdf_bytes: bytes) -> CueSheet:
        text = self._pdf_to_text(pdf_bytes)
        response = await llm.complete(self.EXTRACTION_PROMPT.format(text=text))
        raw_cues = json.loads(response)
        validated = [self._validate_cue(c) for c in raw_cues]
        return CueSheet(cues=validated, extraction_confidence=self._score(validated))
```

### 6.3 Cue-to-Recording Matcher

After extraction, the AI matcher links each extracted cue title/artist to a Recording in XR7:

```
Extracted: {title: "Shape of You", artist: "Ed Sheeran", duration: 45s}
     │
     ▼
Title+artist embedding similarity → top-5 candidates from recording catalog
     │
     ▼
Duration filter: candidates within ±20% of cue duration
     │
     ▼
MusicBrainz cross-reference: confirm ISRC for highest-confidence match
     │
     ▼
Result: recording_id with confidence score
```

### 6.4 Automatic Cue Sheet Filing Suggestion

High-confidence reconstructed cue sheets (confidence > 0.85) are queued for analyst fast-track approval. The analyst reviews a pre-populated form and clicks "Approve" or makes corrections before the cue sheet is filed with the relevant PRO.

---

## 7. AI-Based Recovery Opportunity Ranking

### 7.1 Problem

A large publisher with 50,000 works may have hundreds of identified anomalies after reconciliation. Without prioritization, analysts pursue low-value claims first. An ML ranking model can identify the highest-value, most-likely-to-settle opportunities.

### 7.2 Recovery Opportunity Ranker

**Model type:** Learning-to-rank (LambdaMART) trained on historical claim outcomes.

**Features for each identified anomaly:**
```python
RANKER_FEATURES = [
    "anomaly_amount_usd",         # estimated recoverable amount
    "dsp_settlement_rate",        # historical % of claims settled by this DSP
    "dsp_response_time_days",     # how fast this DSP typically responds
    "claim_type",                 # underpayment vs. non-payment vs. metadata_error
    "evidence_completeness_score",# how complete is the evidence (0–1)
    "similar_claims_settled",     # how many similar claims have settled before (count)
    "territory",                  # some territories have better settlement rates
    "claim_age_days",             # older anomalies may have passed limitation periods
    "analyst_workload",           # balance across analysts
    "tenant_tier",                # enterprise claims may have faster DSP attention
]

TARGET: revenue_recovered_within_90_days (regression target)
```

**Output ranked list:**
```json
[
  {
    "anomaly_id": "anm_abc123",
    "estimated_recovery_usd": 12450.00,
    "settlement_probability": 0.87,
    "expected_value_usd": 10831.50,
    "rank": 1,
    "reasoning": "Spotify underpayment with complete ISRC evidence; DSP settles 91% of ISRC-backed claims"
  },
  ...
]
```

---

## 8. AI-Based Claim-Packaging Automation

### 8.1 Problem

Filing a recovery claim requires:
- A written dispute narrative explaining the discrepancy
- Supporting evidence (statement rows, expected rate calculations, ISRC documentation)
- Correct formatting for each DSP's submission requirements

Currently this takes an analyst 30–90 minutes per claim. With 500 claims per month at scale, this is the primary bottleneck.

### 8.2 Claim Narrative Generation

**LLM-generated narrative (analyst reviews and approves):**

```python
CLAIM_NARRATIVE_PROMPT = """
You are a music rights attorney drafting a royalty recovery claim.

Context:
- DSP: {dsp}
- Claimant: {artist_name} (represented by {publisher_name})
- ISRC: {isrc}
- Work title: {work_title}
- Period: {period_from} to {period_to}
- Reported plays: {reported_plays:,}
- Reported amount: ${reported_amount:,.2f}
- Expected amount (at {rate_basis}): ${expected_amount:,.2f}
- Discrepancy: ${discrepancy:,.2f} ({discrepancy_pct:.1f}%)

Write a formal but concise dispute claim of 2–3 paragraphs that:
1. States the discrepancy with specific figures
2. References the rate basis (statutory rate under MMA / contractual rate / historical average)
3. Requests payment of the outstanding amount plus any applicable interest
4. References the attached evidence bundle

Do not use speculative language. Cite only facts from the context above.
"""
```

**Evidence selection AI:**
For each claim, the AI recommends which supporting documents to include from the evidence library (past verified statement rows, rate documentation, ISRC registration, prior communications with the DSP). Analyst confirms the selection.

### 8.3 DSP-Specific Formatting

After analyst approval, the system auto-formats the claim for the DSP's required format:

```python
class ClaimFormatter:
    FORMATTERS = {
        "spotify": SpotifyClaimFormatter,        # JSON API submission
        "apple": AppleClaimFormatter,            # Structured JSON
        "amazon": AmazonPDFClaimFormatter,       # PDF with specific layout
        "default": GenericPDFClaimFormatter,
    }

    def format(self, claim: Claim, narrative: str, evidence: list) -> bytes:
        formatter = self.FORMATTERS.get(claim.payer, self.FORMATTERS["default"])
        return formatter().render(claim, narrative, evidence)
```

---

## 9. AI-Based Customer Insights & Reporting

### 9.1 Proactive Insight Engine

Instead of waiting for users to view dashboards, the insight engine proactively surfaces notable findings:

```
Weekly insight scan (per tenant):
  • "Your Spotify US match rate dropped from 94% to 81% this month — 
     possible format change. 3 other artists on the same label saw the same drop."
  • "You have $4,200 in unsubmitted anomalies > 60 days old — 
     these may expire under Spotify's 12-month claim window."
  • "PRO (ASCAP) payout for Q4 was 23% lower than Q3 with no catalog change — 
     recommend PRO reconciliation review."
```

**Architecture:**
```
Nightly batch job: compute insight candidates per tenant
     │
     LLM: rank by relevance + drafts human-readable explanation
     │
     Push to tenant dashboard (notification panel)
     + Weekly digest email (configurable)
```

### 9.2 Natural Language Query Interface

Pro and Enterprise tier users can query their data in plain English:

```
User: "How much did Spotify underpay me for 'Blinding Lights' in 2025?"

→ System parses intent → SQL query generated → result returned as natural language:

"In 2025, Spotify reported $18,440 for 'Blinding Lights'. 
 Based on your contracted rate of $0.00042/stream and 
 47.2M reported streams, the expected amount was $19,824. 
 The discrepancy is $1,384 (7.0%). 
 A claim was filed in October and is currently under review."
```

**Implementation:**
- uses LangChain Text-to-SQL or custom SQLCoder fine-tune on XR7's schema
- All generated SQL is sandboxed to the authenticated tenant_id
- All queries logged to audit_events with the generated SQL for review

---

## 10. Phased Roadmap: v2.0 → v2.5 → v3.0

### v2.0 (2026 Q3 — GA Launch)

**Theme:** Foundation ML — rule-augmented with ML confidence scoring

| Feature | Status | Model type |
|---------|--------|-----------|
| Multi-signal match confidence scoring | ✅ Shipping | XGBoost on ISRC/title/fingerprint features |
| Rate deviation anomaly detection | ✅ Shipping | Isolation Forest + statistical threshold |
| Title normalization (rule-based + similarity) | ✅ Shipping | Sentence-Transformer (all-MiniLM-L6-v2) |
| Recovery opportunity ranking (basic) | ✅ Shipping | Heuristic scoring (amount × DSP settlement rate) |
| Active learning data collection | ✅ Shipping | Logging analyst corrections for future training |

---

### v2.5 (2027 Q1)

**Theme:** Generative AI integration — LLM for narrative + structured prediction for cue sheets

| Feature | Status | Model type |
|---------|--------|-----------|
| AI claim narrative generation | 🔜 Planned | GPT-4o / Llama 3 (enterprise: local) |
| Cue sheet PDF extraction | 🔜 Planned | LLM extraction + structured validation |
| Cue-to-recording matcher | 🔜 Planned | Embedding similarity + duration filter |
| Foreign society anomaly models (v1) | 🔜 Planned | Per-society Isolation Forest |
| Party name deduplication (LLM-assisted) | 🔜 Planned | LLM binary classification |
| Proactive insight engine (v1) | 🔜 Planned | Rule-based triggers + LLM explanations |
| Natural language query (beta) | 🔜 Planned | SQLCoder fine-tuned on XR7 schema |

---

### v3.0 (2027 Q4)

**Theme:** Autonomous intelligence — high-confidence decisions execute without analyst review

| Feature | Status | Model type |
|---------|--------|-----------|
| Fully autonomous ingestion (no human review for HIGH confidence) | 🔮 Research | Ensemble of v2.5 models + policy engine |
| AI reconciliation scoring (replaces rule engine) | 🔮 Research | LightGBM reconciliation scorer |
| Foreign society leakage (cross-society meta-model) | 🔮 Research | Multi-task learning across societies |
| AI claim packaging (auto-approve HIGH confidence) | 🔮 Research | LLM + evidence ranker + format adapter |
| Tenant-isolated fine-tuned models | 🔮 Research | PEFT (LoRA) fine-tuning on tenant data |
| AI-generated quarterly recovery strategy reports | 🔮 Research | Multi-step LLM reasoning chain |
| Predictive settlement timeline | 🔮 Research | Survival analysis on claim lifecycle |

---

## 11. Responsible AI Use Guide

### 11.1 Core Principles

**1. Transparency:** Every AI decision exposed to a user or that drives financial action must include an explanation. "The AI said so" is never sufficient justification.

**2. Human Accountability:** A human analyst is always responsible for the outcome of a claim or financial transaction, even if the AI prepared it. The AI is a tool, not the decision-maker for high-stakes actions.

**3. Auditability:** Every AI inference that affects a financial outcome is logged to the audit trail with: model version, input features, output, confidence score, and any human override.

**4. Fairness:** AI models are audited for bias against smaller catalogs, non-English-language titles, and non-major-label artists. Bias audits are performed before every major model update.

**5. Data Minimization:** AI models are trained only on data that tenants have consented to use for training. Enterprise tenants can opt out of contributing their data to the shared model.

**6. Reversibility:** Any AI-automated action (auto-approved match, auto-filed claim) can be reversed by an analyst within 72 hours without any data loss.

### 11.2 What AI Is Not Allowed to Do Automatically

These actions require human approval regardless of AI confidence:

- **Filing a legal claim** with a DSP (legal consequence; human must approve)
- **Merging party records** (irreversible without careful data management)
- **Sending money** (any recovery advance or disbursement)
- **Deleting data** (including marking a work as "no royalties owed")
- **Contacting external parties** (DSPs, PROs, legal counsel) on behalf of a tenant

### 11.3 AI Disclosure to End Users

Users are informed when AI has contributed to a decision displayed in the UI:

```
"This match was scored by XR7's AI with 94% confidence. 
 Your analyst will review it within 48 hours."

"This claim narrative was drafted by AI. 
 Click 'Review' to read and approve before submission."
```

---

## 12. Human-in-the-Loop Review Framework

### 12.1 Review Queue Architecture

```
AI Inference Engine
     │
     ├── Confidence ≥ 0.95 → Auto-approve queue (logged; analyst sees batch summary)
     ├── Confidence 0.80–0.94 → Analyst review queue (48h SLA)
     ├── Confidence 0.60–0.79 → Analyst review queue (24h SLA; priority label)
     └── Confidence < 0.60 → Manual investigation queue (no AI suggestion shown)
```

### 12.2 Analyst Review Interface

For each item in the review queue, analysts see:

1. **AI recommendation:** Suggested match / anomaly flag / claim narrative
2. **Confidence score:** Displayed with color (green / yellow / red)
3. **Explanation:** "Matched via ISRC + title similarity (0.97) + duration within 2s"
4. **Top alternatives:** If the AI considers multiple options, show top 3 with scores
5. **Evidence panel:** Raw data used to make the decision (statement row, catalog entry)
6. **Override options:**
   - Accept AI recommendation
   - Accept with modification
   - Reject with reason (reason feeds training data)
   - Escalate (second analyst review)

### 12.3 Override Tracking

```sql
CREATE TABLE ai_human_overrides (
    override_id         UUID PRIMARY KEY,
    inference_id        UUID NOT NULL,          -- links to ai_inferences log
    model_name          VARCHAR(100),
    model_version       VARCHAR(20),
    ai_recommendation   JSONB,
    ai_confidence       NUMERIC(4,3),
    human_decision      VARCHAR(50),            -- 'accept', 'modify', 'reject', 'escalate'
    human_reasoning     TEXT,
    analyst_id          UUID,
    occurred_at         TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

**Override rate targets:**
- If reject rate > 20% for a model → investigate for systematic error
- If override rate > 30% → model needs retraining before next auto-approve threshold is applied

---

## 13. Model Evaluation & Drift Monitoring Plan

### 13.1 Model Registry

All production models are registered with version, training date, metrics, and approval sign-off:

```sql
CREATE TABLE ml_model_registry (
    model_id        UUID PRIMARY KEY,
    model_name      VARCHAR(100) NOT NULL,   -- 'match_confidence_v3', 'anomaly_detector_spotify_v2'
    version         VARCHAR(20) NOT NULL,
    artifact_path   VARCHAR(500),            -- S3 path to model artifact
    framework       VARCHAR(30),             -- 'xgboost', 'lightgbm', 'sentence-transformers'
    training_date   DATE,
    eval_metrics    JSONB,                   -- {"precision": 0.94, "recall": 0.91, "f1": 0.92}
    training_samples INTEGER,
    approved_by     UUID,                    -- analyst or ML lead who signed off
    deployed_at     TIMESTAMPTZ,
    retired_at      TIMESTAMPTZ,
    notes           TEXT
);
```

### 13.2 Evaluation Metrics by Model

| Model | Primary metric | Threshold to deploy | Threshold to retrain |
|-------|---------------|--------------------|--------------------|
| Match confidence | F1 (matched vs. unmatched) | F1 ≥ 0.90 | F1 drops below 0.85 |
| Anomaly detector | Precision @ Recall=0.80 | Precision ≥ 0.85 | Precision drops below 0.75 |
| Reconciliation scorer | RMSE (USD) | RMSE ≤ $50 per row | RMSE exceeds $100 |
| Recovery ranker | NDCG@10 | NDCG ≥ 0.75 | NDCG drops below 0.65 |
| Title normalizer | Accuracy on held-out pairs | Accuracy ≥ 0.95 | Accuracy drops below 0.88 |

### 13.3 Drift Detection

Models can degrade silently without re-training if the input data distribution changes (DSP format changes, new music genres, new territories). XR7 monitors for drift:

**Input drift (data drift):**
```python
# Nightly job per model
async def check_input_drift(model_name: str):
    current_features = await get_recent_feature_distribution(model_name, days=7)
    baseline_features = await get_baseline_distribution(model_name)
    
    for feature, dist in current_features.items():
        psi = calculate_population_stability_index(baseline_features[feature], dist)
        if psi > 0.2:   # PSI > 0.2 = significant drift
            await alert_ml_team(model_name, feature, psi)
            await flag_model_for_review(model_name)
```

**Output drift (prediction drift):**
```python
# Compare model output distribution week over week
async def check_prediction_drift(model_name: str):
    current_confidence_dist = await get_confidence_distribution(model_name, days=7)
    baseline_confidence_dist = await get_confidence_distribution(model_name, reference_days=30)
    ks_stat, p_value = ks_2samp(current_confidence_dist, baseline_confidence_dist)
    if p_value < 0.05:   # Statistically significant shift
        await alert_ml_team(model_name, "prediction_drift", ks_stat)
```

**Business metric drift:**
```python
# If match rate drops even if model confidence hasn't changed → something else is wrong
async def check_business_drift(dsp: str):
    current_match_rate = await compute_match_rate(dsp, days=7)
    historical_match_rate = await compute_match_rate(dsp, days=30)
    if current_match_rate < historical_match_rate * 0.9:  # >10% drop
        await trigger_investigation(dsp, "match_rate_drop", current_match_rate)
```

### 13.4 Retraining Triggers

A model is automatically queued for retraining when:

| Trigger | Threshold |
|---------|-----------|
| Drift alert | PSI > 0.2 on any primary feature |
| Override rate | Analyst reject rate > 20% over 7 days |
| Business metric drop | Match rate / anomaly detection rate drops >10% |
| New training data | ≥ 1,000 new labeled examples accumulated |
| Scheduled | Monthly (unconditional; for currency) |

### 13.5 Model Approval Process

1. **Offline evaluation:** New model trained → evaluated on held-out test set → metrics meet thresholds
2. **Shadow mode deployment:** New model runs in parallel with production model for 7 days; output compared but not used
3. **Canary deployment:** New model handles 10% of traffic for 3 days; business metrics monitored
4. **Full rollout:** If canary metrics match or exceed production → full rollout; old model retired
5. **Sign-off:** ML lead + product owner approve each model promotion to production
