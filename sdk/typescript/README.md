# @xr7/sdk@2.0.0

A TypeScript SDK client for the localhost API.

## Usage

First, install the SDK from npm.

```bash
npm install @xr7/sdk --save
```

Next, try it out.


```ts
import {
  Configuration,
  AdminApi,
} from '@xr7/sdk';
import type { AdminOverviewAdminOverviewGetRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new AdminApi();

  const body = {
    // string (optional)
    xAdminKey: xAdminKey_example,
    // string (optional)
    xAdminActor: xAdminActor_example,
  } satisfies AdminOverviewAdminOverviewGetRequest;

  try {
    const data = await api.adminOverviewAdminOverviewGet(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```


## Documentation

### API Endpoints

All URIs are relative to *http://localhost*

| Class | Method | HTTP request | Description
| ----- | ------ | ------------ | -------------
*AdminApi* | [**adminOverviewAdminOverviewGet**](docs/AdminApi.md#adminoverviewadminoverviewget) | **GET** /admin/overview | Admin Overview
*AdminApi* | [**assignFounderManuallyAdminArtistsArtistIdFounderAssignPost**](docs/AdminApi.md#assignfoundermanuallyadminartistsartistidfounderassignpost) | **POST** /admin/artists/{artist_id}/founder/assign | Assign Founder Manually
*AdminApi* | [**founderCohortReportAdminReportsFounderCohortGet**](docs/AdminApi.md#foundercohortreportadminreportsfoundercohortget) | **GET** /admin/reports/founder-cohort | Founder Cohort Report
*AdminApi* | [**founderRosterAdminFoundersGet**](docs/AdminApi.md#founderrosteradminfoundersget) | **GET** /admin/founders | Founder Roster
*AdminApi* | [**listAnomaliesAdminAnomaliesGet**](docs/AdminApi.md#listanomaliesadminanomaliesget) | **GET** /admin/anomalies | List Anomalies
*AdminApi* | [**listArtistsAdminArtistsGet**](docs/AdminApi.md#listartistsadminartistsget) | **GET** /admin/artists | List Artists
*AdminApi* | [**listAuditLogsAdminAuditLogsGet**](docs/AdminApi.md#listauditlogsadminauditlogsget) | **GET** /admin/audit-logs | List Audit Logs
*AdminApi* | [**listClaimsAdminClaimsGet**](docs/AdminApi.md#listclaimsadminclaimsget) | **GET** /admin/claims | List Claims
*AdminApi* | [**listReviewQueueAdminReviewQueueGet**](docs/AdminApi.md#listreviewqueueadminreviewqueueget) | **GET** /admin/review-queue | List Review Queue
*AdminApi* | [**listTransactionsAdminTransactionsGet**](docs/AdminApi.md#listtransactionsadmintransactionsget) | **GET** /admin/transactions | List Transactions
*AdminApi* | [**solRiskReportAdminReportsSolRiskGet**](docs/AdminApi.md#solriskreportadminreportssolriskget) | **GET** /admin/reports/sol-risk | Sol Risk Report
*AdminApi* | [**updateFounderCohortLimitAdminFounderCohortLimitPut**](docs/AdminApi.md#updatefoundercohortlimitadminfoundercohortlimitput) | **PUT** /admin/founder/cohort-limit | Update Founder Cohort Limit
*AdvanceGovernanceApi* | [**acceptArtistOfferArtistsArtistIdAdvanceOffersOfferIdAcceptPost**](docs/AdvanceGovernanceApi.md#acceptartistofferartistsartistidadvanceoffersofferidacceptpost) | **POST** /artists/{artist_id}/advance/offers/{offer_id}/accept | Accept Artist Offer
*AdvanceGovernanceApi* | [**analystQueueAdminAdvancesQueueAnalystGet**](docs/AdvanceGovernanceApi.md#analystqueueadminadvancesqueueanalystget) | **GET** /admin/advances/queue/analyst | Analyst Queue
*AdvanceGovernanceApi* | [**approveAnalystAdminAdvancesOpportunitiesOpportunityIdAnalystDecisionPost**](docs/AdvanceGovernanceApi.md#approveanalystadminadvancesopportunitiesopportunityidanalystdecisionpost) | **POST** /admin/advances/opportunities/{opportunity_id}/analyst-decision | Approve Analyst
*AdvanceGovernanceApi* | [**approveExecutiveAdminAdvancesOpportunitiesOpportunityIdExecutiveDecisionPost**](docs/AdvanceGovernanceApi.md#approveexecutiveadminadvancesopportunitiesopportunityidexecutivedecisionpost) | **POST** /admin/advances/opportunities/{opportunity_id}/executive-decision | Approve Executive
*AdvanceGovernanceApi* | [**createFailedPacketAdminAdvancesOffersOfferIdFailedRecoveryPacketPost**](docs/AdvanceGovernanceApi.md#createfailedpacketadminadvancesoffersofferidfailedrecoverypacketpost) | **POST** /admin/advances/offers/{offer_id}/failed-recovery-packet | Create Failed Packet
*AdvanceGovernanceApi* | [**executiveQueueAdminAdvancesQueueExecutiveGet**](docs/AdvanceGovernanceApi.md#executivequeueadminadvancesqueueexecutiveget) | **GET** /admin/advances/queue/executive | Executive Queue
*AdvanceGovernanceApi* | [**listArtistOffersArtistsArtistIdAdvanceOffersGet**](docs/AdvanceGovernanceApi.md#listartistoffersartistsartistidadvanceoffersget) | **GET** /artists/{artist_id}/advance/offers | List Artist Offers
*AdvanceGovernanceApi* | [**publishOfferAdminAdvancesOpportunitiesOpportunityIdPublishOfferPost**](docs/AdvanceGovernanceApi.md#publishofferadminadvancesopportunitiesopportunityidpublishofferpost) | **POST** /admin/advances/opportunities/{opportunity_id}/publish-offer | Publish Offer
*AdvanceGovernanceApi* | [**runNightlyEvalAdminAdvancesRunNightlyEvalPost**](docs/AdvanceGovernanceApi.md#runnightlyevaladminadvancesrunnightlyevalpost) | **POST** /admin/advances/run-nightly-eval | Run Nightly Eval
*AnomaliesApi* | [**anomalyRecoveryProbabilityEndpointAnomaliesAnomalyIdRecoveryProbabilityGet**](docs/AnomaliesApi.md#anomalyrecoveryprobabilityendpointanomaliesanomalyidrecoveryprobabilityget) | **GET** /anomalies/{anomaly_id}/recovery-probability | Anomaly Recovery Probability Endpoint
*AnomaliesApi* | [**detectAnomaliesArtistsArtistIdAnomaliesDetectPost**](docs/AnomaliesApi.md#detectanomaliesartistsartistidanomaliesdetectpost) | **POST** /artists/{artist_id}/anomalies/detect | Detect Anomalies
*AnomaliesApi* | [**fraudScanArtistsArtistIdAnomaliesFraudScanPost**](docs/AnomaliesApi.md#fraudscanartistsartistidanomaliesfraudscanpost) | **POST** /artists/{artist_id}/anomalies/fraud-scan | Fraud Scan
*AnomaliesApi* | [**getAnomalyAnomaliesAnomalyIdGet**](docs/AnomaliesApi.md#getanomalyanomaliesanomalyidget) | **GET** /anomalies/{anomaly_id} | Get Anomaly
*AnomaliesApi* | [**listAnomaliesArtistsArtistIdAnomaliesGet**](docs/AnomaliesApi.md#listanomaliesartistsartistidanomaliesget) | **GET** /artists/{artist_id}/anomalies | List Anomalies
*AnomaliesApi* | [**scanAiInfluenceArtistsArtistIdAiMusicScanInfluencePost**](docs/AnomaliesApi.md#scanaiinfluenceartistsartistidaimusicscaninfluencepost) | **POST** /artists/{artist_id}/ai-music/scan-influence | Scan Ai Influence
*ArtistsApi* | [**artistSummaryArtistsArtistIdSummaryGet**](docs/ArtistsApi.md#artistsummaryartistsartistidsummaryget) | **GET** /artists/{artist_id}/summary | Artist Summary
*ArtistsApi* | [**catalogHealthArtistsArtistIdMlCatalogHealthGet**](docs/ArtistsApi.md#cataloghealthartistsartistidmlcataloghealthget) | **GET** /artists/{artist_id}/ml/catalog-health | Catalog Health
*ArtistsApi* | [**connectArtistArtistsArtistIdConnectPost**](docs/ArtistsApi.md#connectartistartistsartistidconnectpost) | **POST** /artists/{artist_id}/connect | Connect Artist
*ArtistsApi* | [**connectProviderArtistsArtistIdConnectProviderPost**](docs/ArtistsApi.md#connectproviderartistsartistidconnectproviderpost) | **POST** /artists/{artist_id}/connect/{provider} | Connect Provider
*ArtistsApi* | [**createArtistArtistsPost**](docs/ArtistsApi.md#createartistartistspost) | **POST** /artists/ | Create Artist
*ArtistsApi* | [**getArtistArtistsArtistIdGet**](docs/ArtistsApi.md#getartistartistsartistidget) | **GET** /artists/{artist_id} | Get Artist
*ArtistsApi* | [**getArtistPreferencesArtistsArtistIdPreferencesGet**](docs/ArtistsApi.md#getartistpreferencesartistsartistidpreferencesget) | **GET** /artists/{artist_id}/preferences | Get Artist Preferences
*ArtistsApi* | [**providerConnectionStatusArtistsArtistIdConnectProviderStatusGet**](docs/ArtistsApi.md#providerconnectionstatusartistsartistidconnectproviderstatusget) | **GET** /artists/{artist_id}/connect/{provider}/status | Provider Connection Status
*ArtistsApi* | [**updateArtistPreferencesArtistsArtistIdPreferencesPut**](docs/ArtistsApi.md#updateartistpreferencesartistsartistidpreferencesput) | **PUT** /artists/{artist_id}/preferences | Update Artist Preferences
*ArtistsApi* | [**weeklyDigestArtistsArtistIdDigestWeeklyGet**](docs/ArtistsApi.md#weeklydigestartistsartistiddigestweeklyget) | **GET** /artists/{artist_id}/digest/weekly | Weekly Digest
*AuthApi* | [**adminLoginAuthLoginAdminPost**](docs/AuthApi.md#adminloginauthloginadminpost) | **POST** /auth/login/admin | Admin Login
*AuthApi* | [**artistLoginAuthLoginArtistPost**](docs/AuthApi.md#artistloginauthloginartistpost) | **POST** /auth/login/artist | Artist Login
*AuthApi* | [**authMeAuthMeGet**](docs/AuthApi.md#authmeauthmeget) | **GET** /auth/me | Auth Me
*B2bApi* | [**b2bDashboardB2bOrgOrgIdDashboardGet**](docs/B2bApi.md#b2bdashboardb2borgorgiddashboardget) | **GET** /b2b/org/{org_id}/dashboard | B2B Dashboard
*B2bApi* | [**bulkOnboardB2bOrgOrgIdArtistsBulkOnboardPost**](docs/B2bApi.md#bulkonboardb2borgorgidartistsbulkonboardpost) | **POST** /b2b/org/{org_id}/artists/bulk-onboard | Bulk Onboard
*B2bApi* | [**managementAnomaliesDrilldownManagementOrgIdAnomaliesGet**](docs/B2bApi.md#managementanomaliesdrilldownmanagementorgidanomaliesget) | **GET** /management/{org_id}/anomalies | Management Anomalies Drilldown
*B2bApi* | [**managementArtistDrilldownManagementOrgIdArtistsArtistIdGet**](docs/B2bApi.md#managementartistdrilldownmanagementorgidartistsartistidget) | **GET** /management/{org_id}/artists/{artist_id} | Management Artist Drilldown
*B2bApi* | [**managementCatalogDrilldownManagementOrgIdCatalogGet**](docs/B2bApi.md#managementcatalogdrilldownmanagementorgidcatalogget) | **GET** /management/{org_id}/catalog | Management Catalog Drilldown
*B2bApi* | [**managementClaimsDrilldownManagementOrgIdClaimsGet**](docs/B2bApi.md#managementclaimsdrilldownmanagementorgidclaimsget) | **GET** /management/{org_id}/claims | Management Claims Drilldown
*B2bApi* | [**managementDashboardManagementOrgIdDashboardGet**](docs/B2bApi.md#managementdashboardmanagementorgiddashboardget) | **GET** /management/{org_id}/dashboard | Management Dashboard
*B2bApi* | [**managementDashboardV2ManagementOrgIdDashboardV2Get**](docs/B2bApi.md#managementdashboardv2managementorgiddashboardv2get) | **GET** /management/{org_id}/dashboard/v2 | Management Dashboard V2
*B2bApi* | [**managementForecastManagementOrgIdForecastGet**](docs/B2bApi.md#managementforecastmanagementorgidforecastget) | **GET** /management/{org_id}/forecast | Management Forecast
*B2bApi* | [**orgPortfolioOrgOrgIdPortfolioGet**](docs/B2bApi.md#orgportfolioorgorgidportfolioget) | **GET** /org/{org_id}/portfolio | Org Portfolio
*B2bApi* | [**xr7OperatorDashboardXr7OperatorDashboardGet**](docs/B2bApi.md#xr7operatordashboardxr7operatordashboardget) | **GET** /xr7/operator/dashboard | Xr7 Operator Dashboard
*BillingApi* | [**getBillingSummaryArtistsArtistIdBillingGet**](docs/BillingApi.md#getbillingsummaryartistsartistidbillingget) | **GET** /artists/{artist_id}/billing | Get Billing Summary
*BillingApi* | [**listInvoicesArtistsArtistIdInvoicesGet**](docs/BillingApi.md#listinvoicesartistsartistidinvoicesget) | **GET** /artists/{artist_id}/invoices | List Invoices
*BrandingApi* | [**brandingTemplatesBrandingOrgIdTemplatesGet**](docs/BrandingApi.md#brandingtemplatesbrandingorgidtemplatesget) | **GET** /branding/{org_id}/templates | Branding Templates
*BrandingApi* | [**createBrandingBrandingOrgIdPost**](docs/BrandingApi.md#createbrandingbrandingorgidpost) | **POST** /branding/{org_id} | Create Branding
*BrandingApi* | [**createHelpArticleBrandingOrgIdHelpArticlesPost**](docs/BrandingApi.md#createhelparticlebrandingorgidhelparticlespost) | **POST** /branding/{org_id}/help-articles | Create Help Article
*BrandingApi* | [**getBrandingBrandingOrgIdGet**](docs/BrandingApi.md#getbrandingbrandingorgidget) | **GET** /branding/{org_id} | Get Branding
*BrandingApi* | [**listHelpArticlesBrandingOrgIdHelpArticlesGet**](docs/BrandingApi.md#listhelparticlesbrandingorgidhelparticlesget) | **GET** /branding/{org_id}/help-articles | List Help Articles
*BrandingApi* | [**patchBrandingBrandingOrgIdPatch**](docs/BrandingApi.md#patchbrandingbrandingorgidpatch) | **PATCH** /branding/{org_id} | Patch Branding
*BrandingApi* | [**uiShellUiShellGet**](docs/BrandingApi.md#uishelluishellget) | **GET** /ui/shell | Ui Shell
*ClaimsApi* | [**activateNegotiatorAgentClaimsClaimIdActivateAgentPost**](docs/ClaimsApi.md#activatenegotiatoragentclaimsclaimidactivateagentpost) | **POST** /claims/{claim_id}/activate-agent | Activate Negotiator Agent
*ClaimsApi* | [**advanceClaimClaimsClaimIdAdvancePost**](docs/ClaimsApi.md#advanceclaimclaimsclaimidadvancepost) | **POST** /claims/{claim_id}/advance | Advance Claim
*ClaimsApi* | [**claimAutomationPlanClaimsClaimIdAutomationPlanGet**](docs/ClaimsApi.md#claimautomationplanclaimsclaimidautomationplanget) | **GET** /claims/{claim_id}/automation-plan | Claim Automation Plan
*ClaimsApi* | [**claimEvidenceOptimizedClaimsClaimIdEvidenceOptimizedGet**](docs/ClaimsApi.md#claimevidenceoptimizedclaimsclaimidevidenceoptimizedget) | **GET** /claims/{claim_id}/evidence/optimized | Claim Evidence Optimized
*ClaimsApi* | [**claimEvidenceStrengthClaimsClaimIdEvidenceStrengthGet**](docs/ClaimsApi.md#claimevidencestrengthclaimsclaimidevidencestrengthget) | **GET** /claims/{claim_id}/evidence/strength | Claim Evidence Strength
*ClaimsApi* | [**claimForecastClaimsClaimIdForecastGet**](docs/ClaimsApi.md#claimforecastclaimsclaimidforecastget) | **GET** /claims/{claim_id}/forecast | Claim Forecast
*ClaimsApi* | [**claimNegotiationIntelClaimsClaimIdNegotiationIntelGet**](docs/ClaimsApi.md#claimnegotiationintelclaimsclaimidnegotiationintelget) | **GET** /claims/{claim_id}/negotiation-intel | Claim Negotiation Intel
*ClaimsApi* | [**claimPlaybookClaimsClaimIdPlaybookGet**](docs/ClaimsApi.md#claimplaybookclaimsclaimidplaybookget) | **GET** /claims/{claim_id}/playbook | Claim Playbook
*ClaimsApi* | [**claimSlaPredictionClaimsClaimIdSlaPredictionGet**](docs/ClaimsApi.md#claimslapredictionclaimsclaimidslapredictionget) | **GET** /claims/{claim_id}/sla-prediction | Claim Sla Prediction
*ClaimsApi* | [**claimStrengthExplainerClaimsClaimIdStrengthExplainerGet**](docs/ClaimsApi.md#claimstrengthexplainerclaimsclaimidstrengthexplainerget) | **GET** /claims/{claim_id}/strength-explainer | Claim Strength Explainer
*ClaimsApi* | [**createClaimForArtistArtistsArtistIdClaimsPost**](docs/ClaimsApi.md#createclaimforartistartistsartistidclaimspost) | **POST** /artists/{artist_id}/claims | Create Claim For Artist
*ClaimsApi* | [**escalateLegalClaimsClaimIdEscalateLegalPost**](docs/ClaimsApi.md#escalatelegalclaimsclaimidescalatelegalpost) | **POST** /claims/{claim_id}/escalate-legal | Escalate Legal
*ClaimsApi* | [**exportEvidencePacketClaimsClaimIdEvidenceExportGet**](docs/ClaimsApi.md#exportevidencepacketclaimsclaimidevidenceexportget) | **GET** /claims/{claim_id}/evidence/export | Export Evidence Packet
*ClaimsApi* | [**exportEvidencePacketExpertModeClaimsClaimIdEvidenceExportPost**](docs/ClaimsApi.md#exportevidencepacketexpertmodeclaimsclaimidevidenceexportpost) | **POST** /claims/{claim_id}/evidence/export | Export Evidence Packet Expert Mode
*ClaimsApi* | [**generateAttorneyEvidenceFileApiClaimsClaimIdAttorneyEvidencePost**](docs/ClaimsApi.md#generateattorneyevidencefileapiclaimsclaimidattorneyevidencepost) | **POST** /api/claims/{claim_id}/attorney-evidence | Generate Attorney Evidence File
*ClaimsApi* | [**generateAttorneyEvidenceFileClaimsClaimIdAttorneyEvidencePost**](docs/ClaimsApi.md#generateattorneyevidencefileclaimsclaimidattorneyevidencepost) | **POST** /claims/{claim_id}/attorney-evidence | Generate Attorney Evidence File
*ClaimsApi* | [**generateEvidenceClaimsClaimIdEvidencePost**](docs/ClaimsApi.md#generateevidenceclaimsclaimidevidencepost) | **POST** /claims/{claim_id}/evidence | Generate Evidence
*ClaimsApi* | [**getClaimClaimsClaimIdGet**](docs/ClaimsApi.md#getclaimclaimsclaimidget) | **GET** /claims/{claim_id} | Get Claim
*ClaimsApi* | [**getEvidenceClaimsClaimIdEvidenceGet**](docs/ClaimsApi.md#getevidenceclaimsclaimidevidenceget) | **GET** /claims/{claim_id}/evidence | Get Evidence
*ClaimsApi* | [**listClaimsArtistsArtistIdClaimsGet**](docs/ClaimsApi.md#listclaimsartistsartistidclaimsget) | **GET** /artists/{artist_id}/claims | List Claims
*ClaimsApi* | [**reconcileClaimClaimsClaimIdReconcilePost**](docs/ClaimsApi.md#reconcileclaimclaimsclaimidreconcilepost) | **POST** /claims/{claim_id}/reconcile | Reconcile Claim
*ClaimsApi* | [**verifyEvidencePacketClaimsClaimIdEvidenceVerifyGet**](docs/ClaimsApi.md#verifyevidencepacketclaimsclaimidevidenceverifyget) | **GET** /claims/{claim_id}/evidence/verify | Verify Evidence Packet
*ClassActionApi* | [**listClassActionSignalsAdminClassActionSignalsGet**](docs/ClassActionApi.md#listclassactionsignalsadminclassactionsignalsget) | **GET** /admin/class-action/signals | List Class Action Signals
*ClassActionApi* | [**runClassActionAggregationAdminClassActionAggregatePost**](docs/ClassActionApi.md#runclassactionaggregationadminclassactionaggregatepost) | **POST** /admin/class-action/aggregate | Run Class Action Aggregation
*ConfigApi* | [**getFounderStatusConfigFounderStatusGet**](docs/ConfigApi.md#getfounderstatusconfigfounderstatusget) | **GET** /config/founder-status | Get Founder Status
*ConnectApi* | [**connectGlobalSocialArtistsArtistIdConnectGlobalSocialPost**](docs/ConnectApi.md#connectglobalsocialartistsartistidconnectglobalsocialpost) | **POST** /artists/{artist_id}/connect/global-social | Connect Global Social
*ConnectApi* | [**connectGlobalSocialStatusArtistsArtistIdConnectGlobalSocialStatusGet**](docs/ConnectApi.md#connectglobalsocialstatusartistsartistidconnectglobalsocialstatusget) | **GET** /artists/{artist_id}/connect/global-social/status | Connect Global Social Status
*ConnectApi* | [**connectSoundcloudArtistsArtistIdConnectSoundcloudPost**](docs/ConnectApi.md#connectsoundcloudartistsartistidconnectsoundcloudpost) | **POST** /artists/{artist_id}/connect/soundcloud | Connect Soundcloud
*ConnectApi* | [**connectSoundcloudStatusArtistsArtistIdConnectSoundcloudStatusGet**](docs/ConnectApi.md#connectsoundcloudstatusartistsartistidconnectsoundcloudstatusget) | **GET** /artists/{artist_id}/connect/soundcloud/status | Connect Soundcloud Status
*CreatorEconomyApi* | [**ingestCreatorDataArtistsArtistIdCreatorIngestPost**](docs/CreatorEconomyApi.md#ingestcreatordataartistsartistidcreatoringestpost) | **POST** /artists/{artist_id}/creator/ingest | Ingest Creator Data
*CreatorEconomyApi* | [**listCreatorPlatformsArtistsArtistIdCreatorPlatformsGet**](docs/CreatorEconomyApi.md#listcreatorplatformsartistsartistidcreatorplatformsget) | **GET** /artists/{artist_id}/creator/platforms | List Creator Platforms
*DashboardApi* | [**agentTraceArtistsArtistIdAgentTraceRunIdGet**](docs/DashboardApi.md#agenttraceartistsartistidagenttracerunidget) | **GET** /artists/{artist_id}/agent-trace/{run_id} | Agent Trace
*DashboardApi* | [**chatRoyaltiesArtistsArtistIdChatRoyaltiesPost**](docs/DashboardApi.md#chatroyaltiesartistsartistidchatroyaltiespost) | **POST** /artists/{artist_id}/chat/royalties | Chat Royalties
*DashboardApi* | [**dashboardBenchmarksArtistsArtistIdBenchmarksGet**](docs/DashboardApi.md#dashboardbenchmarksartistsartistidbenchmarksget) | **GET** /artists/{artist_id}/benchmarks | Dashboard Benchmarks
*DashboardApi* | [**dashboardFlowArtistsArtistIdDashboardFlowGet**](docs/DashboardApi.md#dashboardflowartistsartistiddashboardflowget) | **GET** /artists/{artist_id}/dashboard/flow | Dashboard Flow
*DashboardApi* | [**exportFullTransparencyArtistsArtistIdExportFullTransparencyGet**](docs/DashboardApi.md#exportfulltransparencyartistsartistidexportfulltransparencyget) | **GET** /artists/{artist_id}/export/full-transparency | Export Full Transparency
*DashboardApi* | [**exportGuidanceArtistsArtistIdDashboardExportGuidanceGet**](docs/DashboardApi.md#exportguidanceartistsartistiddashboardexportguidanceget) | **GET** /artists/{artist_id}/dashboard/export-guidance | Export Guidance
*DashboardApi* | [**getAgentsStatusArtistsArtistIdAgentsStatusGet**](docs/DashboardApi.md#getagentsstatusartistsartistidagentsstatusget) | **GET** /artists/{artist_id}/agents/status | Get Agents Status
*DashboardApi* | [**getArtistDashboardArtistsArtistIdDashboardGet**](docs/DashboardApi.md#getartistdashboardartistsartistiddashboardget) | **GET** /artists/{artist_id}/dashboard | Get Artist Dashboard
*DashboardApi* | [**getDashboardUiDashboardUiGet**](docs/DashboardApi.md#getdashboarduidashboarduiget) | **GET** /dashboard/ui | Get Dashboard Ui
*DefaultApi* | [**healthHealthGet**](docs/DefaultApi.md#healthhealthget) | **GET** /health | Health
*DefaultApi* | [**readinessHealthReadinessGet**](docs/DefaultApi.md#readinesshealthreadinessget) | **GET** /health/readiness | Readiness
*EarningsApi* | [**forecastEarningsArtistsArtistIdMlForecastPost**](docs/EarningsApi.md#forecastearningsartistsartistidmlforecastpost) | **POST** /artists/{artist_id}/ml/forecast | Forecast Earnings
*EarningsApi* | [**getEarningsHistoryArtistsArtistIdEarningsHistoryGet**](docs/EarningsApi.md#getearningshistoryartistsartistidearningshistoryget) | **GET** /artists/{artist_id}/earnings/history | Get Earnings History
*EarningsApi* | [**getEarningsSummaryArtistsArtistIdEarningsGet**](docs/EarningsApi.md#getearningssummaryartistsartistidearningsget) | **GET** /artists/{artist_id}/earnings | Get Earnings Summary
*EarningsApi* | [**getPostRepairForecastArtistsArtistIdEarningsForecastGet**](docs/EarningsApi.md#getpostrepairforecastartistsartistidearningsforecastget) | **GET** /artists/{artist_id}/earnings/forecast | Get Post Repair Forecast
*EarningsApi* | [**reconstructEarningsArtistsArtistIdEarningsReconstructPost**](docs/EarningsApi.md#reconstructearningsartistsartistidearningsreconstructpost) | **POST** /artists/{artist_id}/earnings/reconstruct | Reconstruct Earnings
*ExpansionApi* | [**addTeamMemberArtistsArtistIdTeamMembersPost**](docs/ExpansionApi.md#addteammemberartistsartistidteammemberspost) | **POST** /artists/{artist_id}/team/members | Add Team Member
*ExpansionApi* | [**anchorEvidencePacketInternalImmutableLog**](docs/ExpansionApi.md#anchorevidencepacketinternalimmutablelog) | **POST** /claims/{claim_id}/evidence/anchor | Anchor Evidence Packet
*ExpansionApi* | [**benchmarkPercentilesArtistsArtistIdRecoveryBenchmarkPercentilesGet**](docs/ExpansionApi.md#benchmarkpercentilesartistsartistidrecoverybenchmarkpercentilesget) | **GET** /artists/{artist_id}/recovery/benchmark-percentiles | Benchmark Percentiles
*ExpansionApi* | [**createOauthSessionArtistsArtistIdConnectOauthSessionPost**](docs/ExpansionApi.md#createoauthsessionartistsartistidconnectoauthsessionpost) | **POST** /artists/{artist_id}/connect/oauth-session | Create Oauth Session
*ExpansionApi* | [**dashboardChartsDataArtistsArtistIdDashboardChartsGet**](docs/ExpansionApi.md#dashboardchartsdataartistsartistiddashboardchartsget) | **GET** /artists/{artist_id}/dashboard/charts | Dashboard Charts Data
*ExpansionApi* | [**disconnectConnectedAccountArtistsArtistIdConnectAccountsAccountIdDelete**](docs/ExpansionApi.md#disconnectconnectedaccountartistsartistidconnectaccountsaccountiddelete) | **DELETE** /artists/{artist_id}/connect/accounts/{account_id} | Disconnect Connected Account
*ExpansionApi* | [**educationGuideDetailEducationGuidesGuideIdGet**](docs/ExpansionApi.md#educationguidedetaileducationguidesguideidget) | **GET** /education/guides/{guide_id} | Education Guide Detail
*ExpansionApi* | [**educationGuidesIndexEducationGuidesGet**](docs/ExpansionApi.md#educationguidesindexeducationguidesget) | **GET** /education/guides | Education Guides Index
*ExpansionApi* | [**estimateWithholdingArtistsArtistIdIntelligenceWithholdingEstimatePost**](docs/ExpansionApi.md#estimatewithholdingartistsartistidintelligencewithholdingestimatepost) | **POST** /artists/{artist_id}/intelligence/withholding-estimate | Estimate Withholding
*ExpansionApi* | [**exchangeOauthCodeArtistsArtistIdConnectOauthSessionSessionIdExchangePost**](docs/ExpansionApi.md#exchangeoauthcodeartistsartistidconnectoauthsessionsessionidexchangepost) | **POST** /artists/{artist_id}/connect/oauth-session/{session_id}/exchange | Exchange Oauth Code
*ExpansionApi* | [**exportSummaryReportArtistsArtistIdReportsSummaryGet**](docs/ExpansionApi.md#exportsummaryreportartistsartistidreportssummaryget) | **GET** /artists/{artist_id}/reports/summary | Export Summary Report
*ExpansionApi* | [**generateAuditDemandLetterArtistsArtistIdRecoveryAuditDemandLetterGet**](docs/ExpansionApi.md#generateauditdemandletterartistsartistidrecoveryauditdemandletterget) | **GET** /artists/{artist_id}/recovery/audit-demand-letter | Generate Audit Demand Letter
*ExpansionApi* | [**generateClaimTemplateArtistsArtistIdClaimsTemplatesPost**](docs/ExpansionApi.md#generateclaimtemplateartistsartistidclaimstemplatespost) | **POST** /artists/{artist_id}/claims/templates | Generate Claim Template
*ExpansionApi* | [**getNotificationPreferencesArtistsArtistIdNotificationsPreferencesGet**](docs/ExpansionApi.md#getnotificationpreferencesartistsartistidnotificationspreferencesget) | **GET** /artists/{artist_id}/notifications/preferences | Get Notification Preferences
*ExpansionApi* | [**listConnectFallbacksArtistsArtistIdConnectFallbacksGet**](docs/ExpansionApi.md#listconnectfallbacksartistsartistidconnectfallbacksget) | **GET** /artists/{artist_id}/connect/fallbacks | List Connect Fallbacks
*ExpansionApi* | [**listConnectedAccountsArtistsArtistIdConnectAccountsGet**](docs/ExpansionApi.md#listconnectedaccountsartistsartistidconnectaccountsget) | **GET** /artists/{artist_id}/connect/accounts | List Connected Accounts
*ExpansionApi* | [**listTeamMembersArtistsArtistIdTeamMembersGet**](docs/ExpansionApi.md#listteammembersartistsartistidteammembersget) | **GET** /artists/{artist_id}/team/members | List Team Members
*ExpansionApi* | [**partnershipTargetsPartnershipsTargetsGet**](docs/ExpansionApi.md#partnershiptargetspartnershipstargetsget) | **GET** /partnerships/targets | Partnership Targets
*ExpansionApi* | [**predictTotalRecoverableArtistsArtistIdMlPredictRecoverablePost**](docs/ExpansionApi.md#predicttotalrecoverableartistsartistidmlpredictrecoverablepost) | **POST** /artists/{artist_id}/ml/predict-recoverable | Predict Total Recoverable
*ExpansionApi* | [**publicRecoveryStatsStatsPublicRecoveryGet**](docs/ExpansionApi.md#publicrecoverystatsstatspublicrecoveryget) | **GET** /stats/public/recovery | Public Recovery Stats
*ExpansionApi* | [**refreshConnectedAccountTokenArtistsArtistIdConnectAccountsAccountIdRefreshPost**](docs/ExpansionApi.md#refreshconnectedaccounttokenartistsartistidconnectaccountsaccountidrefreshpost) | **POST** /artists/{artist_id}/connect/accounts/{account_id}/refresh | Refresh Connected Account Token
*ExpansionApi* | [**removeTeamMemberArtistsArtistIdTeamMembersMemberIdDelete**](docs/ExpansionApi.md#removeteammemberartistsartistidteammembersmemberiddelete) | **DELETE** /artists/{artist_id}/team/members/{member_id} | Remove Team Member
*ExpansionApi* | [**upsertNotificationPreferencesArtistsArtistIdNotificationsPreferencesPut**](docs/ExpansionApi.md#upsertnotificationpreferencesartistsartistidnotificationspreferencesput) | **PUT** /artists/{artist_id}/notifications/preferences | Upsert Notification Preferences
*ExpansionApi* | [**urgentSolNotificationCheckArtistsArtistIdNotificationsUrgentSolCheckPost**](docs/ExpansionApi.md#urgentsolnotificationcheckartistsartistidnotificationsurgentsolcheckpost) | **POST** /artists/{artist_id}/notifications/urgent-sol-check | Urgent Sol Notification Check
*ExpansionApi* | [**whiteLabelPortfolioB2bPortfolioOrgIdGet**](docs/ExpansionApi.md#whitelabelportfoliob2bportfolioorgidget) | **GET** /b2b/portfolio/{org_id} | White Label Portfolio
*FetchersApi* | [**fetchGlobalSocialArtistsArtistIdFetchersGlobalSocialPost**](docs/FetchersApi.md#fetchglobalsocialartistsartistidfetchersglobalsocialpost) | **POST** /artists/{artist_id}/fetchers/global-social | Fetch Global Social
*ForensicApiApi* | [**authConnectAuthConnectProviderPost**](docs/ForensicApiApi.md#authconnectauthconnectproviderpost) | **POST** /auth/connect/{provider} | Auth Connect
*ForensicApiApi* | [**authProvidersAuthProvidersGet**](docs/ForensicApiApi.md#authprovidersauthprovidersget) | **GET** /auth/providers | Auth Providers
*ForensicApiApi* | [**confirmCatalogCatalogConfirmPost**](docs/ForensicApiApi.md#confirmcatalogcatalogconfirmpost) | **POST** /catalog/confirm | Confirm Catalog
*ForensicApiApi* | [**getCatalogCatalogGet**](docs/ForensicApiApi.md#getcatalogcatalogget) | **GET** /catalog | Get Catalog
*ForensicApiApi* | [**getLedgerEntryLedgerEntryIdGet**](docs/ForensicApiApi.md#getledgerentryledgerentryidget) | **GET** /ledger/{entry_id} | Get Ledger Entry
*ForensicApiApi* | [**listLedgerLedgerGet**](docs/ForensicApiApi.md#listledgerledgerget) | **GET** /ledger | List Ledger
*ForensicApiApi* | [**listVarianceVarianceGet**](docs/ForensicApiApi.md#listvariancevarianceget) | **GET** /variance | List Variance
*ForensicApiApi* | [**recoverySubmitRecoveryClaimIdSubmitPost**](docs/ForensicApiApi.md#recoverysubmitrecoveryclaimidsubmitpost) | **POST** /recovery/{claim_id}/submit | Recovery Submit
*ForensicApiApi* | [**statementsStatusStatementsStatementIdStatusGet**](docs/ForensicApiApi.md#statementsstatusstatementsstatementidstatusget) | **GET** /statements/{statement_id}/status | Statements Status
*ForensicApiApi* | [**statementsUploadStatementsUploadPost**](docs/ForensicApiApi.md#statementsuploadstatementsuploadpost) | **POST** /statements/upload | Statements Upload
*ForensicApiApi* | [**varianceEvidenceVarianceVarianceIdEvidenceGet**](docs/ForensicApiApi.md#varianceevidencevariancevarianceidevidenceget) | **GET** /variance/{variance_id}/evidence | Variance Evidence
*GovernanceApi* | [**eraseArtistDataArtistsArtistIdPrivacyErasePost**](docs/GovernanceApi.md#eraseartistdataartistsartistidprivacyerasepost) | **POST** /artists/{artist_id}/privacy/erase | Erase Artist Data
*GovernanceApi* | [**exportArtistDataArtistsArtistIdPrivacyExportPost**](docs/GovernanceApi.md#exportartistdataartistsartistidprivacyexportpost) | **POST** /artists/{artist_id}/privacy/export | Export Artist Data
*GovernanceApi* | [**listAdminAuditEventsAdminAuditEventsGet**](docs/GovernanceApi.md#listadminauditeventsadminauditeventsget) | **GET** /admin/audit/events | List Admin Audit Events
*IdentityApi* | [**autoMatchIdentityArtistsArtistIdIdentityAutoMatchPost**](docs/IdentityApi.md#automatchidentityartistsartistididentityautomatchpost) | **POST** /artists/{artist_id}/identity/auto-match | Auto Match Identity
*IdentityApi* | [**decideIdentityMatchArtistsArtistIdIdentityMatchesMatchIdDecisionPost**](docs/IdentityApi.md#decideidentitymatchartistsartistididentitymatchesmatchiddecisionpost) | **POST** /artists/{artist_id}/identity/matches/{match_id}/decision | Decide Identity Match
*IdentityApi* | [**getIdentityMatchAuditArtistsArtistIdIdentityMatchesMatchIdAuditGet**](docs/IdentityApi.md#getidentitymatchauditartistsartistididentitymatchesmatchidauditget) | **GET** /artists/{artist_id}/identity/matches/{match_id}/audit | Get Identity Match Audit
*IdentityApi* | [**listIdentityMatchesArtistsArtistIdIdentityMatchesGet**](docs/IdentityApi.md#listidentitymatchesartistsartistididentitymatchesget) | **GET** /artists/{artist_id}/identity/matches | List Identity Matches
*IngestionApi* | [**connectRegionalGlobalArtistsArtistIdConnectRegionalGlobalPost**](docs/IngestionApi.md#connectregionalglobalartistsartistidconnectregionalglobalpost) | **POST** /artists/{artist_id}/connect/regional-global | Connect Regional Global
*IngestionApi* | [**connectSoundexchangeMlcArtistsArtistIdConnectSoundexchangeMlcPost**](docs/IngestionApi.md#connectsoundexchangemlcartistsartistidconnectsoundexchangemlcpost) | **POST** /artists/{artist_id}/connect/soundexchange-mlc | Connect Soundexchange Mlc
*IngestionApi* | [**getStatementArtistsArtistIdStatementsStatementIdGet**](docs/IngestionApi.md#getstatementartistsartistidstatementsstatementidget) | **GET** /artists/{artist_id}/statements/{statement_id} | Get Statement
*IngestionApi* | [**listStatementsArtistsArtistIdStatementsGet**](docs/IngestionApi.md#liststatementsartistsartistidstatementsget) | **GET** /artists/{artist_id}/statements | List Statements
*IngestionApi* | [**regionalGlobalStatusArtistsArtistIdConnectRegionalGlobalStatusGet**](docs/IngestionApi.md#regionalglobalstatusartistsartistidconnectregionalglobalstatusget) | **GET** /artists/{artist_id}/connect/regional-global/status | Regional Global Status
*IngestionApi* | [**soundexchangeMlcStatusArtistsArtistIdConnectSoundexchangeMlcStatusGet**](docs/IngestionApi.md#soundexchangemlcstatusartistsartistidconnectsoundexchangemlcstatusget) | **GET** /artists/{artist_id}/connect/soundexchange-mlc/status | Soundexchange Mlc Status
*IngestionApi* | [**supportedFormatsIngestionSupportedFormatsGet**](docs/IngestionApi.md#supportedformatsingestionsupportedformatsget) | **GET** /ingestion/supported-formats | Supported Formats
*IngestionApi* | [**uploadStatementArtistsArtistIdStatementsUploadPost**](docs/IngestionApi.md#uploadstatementartistsartistidstatementsuploadpost) | **POST** /artists/{artist_id}/statements/upload | Upload Statement
*IngestionApi* | [**uploadStatementBatchArtistsArtistIdStatementsUploadBatchPost**](docs/IngestionApi.md#uploadstatementbatchartistsartistidstatementsuploadbatchpost) | **POST** /artists/{artist_id}/statements/upload-batch | Upload Statement Batch
*IntelligenceApi* | [**catalogValuationArtistsArtistIdMlCatalogValuationPost**](docs/IntelligenceApi.md#catalogvaluationartistsartistidmlcatalogvaluationpost) | **POST** /artists/{artist_id}/ml/catalog-valuation | Catalog Valuation
*IntelligenceApi* | [**createOutcomeFeedbackArtistsArtistIdIntelligenceFeedbackPost**](docs/IntelligenceApi.md#createoutcomefeedbackartistsartistidintelligencefeedbackpost) | **POST** /artists/{artist_id}/intelligence/feedback | Create Outcome Feedback
*IntelligenceApi* | [**extractContractTermsArtistsArtistIdIntelligenceContractsExtractPost**](docs/IntelligenceApi.md#extractcontracttermsartistsartistidintelligencecontractsextractpost) | **POST** /artists/{artist_id}/intelligence/contracts/extract | Extract Contract Terms
*IntelligenceApi* | [**extractContractTermsUploadArtistsArtistIdIntelligenceContractsExtractUploadPost**](docs/IntelligenceApi.md#extractcontracttermsuploadartistsartistidintelligencecontractsextractuploadpost) | **POST** /artists/{artist_id}/intelligence/contracts/extract-upload | Extract Contract Terms Upload
*IntelligenceApi* | [**financingMatchesArtistsArtistIdMlFinancingMatchesPost**](docs/IntelligenceApi.md#financingmatchesartistsartistidmlfinancingmatchespost) | **POST** /artists/{artist_id}/ml/financing-matches | Financing Matches
*IntelligenceApi* | [**getCalibrationHealthArtistsArtistIdIntelligenceCalibrationGet**](docs/IntelligenceApi.md#getcalibrationhealthartistsartistidintelligencecalibrationget) | **GET** /artists/{artist_id}/intelligence/calibration | Get Calibration Health
*IntelligenceApi* | [**ingestRoyaltyLedgerArtistsArtistIdIntelligenceLedgerIngestPost**](docs/IntelligenceApi.md#ingestroyaltyledgerartistsartistidintelligenceledgeringestpost) | **POST** /artists/{artist_id}/intelligence/ledger/ingest | Ingest Royalty Ledger
*IntelligenceApi* | [**listFeedbackEventsArtistsArtistIdIntelligenceFeedbackEventsGet**](docs/IntelligenceApi.md#listfeedbackeventsartistsartistidintelligencefeedbackeventsget) | **GET** /artists/{artist_id}/intelligence/feedback/events | List Feedback Events
*IntelligenceApi* | [**preSignatureContractReviewArtistsArtistIdIntelligenceContractsPreSignatureReviewPost**](docs/IntelligenceApi.md#presignaturecontractreviewartistsartistidintelligencecontractspresignaturereviewpost) | **POST** /artists/{artist_id}/intelligence/contracts/pre-signature-review | Pre Signature Contract Review
*IntelligenceApi* | [**rankByExpectedUtilityArtistsArtistIdIntelligenceRankUtilityPost**](docs/IntelligenceApi.md#rankbyexpectedutilityartistsartistidintelligencerankutilitypost) | **POST** /artists/{artist_id}/intelligence/rank-utility | Rank By Expected Utility
*IntelligenceApi* | [**registrationAutoFixArtistsArtistIdRegistrationAutoFixPost**](docs/IntelligenceApi.md#registrationautofixartistsartistidregistrationautofixpost) | **POST** /artists/{artist_id}/registration/auto-fix | Registration Auto Fix
*IntelligenceApi* | [**registrationStatusArtistsArtistIdRegistrationStatusGet**](docs/IntelligenceApi.md#registrationstatusartistsartistidregistrationstatusget) | **GET** /artists/{artist_id}/registration/status | Registration Status
*IntelligenceApi* | [**runCatalogAuditOnDemandArtistsArtistIdMlCatalogAuditPost**](docs/IntelligenceApi.md#runcatalogauditondemandartistsartistidmlcatalogauditpost) | **POST** /artists/{artist_id}/ml/catalog-audit | Run Catalog Audit On Demand
*IntelligenceApi* | [**runTaxOptimizerArtistsArtistIdIntelligenceTaxOptimizerPost**](docs/IntelligenceApi.md#runtaxoptimizerartistsartistidintelligencetaxoptimizerpost) | **POST** /artists/{artist_id}/intelligence/tax-optimizer | Run Tax Optimizer
*IntelligenceApi* | [**simulateExpectedPayoutArtistsArtistIdIntelligenceSimulateExpectedPayoutPost**](docs/IntelligenceApi.md#simulateexpectedpayoutartistsartistidintelligencesimulateexpectedpayoutpost) | **POST** /artists/{artist_id}/intelligence/simulate-expected-payout | Simulate Expected Payout
*IntelligenceApi* | [**simulateOptimizationArtistsArtistIdMlSimulateOptimizationPost**](docs/IntelligenceApi.md#simulateoptimizationartistsartistidmlsimulateoptimizationpost) | **POST** /artists/{artist_id}/ml/simulate-optimization | Simulate Optimization
*MessagesApi* | [**businessManagerChatArtistsArtistIdMessagesChatPost**](docs/MessagesApi.md#businessmanagerchatartistsartistidmessageschatpost) | **POST** /artists/{artist_id}/messages/chat | Business Manager Chat
*MessagesApi* | [**createWeeklyStoryArtistsArtistIdMessagesWeeklyStoryPost**](docs/MessagesApi.md#createweeklystoryartistsartistidmessagesweeklystorypost) | **POST** /artists/{artist_id}/messages/weekly-story | Create Weekly Story
*MessagesApi* | [**getFeedArtistsArtistIdMessagesFeedGet**](docs/MessagesApi.md#getfeedartistsartistidmessagesfeedget) | **GET** /artists/{artist_id}/messages/feed | Get Feed
*MlSuiteApi* | [**mlCalibrationDashboardArtistsArtistIdMlCalibrationDashboardGet**](docs/MlSuiteApi.md#mlcalibrationdashboardartistsartistidmlcalibrationdashboardget) | **GET** /artists/{artist_id}/ml/calibration-dashboard | Ml Calibration Dashboard
*MlSuiteApi* | [**mlExplainArtistsArtistIdMlExplainGet**](docs/MlSuiteApi.md#mlexplainartistsartistidmlexplainget) | **GET** /artists/{artist_id}/ml/explain | Ml Explain
*NotificationsApi* | [**dispatchNotificationsArtistsArtistIdNotificationsDispatchPost**](docs/NotificationsApi.md#dispatchnotificationsartistsartistidnotificationsdispatchpost) | **POST** /artists/{artist_id}/notifications/dispatch | Dispatch Notifications
*NotificationsApi* | [**pushRegisterArtistsArtistIdNotificationsPushRegisterPost**](docs/NotificationsApi.md#pushregisterartistsartistidnotificationspushregisterpost) | **POST** /artists/{artist_id}/notifications/push-register | Push Register
*NotificationsApi* | [**setNotificationPreferencesArtistsArtistIdNotificationsPreferencesPost**](docs/NotificationsApi.md#setnotificationpreferencesartistsartistidnotificationspreferencespost) | **POST** /artists/{artist_id}/notifications/preferences | Set Notification Preferences
*NotificationsApi* | [**voiceQueryArtistsArtistIdNotificationsVoiceQueryPost**](docs/NotificationsApi.md#voicequeryartistsartistidnotificationsvoicequerypost) | **POST** /artists/{artist_id}/notifications/voice-query | Voice Query
*OnboardingApi* | [**applySplitRepairsArtistsArtistIdSplitsRepairPost**](docs/OnboardingApi.md#applysplitrepairsartistsartistidsplitsrepairpost) | **POST** /artists/{artist_id}/splits/repair | Apply Split Repairs
*OnboardingApi* | [**buildCatalogWorkGraphArtistsArtistIdCatalogGraphBuildPost**](docs/OnboardingApi.md#buildcatalogworkgraphartistsartistidcataloggraphbuildpost) | **POST** /artists/{artist_id}/catalog/graph/build | Build Catalog Work Graph
*OnboardingApi* | [**catalogMetadataHealthArtistsArtistIdCatalogMetadataHealthGet**](docs/OnboardingApi.md#catalogmetadatahealthartistsartistidcatalogmetadatahealthget) | **GET** /artists/{artist_id}/catalog/metadata-health | Catalog Metadata Health
*OnboardingApi* | [**catalogRepairsArtistsArtistIdCatalogRepairsGet**](docs/OnboardingApi.md#catalogrepairsartistsartistidcatalogrepairsget) | **GET** /artists/{artist_id}/catalog/repairs | Catalog Repairs
*OnboardingApi* | [**confirmCatalogItemArtistsArtistIdCatalogConfirmPost**](docs/OnboardingApi.md#confirmcatalogitemartistsartistidcatalogconfirmpost) | **POST** /artists/{artist_id}/catalog/confirm | Confirm Catalog Item
*OnboardingApi* | [**createSyncJobArtistsArtistIdSyncJobsPost**](docs/OnboardingApi.md#createsyncjobartistsartistidsyncjobspost) | **POST** /artists/{artist_id}/sync/jobs | Create Sync Job
*OnboardingApi* | [**generateAuditEvidencePacketClaimsClaimIdEvidenceGenerateAuditPost**](docs/OnboardingApi.md#generateauditevidencepacketclaimsclaimidevidencegenerateauditpost) | **POST** /claims/{claim_id}/evidence/generate-audit | Generate Audit Evidence Packet
*OnboardingApi* | [**getPermissionsDashboardUiPermissionsUiGet**](docs/OnboardingApi.md#getpermissionsdashboarduipermissionsuiget) | **GET** /permissions/ui | Get Permissions Dashboard Ui
*OnboardingApi* | [**getSyncJobArtistsArtistIdSyncJobsJobIdGet**](docs/OnboardingApi.md#getsyncjobartistsartistidsyncjobsjobidget) | **GET** /artists/{artist_id}/sync/jobs/{job_id} | Get Sync Job
*OnboardingApi* | [**inferCatalogArtistsArtistIdCatalogInferPost**](docs/OnboardingApi.md#infercatalogartistsartistidcataloginferpost) | **POST** /artists/{artist_id}/catalog/infer | Infer Catalog
*OnboardingApi* | [**listCatalogConfirmationsArtistsArtistIdCatalogConfirmGet**](docs/OnboardingApi.md#listcatalogconfirmationsartistsartistidcatalogconfirmget) | **GET** /artists/{artist_id}/catalog/confirm | List Catalog Confirmations
*OnboardingApi* | [**listImmutableLedgerEntriesArtistsArtistIdLedgerImmutableGet**](docs/OnboardingApi.md#listimmutableledgerentriesartistsartistidledgerimmutableget) | **GET** /artists/{artist_id}/ledger/immutable | List Immutable Ledger Entries
*OnboardingApi* | [**listParserPluginsArtistsArtistIdParsersPluginsGet**](docs/OnboardingApi.md#listparserpluginsartistsartistidparserspluginsget) | **GET** /artists/{artist_id}/parsers/plugins | List Parser Plugins
*OnboardingApi* | [**listSyncJobsArtistsArtistIdSyncJobsGet**](docs/OnboardingApi.md#listsyncjobsartistsartistidsyncjobsget) | **GET** /artists/{artist_id}/sync/jobs | List Sync Jobs
*OnboardingApi* | [**missingDataStatusArtistsArtistIdIngestionMissingDataGet**](docs/OnboardingApi.md#missingdatastatusartistsartistidingestionmissingdataget) | **GET** /artists/{artist_id}/ingestion/missing-data | Missing Data Status
*OnboardingApi* | [**onboardingAutoArtistsArtistIdOnboardingAutoPost**](docs/OnboardingApi.md#onboardingautoartistsartistidonboardingautopost) | **POST** /artists/{artist_id}/onboarding/auto | Onboarding Auto
*OnboardingApi* | [**onboardingStatusArtistsArtistIdOnboardingStatusGet**](docs/OnboardingApi.md#onboardingstatusartistsartistidonboardingstatusget) | **GET** /artists/{artist_id}/onboarding/status | Onboarding Status
*OnboardingApi* | [**parseStatementWithEngineArtistsArtistIdParsersParserTypePost**](docs/OnboardingApi.md#parsestatementwithengineartistsartistidparsersparsertypepost) | **POST** /artists/{artist_id}/parsers/{parser_type} | Parse Statement With Engine
*OnboardingApi* | [**permissionsDashboardArtistsArtistIdConnectPermissionsDashboardGet**](docs/OnboardingApi.md#permissionsdashboardartistsartistidconnectpermissionsdashboardget) | **GET** /artists/{artist_id}/connect/permissions-dashboard | Permissions Dashboard
*OnboardingApi* | [**previewFullWorkflowArtistsArtistIdWorkflowPreviewGet**](docs/OnboardingApi.md#previewfullworkflowartistsartistidworkflowpreviewget) | **GET** /artists/{artist_id}/workflow/preview | Preview Full Workflow
*OnboardingApi* | [**requeueDueSyncJobsArtistsArtistIdSyncJobsRequeueDuePost**](docs/OnboardingApi.md#requeueduesyncjobsartistsartistidsyncjobsrequeueduepost) | **POST** /artists/{artist_id}/sync/jobs/requeue-due | Requeue Due Sync Jobs
*OnboardingApi* | [**runDataFetcherArtistsArtistIdFetchersIntegrationPost**](docs/OnboardingApi.md#rundatafetcherartistsartistidfetchersintegrationpost) | **POST** /artists/{artist_id}/fetchers/{integration} | Run Data Fetcher
*OnboardingApi* | [**runFullWorkflowArtistsArtistIdWorkflowRunPost**](docs/OnboardingApi.md#runfullworkflowartistsartistidworkflowrunpost) | **POST** /artists/{artist_id}/workflow/run | Run Full Workflow
*OnboardingApi* | [**runRecoveryAutomationArtistsArtistIdRecoveryAutomatePost**](docs/OnboardingApi.md#runrecoveryautomationartistsartistidrecoveryautomatepost) | **POST** /artists/{artist_id}/recovery/automate | Run Recovery Automation
*OnboardingApi* | [**runSyncJobNowArtistsArtistIdSyncJobsJobIdRunPost**](docs/OnboardingApi.md#runsyncjobnowartistsartistidsyncjobsjobidrunpost) | **POST** /artists/{artist_id}/sync/jobs/{job_id}/run | Run Sync Job Now
*OnboardingApi* | [**uploadAnyStatementArtistsArtistIdIngestionUploadAnyPost**](docs/OnboardingApi.md#uploadanystatementartistsartistidingestionuploadanypost) | **POST** /artists/{artist_id}/ingestion/upload-any | Upload Any Statement
*OnboardingApi* | [**upsertParserPluginArtistsArtistIdParsersPluginsPut**](docs/OnboardingApi.md#upsertparserpluginartistsartistidparserspluginsput) | **PUT** /artists/{artist_id}/parsers/plugins | Upsert Parser Plugin
*OnboardingApi* | [**varianceScanArtistsArtistIdVarianceScanPost**](docs/OnboardingApi.md#variancescanartistsartistidvariancescanpost) | **POST** /artists/{artist_id}/variance/scan | Variance Scan
*PayersApi* | [**payerBehaviorPayersPayerIdBehaviorGet**](docs/PayersApi.md#payerbehaviorpayerspayeridbehaviorget) | **GET** /payers/{payer_id}/behavior | Payer Behavior
*PayersApi* | [**payerRiskPayersPayerIdRiskGet**](docs/PayersApi.md#payerriskpayerspayeridriskget) | **GET** /payers/{payer_id}/risk | Payer Risk
*PublicApi* | [**advocacyKitArtistsArtistIdAdvocacyKitPost**](docs/PublicApi.md#advocacykitartistsartistidadvocacykitpost) | **POST** /artists/{artist_id}/advocacy/kit | Advocacy Kit
*PublicApi* | [**publicAggregatesStatsPublicAggregatesGet**](docs/PublicApi.md#publicaggregatesstatspublicaggregatesget) | **GET** /stats/public/aggregates | Public Aggregates
*PublicApi* | [**publicLeaderboardStatsPublicLeaderboardGet**](docs/PublicApi.md#publicleaderboardstatspublicleaderboardget) | **GET** /stats/public/leaderboard | Public Leaderboard
*PublicApi* | [**publicSuccessStoriesStatsPublicSuccessStoriesGet**](docs/PublicApi.md#publicsuccessstoriesstatspublicsuccessstoriesget) | **GET** /stats/public/success-stories | Public Success Stories
*RecoveryApi* | [**artistBenchmarkingArtistsArtistIdBenchmarkingGet**](docs/RecoveryApi.md#artistbenchmarkingartistsartistidbenchmarkingget) | **GET** /artists/{artist_id}/benchmarking | Artist Benchmarking
*RecoveryApi* | [**auditEligibilityArtistsArtistIdRecoveryAuditEligibilityGet**](docs/RecoveryApi.md#auditeligibilityartistsartistidrecoveryauditeligibilityget) | **GET** /artists/{artist_id}/recovery/audit-eligibility | Audit Eligibility
*RecoveryApi* | [**catalogIntegrityArtistsArtistIdCatalogIntegrityGet**](docs/RecoveryApi.md#catalogintegrityartistsartistidcatalogintegrityget) | **GET** /artists/{artist_id}/catalog/integrity | Catalog Integrity
*RecoveryApi* | [**deadlineRiskArtistsArtistIdRecoveryDeadlineRiskGet**](docs/RecoveryApi.md#deadlineriskartistsartistidrecoverydeadlineriskget) | **GET** /artists/{artist_id}/recovery/deadline-risk | Deadline Risk
*RecoveryApi* | [**edmFestivalAuditArtistsArtistIdRecoveryEdmFestivalAuditPost**](docs/RecoveryApi.md#edmfestivalauditartistsartistidrecoveryedmfestivalauditpost) | **POST** /artists/{artist_id}/recovery/edm-festival-audit | Edm Festival Audit
*RecoveryApi* | [**fraudScanArtistsArtistIdFraudScanPost**](docs/RecoveryApi.md#fraudscanartistsartistidfraudscanpost) | **POST** /artists/{artist_id}/fraud-scan | Fraud Scan
*RecoveryApi* | [**hiphopBrandAuditArtistsArtistIdRecoveryHiphopBrandAuditPost**](docs/RecoveryApi.md#hiphopbrandauditartistsartistidrecoveryhiphopbrandauditpost) | **POST** /artists/{artist_id}/recovery/hiphop-brand-audit | Hiphop Brand Audit
*RecoveryApi* | [**playbookSummaryArtistsArtistIdRecoveryPlaybookSummaryGet**](docs/RecoveryApi.md#playbooksummaryartistsartistidrecoveryplaybooksummaryget) | **GET** /artists/{artist_id}/recovery/playbook-summary | Playbook Summary
*RecoveryApi* | [**pooledClaimArtistsArtistIdNetworkPooledClaimPost**](docs/RecoveryApi.md#pooledclaimartistsartistidnetworkpooledclaimpost) | **POST** /artists/{artist_id}/network/pooled-claim | Pooled Claim
*RecoveryApi* | [**priorityQueueArtistsArtistIdRecoveryPriorityQueueGet**](docs/RecoveryApi.md#priorityqueueartistsartistidrecoverypriorityqueueget) | **GET** /artists/{artist_id}/recovery/priority-queue | Priority Queue
*RecoveryApi* | [**rateBenchmarkAdvancedArtistsArtistIdRecoveryRateBenchmarkAdvancedGet**](docs/RecoveryApi.md#ratebenchmarkadvancedartistsartistidrecoveryratebenchmarkadvancedget) | **GET** /artists/{artist_id}/recovery/rate-benchmark-advanced | Rate Benchmark Advanced
*RecoveryApi* | [**rateBenchmarkArtistsArtistIdRecoveryRateBenchmarkGet**](docs/RecoveryApi.md#ratebenchmarkartistsartistidrecoveryratebenchmarkget) | **GET** /artists/{artist_id}/recovery/rate-benchmark | Rate Benchmark
*RecoveryApi* | [**reconstructHistoricalArtistsArtistIdRecoveryReconstructHistoricalPost**](docs/RecoveryApi.md#reconstructhistoricalartistsartistidrecoveryreconstructhistoricalpost) | **POST** /artists/{artist_id}/recovery/reconstruct-historical | Reconstruct Historical
*RecoveryApi* | [**recoupmentArtistsArtistIdRecoveryRecoupmentGet**](docs/RecoveryApi.md#recoupmentartistsartistidrecoveryrecoupmentget) | **GET** /artists/{artist_id}/recovery/recoupment | Recoupment
*RecoveryApi* | [**recoupmentDeepAuditArtistsArtistIdRecoveryRecoupmentDeepAuditGet**](docs/RecoveryApi.md#recoupmentdeepauditartistsartistidrecoveryrecoupmentdeepauditget) | **GET** /artists/{artist_id}/recovery/recoupment-deep-audit | Recoupment Deep Audit
*RecoveryApi* | [**recoveryAttributionArtistsArtistIdRecoveryAttributionGet**](docs/RecoveryApi.md#recoveryattributionartistsartistidrecoveryattributionget) | **GET** /artists/{artist_id}/recovery/attribution | Recovery Attribution
*RecoveryApi* | [**recoveryExpectedValueArtistsArtistIdRecoveryExpectedValueGet**](docs/RecoveryApi.md#recoveryexpectedvalueartistsartistidrecoveryexpectedvalueget) | **GET** /artists/{artist_id}/recovery/expected-value | Recovery Expected Value
*RecoveryApi* | [**recoveryFunnelArtistsArtistIdRecoveryFunnelGet**](docs/RecoveryApi.md#recoveryfunnelartistsartistidrecoveryfunnelget) | **GET** /artists/{artist_id}/recovery/funnel | Recovery Funnel
*RecoveryApi* | [**recoveryPlaybookArtistsArtistIdRecoveryPlaybookGet**](docs/RecoveryApi.md#recoveryplaybookartistsartistidrecoveryplaybookget) | **GET** /artists/{artist_id}/recovery/playbook | Recovery Playbook
*RecoveryApi* | [**recoveryRoiArtistsArtistIdRecoveryRoiGet**](docs/RecoveryApi.md#recoveryroiartistsartistidrecoveryroiget) | **GET** /artists/{artist_id}/recovery/roi | Recovery Roi
*RecoveryApi* | [**runRecoveryAutopilotArtistsArtistIdRecoveryAutoPost**](docs/RecoveryApi.md#runrecoveryautopilotartistsartistidrecoveryautopost) | **POST** /artists/{artist_id}/recovery/auto | Run Recovery Autopilot
*RecoveryApi* | [**slaStatusArtistsArtistIdSlaStatusGet**](docs/RecoveryApi.md#slastatusartistsartistidslastatusget) | **GET** /artists/{artist_id}/sla/status | Sla Status
*RecoveryApi* | [**solStatusArtistsArtistIdRecoverySolStatusGet**](docs/RecoveryApi.md#solstatusartistsartistidrecoverysolstatusget) | **GET** /artists/{artist_id}/recovery/sol-status | Sol Status
*RecoveryApi* | [**splitConflictsArtistsArtistIdSplitsConflictsGet**](docs/RecoveryApi.md#splitconflictsartistsartistidsplitsconflictsget) | **GET** /artists/{artist_id}/splits/conflicts | Split Conflicts
*RecoveryApi* | [**splitVerificationArtistsArtistIdSplitsVerificationGet**](docs/RecoveryApi.md#splitverificationartistsartistidsplitsverificationget) | **GET** /artists/{artist_id}/splits/verification | Split Verification
*RecoveryApi* | [**touringAuditArtistsArtistIdRecoveryTouringAuditPost**](docs/RecoveryApi.md#touringauditartistsartistidrecoverytouringauditpost) | **POST** /artists/{artist_id}/recovery/touring-audit | Touring Audit
*RecoveryApi* | [**ugcAutoClaimArtistsArtistIdRecoveryUgcAutoClaimPost**](docs/RecoveryApi.md#ugcautoclaimartistsartistidrecoveryugcautoclaimpost) | **POST** /artists/{artist_id}/recovery/ugc-auto-claim | Ugc Auto Claim
*RecoveryApi* | [**ugcClaimArtistsArtistIdUgcClaimPost**](docs/RecoveryApi.md#ugcclaimartistsartistidugcclaimpost) | **POST** /artists/{artist_id}/ugc/claim | Ugc Claim
*RecoveryApi* | [**ugcGlobalScanArtistsArtistIdUgcGlobalScanPost**](docs/RecoveryApi.md#ugcglobalscanartistsartistidugcglobalscanpost) | **POST** /artists/{artist_id}/ugc/global-scan | Ugc Global Scan
*RecoveryApi* | [**ugcMonitorArtistsArtistIdUgcMonitorGet**](docs/RecoveryApi.md#ugcmonitorartistsartistidugcmonitorget) | **GET** /artists/{artist_id}/ugc/monitor | Ugc Monitor
*RecoveryApi* | [**underpaymentHeatmapArtistsArtistIdRecoveryHeatmapGet**](docs/RecoveryApi.md#underpaymentheatmapartistsartistidrecoveryheatmapget) | **GET** /artists/{artist_id}/recovery/heatmap | Underpayment Heatmap
*RecoveryIntelligenceLLMApi* | [**llmDemandLetterArtistsArtistIdLlmDemandLetterPost**](docs/RecoveryIntelligenceLLMApi.md#llmdemandletterartistsartistidllmdemandletterpost) | **POST** /artists/{artist_id}/llm/demand-letter | Llm Demand Letter
*RecoveryIntelligenceLLMApi* | [**llmNegotiationScriptArtistsArtistIdLlmNegotiationScriptPost**](docs/RecoveryIntelligenceLLMApi.md#llmnegotiationscriptartistsartistidllmnegotiationscriptpost) | **POST** /artists/{artist_id}/llm/negotiation-script | Llm Negotiation Script
*RecoveryIntelligenceLLMApi* | [**llmPersonalizedAdviceArtistsArtistIdLlmAdvicePost**](docs/RecoveryIntelligenceLLMApi.md#llmpersonalizedadviceartistsartistidllmadvicepost) | **POST** /artists/{artist_id}/llm/advice | Llm Personalized Advice
*ReferralsApi* | [**getReferralsArtistsArtistIdReferralsGet**](docs/ReferralsApi.md#getreferralsartistsartistidreferralsget) | **GET** /artists/{artist_id}/referrals | Get Referrals
*ReferralsApi* | [**registerReferralArtistsArtistIdReferralsPost**](docs/ReferralsApi.md#registerreferralartistsartistidreferralspost) | **POST** /artists/{artist_id}/referrals | Register Referral
*ReviewQueueApi* | [**assignReviewItemReviewQueueItemsItemIdAssignPost**](docs/ReviewQueueApi.md#assignreviewitemreviewqueueitemsitemidassignpost) | **POST** /review-queue/items/{item_id}/assign | Assign Review Item
*ReviewQueueApi* | [**checkThresholdReviewQueueThresholdCheckPost**](docs/ReviewQueueApi.md#checkthresholdreviewqueuethresholdcheckpost) | **POST** /review-queue/threshold-check | Check Threshold
*ReviewQueueApi* | [**createReviewItemReviewQueueItemsPost**](docs/ReviewQueueApi.md#createreviewitemreviewqueueitemspost) | **POST** /review-queue/items | Create Review Item
*ReviewQueueApi* | [**decideReviewItemReviewQueueItemsItemIdDecisionPost**](docs/ReviewQueueApi.md#decidereviewitemreviewqueueitemsitemiddecisionpost) | **POST** /review-queue/items/{item_id}/decision | Decide Review Item
*ReviewQueueApi* | [**listDecisionsReviewQueueDecisionsGet**](docs/ReviewQueueApi.md#listdecisionsreviewqueuedecisionsget) | **GET** /review-queue/decisions | List Decisions
*ReviewQueueApi* | [**listReviewItemsReviewQueueItemsGet**](docs/ReviewQueueApi.md#listreviewitemsreviewqueueitemsget) | **GET** /review-queue/items | List Review Items
*ReviewQueueApi* | [**reviewQueueMetricsReviewQueueMetricsGet**](docs/ReviewQueueApi.md#reviewqueuemetricsreviewqueuemetricsget) | **GET** /review-queue/metrics | Review Queue Metrics
*SovereigntyApi* | [**acceptAdvanceOfferArtistsArtistIdAdvanceAcceptPost**](docs/SovereigntyApi.md#acceptadvanceofferartistsartistidadvanceacceptpost) | **POST** /artists/{artist_id}/advance/accept | Accept Advance Offer
*SovereigntyApi* | [**createAdvanceOfferArtistsArtistIdAdvanceOfferPost**](docs/SovereigntyApi.md#createadvanceofferartistsartistidadvanceofferpost) | **POST** /artists/{artist_id}/advance/offer | Create Advance Offer
*SovereigntyApi* | [**listAdvanceHistoryArtistsArtistIdAdvanceHistoryGet**](docs/SovereigntyApi.md#listadvancehistoryartistsartistidadvancehistoryget) | **GET** /artists/{artist_id}/advance/history | List Advance History
*SovereigntyApi* | [**listRightsGapsArtistsArtistIdRightsGapsGet**](docs/SovereigntyApi.md#listrightsgapsartistsartistidrightsgapsget) | **GET** /artists/{artist_id}/rights/gaps | List Rights Gaps
*SovereigntyApi* | [**registerRightsPacketsArtistsArtistIdRightsRegisterPost**](docs/SovereigntyApi.md#registerrightspacketsartistsartistidrightsregisterpost) | **POST** /artists/{artist_id}/rights/register | Register Rights Packets
*SovereigntyApi* | [**scanRightsArtistsArtistIdRightsScanGet**](docs/SovereigntyApi.md#scanrightsartistsartistidrightsscanget) | **GET** /artists/{artist_id}/rights/scan | Scan Rights
*SupportApi* | [**supportActionArtistsArtistIdSupportActionPost**](docs/SupportApi.md#supportactionartistsartistidsupportactionpost) | **POST** /artists/{artist_id}/support/action | Support Action
*SupportApi* | [**supportChatArtistsArtistIdSupportChatPost**](docs/SupportApi.md#supportchatartistsartistidsupportchatpost) | **POST** /artists/{artist_id}/support/chat | Support Chat
*SupportApi* | [**supportHistoryArtistsArtistIdSupportHistoryGet**](docs/SupportApi.md#supporthistoryartistsartistidsupporthistoryget) | **GET** /artists/{artist_id}/support/history | Support History
*SupportApi* | [**supportSuggestionsArtistsArtistIdSupportSuggestionsGet**](docs/SupportApi.md#supportsuggestionsartistsartistidsupportsuggestionsget) | **GET** /artists/{artist_id}/support/suggestions | Support Suggestions
*TeamApi* | [**networkInviteArtistsArtistIdNetworkInvitePost**](docs/TeamApi.md#networkinviteartistsartistidnetworkinvitepost) | **POST** /artists/{artist_id}/network/invite | Network Invite
*TermsApi* | [**acceptTermsArtistsArtistIdTermsAcceptPost**](docs/TermsApi.md#accepttermsartistsartistidtermsacceptpost) | **POST** /artists/{artist_id}/terms/accept | Accept Terms
*TermsApi* | [**getTermsTermsGet**](docs/TermsApi.md#gettermstermsget) | **GET** /terms | Get Terms
*TermsApi* | [**termsStatusArtistsArtistIdTermsStatusGet**](docs/TermsApi.md#termsstatusartistsartistidtermsstatusget) | **GET** /artists/{artist_id}/terms/status | Terms Status
*TransparencyApi* | [**explainAnomalyArtistsArtistIdAnomaliesAnomalyIdExplainGet**](docs/TransparencyApi.md#explainanomalyartistsartistidanomaliesanomalyidexplainget) | **GET** /artists/{artist_id}/anomalies/{anomaly_id}/explain | Explain Anomaly
*TransparencyApi* | [**fullLedgerArtistsArtistIdLedgerFullGet**](docs/TransparencyApi.md#fullledgerartistsartistidledgerfullget) | **GET** /artists/{artist_id}/ledger/full | Full Ledger
*TrolleyApi* | [**createTrolleyRecipientArtistsArtistIdTrolleyRecipientPost**](docs/TrolleyApi.md#createtrolleyrecipientartistsartistidtrolleyrecipientpost) | **POST** /artists/{artist_id}/trolley/recipient | Create Trolley Recipient
*TrolleyApi* | [**disburseClaimClaimsClaimIdDisbursePost**](docs/TrolleyApi.md#disburseclaimclaimsclaimiddisbursepost) | **POST** /claims/{claim_id}/disburse | Disburse Claim
*TrolleyApi* | [**getTrolleyStatusArtistsArtistIdTrolleyStatusGet**](docs/TrolleyApi.md#gettrolleystatusartistsartistidtrolleystatusget) | **GET** /artists/{artist_id}/trolley/status | Get Trolley Status
*TrolleyApi* | [**getTrolleyWidgetUrlArtistsArtistIdTrolleyWidgetUrlGet**](docs/TrolleyApi.md#gettrolleywidgeturlartistsartistidtrolleywidgeturlget) | **GET** /artists/{artist_id}/trolley/widget-url | Get Trolley Widget Url
*TrolleyApi* | [**manualRemittanceArtistsArtistIdClaimsClaimIdManualRemittancePost**](docs/TrolleyApi.md#manualremittanceartistsartistidclaimsclaimidmanualremittancepost) | **POST** /artists/{artist_id}/claims/{claim_id}/manual-remittance | Manual Remittance
*TrolleyApi* | [**trolleyWebhookWebhooksTrolleyPost**](docs/TrolleyApi.md#trolleywebhookwebhookstrolleypost) | **POST** /webhooks/trolley | Trolley Webhook
*TrustApi* | [**getTrustTraceArtistsArtistIdTrustTraceGet**](docs/TrustApi.md#gettrusttraceartistsartistidtrusttraceget) | **GET** /artists/{artist_id}/trust/trace | Get Trust Trace
*WidgetApi* | [**claimWidgetClaimPost**](docs/WidgetApi.md#claimwidgetclaimpost) | **POST** /widget/claim | Claim
*WidgetApi* | [**estimateWidgetEstimatePost**](docs/WidgetApi.md#estimatewidgetestimatepost) | **POST** /widget/estimate | Estimate
*WidgetApi* | [**listLeadsWidgetLeadsGet**](docs/WidgetApi.md#listleadswidgetleadsget) | **GET** /widget/leads | List Leads
*WidgetApi* | [**registerWidgetRegisterPost**](docs/WidgetApi.md#registerwidgetregisterpost) | **POST** /widget/register | Register
*WidgetApi* | [**verifyWidgetVerifyPost**](docs/WidgetApi.md#verifywidgetverifypost) | **POST** /widget/verify | Verify
*WorkflowApi* | [**runFullAutonomousWorkflowArtistsArtistIdWorkflowRunFullAutonomousPost**](docs/WorkflowApi.md#runfullautonomousworkflowartistsartistidworkflowrunfullautonomouspost) | **POST** /artists/{artist_id}/workflow/run-full-autonomous | Run Full Autonomous Workflow
*WorkflowApi* | [**workflowRunStatusArtistsArtistIdWorkflowRunsRunIdGet**](docs/WorkflowApi.md#workflowrunstatusartistsartistidworkflowrunsrunidget) | **GET** /artists/{artist_id}/workflow/runs/{run_id} | Workflow Run Status
*WorkspaceApi* | [**workspaceArtistsWorkspaceArtistsGet**](docs/WorkspaceApi.md#workspaceartistsworkspaceartistsget) | **GET** /workspace/artists | Workspace Artists
*WorkspaceApi* | [**workspaceClaimsWorkspaceClaimsGet**](docs/WorkspaceApi.md#workspaceclaimsworkspaceclaimsget) | **GET** /workspace/claims | Workspace Claims
*WorkspaceApi* | [**workspaceDeadlinesWorkspaceDeadlinesGet**](docs/WorkspaceApi.md#workspacedeadlinesworkspacedeadlinesget) | **GET** /workspace/deadlines | Workspace Deadlines
*WorkspaceApi* | [**workspaceOverviewWorkspaceOverviewGet**](docs/WorkspaceApi.md#workspaceoverviewworkspaceoverviewget) | **GET** /workspace/overview | Workspace Overview
*Xr7ForensicsApi* | [**getGapReportArtistsArtistIdXr7ReconciliationGapsGet**](docs/Xr7ForensicsApi.md#getgapreportartistsartistidxr7reconciliationgapsget) | **GET** /artists/{artist_id}/xr7/reconciliation/gaps | Get Gap Report
*Xr7ForensicsApi* | [**queueApiIngestionArtistsArtistIdXr7QueueApiIngestionPost**](docs/Xr7ForensicsApi.md#queueapiingestionartistsartistidxr7queueapiingestionpost) | **POST** /artists/{artist_id}/xr7/queue/api-ingestion | Queue Api Ingestion
*Xr7ForensicsApi* | [**queueBlackBoxArtistsArtistIdXr7QueueBlackBoxDetectionPost**](docs/Xr7ForensicsApi.md#queueblackboxartistsartistidxr7queueblackboxdetectionpost) | **POST** /artists/{artist_id}/xr7/queue/black-box-detection | Queue Black Box
*Xr7ForensicsApi* | [**queueFileIngestionArtistsArtistIdXr7QueueFileIngestionPost**](docs/Xr7ForensicsApi.md#queuefileingestionartistsartistidxr7queuefileingestionpost) | **POST** /artists/{artist_id}/xr7/queue/file-ingestion | Queue File Ingestion
*Xr7ForensicsApi* | [**queueFingerprintingArtistsArtistIdXr7QueueFingerprintingPost**](docs/Xr7ForensicsApi.md#queuefingerprintingartistsartistidxr7queuefingerprintingpost) | **POST** /artists/{artist_id}/xr7/queue/fingerprinting | Queue Fingerprinting
*Xr7ForensicsApi* | [**queueReconciliationArtistsArtistIdXr7QueueReconciliationPost**](docs/Xr7ForensicsApi.md#queuereconciliationartistsartistidxr7queuereconciliationpost) | **POST** /artists/{artist_id}/xr7/queue/reconciliation | Queue Reconciliation
*Xr7ForensicsApi* | [**runApiIngestionArtistsArtistIdXr7PipelinesApiIngestionPost**](docs/Xr7ForensicsApi.md#runapiingestionartistsartistidxr7pipelinesapiingestionpost) | **POST** /artists/{artist_id}/xr7/pipelines/api-ingestion | Run Api Ingestion
*Xr7ForensicsApi* | [**runBlackBoxArtistsArtistIdXr7PipelinesBlackBoxDetectionPost**](docs/Xr7ForensicsApi.md#runblackboxartistsartistidxr7pipelinesblackboxdetectionpost) | **POST** /artists/{artist_id}/xr7/pipelines/black-box-detection | Run Black Box
*Xr7ForensicsApi* | [**runFileIngestionArtistsArtistIdXr7PipelinesFileIngestionPost**](docs/Xr7ForensicsApi.md#runfileingestionartistsartistidxr7pipelinesfileingestionpost) | **POST** /artists/{artist_id}/xr7/pipelines/file-ingestion | Run File Ingestion
*Xr7ForensicsApi* | [**runFingerprintingArtistsArtistIdXr7PipelinesFingerprintingPost**](docs/Xr7ForensicsApi.md#runfingerprintingartistsartistidxr7pipelinesfingerprintingpost) | **POST** /artists/{artist_id}/xr7/pipelines/fingerprinting | Run Fingerprinting
*Xr7ForensicsApi* | [**runReconciliationArtistsArtistIdXr7PipelinesReconciliationPost**](docs/Xr7ForensicsApi.md#runreconciliationartistsartistidxr7pipelinesreconciliationpost) | **POST** /artists/{artist_id}/xr7/pipelines/reconciliation | Run Reconciliation
*Xr7ForensicsApi* | [**upsertXr7CredentialsArtistsArtistIdXr7CredentialsPost**](docs/Xr7ForensicsApi.md#upsertxr7credentialsartistsartistidxr7credentialspost) | **POST** /artists/{artist_id}/xr7/credentials | Upsert Xr7 Credentials
*Xr7MetadataApi* | [**applyRepairsArtistsArtistIdXr7MetadataRepairApplyPost**](docs/Xr7MetadataApi.md#applyrepairsartistsartistidxr7metadatarepairapplypost) | **POST** /artists/{artist_id}/xr7/metadata/repair/apply | Apply Repairs
*Xr7MetadataApi* | [**suggestRepairsArtistsArtistIdXr7MetadataRepairSuggestPost**](docs/Xr7MetadataApi.md#suggestrepairsartistsartistidxr7metadatarepairsuggestpost) | **POST** /artists/{artist_id}/xr7/metadata/repair/suggest | Suggest Repairs
*Xr7UgcApi* | [**ingestSignalsArtistsArtistIdXr7UgcSignalsIngestPost**](docs/Xr7UgcApi.md#ingestsignalsartistsartistidxr7ugcsignalsingestpost) | **POST** /artists/{artist_id}/xr7/ugc/signals/ingest | Ingest Signals
*Xr7UgcApi* | [**ugcOpportunitiesArtistsArtistIdXr7UgcOpportunitiesGet**](docs/Xr7UgcApi.md#ugcopportunitiesartistsartistidxr7ugcopportunitiesget) | **GET** /artists/{artist_id}/xr7/ugc/opportunities | Ugc Opportunities
*Xr7ValuationApi* | [**catalogHealthArtistsArtistIdXr7CatalogHealthGet**](docs/Xr7ValuationApi.md#cataloghealthartistsartistidxr7cataloghealthget) | **GET** /artists/{artist_id}/xr7/catalog/health | Catalog Health
*Xr7ValuationApi* | [**recoveryForecastArtistsArtistIdXr7ForecastRecoveryPost**](docs/Xr7ValuationApi.md#recoveryforecastartistsartistidxr7forecastrecoverypost) | **POST** /artists/{artist_id}/xr7/forecast/recovery | Recovery Forecast
*Xr7ValuationApi* | [**simulationArtistsArtistIdXr7SimulationsWhatIfPost**](docs/Xr7ValuationApi.md#simulationartistsartistidxr7simulationswhatifpost) | **POST** /artists/{artist_id}/xr7/simulations/what-if | Simulation
*Xr7ValuationApi* | [**valuationSnapshotArtistsArtistIdXr7ValuationSnapshotGet**](docs/Xr7ValuationApi.md#valuationsnapshotartistsartistidxr7valuationsnapshotget) | **GET** /artists/{artist_id}/xr7/valuation/snapshot | Valuation Snapshot


### Models

- [APIIngestionRequest](docs/APIIngestionRequest.md)
- [AdminAuditLogSchema](docs/AdminAuditLogSchema.md)
- [AdminLoginRequest](docs/AdminLoginRequest.md)
- [AdvanceAcceptRequest](docs/AdvanceAcceptRequest.md)
- [AdvanceOfferRequest](docs/AdvanceOfferRequest.md)
- [AdviceRequest](docs/AdviceRequest.md)
- [AdviceResponse](docs/AdviceResponse.md)
- [AnomalyCategory](docs/AnomalyCategory.md)
- [AnomalySchema](docs/AnomalySchema.md)
- [AnomalySeverity](docs/AnomalySeverity.md)
- [AnomalyStatus](docs/AnomalyStatus.md)
- [ApprovalRequest](docs/ApprovalRequest.md)
- [ArtistCreate](docs/ArtistCreate.md)
- [ArtistIdentityMatchSchema](docs/ArtistIdentityMatchSchema.md)
- [ArtistLifecycleStatus](docs/ArtistLifecycleStatus.md)
- [ArtistLoginRequest](docs/ArtistLoginRequest.md)
- [ArtistPreferenceUpdateRequest](docs/ArtistPreferenceUpdateRequest.md)
- [ArtistSchema](docs/ArtistSchema.md)
- [AssignReviewItemRequest](docs/AssignReviewItemRequest.md)
- [AttorneyEvidenceRequest](docs/AttorneyEvidenceRequest.md)
- [AuthConnectResponse](docs/AuthConnectResponse.md)
- [BlackBoxRequest](docs/BlackBoxRequest.md)
- [BodyEdmFestivalAuditArtistsArtistIdRecoveryEdmFestivalAuditPost](docs/BodyEdmFestivalAuditArtistsArtistIdRecoveryEdmFestivalAuditPost.md)
- [BrandingProfilePatchRequest](docs/BrandingProfilePatchRequest.md)
- [BrandingProfileUpsertRequest](docs/BrandingProfileUpsertRequest.md)
- [BulkOnboardRequest](docs/BulkOnboardRequest.md)
- [CatalogConfirmationSchema](docs/CatalogConfirmationSchema.md)
- [ChatRequest](docs/ChatRequest.md)
- [ClaimCreateRequest](docs/ClaimCreateRequest.md)
- [ClaimRequest](docs/ClaimRequest.md)
- [ClaimSchema](docs/ClaimSchema.md)
- [ClaimStatus](docs/ClaimStatus.md)
- [ClaimTemplateRequest](docs/ClaimTemplateRequest.md)
- [ContractExtractRequest](docs/ContractExtractRequest.md)
- [CreateReviewItemRequest](docs/CreateReviewItemRequest.md)
- [CreatorIngestRequest](docs/CreatorIngestRequest.md)
- [CurrencyTaxEstimateRequest](docs/CurrencyTaxEstimateRequest.md)
- [DecideReviewItemRequest](docs/DecideReviewItemRequest.md)
- [DemandLetterRequest](docs/DemandLetterRequest.md)
- [DemandLetterResponse](docs/DemandLetterResponse.md)
- [EstimateRequest](docs/EstimateRequest.md)
- [EvidenceAnchorSchema](docs/EvidenceAnchorSchema.md)
- [FailedPacketRequest](docs/FailedPacketRequest.md)
- [FeedbackOutcome](docs/FeedbackOutcome.md)
- [FingerprintingRequest](docs/FingerprintingRequest.md)
- [ForensicUniversalRoyaltyEventCreate](docs/ForensicUniversalRoyaltyEventCreate.md)
- [ForensicUniversalRoyaltyEventSchema](docs/ForensicUniversalRoyaltyEventSchema.md)
- [FounderAssignRequest](docs/FounderAssignRequest.md)
- [FounderCohortLimitUpdateRequest](docs/FounderCohortLimitUpdateRequest.md)
- [HTTPValidationError](docs/HTTPValidationError.md)
- [HelpArticleCreateRequest](docs/HelpArticleCreateRequest.md)
- [IdentityConfidenceBand](docs/IdentityConfidenceBand.md)
- [IdentityDecisionRequest](docs/IdentityDecisionRequest.md)
- [IdentityDecisionStatus](docs/IdentityDecisionStatus.md)
- [IdentityMatchRequest](docs/IdentityMatchRequest.md)
- [ImmutableLedgerEntrySchema](docs/ImmutableLedgerEntrySchema.md)
- [InviteRequest](docs/InviteRequest.md)
- [LedgerIngestRequest](docs/LedgerIngestRequest.md)
- [LedgerRecordType](docs/LedgerRecordType.md)
- [LocationInner](docs/LocationInner.md)
- [MLFeedbackEventSchema](docs/MLFeedbackEventSchema.md)
- [MLFeedbackType](docs/MLFeedbackType.md)
- [ManualRemittanceRequest](docs/ManualRemittanceRequest.md)
- [MetadataRepairApplyRequest](docs/MetadataRepairApplyRequest.md)
- [MetadataRepairSuggestRequest](docs/MetadataRepairSuggestRequest.md)
- [NegotiationScriptRequest](docs/NegotiationScriptRequest.md)
- [NegotiationScriptResponse](docs/NegotiationScriptResponse.md)
- [NotificationDispatchRequest](docs/NotificationDispatchRequest.md)
- [NotificationPreferenceRequest](docs/NotificationPreferenceRequest.md)
- [NotificationPreferenceSchema](docs/NotificationPreferenceSchema.md)
- [NotificationPreferenceUpsert](docs/NotificationPreferenceUpsert.md)
- [OAuthSessionCreateRequest](docs/OAuthSessionCreateRequest.md)
- [OAuthTokenExchangeRequest](docs/OAuthTokenExchangeRequest.md)
- [OAuthTokenRefreshRequest](docs/OAuthTokenRefreshRequest.md)
- [OnboardingAutoRequest](docs/OnboardingAutoRequest.md)
- [OptimizationSimulationRequest](docs/OptimizationSimulationRequest.md)
- [ParserPluginSchema](docs/ParserPluginSchema.md)
- [ParserPluginUpsertRequest](docs/ParserPluginUpsertRequest.md)
- [PreSignatureContractReviewRequest](docs/PreSignatureContractReviewRequest.md)
- [PredictRecoverableRequest](docs/PredictRecoverableRequest.md)
- [ReconcileRequest](docs/ReconcileRequest.md)
- [ReconciliationRequest](docs/ReconciliationRequest.md)
- [ReconstructRequest](docs/ReconstructRequest.md)
- [RecoveryAutoRequest](docs/RecoveryAutoRequest.md)
- [RecoveryOutcomeFeedbackSchema](docs/RecoveryOutcomeFeedbackSchema.md)
- [RecoverySubmitResponse](docs/RecoverySubmitResponse.md)
- [ReferralRequest](docs/ReferralRequest.md)
- [RegisterRequest](docs/RegisterRequest.md)
- [RegisterResponse](docs/RegisterResponse.md)
- [ReviewAssignmentSchema](docs/ReviewAssignmentSchema.md)
- [ReviewDecisionSchema](docs/ReviewDecisionSchema.md)
- [ReviewDecisionType](docs/ReviewDecisionType.md)
- [ReviewItemSchema](docs/ReviewItemSchema.md)
- [ReviewItemStatus](docs/ReviewItemStatus.md)
- [ReviewSourceType](docs/ReviewSourceType.md)
- [RoyaltyLedgerEntryCreate](docs/RoyaltyLedgerEntryCreate.md)
- [SimulatePayoutRequest](docs/SimulatePayoutRequest.md)
- [SimulationRequest](docs/SimulationRequest.md)
- [SplitRepairRequest](docs/SplitRepairRequest.md)
- [StatementSchema](docs/StatementSchema.md)
- [StructuredFeedbackRequest](docs/StructuredFeedbackRequest.md)
- [SupportActionRequest](docs/SupportActionRequest.md)
- [SupportActionResponse](docs/SupportActionResponse.md)
- [SupportChatRequest](docs/SupportChatRequest.md)
- [SupportChatResponse](docs/SupportChatResponse.md)
- [SupportHistoryResponse](docs/SupportHistoryResponse.md)
- [SupportMessageView](docs/SupportMessageView.md)
- [SupportSuggestionResponse](docs/SupportSuggestionResponse.md)
- [SyncJobCreateRequest](docs/SyncJobCreateRequest.md)
- [SyncJobSchema](docs/SyncJobSchema.md)
- [TaxOptimizerRequest](docs/TaxOptimizerRequest.md)
- [TeamMemberCreate](docs/TeamMemberCreate.md)
- [TeamMemberSchema](docs/TeamMemberSchema.md)
- [TeamRole](docs/TeamRole.md)
- [TermsAcceptRequest](docs/TermsAcceptRequest.md)
- [TermsAcceptanceSchema](docs/TermsAcceptanceSchema.md)
- [TokenResponse](docs/TokenResponse.md)
- [TrolleyTransactionSchema](docs/TrolleyTransactionSchema.md)
- [TrolleyTxnStatus](docs/TrolleyTxnStatus.md)
- [TrolleyTxnType](docs/TrolleyTxnType.md)
- [UGCSignalIngestRequest](docs/UGCSignalIngestRequest.md)
- [UtilityRankRequest](docs/UtilityRankRequest.md)
- [ValidationError](docs/ValidationError.md)
- [VarianceScanRequest](docs/VarianceScanRequest.md)
- [VerifyRequest](docs/VerifyRequest.md)
- [VerifyResponse](docs/VerifyResponse.md)
- [WeeklyStoryRequest](docs/WeeklyStoryRequest.md)
- [WidgetLeadSchema](docs/WidgetLeadSchema.md)
- [WorkflowRunRequest](docs/WorkflowRunRequest.md)
- [WorkflowRunResponse](docs/WorkflowRunResponse.md)
- [XR7ApiRoutersEarningsForecastRequest](docs/XR7ApiRoutersEarningsForecastRequest.md)
- [XR7ApiRoutersForensicCatalogConfirmRequest](docs/XR7ApiRoutersForensicCatalogConfirmRequest.md)
- [XR7ApiRoutersOnboardingCatalogConfirmRequest](docs/XR7ApiRoutersOnboardingCatalogConfirmRequest.md)
- [XR7ApiRoutersXr7ValuationForecastRequest](docs/XR7ApiRoutersXr7ValuationForecastRequest.md)
- [XR7ConnectorCredentialUpsert](docs/XR7ConnectorCredentialUpsert.md)

### Authorization


Authentication schemes defined for the API:
<a id="HTTPBearer"></a>
#### HTTPBearer


- **Type**: HTTP Bearer Token authentication

## About

This TypeScript SDK client supports the [Fetch API](https://fetch.spec.whatwg.org/)
and is automatically generated by the
[OpenAPI Generator](https://openapi-generator.tech) project:

- API version: `2.0.0`
- Package version: `2.0.0`
- Generator version: `7.21.0-SNAPSHOT`
- Build package: `org.openapitools.codegen.languages.TypeScriptFetchClientCodegen`

The generated npm module supports the following:

- Environments
  * Node.js
  * Webpack
  * Browserify
- Language levels
  * ES5 - you must have a Promises/A+ library installed
  * ES6
- Module systems
  * CommonJS
  * ES6 module system


## Development

### Building

To build the TypeScript source code, you need to have Node.js and npm installed.
After cloning the repository, navigate to the project directory and run:

```bash
npm install
npm run build
```

### Publishing

Once you've built the package, you can publish it to npm:

```bash
npm publish
```

## License

[]()
