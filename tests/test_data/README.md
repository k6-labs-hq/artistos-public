# Test Data — Nova Zephyr

Fictional artist **Nova Zephyr** with three tracks used across all files:

| Track | ISRC | ISWC |
|---|---|---|
| Electric Pulse | USXR72024001 | T-923847561-0 |
| Autumn Waves | USXR72024002 | T-847293016-0 |
| Midnight Run | USXR72023003 | T-736182940-0 |

Coverage period: **January–December 2025** (full year).
All monetary amounts are in **USD** unless noted.

---

## Distributor Statements

| File | Format | Notes |
|---|---|---|
| `distrokid_sample.csv` | DistroKid | 12 months, 3 tracks, 8+ DSPs, multi-territory. Includes June RU/IN geo spike for fraud detection |
| `tunecore_sample.csv` | TuneCore | 12 months, adds Deezer, Tidal, Pandora, iTunes download sales |
| `cdbaby_sample.csv` | CD Baby | 12 months, includes Bandcamp physical/digital line items |
| `amuse_sample.csv` | Amuse | 12 months, clean baseline for cross-distributor comparison |
| `unitedmasters_sample.csv` | United Masters | 12 months, Country/Region uses full country names |
| `onerpm_sample.csv` | ONErpm | 12 months, includes Napster (low-volume DSP) |
| `stem_sample.csv` | Stem | 12 months, Country Code abbreviated |
| `landr_sample.csv` | LANDR | 12 months, Territory column, includes Deezer |
| `ditto_sample.csv` | Ditto Music | 12 months, clean baseline |
| `reverbnation_sample.csv` | ReverbNation | 12 months, Song column (not Title) |
| `bandcamp_sample.csv` | Bandcamp | 90 line items, individual fan transactions, physical + digital, Buyer Name anonymised |

---

## PRO / Mechanical Statements

| File | Format | Notes |
|---|---|---|
| `ascap_sample.csv` | ASCAP | 12 months, includes Digital, Broadcast, Live Performance, Background Music sources |
| `bmi_sample.csv` | BMI | 12 months, Payer-level breakdown (Spotify, Amazon, Pandora, YouTube) |
| `mlc_sample.csv` | The MLC | 12 months, Interactive Streaming mechanicals at $0.000912/stream, licensee-level |

---

## DSP Direct Reports

| File | Format | Notes |
|---|---|---|
| `spotify_sample.csv` | Spotify for Artists | 12 months, per-country, includes June RU/IN anomaly rows matching distributor spike |
| `soundcloud_sample.csv` | SoundCloud | 12 months, SoundCloud Track ID column, per-country |

---

## Creator-Economy Platforms

| File | Format | Notes |
|---|---|---|
| `youtube_studio_sample.csv` | YouTube Studio | 12 months, Music Video + Lyric Video per country, RPM column |
| `tiktok_creator_fund_sample.csv` | TikTok Creator Fund | 12 months, aggregate payout per period |
| `instagram_reels_sample.csv` | Instagram Reels Bonus | 12 months, Plays + Bonus Amount |
| `twitch_sample.csv` | Twitch | 12 months, subscription / bits / ad_revenue breakdown |
| `patreon_sample.csv` | Patreon | 12 months, Patron Count growth, monthly payout |
| `shopify_sample.csv` | Shopify Merch | 12 months, 4 product SKUs, includes holiday Q4 surge |

---

## Generic / Other Distributors

| File | Format | Notes |
|---|---|---|
| `generic_kobalt_awal_sample.csv` | Generic CSV | Kobalt Music and AWAL rows in a single generic-format file; tests fallback parser |

---

## Anomaly / Edge-Case Scenarios

Use these files to exercise the fraud detection, gap analysis, and rate-audit modules.

| File | Scenario | What to Look For |
|---|---|---|
| `anomaly_bot_geo_spike.csv` | **Bot-like geographic spike** | June 2025: RU streams jump to 984,000 (vs ≤18,400 every other month). UA/BY rows appear only in June. Revenue-per-stream drops to ~$0.00028 — far below the $0.004 baseline. Flag with `FraudInflationDetector`. |
| `anomaly_missing_pro_quarter.csv` | **Missing PRO payment period** | ASCAP statement with Q3 2025 entirely absent (Jul, Aug rows missing). Cross-reference against distributor files to quantify unclaimed performance royalties. |
| `anomaly_per_stream_rate_drop.csv` | **Silent per-stream rate cut** | Stream quantities track identically to `distrokid_sample.csv` but Earnings are ~35% lower across all months and territories — consistent with an undisclosed rate renegotiation by the distributor. Run rate benchmarking to surface the gap. |
| `anomaly_missing_q2_payment.csv` | **Missing Q2 royalty statement** | ONErpm statement with May and June rows entirely absent despite continuity on all other months. Use gap detection to identify the missing periods and estimate the owed amount. |

---

## International Collection Societies

### Performing Rights Organizations (International)

| File | Society | Territory | Currency | Notes |
|---|---|---|---|---|
| `apra_amcos_sample.csv` | APRA AMCOS | AU / NZ | AUD / NZD | Digital + broadcast, 39 rows Jan–Dec 2025 |
| `jasrac_sample.csv` | JASRAC | JP | JPY | Digital (Spotify, Apple Music) + NHK broadcast |
| `komca_sample.csv` | KOMCA | KR | KRW | Digital (Melon, Genie) + KBS/MBC/SBS broadcast |
| `sacem_sample.csv` | SACEM | FR | EUR | Digital + radio broadcast + background music tariff |
| `prs_sample.csv` | PRS for Music | GB | GBP | Digital + BBC broadcast + live performance licensing |
| `socan_sample.csv` | SOCAN | CA | CAD | Digital + CBC broadcast |
| `gema_sample.csv` | GEMA | DE | EUR | Digital + ARD/ZDF broadcast + hotel/restaurant tariff |

### Neighboring Rights (Sound Recording)

| File | Society | Territory | Currency | Notes |
|---|---|---|---|---|
| `soundexchange_sample.csv` | SoundExchange | US | USD | Quarterly; Pandora, SiriusXM, iHeart non-interactive; performer + label split |
| `ppl_sample.csv` | PPL | GB | GBP | Quarterly; BBC Radio 1, ITV, Sky broadcast; performer + label split |

### US PRO Supplement (SESAC + GMR)

| File | Society | Territory | Currency | Notes |
|---|---|---|---|---|
| `sesac_sample.csv` | SESAC | US | USD | Quarterly; Spotify, Apple Music, NBC Universal, CBS |
| `gmr_sample.csv` | GMR | US | USD | Quarterly; Spotify, Apple Music, ABC, FOX, YouTube Music |

---

## Sync / Licensing

| File | Format | Notes |
|---|---|---|
| `sync_placements_sample.csv` | Sync Licensing | 20 TV/film/streaming placements Jan–Dec 2025; master+sync fees, backend royalty rates, contract references |

---

## Live Performance / Touring

| File | Format | Notes |
|---|---|---|
| `ticketmaster_settlement_sample.csv` | Tour Settlement | 16 shows Feb–Dec 2025; venue capacity, tickets sold, gross revenue, promoter deductions, artist guarantee, net settlement, merch |

---

## Publishing / Splits / Advances

| File | Format | Notes |
|---|---|---|
| `publishing_splits_sample.csv` | Co-Write Registry | Writer + publisher shares for all 3 tracks; Electric Pulse is a 3-way split (50/35/15%) |
| `distributor_advance_sample.csv` | Advance Recoupment | Two advances (DistroKid $5,000 recouped Jun 2025; TuneCore $8,000 still recouping), monthly recoupment ledger |

---

## YouTube Content ID / UGC

| File | Format | Notes |
|---|---|---|
| `youtube_content_id_sample.csv` | Content ID Claims | 22 UGC claims Jan–Dec 2025; active/disputed/taken_down statuses; monthly revenue per claim; peak $2,410 from holiday playlist |

---

## Extended Anomaly / Edge-Case Scenarios

| File | Scenario | Anomaly Rules Exercised |
|---|---|---|
| `anomaly_bot_geo_spike.csv` | **Bot-like geographic spike** | `FraudInflationDetector`, `LOW_STREAM_RATE` |
| `anomaly_missing_pro_quarter.csv` | **Missing PRO payment period** | `check_missing_periods`, gap detection |
| `anomaly_per_stream_rate_drop.csv` | **Silent per-stream rate cut** | `check_incorrect_rates` (>5% threshold) |
| `anomaly_missing_q2_payment.csv` | **Missing Q2 royalty statement** | `MISSING_PLATFORM_PAYMENT`, gap detection |
| `anomaly_unlicensed_sync.csv` | **Unlicensed sync + brand impression** | `SYNC_USAGE` (CRITICAL), `UNLICENSED_USAGE`, `BRAND_IMPRESSION`, `BRAND_PAYMENT_MISSING` |
| `anomaly_touring_settlement_gap.csv` | **Touring settlement shortfall** | `MISSING_GUARANTEE` (HIGH), `SETTLEMENT_DISCREPANCY` (>95% threshold, MEDIUM) |
| `anomaly_currency_conversion_error.csv` | **EUR paid at 1:1 USD rate** | `check_incorrect_rates`, FX conversion audit |
| `anomaly_withholding_tax.csv` | **German Quellensteuer not disclosed** | `check_incorrect_rates`, undisclosed 25% withholding |
| `anomaly_cowrite_undercrediting.csv` | **Co-writer shares missing** | `co_write_under_crediting`, writer split mismatch vs `publishing_splits_sample.csv` |
| `anomaly_isrc_mismatch.csv` | **Track split across two ISRCs** | `check_unmatched_works`, `LOW_STREAM_RATE` (both ISRCs appear below threshold) |
| `anomaly_duplicate_statement.csv` | **Same streams reported by two distributors** | `duplicate_payment_detection`, double-counting across DistroKid + TuneCore |
| `anomaly_black_box_unclaimed.csv` | **Unclaimed royalties held by foreign societies** | `check_unmatched_works`, `black_box_detection`; JASRAC/SACEM/SOCAN/KOMCA holding 2024 royalties due to missing registrations |

---

## Cross-Source Analysis Scenarios

The files are designed to be uploaded together so the system can perform deep-dive reconciliation:

1. **Distributor vs PRO reconciliation** — Upload any distributor file (e.g. `distrokid_sample.csv`) alongside `ascap_sample.csv` and `bmi_sample.csv`. The system should correlate stream counts to expected performance royalty payments and flag under-reported periods.

2. **MLC mechanical vs distributor stream count** — Upload `mlc_sample.csv` alongside `spotify_sample.csv`. Compare Units in MLC against Streams in Spotify direct report. Any delta > 5% indicates unreported mechanicals.

3. **Multi-distributor catalog audit** — Upload all 11 distributor files together. The system deduplicates events by ISRC + period + platform to identify which distributors are reporting the same streams (potential double-counting) and which have gaps.

4. **Bandcamp direct-to-fan vs distributor totals** — `bandcamp_sample.csv` contains sales that bypass DSP aggregation. Cross-reference against `cdbaby_sample.csv` Bandcamp line items to verify the distributor is passing through all direct sales correctly.

5. **Creator-economy completeness** — Upload YouTube, TikTok, Instagram, Twitch, and Patreon files. The system should map these to the total revenue picture and flag quarters where social/video revenue exceeds streaming income (a common indicator of catalog undervaluation).

6. **Fraud detection end-to-end** — Upload `anomaly_bot_geo_spike.csv` + `spotify_sample.csv` together. Both files contain matching June RU/IN spikes; cross-source confirmation should trigger a high-confidence fraud alert from `FraudInflationDetector`.

7. **International society triangulation** — Upload `jasrac_sample.csv`, `komca_sample.csv`, `sacem_sample.csv`, `prs_sample.csv`, `socan_sample.csv`, `gema_sample.csv`, and `apra_amcos_sample.csv` together. The system should aggregate by ISRC across all territories, convert to USD, and verify against the `check_foreign_royalties_not_remitted` rule. The anomaly files `anomaly_currency_conversion_error.csv` and `anomaly_withholding_tax.csv` layer in rate and FX discrepancies for SACEM/GEMA rows.

8. **Neighboring rights vs PRO reconciliation** — Upload `soundexchange_sample.csv` + `ppl_sample.csv` (neighboring rights) against `ascap_sample.csv`, `sesac_sample.csv`, `gmr_sample.csv` (performance rights). System should distinguish composer/publisher royalties from performer/sound-recording royalties and flag any period where one stream is present but the corresponding right is absent.

9. **Sync license vs PRO cue sheet audit** — Upload `sync_placements_sample.csv` against `ascap_sample.csv` and `bmi_sample.csv`. Every network placement should generate a corresponding PRO cue sheet payment within 90 days. Upload `anomaly_unlicensed_sync.csv` to add uncontracted usages; the system should flag them as CRITICAL `UNLICENSED_USAGE` and estimate recovery value.

10. **Tour settlement audit** — Upload `ticketmaster_settlement_sample.csv` alongside `anomaly_touring_settlement_gap.csv`. The 16 clean shows establish the per-show revenue and expense pattern. The 6 anomaly shows each have a shortfall below the contracted guarantee; at least 3 have no written settlement — the system should escalate those as `MISSING_GUARANTEE` HIGH severity.

11. **Full catalog ownership reconciliation** — Upload `publishing_splits_sample.csv` alongside all PRO files (ASCAP, BMI, SESAC, GMR) and `anomaly_cowrite_undercrediting.csv`. The system should verify that sum of all writer shares equals 100% per work, that each writer's PRO affiliation matches the paying society, and that the ASCAP/BMI payments to Nova Zephyr are at 50% (not 100%) for Electric Pulse.

12. **Co-distributor duplicate detection** — Upload all 11 distributor files + `anomaly_duplicate_statement.csv`. The system should detect that DistroKid and TuneCore both claim Q1 2025 Spotify US streams for all three tracks, surface the duplicate_of references, and exclude the duplicate rows from total revenue calculations.

13. **Advance recoupment + earnings bridge** — Upload `distributor_advance_sample.csv` alongside `distrokid_sample.csv` and `tunecore_sample.csv`. The system should track recoupment progress month-by-month, confirm Electric Pulse advance recouped in June 2025, and project the remaining Autumn Waves balance vs earnings trend.

14. **UGC revenue gap analysis** — Upload `youtube_content_id_sample.csv` alongside `youtube_studio_sample.csv`. The system should compare Content ID claim revenue (UGC third-party monetization) against first-party YouTube Studio earnings. Q4 2025 `HolidayMusicMix` claim alone generates $2,410 — the system should flag whether this is captured in the studio report or represents incremental revenue.

15. **Black box recovery sweep** — Upload `anomaly_black_box_unclaimed.csv` against international PRO files for 2025. The system should cross-reference the unregistered 2024 works against the 2025 registration activity, calculate estimated recovery value in USD, and generate a registration action plan sorted by recoverable amount.
