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
*AdminApi* | [**listAnomaliesAdminAnomaliesGet**](docs/AdminApi.md#listanomaliesadminanomaliesget) | **GET** /admin/anomalies | List Anomalies
*AdminApi* | [**listArtistsAdminArtistsGet**](docs/AdminApi.md#listartistsadminartistsget) | **GET** /admin/artists | List Artists
*AdminApi* | [**listAuditLogsAdminAuditLogsGet**](docs/AdminApi.md#listauditlogsadminauditlogsget) | **GET** /admin/audit-logs | List Audit Logs
*AdminApi* | [**listClaimsAdminClaimsGet**](docs/AdminApi.md#listclaimsadminclaimsget) | **GET** /admin/claims | List Claims
*AdminApi* | [**listReviewQueueAdminReviewQueueGet**](docs/AdminApi.md#listreviewqueueadminreviewqueueget) | **GET** /admin/review-queue | List Review Queue
*AdminApi* | [**listTransactionsAdminTransactionsGet**](docs/AdminApi.md#listtransactionsadmintransactionsget) | **GET** /admin/transactions | List Transactions
*AnomaliesApi* | [**detectAnomaliesArtistsArtistIdAnomaliesDetectPost**](docs/AnomaliesApi.md#detectanomaliesartistsartistidanomaliesdetectpost) | **POST** /artists/{artist_id}/anomalies/detect | Detect Anomalies
*AnomaliesApi* | [**getAnomalyAnomaliesAnomalyIdGet**](docs/AnomaliesApi.md#getanomalyanomaliesanomalyidget) | **GET** /anomalies/{anomaly_id} | Get Anomaly
*AnomaliesApi* | [**listAnomaliesArtistsArtistIdAnomaliesGet**](docs/AnomaliesApi.md#listanomaliesartistsartistidanomaliesget) | **GET** /artists/{artist_id}/anomalies | List Anomalies
*ArtistsApi* | [**artistSummaryArtistsArtistIdSummaryGet**](docs/ArtistsApi.md#artistsummaryartistsartistidsummaryget) | **GET** /artists/{artist_id}/summary | Artist Summary
*ArtistsApi* | [**catalogHealthArtistsArtistIdMlCatalogHealthGet**](docs/ArtistsApi.md#cataloghealthartistsartistidmlcataloghealthget) | **GET** /artists/{artist_id}/ml/catalog-health | Catalog Health
*ArtistsApi* | [**connectArtistArtistsArtistIdConnectPost**](docs/ArtistsApi.md#connectartistartistsartistidconnectpost) | **POST** /artists/{artist_id}/connect | Connect Artist
*ArtistsApi* | [**createArtistArtistsPost**](docs/ArtistsApi.md#createartistartistspost) | **POST** /artists/ | Create Artist
*ArtistsApi* | [**getArtistArtistsArtistIdGet**](docs/ArtistsApi.md#getartistartistsartistidget) | **GET** /artists/{artist_id} | Get Artist
*BillingApi* | [**getBillingSummaryArtistsArtistIdBillingGet**](docs/BillingApi.md#getbillingsummaryartistsartistidbillingget) | **GET** /artists/{artist_id}/billing | Get Billing Summary
*BillingApi* | [**listInvoicesArtistsArtistIdInvoicesGet**](docs/BillingApi.md#listinvoicesartistsartistidinvoicesget) | **GET** /artists/{artist_id}/invoices | List Invoices
*CeleroApi* | [**celeroWebhookCeleroWebhookPost**](docs/CeleroApi.md#celerowebhookcelerowebhookpost) | **POST** /celero/webhook | Celero Webhook
*CeleroApi* | [**chargeContingencyFeeArtistsArtistIdCeleroChargePost**](docs/CeleroApi.md#chargecontingencyfeeartistsartistidcelerochargepost) | **POST** /artists/{artist_id}/celero/charge | Charge Contingency Fee
*CeleroApi* | [**disburseToArtistArtistsArtistIdCeleroDisbursePost**](docs/CeleroApi.md#disbursetoartistartistsartistidcelerodisbursepost) | **POST** /artists/{artist_id}/celero/disburse | Disburse To Artist
*CeleroApi* | [**getCeleroStatusArtistsArtistIdCeleroStatusGet**](docs/CeleroApi.md#getcelerostatusartistsartistidcelerostatusget) | **GET** /artists/{artist_id}/celero/status | Get Celero Status
*CeleroApi* | [**getCeleroTransactionArtistsArtistIdCeleroTransactionsTransactionIdGet**](docs/CeleroApi.md#getcelerotransactionartistsartistidcelerotransactionstransactionidget) | **GET** /artists/{artist_id}/celero/transactions/{transaction_id} | Get Celero Transaction
*CeleroApi* | [**listCeleroTransactionsArtistsArtistIdCeleroTransactionsGet**](docs/CeleroApi.md#listcelerotransactionsartistsartistidcelerotransactionsget) | **GET** /artists/{artist_id}/celero/transactions | List Celero Transactions
*CeleroApi* | [**refundTransactionArtistsArtistIdCeleroTransactionsTransactionIdRefundPost**](docs/CeleroApi.md#refundtransactionartistsartistidcelerotransactionstransactionidrefundpost) | **POST** /artists/{artist_id}/celero/transactions/{transaction_id}/refund | Refund Transaction
*CeleroApi* | [**registerArtistWithCeleroArtistsArtistIdCeleroRegisterPost**](docs/CeleroApi.md#registerartistwithceleroartistsartistidceleroregisterpost) | **POST** /artists/{artist_id}/celero/register | Register Artist With Celero
*CeleroApi* | [**updateCeleroCustomerArtistsArtistIdCeleroCustomerPut**](docs/CeleroApi.md#updatecelerocustomerartistsartistidcelerocustomerput) | **PUT** /artists/{artist_id}/celero/customer | Update Celero Customer
*CeleroApi* | [**voidTransactionArtistsArtistIdCeleroTransactionsTransactionIdVoidPost**](docs/CeleroApi.md#voidtransactionartistsartistidcelerotransactionstransactionidvoidpost) | **POST** /artists/{artist_id}/celero/transactions/{transaction_id}/void | Void Transaction
*ClaimsApi* | [**advanceClaimClaimsClaimIdAdvancePost**](docs/ClaimsApi.md#advanceclaimclaimsclaimidadvancepost) | **POST** /claims/{claim_id}/advance | Advance Claim
*ClaimsApi* | [**exportEvidencePacketClaimsClaimIdEvidenceExportGet**](docs/ClaimsApi.md#exportevidencepacketclaimsclaimidevidenceexportget) | **GET** /claims/{claim_id}/evidence/export | Export Evidence Packet
*ClaimsApi* | [**generateEvidenceClaimsClaimIdEvidencePost**](docs/ClaimsApi.md#generateevidenceclaimsclaimidevidencepost) | **POST** /claims/{claim_id}/evidence | Generate Evidence
*ClaimsApi* | [**getClaimClaimsClaimIdGet**](docs/ClaimsApi.md#getclaimclaimsclaimidget) | **GET** /claims/{claim_id} | Get Claim
*ClaimsApi* | [**listClaimsArtistsArtistIdClaimsGet**](docs/ClaimsApi.md#listclaimsartistsartistidclaimsget) | **GET** /artists/{artist_id}/claims | List Claims
*ClaimsApi* | [**reconcileClaimClaimsClaimIdReconcilePost**](docs/ClaimsApi.md#reconcileclaimclaimsclaimidreconcilepost) | **POST** /claims/{claim_id}/reconcile | Reconcile Claim
*ClaimsApi* | [**verifyEvidencePacketClaimsClaimIdEvidenceVerifyGet**](docs/ClaimsApi.md#verifyevidencepacketclaimsclaimidevidenceverifyget) | **GET** /claims/{claim_id}/evidence/verify | Verify Evidence Packet
*DashboardApi* | [**getArtistDashboardArtistsArtistIdDashboardGet**](docs/DashboardApi.md#getartistdashboardartistsartistiddashboardget) | **GET** /artists/{artist_id}/dashboard | Get Artist Dashboard
*DashboardApi* | [**getDashboardUiDashboardUiGet**](docs/DashboardApi.md#getdashboarduidashboarduiget) | **GET** /dashboard/ui | Get Dashboard Ui
*DefaultApi* | [**healthHealthGet**](docs/DefaultApi.md#healthhealthget) | **GET** /health | Health
*DefaultApi* | [**readinessHealthReadinessGet**](docs/DefaultApi.md#readinesshealthreadinessget) | **GET** /health/readiness | Readiness
*EarningsApi* | [**forecastEarningsArtistsArtistIdMlForecastPost**](docs/EarningsApi.md#forecastearningsartistsartistidmlforecastpost) | **POST** /artists/{artist_id}/ml/forecast | Forecast Earnings
*EarningsApi* | [**getEarningsHistoryArtistsArtistIdEarningsHistoryGet**](docs/EarningsApi.md#getearningshistoryartistsartistidearningshistoryget) | **GET** /artists/{artist_id}/earnings/history | Get Earnings History
*EarningsApi* | [**getEarningsSummaryArtistsArtistIdEarningsGet**](docs/EarningsApi.md#getearningssummaryartistsartistidearningsget) | **GET** /artists/{artist_id}/earnings | Get Earnings Summary
*EarningsApi* | [**reconstructEarningsArtistsArtistIdEarningsReconstructPost**](docs/EarningsApi.md#reconstructearningsartistsartistidearningsreconstructpost) | **POST** /artists/{artist_id}/earnings/reconstruct | Reconstruct Earnings
*ExpansionApi* | [**addTeamMemberArtistsArtistIdTeamMembersPost**](docs/ExpansionApi.md#addteammemberartistsartistidteammemberspost) | **POST** /artists/{artist_id}/team/members | Add Team Member
*ExpansionApi* | [**anchorEvidencePacketClaimsClaimIdEvidenceAnchorPost**](docs/ExpansionApi.md#anchorevidencepacketclaimsclaimidevidenceanchorpost) | **POST** /claims/{claim_id}/evidence/anchor | Anchor Evidence Packet
*ExpansionApi* | [**benchmarkPercentilesArtistsArtistIdRecoveryBenchmarkPercentilesGet**](docs/ExpansionApi.md#benchmarkpercentilesartistsartistidrecoverybenchmarkpercentilesget) | **GET** /artists/{artist_id}/recovery/benchmark-percentiles | Benchmark Percentiles
*ExpansionApi* | [**createOauthSessionArtistsArtistIdConnectOauthSessionPost**](docs/ExpansionApi.md#createoauthsessionartistsartistidconnectoauthsessionpost) | **POST** /artists/{artist_id}/connect/oauth-session | Create Oauth Session
*ExpansionApi* | [**dashboardChartsDataArtistsArtistIdDashboardChartsGet**](docs/ExpansionApi.md#dashboardchartsdataartistsartistiddashboardchartsget) | **GET** /artists/{artist_id}/dashboard/charts | Dashboard Charts Data
*ExpansionApi* | [**disconnectConnectedAccountArtistsArtistIdConnectAccountsAccountIdDelete**](docs/ExpansionApi.md#disconnectconnectedaccountartistsartistidconnectaccountsaccountiddelete) | **DELETE** /artists/{artist_id}/connect/accounts/{account_id} | Disconnect Connected Account
*ExpansionApi* | [**dispatchNotificationArtistsArtistIdNotificationsDispatchPost**](docs/ExpansionApi.md#dispatchnotificationartistsartistidnotificationsdispatchpost) | **POST** /artists/{artist_id}/notifications/dispatch | Dispatch Notification
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
*IngestionApi* | [**getStatementArtistsArtistIdStatementsStatementIdGet**](docs/IngestionApi.md#getstatementartistsartistidstatementsstatementidget) | **GET** /artists/{artist_id}/statements/{statement_id} | Get Statement
*IngestionApi* | [**listStatementsArtistsArtistIdStatementsGet**](docs/IngestionApi.md#liststatementsartistsartistidstatementsget) | **GET** /artists/{artist_id}/statements | List Statements
*IngestionApi* | [**supportedFormatsIngestionSupportedFormatsGet**](docs/IngestionApi.md#supportedformatsingestionsupportedformatsget) | **GET** /ingestion/supported-formats | Supported Formats
*IngestionApi* | [**uploadStatementArtistsArtistIdStatementsUploadPost**](docs/IngestionApi.md#uploadstatementartistsartistidstatementsuploadpost) | **POST** /artists/{artist_id}/statements/upload | Upload Statement
*IngestionApi* | [**uploadStatementBatchArtistsArtistIdStatementsUploadBatchPost**](docs/IngestionApi.md#uploadstatementbatchartistsartistidstatementsuploadbatchpost) | **POST** /artists/{artist_id}/statements/upload-batch | Upload Statement Batch
*IntelligenceApi* | [**createOutcomeFeedbackArtistsArtistIdIntelligenceFeedbackPost**](docs/IntelligenceApi.md#createoutcomefeedbackartistsartistidintelligencefeedbackpost) | **POST** /artists/{artist_id}/intelligence/feedback | Create Outcome Feedback
*IntelligenceApi* | [**extractContractTermsArtistsArtistIdIntelligenceContractsExtractPost**](docs/IntelligenceApi.md#extractcontracttermsartistsartistidintelligencecontractsextractpost) | **POST** /artists/{artist_id}/intelligence/contracts/extract | Extract Contract Terms
*IntelligenceApi* | [**extractContractTermsUploadArtistsArtistIdIntelligenceContractsExtractUploadPost**](docs/IntelligenceApi.md#extractcontracttermsuploadartistsartistidintelligencecontractsextractuploadpost) | **POST** /artists/{artist_id}/intelligence/contracts/extract-upload | Extract Contract Terms Upload
*IntelligenceApi* | [**getCalibrationHealthArtistsArtistIdIntelligenceCalibrationGet**](docs/IntelligenceApi.md#getcalibrationhealthartistsartistidintelligencecalibrationget) | **GET** /artists/{artist_id}/intelligence/calibration | Get Calibration Health
*IntelligenceApi* | [**ingestRoyaltyLedgerArtistsArtistIdIntelligenceLedgerIngestPost**](docs/IntelligenceApi.md#ingestroyaltyledgerartistsartistidintelligenceledgeringestpost) | **POST** /artists/{artist_id}/intelligence/ledger/ingest | Ingest Royalty Ledger
*IntelligenceApi* | [**rankByExpectedUtilityArtistsArtistIdIntelligenceRankUtilityPost**](docs/IntelligenceApi.md#rankbyexpectedutilityartistsartistidintelligencerankutilitypost) | **POST** /artists/{artist_id}/intelligence/rank-utility | Rank By Expected Utility
*IntelligenceApi* | [**simulateExpectedPayoutArtistsArtistIdIntelligenceSimulateExpectedPayoutPost**](docs/IntelligenceApi.md#simulateexpectedpayoutartistsartistidintelligencesimulateexpectedpayoutpost) | **POST** /artists/{artist_id}/intelligence/simulate-expected-payout | Simulate Expected Payout
*OnboardingApi* | [**buildCatalogWorkGraphArtistsArtistIdCatalogGraphBuildPost**](docs/OnboardingApi.md#buildcatalogworkgraphartistsartistidcataloggraphbuildpost) | **POST** /artists/{artist_id}/catalog/graph/build | Build Catalog Work Graph
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
*RecoveryApi* | [**auditEligibilityArtistsArtistIdRecoveryAuditEligibilityGet**](docs/RecoveryApi.md#auditeligibilityartistsartistidrecoveryauditeligibilityget) | **GET** /artists/{artist_id}/recovery/audit-eligibility | Audit Eligibility
*RecoveryApi* | [**priorityQueueArtistsArtistIdRecoveryPriorityQueueGet**](docs/RecoveryApi.md#priorityqueueartistsartistidrecoverypriorityqueueget) | **GET** /artists/{artist_id}/recovery/priority-queue | Priority Queue
*RecoveryApi* | [**rateBenchmarkArtistsArtistIdRecoveryRateBenchmarkGet**](docs/RecoveryApi.md#ratebenchmarkartistsartistidrecoveryratebenchmarkget) | **GET** /artists/{artist_id}/recovery/rate-benchmark | Rate Benchmark
*RecoveryApi* | [**recoupmentArtistsArtistIdRecoveryRecoupmentGet**](docs/RecoveryApi.md#recoupmentartistsartistidrecoveryrecoupmentget) | **GET** /artists/{artist_id}/recovery/recoupment | Recoupment
*RecoveryApi* | [**solStatusArtistsArtistIdRecoverySolStatusGet**](docs/RecoveryApi.md#solstatusartistsartistidrecoverysolstatusget) | **GET** /artists/{artist_id}/recovery/sol-status | Sol Status
*ReviewQueueApi* | [**assignReviewItemReviewQueueItemsItemIdAssignPost**](docs/ReviewQueueApi.md#assignreviewitemreviewqueueitemsitemidassignpost) | **POST** /review-queue/items/{item_id}/assign | Assign Review Item
*ReviewQueueApi* | [**checkThresholdReviewQueueThresholdCheckPost**](docs/ReviewQueueApi.md#checkthresholdreviewqueuethresholdcheckpost) | **POST** /review-queue/threshold-check | Check Threshold
*ReviewQueueApi* | [**createReviewItemReviewQueueItemsPost**](docs/ReviewQueueApi.md#createreviewitemreviewqueueitemspost) | **POST** /review-queue/items | Create Review Item
*ReviewQueueApi* | [**decideReviewItemReviewQueueItemsItemIdDecisionPost**](docs/ReviewQueueApi.md#decidereviewitemreviewqueueitemsitemiddecisionpost) | **POST** /review-queue/items/{item_id}/decision | Decide Review Item
*ReviewQueueApi* | [**listDecisionsReviewQueueDecisionsGet**](docs/ReviewQueueApi.md#listdecisionsreviewqueuedecisionsget) | **GET** /review-queue/decisions | List Decisions
*ReviewQueueApi* | [**listReviewItemsReviewQueueItemsGet**](docs/ReviewQueueApi.md#listreviewitemsreviewqueueitemsget) | **GET** /review-queue/items | List Review Items
*ReviewQueueApi* | [**reviewQueueMetricsReviewQueueMetricsGet**](docs/ReviewQueueApi.md#reviewqueuemetricsreviewqueuemetricsget) | **GET** /review-queue/metrics | Review Queue Metrics
*TermsApi* | [**acceptTermsArtistsArtistIdTermsAcceptPost**](docs/TermsApi.md#accepttermsartistsartistidtermsacceptpost) | **POST** /artists/{artist_id}/terms/accept | Accept Terms
*TermsApi* | [**getTermsTermsGet**](docs/TermsApi.md#gettermstermsget) | **GET** /terms | Get Terms
*TermsApi* | [**termsStatusArtistsArtistIdTermsStatusGet**](docs/TermsApi.md#termsstatusartistsartistidtermsstatusget) | **GET** /artists/{artist_id}/terms/status | Terms Status
*WidgetApi* | [**claimWidgetClaimPost**](docs/WidgetApi.md#claimwidgetclaimpost) | **POST** /widget/claim | Claim
*WidgetApi* | [**estimateWidgetEstimatePost**](docs/WidgetApi.md#estimatewidgetestimatepost) | **POST** /widget/estimate | Estimate
*WidgetApi* | [**listLeadsWidgetLeadsGet**](docs/WidgetApi.md#listleadswidgetleadsget) | **GET** /widget/leads | List Leads
*WidgetApi* | [**registerWidgetRegisterPost**](docs/WidgetApi.md#registerwidgetregisterpost) | **POST** /widget/register | Register
*WidgetApi* | [**verifyWidgetVerifyPost**](docs/WidgetApi.md#verifywidgetverifypost) | **POST** /widget/verify | Verify


### Models

- [AdminAuditLogSchema](docs/AdminAuditLogSchema.md)
- [AnomalyCategory](docs/AnomalyCategory.md)
- [AnomalySchema](docs/AnomalySchema.md)
- [AnomalySeverity](docs/AnomalySeverity.md)
- [AnomalyStatus](docs/AnomalyStatus.md)
- [ArtistCreate](docs/ArtistCreate.md)
- [ArtistLifecycleStatus](docs/ArtistLifecycleStatus.md)
- [ArtistSchema](docs/ArtistSchema.md)
- [AssignReviewItemRequest](docs/AssignReviewItemRequest.md)
- [AuthConnectResponse](docs/AuthConnectResponse.md)
- [CatalogConfirmationSchema](docs/CatalogConfirmationSchema.md)
- [CeleroChargeRequest](docs/CeleroChargeRequest.md)
- [CeleroDisburseRequest](docs/CeleroDisburseRequest.md)
- [CeleroRefundRequest](docs/CeleroRefundRequest.md)
- [CeleroRegisterRequest](docs/CeleroRegisterRequest.md)
- [CeleroTransactionSchema](docs/CeleroTransactionSchema.md)
- [CeleroTxnStatus](docs/CeleroTxnStatus.md)
- [CeleroTxnType](docs/CeleroTxnType.md)
- [ClaimRequest](docs/ClaimRequest.md)
- [ClaimSchema](docs/ClaimSchema.md)
- [ClaimStatus](docs/ClaimStatus.md)
- [ClaimTemplateRequest](docs/ClaimTemplateRequest.md)
- [ContractExtractRequest](docs/ContractExtractRequest.md)
- [CreateReviewItemRequest](docs/CreateReviewItemRequest.md)
- [CurrencyTaxEstimateRequest](docs/CurrencyTaxEstimateRequest.md)
- [DecideReviewItemRequest](docs/DecideReviewItemRequest.md)
- [EstimateRequest](docs/EstimateRequest.md)
- [EvidenceAnchorSchema](docs/EvidenceAnchorSchema.md)
- [FeedbackOutcome](docs/FeedbackOutcome.md)
- [ForecastRequest](docs/ForecastRequest.md)
- [ForensicUniversalRoyaltyEventCreate](docs/ForensicUniversalRoyaltyEventCreate.md)
- [ForensicUniversalRoyaltyEventSchema](docs/ForensicUniversalRoyaltyEventSchema.md)
- [HTTPValidationError](docs/HTTPValidationError.md)
- [ImmutableLedgerEntrySchema](docs/ImmutableLedgerEntrySchema.md)
- [LedgerIngestRequest](docs/LedgerIngestRequest.md)
- [LedgerRecordType](docs/LedgerRecordType.md)
- [LocationInner](docs/LocationInner.md)
- [NotificationDispatchRequest](docs/NotificationDispatchRequest.md)
- [NotificationPreferenceSchema](docs/NotificationPreferenceSchema.md)
- [NotificationPreferenceUpsert](docs/NotificationPreferenceUpsert.md)
- [OAuthSessionCreateRequest](docs/OAuthSessionCreateRequest.md)
- [OAuthTokenExchangeRequest](docs/OAuthTokenExchangeRequest.md)
- [OAuthTokenRefreshRequest](docs/OAuthTokenRefreshRequest.md)
- [ParserPluginSchema](docs/ParserPluginSchema.md)
- [ParserPluginUpsertRequest](docs/ParserPluginUpsertRequest.md)
- [PredictRecoverableRequest](docs/PredictRecoverableRequest.md)
- [ReconcileRequest](docs/ReconcileRequest.md)
- [ReconstructRequest](docs/ReconstructRequest.md)
- [RecoveryOutcomeFeedbackCreate](docs/RecoveryOutcomeFeedbackCreate.md)
- [RecoveryOutcomeFeedbackSchema](docs/RecoveryOutcomeFeedbackSchema.md)
- [RecoverySubmitResponse](docs/RecoverySubmitResponse.md)
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
- [StatementSchema](docs/StatementSchema.md)
- [SyncJobCreateRequest](docs/SyncJobCreateRequest.md)
- [SyncJobSchema](docs/SyncJobSchema.md)
- [TeamMemberCreate](docs/TeamMemberCreate.md)
- [TeamMemberSchema](docs/TeamMemberSchema.md)
- [TeamRole](docs/TeamRole.md)
- [TermsAcceptRequest](docs/TermsAcceptRequest.md)
- [TermsAcceptanceSchema](docs/TermsAcceptanceSchema.md)
- [UtilityRankRequest](docs/UtilityRankRequest.md)
- [ValidationError](docs/ValidationError.md)
- [VarianceScanRequest](docs/VarianceScanRequest.md)
- [VerifyRequest](docs/VerifyRequest.md)
- [VerifyResponse](docs/VerifyResponse.md)
- [WidgetLeadSchema](docs/WidgetLeadSchema.md)
- [WorkflowRunRequest](docs/WorkflowRunRequest.md)
- [XR7ApiRoutersForensicCatalogConfirmRequest](docs/XR7ApiRoutersForensicCatalogConfirmRequest.md)
- [XR7ApiRoutersOnboardingCatalogConfirmRequest](docs/XR7ApiRoutersOnboardingCatalogConfirmRequest.md)

### Authorization

Endpoints do not require authorization.


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
