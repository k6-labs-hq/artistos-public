# ExpansionApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**addTeamMemberArtistsArtistIdTeamMembersPost**](ExpansionApi.md#addteammemberartistsartistidteammemberspost) | **POST** /artists/{artist_id}/team/members | Add Team Member |
| [**anchorEvidencePacketClaimsClaimIdEvidenceAnchorPost**](ExpansionApi.md#anchorevidencepacketclaimsclaimidevidenceanchorpost) | **POST** /claims/{claim_id}/evidence/anchor | Anchor Evidence Packet |
| [**benchmarkPercentilesArtistsArtistIdRecoveryBenchmarkPercentilesGet**](ExpansionApi.md#benchmarkpercentilesartistsartistidrecoverybenchmarkpercentilesget) | **GET** /artists/{artist_id}/recovery/benchmark-percentiles | Benchmark Percentiles |
| [**createOauthSessionArtistsArtistIdConnectOauthSessionPost**](ExpansionApi.md#createoauthsessionartistsartistidconnectoauthsessionpost) | **POST** /artists/{artist_id}/connect/oauth-session | Create Oauth Session |
| [**dashboardChartsDataArtistsArtistIdDashboardChartsGet**](ExpansionApi.md#dashboardchartsdataartistsartistiddashboardchartsget) | **GET** /artists/{artist_id}/dashboard/charts | Dashboard Charts Data |
| [**disconnectConnectedAccountArtistsArtistIdConnectAccountsAccountIdDelete**](ExpansionApi.md#disconnectconnectedaccountartistsartistidconnectaccountsaccountiddelete) | **DELETE** /artists/{artist_id}/connect/accounts/{account_id} | Disconnect Connected Account |
| [**dispatchNotificationArtistsArtistIdNotificationsDispatchPost**](ExpansionApi.md#dispatchnotificationartistsartistidnotificationsdispatchpost) | **POST** /artists/{artist_id}/notifications/dispatch | Dispatch Notification |
| [**educationGuideDetailEducationGuidesGuideIdGet**](ExpansionApi.md#educationguidedetaileducationguidesguideidget) | **GET** /education/guides/{guide_id} | Education Guide Detail |
| [**educationGuidesIndexEducationGuidesGet**](ExpansionApi.md#educationguidesindexeducationguidesget) | **GET** /education/guides | Education Guides Index |
| [**estimateWithholdingArtistsArtistIdIntelligenceWithholdingEstimatePost**](ExpansionApi.md#estimatewithholdingartistsartistidintelligencewithholdingestimatepost) | **POST** /artists/{artist_id}/intelligence/withholding-estimate | Estimate Withholding |
| [**exchangeOauthCodeArtistsArtistIdConnectOauthSessionSessionIdExchangePost**](ExpansionApi.md#exchangeoauthcodeartistsartistidconnectoauthsessionsessionidexchangepost) | **POST** /artists/{artist_id}/connect/oauth-session/{session_id}/exchange | Exchange Oauth Code |
| [**exportSummaryReportArtistsArtistIdReportsSummaryGet**](ExpansionApi.md#exportsummaryreportartistsartistidreportssummaryget) | **GET** /artists/{artist_id}/reports/summary | Export Summary Report |
| [**generateAuditDemandLetterArtistsArtistIdRecoveryAuditDemandLetterGet**](ExpansionApi.md#generateauditdemandletterartistsartistidrecoveryauditdemandletterget) | **GET** /artists/{artist_id}/recovery/audit-demand-letter | Generate Audit Demand Letter |
| [**generateClaimTemplateArtistsArtistIdClaimsTemplatesPost**](ExpansionApi.md#generateclaimtemplateartistsartistidclaimstemplatespost) | **POST** /artists/{artist_id}/claims/templates | Generate Claim Template |
| [**getNotificationPreferencesArtistsArtistIdNotificationsPreferencesGet**](ExpansionApi.md#getnotificationpreferencesartistsartistidnotificationspreferencesget) | **GET** /artists/{artist_id}/notifications/preferences | Get Notification Preferences |
| [**listConnectFallbacksArtistsArtistIdConnectFallbacksGet**](ExpansionApi.md#listconnectfallbacksartistsartistidconnectfallbacksget) | **GET** /artists/{artist_id}/connect/fallbacks | List Connect Fallbacks |
| [**listConnectedAccountsArtistsArtistIdConnectAccountsGet**](ExpansionApi.md#listconnectedaccountsartistsartistidconnectaccountsget) | **GET** /artists/{artist_id}/connect/accounts | List Connected Accounts |
| [**listTeamMembersArtistsArtistIdTeamMembersGet**](ExpansionApi.md#listteammembersartistsartistidteammembersget) | **GET** /artists/{artist_id}/team/members | List Team Members |
| [**partnershipTargetsPartnershipsTargetsGet**](ExpansionApi.md#partnershiptargetspartnershipstargetsget) | **GET** /partnerships/targets | Partnership Targets |
| [**predictTotalRecoverableArtistsArtistIdMlPredictRecoverablePost**](ExpansionApi.md#predicttotalrecoverableartistsartistidmlpredictrecoverablepost) | **POST** /artists/{artist_id}/ml/predict-recoverable | Predict Total Recoverable |
| [**publicRecoveryStatsStatsPublicRecoveryGet**](ExpansionApi.md#publicrecoverystatsstatspublicrecoveryget) | **GET** /stats/public/recovery | Public Recovery Stats |
| [**refreshConnectedAccountTokenArtistsArtistIdConnectAccountsAccountIdRefreshPost**](ExpansionApi.md#refreshconnectedaccounttokenartistsartistidconnectaccountsaccountidrefreshpost) | **POST** /artists/{artist_id}/connect/accounts/{account_id}/refresh | Refresh Connected Account Token |
| [**removeTeamMemberArtistsArtistIdTeamMembersMemberIdDelete**](ExpansionApi.md#removeteammemberartistsartistidteammembersmemberiddelete) | **DELETE** /artists/{artist_id}/team/members/{member_id} | Remove Team Member |
| [**upsertNotificationPreferencesArtistsArtistIdNotificationsPreferencesPut**](ExpansionApi.md#upsertnotificationpreferencesartistsartistidnotificationspreferencesput) | **PUT** /artists/{artist_id}/notifications/preferences | Upsert Notification Preferences |
| [**urgentSolNotificationCheckArtistsArtistIdNotificationsUrgentSolCheckPost**](ExpansionApi.md#urgentsolnotificationcheckartistsartistidnotificationsurgentsolcheckpost) | **POST** /artists/{artist_id}/notifications/urgent-sol-check | Urgent Sol Notification Check |
| [**whiteLabelPortfolioB2bPortfolioOrgIdGet**](ExpansionApi.md#whitelabelportfoliob2bportfolioorgidget) | **GET** /b2b/portfolio/{org_id} | White Label Portfolio |



## addTeamMemberArtistsArtistIdTeamMembersPost

> TeamMemberSchema addTeamMemberArtistsArtistIdTeamMembersPost(artistId, teamMemberCreate, xActorEmail, xActorRole)

Add Team Member

### Example

```ts
import {
  Configuration,
  ExpansionApi,
} from '@xr7/sdk';
import type { AddTeamMemberArtistsArtistIdTeamMembersPostRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new ExpansionApi();

  const body = {
    // string
    artistId: artistId_example,
    // TeamMemberCreate
    teamMemberCreate: ...,
    // string (optional)
    xActorEmail: xActorEmail_example,
    // string (optional)
    xActorRole: xActorRole_example,
  } satisfies AddTeamMemberArtistsArtistIdTeamMembersPostRequest;

  try {
    const data = await api.addTeamMemberArtistsArtistIdTeamMembersPost(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **artistId** | `string` |  | [Defaults to `undefined`] |
| **teamMemberCreate** | [TeamMemberCreate](TeamMemberCreate.md) |  | |
| **xActorEmail** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xActorRole** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

[**TeamMemberSchema**](TeamMemberSchema.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **201** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## anchorEvidencePacketClaimsClaimIdEvidenceAnchorPost

> EvidenceAnchorSchema anchorEvidencePacketClaimsClaimIdEvidenceAnchorPost(claimId)

Anchor Evidence Packet

### Example

```ts
import {
  Configuration,
  ExpansionApi,
} from '@xr7/sdk';
import type { AnchorEvidencePacketClaimsClaimIdEvidenceAnchorPostRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new ExpansionApi();

  const body = {
    // string
    claimId: claimId_example,
  } satisfies AnchorEvidencePacketClaimsClaimIdEvidenceAnchorPostRequest;

  try {
    const data = await api.anchorEvidencePacketClaimsClaimIdEvidenceAnchorPost(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **claimId** | `string` |  | [Defaults to `undefined`] |

### Return type

[**EvidenceAnchorSchema**](EvidenceAnchorSchema.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## benchmarkPercentilesArtistsArtistIdRecoveryBenchmarkPercentilesGet

> any benchmarkPercentilesArtistsArtistIdRecoveryBenchmarkPercentilesGet(artistId, xActorEmail, xActorRole)

Benchmark Percentiles

### Example

```ts
import {
  Configuration,
  ExpansionApi,
} from '@xr7/sdk';
import type { BenchmarkPercentilesArtistsArtistIdRecoveryBenchmarkPercentilesGetRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new ExpansionApi();

  const body = {
    // string
    artistId: artistId_example,
    // string (optional)
    xActorEmail: xActorEmail_example,
    // string (optional)
    xActorRole: xActorRole_example,
  } satisfies BenchmarkPercentilesArtistsArtistIdRecoveryBenchmarkPercentilesGetRequest;

  try {
    const data = await api.benchmarkPercentilesArtistsArtistIdRecoveryBenchmarkPercentilesGet(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **artistId** | `string` |  | [Defaults to `undefined`] |
| **xActorEmail** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xActorRole** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

**any**

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## createOauthSessionArtistsArtistIdConnectOauthSessionPost

> any createOauthSessionArtistsArtistIdConnectOauthSessionPost(artistId, oAuthSessionCreateRequest, xActorEmail, xActorRole)

Create Oauth Session

### Example

```ts
import {
  Configuration,
  ExpansionApi,
} from '@xr7/sdk';
import type { CreateOauthSessionArtistsArtistIdConnectOauthSessionPostRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new ExpansionApi();

  const body = {
    // string
    artistId: artistId_example,
    // OAuthSessionCreateRequest
    oAuthSessionCreateRequest: ...,
    // string (optional)
    xActorEmail: xActorEmail_example,
    // string (optional)
    xActorRole: xActorRole_example,
  } satisfies CreateOauthSessionArtistsArtistIdConnectOauthSessionPostRequest;

  try {
    const data = await api.createOauthSessionArtistsArtistIdConnectOauthSessionPost(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **artistId** | `string` |  | [Defaults to `undefined`] |
| **oAuthSessionCreateRequest** | [OAuthSessionCreateRequest](OAuthSessionCreateRequest.md) |  | |
| **xActorEmail** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xActorRole** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

**any**

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## dashboardChartsDataArtistsArtistIdDashboardChartsGet

> any dashboardChartsDataArtistsArtistIdDashboardChartsGet(artistId, days, xActorEmail, xActorRole)

Dashboard Charts Data

### Example

```ts
import {
  Configuration,
  ExpansionApi,
} from '@xr7/sdk';
import type { DashboardChartsDataArtistsArtistIdDashboardChartsGetRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new ExpansionApi();

  const body = {
    // string
    artistId: artistId_example,
    // number (optional)
    days: 56,
    // string (optional)
    xActorEmail: xActorEmail_example,
    // string (optional)
    xActorRole: xActorRole_example,
  } satisfies DashboardChartsDataArtistsArtistIdDashboardChartsGetRequest;

  try {
    const data = await api.dashboardChartsDataArtistsArtistIdDashboardChartsGet(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **artistId** | `string` |  | [Defaults to `undefined`] |
| **days** | `number` |  | [Optional] [Defaults to `180`] |
| **xActorEmail** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xActorRole** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

**any**

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## disconnectConnectedAccountArtistsArtistIdConnectAccountsAccountIdDelete

> any disconnectConnectedAccountArtistsArtistIdConnectAccountsAccountIdDelete(artistId, accountId, xActorEmail, xActorRole)

Disconnect Connected Account

### Example

```ts
import {
  Configuration,
  ExpansionApi,
} from '@xr7/sdk';
import type { DisconnectConnectedAccountArtistsArtistIdConnectAccountsAccountIdDeleteRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new ExpansionApi();

  const body = {
    // string
    artistId: artistId_example,
    // string
    accountId: accountId_example,
    // string (optional)
    xActorEmail: xActorEmail_example,
    // string (optional)
    xActorRole: xActorRole_example,
  } satisfies DisconnectConnectedAccountArtistsArtistIdConnectAccountsAccountIdDeleteRequest;

  try {
    const data = await api.disconnectConnectedAccountArtistsArtistIdConnectAccountsAccountIdDelete(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **artistId** | `string` |  | [Defaults to `undefined`] |
| **accountId** | `string` |  | [Defaults to `undefined`] |
| **xActorEmail** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xActorRole** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

**any**

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## dispatchNotificationArtistsArtistIdNotificationsDispatchPost

> any dispatchNotificationArtistsArtistIdNotificationsDispatchPost(artistId, notificationDispatchRequest, xActorEmail, xActorRole)

Dispatch Notification

### Example

```ts
import {
  Configuration,
  ExpansionApi,
} from '@xr7/sdk';
import type { DispatchNotificationArtistsArtistIdNotificationsDispatchPostRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new ExpansionApi();

  const body = {
    // string
    artistId: artistId_example,
    // NotificationDispatchRequest
    notificationDispatchRequest: ...,
    // string (optional)
    xActorEmail: xActorEmail_example,
    // string (optional)
    xActorRole: xActorRole_example,
  } satisfies DispatchNotificationArtistsArtistIdNotificationsDispatchPostRequest;

  try {
    const data = await api.dispatchNotificationArtistsArtistIdNotificationsDispatchPost(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **artistId** | `string` |  | [Defaults to `undefined`] |
| **notificationDispatchRequest** | [NotificationDispatchRequest](NotificationDispatchRequest.md) |  | |
| **xActorEmail** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xActorRole** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

**any**

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## educationGuideDetailEducationGuidesGuideIdGet

> any educationGuideDetailEducationGuidesGuideIdGet(guideId)

Education Guide Detail

### Example

```ts
import {
  Configuration,
  ExpansionApi,
} from '@xr7/sdk';
import type { EducationGuideDetailEducationGuidesGuideIdGetRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new ExpansionApi();

  const body = {
    // string
    guideId: guideId_example,
  } satisfies EducationGuideDetailEducationGuidesGuideIdGetRequest;

  try {
    const data = await api.educationGuideDetailEducationGuidesGuideIdGet(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **guideId** | `string` |  | [Defaults to `undefined`] |

### Return type

**any**

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## educationGuidesIndexEducationGuidesGet

> any educationGuidesIndexEducationGuidesGet()

Education Guides Index

### Example

```ts
import {
  Configuration,
  ExpansionApi,
} from '@xr7/sdk';
import type { EducationGuidesIndexEducationGuidesGetRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new ExpansionApi();

  try {
    const data = await api.educationGuidesIndexEducationGuidesGet();
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters

This endpoint does not need any parameter.

### Return type

**any**

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## estimateWithholdingArtistsArtistIdIntelligenceWithholdingEstimatePost

> any estimateWithholdingArtistsArtistIdIntelligenceWithholdingEstimatePost(artistId, currencyTaxEstimateRequest, xActorEmail, xActorRole)

Estimate Withholding

### Example

```ts
import {
  Configuration,
  ExpansionApi,
} from '@xr7/sdk';
import type { EstimateWithholdingArtistsArtistIdIntelligenceWithholdingEstimatePostRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new ExpansionApi();

  const body = {
    // string
    artistId: artistId_example,
    // CurrencyTaxEstimateRequest
    currencyTaxEstimateRequest: ...,
    // string (optional)
    xActorEmail: xActorEmail_example,
    // string (optional)
    xActorRole: xActorRole_example,
  } satisfies EstimateWithholdingArtistsArtistIdIntelligenceWithholdingEstimatePostRequest;

  try {
    const data = await api.estimateWithholdingArtistsArtistIdIntelligenceWithholdingEstimatePost(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **artistId** | `string` |  | [Defaults to `undefined`] |
| **currencyTaxEstimateRequest** | [CurrencyTaxEstimateRequest](CurrencyTaxEstimateRequest.md) |  | |
| **xActorEmail** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xActorRole** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

**any**

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## exchangeOauthCodeArtistsArtistIdConnectOauthSessionSessionIdExchangePost

> any exchangeOauthCodeArtistsArtistIdConnectOauthSessionSessionIdExchangePost(artistId, sessionId, oAuthTokenExchangeRequest, xActorEmail, xActorRole)

Exchange Oauth Code

### Example

```ts
import {
  Configuration,
  ExpansionApi,
} from '@xr7/sdk';
import type { ExchangeOauthCodeArtistsArtistIdConnectOauthSessionSessionIdExchangePostRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new ExpansionApi();

  const body = {
    // string
    artistId: artistId_example,
    // string
    sessionId: sessionId_example,
    // OAuthTokenExchangeRequest
    oAuthTokenExchangeRequest: ...,
    // string (optional)
    xActorEmail: xActorEmail_example,
    // string (optional)
    xActorRole: xActorRole_example,
  } satisfies ExchangeOauthCodeArtistsArtistIdConnectOauthSessionSessionIdExchangePostRequest;

  try {
    const data = await api.exchangeOauthCodeArtistsArtistIdConnectOauthSessionSessionIdExchangePost(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **artistId** | `string` |  | [Defaults to `undefined`] |
| **sessionId** | `string` |  | [Defaults to `undefined`] |
| **oAuthTokenExchangeRequest** | [OAuthTokenExchangeRequest](OAuthTokenExchangeRequest.md) |  | |
| **xActorEmail** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xActorRole** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

**any**

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## exportSummaryReportArtistsArtistIdReportsSummaryGet

> any exportSummaryReportArtistsArtistIdReportsSummaryGet(artistId, format, xActorEmail, xActorRole)

Export Summary Report

### Example

```ts
import {
  Configuration,
  ExpansionApi,
} from '@xr7/sdk';
import type { ExportSummaryReportArtistsArtistIdReportsSummaryGetRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new ExpansionApi();

  const body = {
    // string
    artistId: artistId_example,
    // string (optional)
    format: format_example,
    // string (optional)
    xActorEmail: xActorEmail_example,
    // string (optional)
    xActorRole: xActorRole_example,
  } satisfies ExportSummaryReportArtistsArtistIdReportsSummaryGetRequest;

  try {
    const data = await api.exportSummaryReportArtistsArtistIdReportsSummaryGet(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **artistId** | `string` |  | [Defaults to `undefined`] |
| **format** | `string` |  | [Optional] [Defaults to `&#39;json&#39;`] |
| **xActorEmail** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xActorRole** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

**any**

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## generateAuditDemandLetterArtistsArtistIdRecoveryAuditDemandLetterGet

> any generateAuditDemandLetterArtistsArtistIdRecoveryAuditDemandLetterGet(artistId, xActorEmail, xActorRole)

Generate Audit Demand Letter

### Example

```ts
import {
  Configuration,
  ExpansionApi,
} from '@xr7/sdk';
import type { GenerateAuditDemandLetterArtistsArtistIdRecoveryAuditDemandLetterGetRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new ExpansionApi();

  const body = {
    // string
    artistId: artistId_example,
    // string (optional)
    xActorEmail: xActorEmail_example,
    // string (optional)
    xActorRole: xActorRole_example,
  } satisfies GenerateAuditDemandLetterArtistsArtistIdRecoveryAuditDemandLetterGetRequest;

  try {
    const data = await api.generateAuditDemandLetterArtistsArtistIdRecoveryAuditDemandLetterGet(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **artistId** | `string` |  | [Defaults to `undefined`] |
| **xActorEmail** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xActorRole** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

**any**

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## generateClaimTemplateArtistsArtistIdClaimsTemplatesPost

> any generateClaimTemplateArtistsArtistIdClaimsTemplatesPost(artistId, claimTemplateRequest, xActorEmail, xActorRole)

Generate Claim Template

### Example

```ts
import {
  Configuration,
  ExpansionApi,
} from '@xr7/sdk';
import type { GenerateClaimTemplateArtistsArtistIdClaimsTemplatesPostRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new ExpansionApi();

  const body = {
    // string
    artistId: artistId_example,
    // ClaimTemplateRequest
    claimTemplateRequest: ...,
    // string (optional)
    xActorEmail: xActorEmail_example,
    // string (optional)
    xActorRole: xActorRole_example,
  } satisfies GenerateClaimTemplateArtistsArtistIdClaimsTemplatesPostRequest;

  try {
    const data = await api.generateClaimTemplateArtistsArtistIdClaimsTemplatesPost(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **artistId** | `string` |  | [Defaults to `undefined`] |
| **claimTemplateRequest** | [ClaimTemplateRequest](ClaimTemplateRequest.md) |  | |
| **xActorEmail** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xActorRole** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

**any**

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## getNotificationPreferencesArtistsArtistIdNotificationsPreferencesGet

> NotificationPreferenceSchema getNotificationPreferencesArtistsArtistIdNotificationsPreferencesGet(artistId, xActorEmail, xActorRole)

Get Notification Preferences

### Example

```ts
import {
  Configuration,
  ExpansionApi,
} from '@xr7/sdk';
import type { GetNotificationPreferencesArtistsArtistIdNotificationsPreferencesGetRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new ExpansionApi();

  const body = {
    // string
    artistId: artistId_example,
    // string (optional)
    xActorEmail: xActorEmail_example,
    // string (optional)
    xActorRole: xActorRole_example,
  } satisfies GetNotificationPreferencesArtistsArtistIdNotificationsPreferencesGetRequest;

  try {
    const data = await api.getNotificationPreferencesArtistsArtistIdNotificationsPreferencesGet(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **artistId** | `string` |  | [Defaults to `undefined`] |
| **xActorEmail** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xActorRole** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

[**NotificationPreferenceSchema**](NotificationPreferenceSchema.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## listConnectFallbacksArtistsArtistIdConnectFallbacksGet

> any listConnectFallbacksArtistsArtistIdConnectFallbacksGet(artistId, xActorEmail, xActorRole)

List Connect Fallbacks

### Example

```ts
import {
  Configuration,
  ExpansionApi,
} from '@xr7/sdk';
import type { ListConnectFallbacksArtistsArtistIdConnectFallbacksGetRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new ExpansionApi();

  const body = {
    // string
    artistId: artistId_example,
    // string (optional)
    xActorEmail: xActorEmail_example,
    // string (optional)
    xActorRole: xActorRole_example,
  } satisfies ListConnectFallbacksArtistsArtistIdConnectFallbacksGetRequest;

  try {
    const data = await api.listConnectFallbacksArtistsArtistIdConnectFallbacksGet(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **artistId** | `string` |  | [Defaults to `undefined`] |
| **xActorEmail** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xActorRole** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

**any**

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## listConnectedAccountsArtistsArtistIdConnectAccountsGet

> any listConnectedAccountsArtistsArtistIdConnectAccountsGet(artistId, provider, tenantId, includeInactive, xActorEmail, xActorRole)

List Connected Accounts

### Example

```ts
import {
  Configuration,
  ExpansionApi,
} from '@xr7/sdk';
import type { ListConnectedAccountsArtistsArtistIdConnectAccountsGetRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new ExpansionApi();

  const body = {
    // string
    artistId: artistId_example,
    // string (optional)
    provider: provider_example,
    // string (optional)
    tenantId: tenantId_example,
    // boolean (optional)
    includeInactive: true,
    // string (optional)
    xActorEmail: xActorEmail_example,
    // string (optional)
    xActorRole: xActorRole_example,
  } satisfies ListConnectedAccountsArtistsArtistIdConnectAccountsGetRequest;

  try {
    const data = await api.listConnectedAccountsArtistsArtistIdConnectAccountsGet(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **artistId** | `string` |  | [Defaults to `undefined`] |
| **provider** | `string` |  | [Optional] [Defaults to `undefined`] |
| **tenantId** | `string` |  | [Optional] [Defaults to `undefined`] |
| **includeInactive** | `boolean` |  | [Optional] [Defaults to `false`] |
| **xActorEmail** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xActorRole** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

**any**

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## listTeamMembersArtistsArtistIdTeamMembersGet

> Array&lt;TeamMemberSchema&gt; listTeamMembersArtistsArtistIdTeamMembersGet(artistId, xActorEmail, xActorRole)

List Team Members

### Example

```ts
import {
  Configuration,
  ExpansionApi,
} from '@xr7/sdk';
import type { ListTeamMembersArtistsArtistIdTeamMembersGetRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new ExpansionApi();

  const body = {
    // string
    artistId: artistId_example,
    // string (optional)
    xActorEmail: xActorEmail_example,
    // string (optional)
    xActorRole: xActorRole_example,
  } satisfies ListTeamMembersArtistsArtistIdTeamMembersGetRequest;

  try {
    const data = await api.listTeamMembersArtistsArtistIdTeamMembersGet(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **artistId** | `string` |  | [Defaults to `undefined`] |
| **xActorEmail** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xActorRole** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

[**Array&lt;TeamMemberSchema&gt;**](TeamMemberSchema.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## partnershipTargetsPartnershipsTargetsGet

> any partnershipTargetsPartnershipsTargetsGet()

Partnership Targets

### Example

```ts
import {
  Configuration,
  ExpansionApi,
} from '@xr7/sdk';
import type { PartnershipTargetsPartnershipsTargetsGetRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new ExpansionApi();

  try {
    const data = await api.partnershipTargetsPartnershipsTargetsGet();
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters

This endpoint does not need any parameter.

### Return type

**any**

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## predictTotalRecoverableArtistsArtistIdMlPredictRecoverablePost

> any predictTotalRecoverableArtistsArtistIdMlPredictRecoverablePost(artistId, predictRecoverableRequest, xActorEmail, xActorRole)

Predict Total Recoverable

### Example

```ts
import {
  Configuration,
  ExpansionApi,
} from '@xr7/sdk';
import type { PredictTotalRecoverableArtistsArtistIdMlPredictRecoverablePostRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new ExpansionApi();

  const body = {
    // string
    artistId: artistId_example,
    // PredictRecoverableRequest
    predictRecoverableRequest: ...,
    // string (optional)
    xActorEmail: xActorEmail_example,
    // string (optional)
    xActorRole: xActorRole_example,
  } satisfies PredictTotalRecoverableArtistsArtistIdMlPredictRecoverablePostRequest;

  try {
    const data = await api.predictTotalRecoverableArtistsArtistIdMlPredictRecoverablePost(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **artistId** | `string` |  | [Defaults to `undefined`] |
| **predictRecoverableRequest** | [PredictRecoverableRequest](PredictRecoverableRequest.md) |  | |
| **xActorEmail** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xActorRole** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

**any**

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## publicRecoveryStatsStatsPublicRecoveryGet

> any publicRecoveryStatsStatsPublicRecoveryGet()

Public Recovery Stats

### Example

```ts
import {
  Configuration,
  ExpansionApi,
} from '@xr7/sdk';
import type { PublicRecoveryStatsStatsPublicRecoveryGetRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new ExpansionApi();

  try {
    const data = await api.publicRecoveryStatsStatsPublicRecoveryGet();
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters

This endpoint does not need any parameter.

### Return type

**any**

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## refreshConnectedAccountTokenArtistsArtistIdConnectAccountsAccountIdRefreshPost

> any refreshConnectedAccountTokenArtistsArtistIdConnectAccountsAccountIdRefreshPost(artistId, accountId, oAuthTokenRefreshRequest, xActorEmail, xActorRole)

Refresh Connected Account Token

### Example

```ts
import {
  Configuration,
  ExpansionApi,
} from '@xr7/sdk';
import type { RefreshConnectedAccountTokenArtistsArtistIdConnectAccountsAccountIdRefreshPostRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new ExpansionApi();

  const body = {
    // string
    artistId: artistId_example,
    // string
    accountId: accountId_example,
    // OAuthTokenRefreshRequest
    oAuthTokenRefreshRequest: ...,
    // string (optional)
    xActorEmail: xActorEmail_example,
    // string (optional)
    xActorRole: xActorRole_example,
  } satisfies RefreshConnectedAccountTokenArtistsArtistIdConnectAccountsAccountIdRefreshPostRequest;

  try {
    const data = await api.refreshConnectedAccountTokenArtistsArtistIdConnectAccountsAccountIdRefreshPost(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **artistId** | `string` |  | [Defaults to `undefined`] |
| **accountId** | `string` |  | [Defaults to `undefined`] |
| **oAuthTokenRefreshRequest** | [OAuthTokenRefreshRequest](OAuthTokenRefreshRequest.md) |  | |
| **xActorEmail** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xActorRole** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

**any**

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## removeTeamMemberArtistsArtistIdTeamMembersMemberIdDelete

> any removeTeamMemberArtistsArtistIdTeamMembersMemberIdDelete(artistId, memberId, xActorEmail, xActorRole)

Remove Team Member

### Example

```ts
import {
  Configuration,
  ExpansionApi,
} from '@xr7/sdk';
import type { RemoveTeamMemberArtistsArtistIdTeamMembersMemberIdDeleteRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new ExpansionApi();

  const body = {
    // string
    artistId: artistId_example,
    // string
    memberId: memberId_example,
    // string (optional)
    xActorEmail: xActorEmail_example,
    // string (optional)
    xActorRole: xActorRole_example,
  } satisfies RemoveTeamMemberArtistsArtistIdTeamMembersMemberIdDeleteRequest;

  try {
    const data = await api.removeTeamMemberArtistsArtistIdTeamMembersMemberIdDelete(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **artistId** | `string` |  | [Defaults to `undefined`] |
| **memberId** | `string` |  | [Defaults to `undefined`] |
| **xActorEmail** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xActorRole** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

**any**

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## upsertNotificationPreferencesArtistsArtistIdNotificationsPreferencesPut

> NotificationPreferenceSchema upsertNotificationPreferencesArtistsArtistIdNotificationsPreferencesPut(artistId, notificationPreferenceUpsert, xActorEmail, xActorRole)

Upsert Notification Preferences

### Example

```ts
import {
  Configuration,
  ExpansionApi,
} from '@xr7/sdk';
import type { UpsertNotificationPreferencesArtistsArtistIdNotificationsPreferencesPutRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new ExpansionApi();

  const body = {
    // string
    artistId: artistId_example,
    // NotificationPreferenceUpsert
    notificationPreferenceUpsert: ...,
    // string (optional)
    xActorEmail: xActorEmail_example,
    // string (optional)
    xActorRole: xActorRole_example,
  } satisfies UpsertNotificationPreferencesArtistsArtistIdNotificationsPreferencesPutRequest;

  try {
    const data = await api.upsertNotificationPreferencesArtistsArtistIdNotificationsPreferencesPut(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **artistId** | `string` |  | [Defaults to `undefined`] |
| **notificationPreferenceUpsert** | [NotificationPreferenceUpsert](NotificationPreferenceUpsert.md) |  | |
| **xActorEmail** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xActorRole** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

[**NotificationPreferenceSchema**](NotificationPreferenceSchema.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## urgentSolNotificationCheckArtistsArtistIdNotificationsUrgentSolCheckPost

> any urgentSolNotificationCheckArtistsArtistIdNotificationsUrgentSolCheckPost(artistId, xActorEmail, xActorRole)

Urgent Sol Notification Check

### Example

```ts
import {
  Configuration,
  ExpansionApi,
} from '@xr7/sdk';
import type { UrgentSolNotificationCheckArtistsArtistIdNotificationsUrgentSolCheckPostRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new ExpansionApi();

  const body = {
    // string
    artistId: artistId_example,
    // string (optional)
    xActorEmail: xActorEmail_example,
    // string (optional)
    xActorRole: xActorRole_example,
  } satisfies UrgentSolNotificationCheckArtistsArtistIdNotificationsUrgentSolCheckPostRequest;

  try {
    const data = await api.urgentSolNotificationCheckArtistsArtistIdNotificationsUrgentSolCheckPost(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **artistId** | `string` |  | [Defaults to `undefined`] |
| **xActorEmail** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xActorRole** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

**any**

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## whiteLabelPortfolioB2bPortfolioOrgIdGet

> any whiteLabelPortfolioB2bPortfolioOrgIdGet(orgId)

White Label Portfolio

### Example

```ts
import {
  Configuration,
  ExpansionApi,
} from '@xr7/sdk';
import type { WhiteLabelPortfolioB2bPortfolioOrgIdGetRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new ExpansionApi();

  const body = {
    // string
    orgId: orgId_example,
  } satisfies WhiteLabelPortfolioB2bPortfolioOrgIdGetRequest;

  try {
    const data = await api.whiteLabelPortfolioB2bPortfolioOrgIdGet(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **orgId** | `string` |  | [Defaults to `undefined`] |

### Return type

**any**

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

