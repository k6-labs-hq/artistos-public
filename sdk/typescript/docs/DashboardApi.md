# DashboardApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**agentTraceArtistsArtistIdAgentTraceRunIdGet**](DashboardApi.md#agenttraceartistsartistidagenttracerunidget) | **GET** /artists/{artist_id}/agent-trace/{run_id} | Agent Trace |
| [**chatRoyaltiesArtistsArtistIdChatRoyaltiesPost**](DashboardApi.md#chatroyaltiesartistsartistidchatroyaltiespost) | **POST** /artists/{artist_id}/chat/royalties | Chat Royalties |
| [**dashboardBenchmarksArtistsArtistIdBenchmarksGet**](DashboardApi.md#dashboardbenchmarksartistsartistidbenchmarksget) | **GET** /artists/{artist_id}/benchmarks | Dashboard Benchmarks |
| [**dashboardFlowArtistsArtistIdDashboardFlowGet**](DashboardApi.md#dashboardflowartistsartistiddashboardflowget) | **GET** /artists/{artist_id}/dashboard/flow | Dashboard Flow |
| [**exportFullTransparencyArtistsArtistIdExportFullTransparencyGet**](DashboardApi.md#exportfulltransparencyartistsartistidexportfulltransparencyget) | **GET** /artists/{artist_id}/export/full-transparency | Export Full Transparency |
| [**exportGuidanceArtistsArtistIdDashboardExportGuidanceGet**](DashboardApi.md#exportguidanceartistsartistiddashboardexportguidanceget) | **GET** /artists/{artist_id}/dashboard/export-guidance | Export Guidance |
| [**getArtistDashboardArtistsArtistIdDashboardGet**](DashboardApi.md#getartistdashboardartistsartistiddashboardget) | **GET** /artists/{artist_id}/dashboard | Get Artist Dashboard |
| [**getDashboardUiDashboardUiGet**](DashboardApi.md#getdashboarduidashboarduiget) | **GET** /dashboard/ui | Get Dashboard Ui |



## agentTraceArtistsArtistIdAgentTraceRunIdGet

> any agentTraceArtistsArtistIdAgentTraceRunIdGet(artistId, runId)

Agent Trace

### Example

```ts
import {
  Configuration,
  DashboardApi,
} from '@xr7/sdk';
import type { AgentTraceArtistsArtistIdAgentTraceRunIdGetRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new DashboardApi();

  const body = {
    // string
    artistId: artistId_example,
    // string
    runId: runId_example,
  } satisfies AgentTraceArtistsArtistIdAgentTraceRunIdGetRequest;

  try {
    const data = await api.agentTraceArtistsArtistIdAgentTraceRunIdGet(body);
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
| **runId** | `string` |  | [Defaults to `undefined`] |

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


## chatRoyaltiesArtistsArtistIdChatRoyaltiesPost

> any chatRoyaltiesArtistsArtistIdChatRoyaltiesPost(artistId, question)

Chat Royalties

### Example

```ts
import {
  Configuration,
  DashboardApi,
} from '@xr7/sdk';
import type { ChatRoyaltiesArtistsArtistIdChatRoyaltiesPostRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new DashboardApi();

  const body = {
    // string
    artistId: artistId_example,
    // string
    question: question_example,
  } satisfies ChatRoyaltiesArtistsArtistIdChatRoyaltiesPostRequest;

  try {
    const data = await api.chatRoyaltiesArtistsArtistIdChatRoyaltiesPost(body);
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
| **question** | `string` |  | [Defaults to `undefined`] |

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


## dashboardBenchmarksArtistsArtistIdBenchmarksGet

> any dashboardBenchmarksArtistsArtistIdBenchmarksGet(artistId)

Dashboard Benchmarks

### Example

```ts
import {
  Configuration,
  DashboardApi,
} from '@xr7/sdk';
import type { DashboardBenchmarksArtistsArtistIdBenchmarksGetRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new DashboardApi();

  const body = {
    // string
    artistId: artistId_example,
  } satisfies DashboardBenchmarksArtistsArtistIdBenchmarksGetRequest;

  try {
    const data = await api.dashboardBenchmarksArtistsArtistIdBenchmarksGet(body);
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


## dashboardFlowArtistsArtistIdDashboardFlowGet

> any dashboardFlowArtistsArtistIdDashboardFlowGet(artistId)

Dashboard Flow

### Example

```ts
import {
  Configuration,
  DashboardApi,
} from '@xr7/sdk';
import type { DashboardFlowArtistsArtistIdDashboardFlowGetRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new DashboardApi();

  const body = {
    // string
    artistId: artistId_example,
  } satisfies DashboardFlowArtistsArtistIdDashboardFlowGetRequest;

  try {
    const data = await api.dashboardFlowArtistsArtistIdDashboardFlowGet(body);
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


## exportFullTransparencyArtistsArtistIdExportFullTransparencyGet

> any exportFullTransparencyArtistsArtistIdExportFullTransparencyGet(artistId)

Export Full Transparency

### Example

```ts
import {
  Configuration,
  DashboardApi,
} from '@xr7/sdk';
import type { ExportFullTransparencyArtistsArtistIdExportFullTransparencyGetRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new DashboardApi();

  const body = {
    // string
    artistId: artistId_example,
  } satisfies ExportFullTransparencyArtistsArtistIdExportFullTransparencyGetRequest;

  try {
    const data = await api.exportFullTransparencyArtistsArtistIdExportFullTransparencyGet(body);
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


## exportGuidanceArtistsArtistIdDashboardExportGuidanceGet

> any exportGuidanceArtistsArtistIdDashboardExportGuidanceGet(artistId, platform)

Export Guidance

### Example

```ts
import {
  Configuration,
  DashboardApi,
} from '@xr7/sdk';
import type { ExportGuidanceArtistsArtistIdDashboardExportGuidanceGetRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new DashboardApi();

  const body = {
    // string
    artistId: artistId_example,
    // string (optional)
    platform: platform_example,
  } satisfies ExportGuidanceArtistsArtistIdDashboardExportGuidanceGetRequest;

  try {
    const data = await api.exportGuidanceArtistsArtistIdDashboardExportGuidanceGet(body);
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
| **platform** | `string` |  | [Optional] [Defaults to `&#39;youtube&#39;`] |

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


## getArtistDashboardArtistsArtistIdDashboardGet

> any getArtistDashboardArtistsArtistIdDashboardGet(artistId)

Get Artist Dashboard

Return the artist\&#39;s full recovery dashboard.  **leakage_discovered** - &#x60;&#x60;total_anomalies&#x60;&#x60; — total number of anomalies detected - &#x60;&#x60;total_estimated_recoverable&#x60;&#x60; — sum of estimated recoverable amounts - &#x60;&#x60;by_category&#x60;&#x60; — breakdown by revenue category (ROYALTY, TOURING, etc.) - &#x60;&#x60;by_severity&#x60;&#x60; — breakdown by severity (LOW / MEDIUM / HIGH / CRITICAL) - &#x60;&#x60;recent_discoveries&#x60;&#x60; — last 10 newly detected anomalies  **in_pursuit** - &#x60;&#x60;active_claim_count&#x60;&#x60; — number of open claims - &#x60;&#x60;total_amount_in_pursuit&#x60;&#x60; — total dollar value of active claims - &#x60;&#x60;total_gross_recovered&#x60;&#x60; — total recovered across all closed/paid claims - &#x60;&#x60;total_net_recovered&#x60;&#x60; — gross minus XR7 contingency fees  **recovered_and_deposited** - &#x60;&#x60;total_deposited&#x60;&#x60; — sum of all Trolley disbursements received - &#x60;&#x60;deposits&#x60;&#x60; — per-deposit log with Trolley payment IDs  **balance_still_pursuing** - &#x60;&#x60;balance_still_pursuing&#x60;&#x60; — the key number: money we are still chasing - &#x60;&#x60;total_pending_deposit&#x60;&#x60; — approved but not yet ACH-settled  **deadlines** - &#x60;&#x60;expired_count&#x60;&#x60; — anomalies whose SOL window has already closed - &#x60;&#x60;urgent_count&#x60;&#x60; — anomalies with &lt;90 days remaining on their SOL window - &#x60;&#x60;at_risk_count&#x60;&#x60; — anomalies with 90–180 days remaining - &#x60;&#x60;top_urgent_items&#x60;&#x60; — up to 5 most time-sensitive anomalies with days_remaining  **priority_actions** - &#x60;&#x60;top_10_actions&#x60;&#x60; — ranked action items (anomalies + claims) by ROI × urgency - &#x60;&#x60;total_open_items&#x60;&#x60; — total items in the priority queue  **catalog_health** - &#x60;&#x60;health_score&#x60;&#x60; — ML composite score 0–100 - &#x60;&#x60;grade&#x60;&#x60; — letter grade A–F - &#x60;&#x60;signals&#x60;&#x60; — per-signal breakdown (metadata, payment regularity, etc.) - &#x60;&#x60;recommendations&#x60;&#x60; — list of actionable improvement suggestions  **earnings_trend** - &#x60;&#x60;trend&#x60;&#x60; — GROWING / FLAT / DECLINING / INSUFFICIENT_DATA - &#x60;&#x60;predicted_total&#x60;&#x60; — predicted earnings over next 90 days - &#x60;&#x60;predicted_low&#x60;&#x60; / &#x60;&#x60;predicted_high&#x60;&#x60; — 95% confidence interval  **activity_feed** - Up to 50 timestamped events: leakage discoveries, claim updates,   and payment deposits, newest first.

### Example

```ts
import {
  Configuration,
  DashboardApi,
} from '@xr7/sdk';
import type { GetArtistDashboardArtistsArtistIdDashboardGetRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new DashboardApi();

  const body = {
    // string
    artistId: artistId_example,
  } satisfies GetArtistDashboardArtistsArtistIdDashboardGetRequest;

  try {
    const data = await api.getArtistDashboardArtistsArtistIdDashboardGet(body);
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


## getDashboardUiDashboardUiGet

> any getDashboardUiDashboardUiGet(orgId)

Get Dashboard Ui

Serve the standalone artist recovery dashboard UI page.

### Example

```ts
import {
  Configuration,
  DashboardApi,
} from '@xr7/sdk';
import type { GetDashboardUiDashboardUiGetRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new DashboardApi();

  const body = {
    // string (optional)
    orgId: orgId_example,
  } satisfies GetDashboardUiDashboardUiGetRequest;

  try {
    const data = await api.getDashboardUiDashboardUiGet(body);
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
| **orgId** | `string` |  | [Optional] [Defaults to `undefined`] |

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

