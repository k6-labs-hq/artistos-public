/**
 * Shared domain types for the XR7 / ArtistOS frontend.
 *
 * Every interface here maps 1-to-1 to a backend API response shape.
 * Import from this module instead of redefining types locally in components.
 *
 * @module shared/types
 */

// ---------------------------------------------------------------------------
// Agent / Orchestration
// ---------------------------------------------------------------------------

export interface AgentOrchestrationStatus {
  current_step?: string | null;
  confidence?: number | null;
  trace_url?: string | null;
}

export interface AgentStatus {
  agent_orchestra_status?: AgentOrchestrationStatus;
  comfort_messages?: string[];
  portal_guidance?: string[];
  follow_up_actions?: Array<Record<string, unknown>>;
}

// ---------------------------------------------------------------------------
// Anomaly
// ---------------------------------------------------------------------------

export type AnomalySeverity = "CRITICAL" | "HIGH" | "MEDIUM" | "LOW";

export interface Anomaly {
  id: string;
  artist_id: string;
  subtype?: string;
  category?: string;
  severity?: AnomalySeverity | string | number;
  estimated_recoverable?: number;
  created_at?: string;
  detected_at?: string;
  description?: string;
  status?: string;
}

// ---------------------------------------------------------------------------
// Recoverability
// ---------------------------------------------------------------------------

export interface RecoverabilityClassSummary {
  count?: number;
  amount?: number;
  estimated_recoverable?: number;
}

export interface RecoverabilityResult {
  black_box_expiration?: {
    expiration_date?: string | null;
  };
  recoverability?: {
    recoverability_class?: string;
    confidence_score?: number;
    reasoning?: string;
  };
  next_steps?: string[];
}

// ---------------------------------------------------------------------------
// Dashboard
// ---------------------------------------------------------------------------

export interface DashboardSection {
  total_estimated_recoverable?: number;
  total_amount_in_pursuit?: number;
  total_deposited?: number;
}

export interface DashboardDeadlines {
  urgent_count?: number;
  upcoming_count?: number;
  overdue_count?: number;
}

export interface RecoverabilityBreakdown {
  probability_narrative?: string;
  contract_clause_citation?: string;
  by_class?: Record<string, RecoverabilityClassSummary>;
  recoverable_total?: number;
  expired_total?: number;
}

export interface PriorityActionsPayload {
  top_10_actions?: Array<Record<string, unknown>>;
}

export interface Dashboard {
  leakage_discovered?: DashboardSection;
  in_pursuit?: DashboardSection;
  recovered_and_deposited?: DashboardSection;
  deadlines?: DashboardDeadlines;
  catalog_health?: Record<string, unknown>;
  earnings_trend?: Record<string, unknown>;
  recoverability_breakdown?: RecoverabilityBreakdown;
  forecast_confidence?: number;
  priority_actions?: PriorityActionsPayload;
}

// ---------------------------------------------------------------------------
// Black Box Countdown
// ---------------------------------------------------------------------------

export type BlackBoxUrgencyTier = "CRITICAL" | "RED" | "AMBER" | "GREEN" | "EXPIRED";

export interface BlackBoxCountdown {
  anomaly_id: string;
  society: string;
  redistribution_deadline: string;
  days_remaining: number;
  hours_remaining: number;
  urgency_tier: BlackBoxUrgencyTier;
  is_expired: boolean;
  estimated_at_risk_value: number;
  description: string | null;
}

export interface BlackBoxCountdownResult {
  countdowns: BlackBoxCountdown[];
  critical_count: number;
  at_risk_value_next_30_days: number;
  chain_of_custody_hash: string;
}

// ---------------------------------------------------------------------------
// Catalog Valuation (Catalog Value Appraiser)
// ---------------------------------------------------------------------------

export interface WaterfallEntry {
  label: string;
  impact: number;
  cumulative: number;
}

export interface CatalogValuation {
  base_nps_income: number;
  valuation_low: number;
  valuation_expected: number;
  valuation_high: number;
  multiple_applied_low: number;
  multiple_applied_high: number;
  recovery_upside_value: number;
  key_value_drivers: string[];
  key_value_risks: string[];
  waterfall: WaterfallEntry[];
  narrative: string;
  disclaimer: string;
  chain_of_custody_hash: string;
}

// ---------------------------------------------------------------------------
// Contract Drift Monitor
// ---------------------------------------------------------------------------

export interface QuarterPoint {
  quarter: string;
  contracted_rate: number;
  actual_rate: number;
  drift_pct: number;
}

export interface ContractDriftResult {
  contract_id: string;
  payer_name: string;
  classification: string;
  current_drift_pct: number;
  cumulative_underpayment: number;
  drift_trend: string;
  quarterly_timeline: QuarterPoint[];
  anomaly_id?: string;
}

// ---------------------------------------------------------------------------
// Ghost Catalog Detector
// ---------------------------------------------------------------------------

export interface GhostWork {
  work_id: string;
  title: string;
  isrc: string | null;
  ghost_score: number;
  estimated_missing_value: number;
  ghost_start_date: string;
  suspected_cause: string;
  recommended_action: string;
  auto_escalate: boolean;
}

export interface GhostCatalogScanResult {
  ghost_works: GhostWork[];
  ghost_count: number;
  total_estimated_missing_value: number;
  chain_of_custody_hash: string;
}

// ---------------------------------------------------------------------------
// Payer Health Score
// ---------------------------------------------------------------------------

export interface PayerSubScores {
  payment_accuracy: number;
  redistribution_timing: number;
  rate_drift: number;
  dispute_resolution: number;
  data_quality: number;
}

export interface PayerEntry {
  payer_id: string;
  payer_name: string;
  total_score: number;
  risk_tier: string;
  sub_scores: PayerSubScores;
  trend: number[];
  flags: string[];
}

// ---------------------------------------------------------------------------
// Recovery Credit Score
// ---------------------------------------------------------------------------

export interface RecoveryCreditScoreComponent {
  score: number;
  max: number;
  explanation: string;
}

export interface RecoveryCreditScoreComponents {
  catalog_health: RecoveryCreditScoreComponent;
  anomaly_recoverability: RecoveryCreditScoreComponent;
  sol_safety: RecoveryCreditScoreComponent;
  contract_clarity: RecoveryCreditScoreComponent;
  payer_reliability: RecoveryCreditScoreComponent;
  territory_coverage: RecoveryCreditScoreComponent;
  platform_diversification: RecoveryCreditScoreComponent;
}

export interface RecoveryCreditScoreActionItem {
  priority: number;
  action: string;
  impact: number;
  module: string;
}

export interface RecoveryCreditScoreResult {
  score: number;
  tier: string;
  score_delta: number;
  trend: string;
  components: RecoveryCreditScoreComponents;
  actions: RecoveryCreditScoreActionItem[];
  narrative: string;
  max_advance_amount?: number;
  chain_of_custody_hash: string;
}

// ---------------------------------------------------------------------------
// Royalty DNA Profile
// ---------------------------------------------------------------------------

export interface RoyaltyPlatformEntry {
  platform: string;
  amount: number;
  pct: number;
  trend: string;
}

export interface RoyaltyTypeEntry {
  type: string;
  amount: number;
  pct: number;
  trend: string;
}

export interface RoyaltyInsight {
  headline: string;
  explanation: string;
  recommended_action: string;
}

export interface RoyaltyDNAStrand {
  segment: string;
  value: number;
  pct: number;
  color: string;
}

export interface RoyaltyDNAResult {
  platform_breakdown: RoyaltyPlatformEntry[];
  territory_gaps: string[];
  royalty_type_breakdown: RoyaltyTypeEntry[];
  revenue_concentration_score: number;
  top3_platform_concentration_pct: number;
  catalog_long_tail_ratio_pct: number;
  dna_strand: RoyaltyDNAStrand[];
  insights: RoyaltyInsight[];
  chain_of_custody_hash: string;
}

// ---------------------------------------------------------------------------
// Earnings Time Machine
// ---------------------------------------------------------------------------

export interface EarningsPeriod {
  period: string;
  actual_earned: number;
  estimated_clean_world_earned: number;
  delta: number;
  cumulative_leakage_to_date: number;
}

export interface EarningsTimeMachineResult {
  time_series: EarningsPeriod[];
  total_actual_earned: number;
  total_clean_world_earned: number;
  total_lifetime_leakage: number;
  confidence_band: { low: number; expected: number; high: number };
  summary: string;
  chain_of_custody_hash: string;
}

// ---------------------------------------------------------------------------
// Artist Persona (enriched public profile)
// ---------------------------------------------------------------------------

export interface PersonaData {
  artist_id: string;
  enrichment_status: "pending" | "in_progress" | "complete" | "failed";
  enriched_at?: string | null;
  imdb_id?: string | null;
  discogs_artist_id?: string | null;
  spotify_artist_id?: string | null;
  musicbrainz_id?: string | null;
  pro_credits?: unknown[] | null;
  social_handles?: Record<string, string> | null;
  detected_roles?: string[] | null;
  primary_vertical?: string | null;
  bio_snippet?: string | null;
  genre_tags?: string[] | null;
  notable_works?: string[] | null;
  collaborators?: string[] | null;
}

// ---------------------------------------------------------------------------
// VIP / Founders Circle
// ---------------------------------------------------------------------------

export interface VipStatus {
  is_vip: boolean;
  tier_level: "FOUNDERS_CIRCLE" | "VIP" | null;
  perks_unlocked: string[];
  referral_slots_remaining: number;
  concierge_analyst_name: string | null;
  concierge_analyst_email: string | null;
  calendly_link: string | null;
  logo_url: string | null;
  watermark_text: string | null;
  joined_at: string | null;
}

export interface VipReferral {
  id: string;
  invitee_name: string;
  invitee_email: string;
  status: string;
  invited_at: string;
  converted_at?: string | null;
}

export interface VipDrop {
  id: string;
  title: string;
  description: string;
  drop_date: string;
  claim_url?: string | null;
}

// ---------------------------------------------------------------------------
// Copilot / XR7 Advisor
// ---------------------------------------------------------------------------

export interface CopilotHistoryItem {
  id: string;
  query_text: string;
  response_text: string;
  confidence: number;
  sources_cited: string[];
  action_suggestions: string[];
  thumbs_up: boolean | null;
  created_at: string;
}

export interface CopilotQueryResponse {
  id: string;
  response_text: string;
  confidence: number;
  sources_cited: string[];
  action_suggestions: string[];
}

// ---------------------------------------------------------------------------
// Collaborators
// ---------------------------------------------------------------------------

export type CollaboratorRole = "co_writer" | "producer" | "publisher" | "manager" | "label" | "other";

export interface CollaboratorShareResult {
  collaborator_name: string;
  role: string;
  invite_link: string;
  invite_token: string;
  lead_id: string;
  hubspot_logged: boolean;
}

export interface CollaboratorShareResponse {
  share_message: string;
  collaborators: CollaboratorShareResult[];
  total_logged: number;
}

// ---------------------------------------------------------------------------
// Weekly Brief
// ---------------------------------------------------------------------------

export interface WeeklyBriefKeyInsight {
  label: string;
  value: string;
  sentiment?: "positive" | "neutral" | "negative";
}

export interface WeeklyBriefActionItem {
  text: string;
  priority: "high" | "medium" | "low";
  completed: boolean;
}

export interface WeeklyBrief {
  id: string;
  brief_week: string;
  status: "PENDING" | "GENERATING" | "READY" | "FAILED";
  text_summary: string | null;
  audio_url: string | null;
  video_url: string | null;
  key_insights: WeeklyBriefKeyInsight[];
  action_items: WeeklyBriefActionItem[];
  generated_at: string | null;
}

// ---------------------------------------------------------------------------
// Recovery Story / Timeline
// ---------------------------------------------------------------------------

export interface TimelineEvent {
  id: string;
  date: string;
  type: string;
  title: string;
  description?: string;
  amount?: number | null;
  anomaly_id?: string | null;
  claim_id?: string | null;
  status?: string | null;
}

// ---------------------------------------------------------------------------
// Legacy Map (catalog graph)
// ---------------------------------------------------------------------------

export interface LegacyNode {
  id: string;
  label: string;
  type: string;
  value?: number;
  metadata?: Record<string, unknown>;
}

export interface LegacyEdge {
  source: string;
  target: string;
  label?: string;
  weight?: number;
}

export interface LegacyMapData {
  nodes: LegacyNode[];
  edges: LegacyEdge[];
}

// ---------------------------------------------------------------------------
// Concierge Inbox
// ---------------------------------------------------------------------------

export interface ConciergeMessage {
  id: string;
  subject: string;
  body: string;
  from_analyst: string;
  sent_at: string;
  read: boolean;
  priority?: "high" | "medium" | "low" | null;
  action_url?: string | null;
}

// ---------------------------------------------------------------------------
// Admin: Workflow Handoffs
// ---------------------------------------------------------------------------

export interface HandoffRow {
  id: string;
  run_id: string;
  artist_id: string;
  artist_name?: string | null;
  handoff_id: string;
  from_agent: string;
  to_agent: string;
  status: string;
  readiness_score: number;
  readiness_threshold: number;
  created_at?: string | null;
}

export interface HandoffListResponse {
  total: number;
  limit: number;
  offset: number;
  items: HandoffRow[];
}
