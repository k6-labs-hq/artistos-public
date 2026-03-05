# Evidence Security Runbook

This runbook defines the operational process for signing, verifying, rotating, and incident-handling claim evidence packets.

## Scope

Applies to:
- `POST /claims/{claim_id}/evidence`
- `GET /claims/{claim_id}/evidence/export?format=zip|pdf`
- `GET /claims/{claim_id}/evidence/verify`

Covers:
- packet integrity (`packet_hash`, `chain_hash`, line hashes)
- signature validation (HMAC or RSA)
- revision-chain verification (`prior_packet_hash`)
- production key management and incident response

## Roles

- Platform engineer: key rotation, env/secrets management, operational checks
- Recovery analyst: packet generation/export and attorney handoff
- Legal ops: independent verification using the public key
- Security lead: incident commander for suspected tamper/key compromise

## Required Production Configuration

Use RSA mode in production.

```bash
XR7_EVIDENCE_SIGNING_MODE=rsa
XR7_EVIDENCE_PRIVATE_KEY_PEM=<private-key-pem>
XR7_EVIDENCE_PUBLIC_KEY_PEM=<public-key-pem>
```

Fallback mode (non-production only):

```bash
XR7_EVIDENCE_SIGNING_MODE=hmac
XR7_EVIDENCE_HMAC_SECRET=<long-random-secret>
```

## Standard Operating Procedure

### 1. Generate Packet

```bash
curl -X POST "http://localhost:8000/claims/{claim_id}/evidence"
```

Expected outcomes:
- `metadata.packet_version` present
- `metadata.revision` increments
- `integrity` block present with hash, chain hash, signature, and algorithm

### 2. Verify Packet

```bash
curl "http://localhost:8000/claims/{claim_id}/evidence/verify"
```

Operator helper (recommended):

```bash
scripts/verify_evidence.sh --claim-id {claim_id}
```

For revision checks:

```bash
scripts/verify_evidence.sh --claim-id {claim_id} --expected-prior-hash {prior_hash}
```

Pass criteria:
- `valid=true`
- all checks are true:
  - `packet_hash_matches`
  - `chain_hash_matches`
  - `line_hashes_match`
  - `signature_valid`

If reviewing a revised packet, enforce prior-chain validation:

```bash
curl "http://localhost:8000/claims/{claim_id}/evidence/verify?expected_prior_packet_hash={prior_hash}"
```

Additional pass criterion:
- `prior_link_matches=true`

### 3. Export Attorney Packet

```bash
curl -L "http://localhost:8000/claims/{claim_id}/evidence/export?format=zip&refresh=true" -o evidence_{claim_id}.zip
```

Operator helper (recommended, verification-gated):

```bash
scripts/export_evidence.sh --claim-id {claim_id} --format zip --refresh
```

Validate ZIP contents:
- `evidence_packet.json`
- `evidence_summary.txt`
- `proof_rows.csv`
- `source_citations.csv`
- `evidence_packet.pdf`
- `integrity_manifest.json`
- `attachments/*` (if source files found)
- `missing_sources.txt` (if any cited files were not resolvable)

### 4. Handoff Gate

Do not hand off to attorneys unless all checks pass.

Minimum gate:
- verification response archived
- exported ZIP archived in immutable storage
- packet hash recorded in case notes

## Key Rotation Procedure (90-Day Cadence)

### Preparation

1. Generate new RSA keypair in secure environment.
2. Store new private key in secrets manager.
3. Stage new public key for verifiers.
4. Announce cutover window to legal/recovery teams.

### Cutover

1. Update runtime secrets with new keypair.
2. Restart service instances.
3. Generate a test packet and verify success.
4. Confirm `signature_algorithm=RSA-SHA256` on new packets.

### Post-Cutover

1. Keep old public key(s) available for historical packet verification.
2. Record rotation event:
   - rotation timestamp
   - key id/version tag
   - operator
   - validation result

## Incident Response: Suspected Tamper or Key Exposure

Trigger conditions:
- `valid=false` on verification
- any integrity check false
- suspicious evidence content drift
- leaked or suspected leaked private key/secret

### Immediate Actions (first 15 minutes)

1. Stop external packet distribution.
2. Capture affected claim IDs and packet hashes.
3. Preserve logs and exported artifacts.
4. Notify security lead and legal ops.

### Containment

1. Rotate keys immediately.
2. Revoke compromised credentials.
3. Re-issue packets for affected claims.
4. Re-verify all re-issued packets and archive verification outputs.

### Recovery

1. Compare old/new packet hashes and revisions.
2. Document root cause and blast radius.
3. Update controls (alerts, access restrictions, review gates).

## Audit Logging Requirements

For each attorney handoff, persist:
- claim id
- packet hash
- prior packet hash
- revision
- packet version
- signature algorithm
- verification timestamp
- verification result
- operator identity

## Legal Verification Notes

External counsel can verify independently when provided:
- exported packet (`evidence_packet.json` and `integrity_manifest.json`)
- current and historical public key(s)
- expected prior hash (for revisioned packet comparisons)

## Operational Checklist (Quick)

1. Generate packet.
2. Run `scripts/verify_evidence.sh --claim-id {claim_id}`.
3. Verify prior link when applicable (`--expected-prior-hash`).
4. Run `scripts/export_evidence.sh --claim-id {claim_id} --format zip --refresh`.
5. Confirm required files are present.
6. Archive ZIP and verification result immutably.
7. Handoff to legal.
