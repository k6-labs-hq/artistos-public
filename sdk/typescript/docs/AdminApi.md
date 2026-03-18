# AdminApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**adminOverviewAdminOverviewGet**](AdminApi.md#adminoverviewadminoverviewget) | **GET** /admin/overview | Admin Overview |
| [**assignFounderManuallyAdminArtistsArtistIdFounderAssignPost**](AdminApi.md#assignfoundermanuallyadminartistsartistidfounderassignpost) | **POST** /admin/artists/{artist_id}/founder/assign | Assign Founder Manually |
| [**founderCohortReportAdminReportsFounderCohortGet**](AdminApi.md#foundercohortreportadminreportsfoundercohortget) | **GET** /admin/reports/founder-cohort | Founder Cohort Report |
| [**founderRosterAdminFoundersGet**](AdminApi.md#founderrosteradminfoundersget) | **GET** /admin/founders | Founder Roster |
| [**listAnomaliesAdminAnomaliesGet**](AdminApi.md#listanomaliesadminanomaliesget) | **GET** /admin/anomalies | List Anomalies |
| [**listArtistsAdminArtistsGet**](AdminApi.md#listartistsadminartistsget) | **GET** /admin/artists | List Artists |
| [**listAuditLogsAdminAuditLogsGet**](AdminApi.md#listauditlogsadminauditlogsget) | **GET** /admin/audit-logs | List Audit Logs |
| [**listClaimsAdminClaimsGet**](AdminApi.md#listclaimsadminclaimsget) | **GET** /admin/claims | List Claims |
| [**listReviewQueueAdminReviewQueueGet**](AdminApi.md#listreviewqueueadminreviewqueueget) | **GET** /admin/review-queue | List Review Queue |
| [**listTransactionsAdminTransactionsGet**](AdminApi.md#listtransactionsadmintransactionsget) | **GET** /admin/transactions | List Transactions |
| [**solRiskReportAdminReportsSolRiskGet**](AdminApi.md#solriskreportadminreportssolriskget) | **GET** /admin/reports/sol-risk | Sol Risk Report |
| [**updateFounderCohortLimitAdminFounderCohortLimitPut**](AdminApi.md#updatefoundercohortlimitadminfoundercohortlimitput) | **PUT** /admin/founder/cohort-limit | Update Founder Cohort Limit |



## adminOverviewAdminOverviewGet

> any adminOverviewAdminOverviewGet(xAdminKey, xAdminActor)

Admin Overview

### Example

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

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **xAdminKey** | `string` |  | [Optional] [Defaults to `&#39;&#39;`] |
| **xAdminActor** | `string` |  | [Optional] [Defaults to `undefined`] |

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


## assignFounderManuallyAdminArtistsArtistIdFounderAssignPost

> any assignFounderManuallyAdminArtistsArtistIdFounderAssignPost(artistId, founderAssignRequest, xAdminKey, xAdminActor)

Assign Founder Manually

### Example

```ts
import {
  Configuration,
  AdminApi,
} from '@xr7/sdk';
import type { AssignFounderManuallyAdminArtistsArtistIdFounderAssignPostRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new AdminApi();

  const body = {
    // string
    artistId: artistId_example,
    // FounderAssignRequest
    founderAssignRequest: ...,
    // string (optional)
    xAdminKey: xAdminKey_example,
    // string (optional)
    xAdminActor: xAdminActor_example,
  } satisfies AssignFounderManuallyAdminArtistsArtistIdFounderAssignPostRequest;

  try {
    const data = await api.assignFounderManuallyAdminArtistsArtistIdFounderAssignPost(body);
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
| **founderAssignRequest** | [FounderAssignRequest](FounderAssignRequest.md) |  | |
| **xAdminKey** | `string` |  | [Optional] [Defaults to `&#39;&#39;`] |
| **xAdminActor** | `string` |  | [Optional] [Defaults to `undefined`] |

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


## founderCohortReportAdminReportsFounderCohortGet

> any founderCohortReportAdminReportsFounderCohortGet(xAdminKey, xAdminActor)

Founder Cohort Report

### Example

```ts
import {
  Configuration,
  AdminApi,
} from '@xr7/sdk';
import type { FounderCohortReportAdminReportsFounderCohortGetRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new AdminApi();

  const body = {
    // string (optional)
    xAdminKey: xAdminKey_example,
    // string (optional)
    xAdminActor: xAdminActor_example,
  } satisfies FounderCohortReportAdminReportsFounderCohortGetRequest;

  try {
    const data = await api.founderCohortReportAdminReportsFounderCohortGet(body);
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
| **xAdminKey** | `string` |  | [Optional] [Defaults to `&#39;&#39;`] |
| **xAdminActor** | `string` |  | [Optional] [Defaults to `undefined`] |

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


## founderRosterAdminFoundersGet

> any founderRosterAdminFoundersGet(limit, offset, xAdminKey, xAdminActor)

Founder Roster

### Example

```ts
import {
  Configuration,
  AdminApi,
} from '@xr7/sdk';
import type { FounderRosterAdminFoundersGetRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new AdminApi();

  const body = {
    // number (optional)
    limit: 56,
    // number (optional)
    offset: 56,
    // string (optional)
    xAdminKey: xAdminKey_example,
    // string (optional)
    xAdminActor: xAdminActor_example,
  } satisfies FounderRosterAdminFoundersGetRequest;

  try {
    const data = await api.founderRosterAdminFoundersGet(body);
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
| **limit** | `number` |  | [Optional] [Defaults to `200`] |
| **offset** | `number` |  | [Optional] [Defaults to `0`] |
| **xAdminKey** | `string` |  | [Optional] [Defaults to `&#39;&#39;`] |
| **xAdminActor** | `string` |  | [Optional] [Defaults to `undefined`] |

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


## listAnomaliesAdminAnomaliesGet

> any listAnomaliesAdminAnomaliesGet(status, severity, artistId, limit, offset, xAdminKey, xAdminActor)

List Anomalies

### Example

```ts
import {
  Configuration,
  AdminApi,
} from '@xr7/sdk';
import type { ListAnomaliesAdminAnomaliesGetRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new AdminApi();

  const body = {
    // string (optional)
    status: status_example,
    // string (optional)
    severity: severity_example,
    // string (optional)
    artistId: artistId_example,
    // number (optional)
    limit: 56,
    // number (optional)
    offset: 56,
    // string (optional)
    xAdminKey: xAdminKey_example,
    // string (optional)
    xAdminActor: xAdminActor_example,
  } satisfies ListAnomaliesAdminAnomaliesGetRequest;

  try {
    const data = await api.listAnomaliesAdminAnomaliesGet(body);
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
| **status** | `string` |  | [Optional] [Defaults to `undefined`] |
| **severity** | `string` |  | [Optional] [Defaults to `undefined`] |
| **artistId** | `string` |  | [Optional] [Defaults to `undefined`] |
| **limit** | `number` |  | [Optional] [Defaults to `50`] |
| **offset** | `number` |  | [Optional] [Defaults to `0`] |
| **xAdminKey** | `string` |  | [Optional] [Defaults to `&#39;&#39;`] |
| **xAdminActor** | `string` |  | [Optional] [Defaults to `undefined`] |

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


## listArtistsAdminArtistsGet

> any listArtistsAdminArtistsGet(status, q, sort, limit, offset, xAdminKey, xAdminActor)

List Artists

### Example

```ts
import {
  Configuration,
  AdminApi,
} from '@xr7/sdk';
import type { ListArtistsAdminArtistsGetRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new AdminApi();

  const body = {
    // string (optional)
    status: status_example,
    // string (optional)
    q: q_example,
    // string (optional)
    sort: sort_example,
    // number (optional)
    limit: 56,
    // number (optional)
    offset: 56,
    // string (optional)
    xAdminKey: xAdminKey_example,
    // string (optional)
    xAdminActor: xAdminActor_example,
  } satisfies ListArtistsAdminArtistsGetRequest;

  try {
    const data = await api.listArtistsAdminArtistsGet(body);
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
| **status** | `string` |  | [Optional] [Defaults to `undefined`] |
| **q** | `string` |  | [Optional] [Defaults to `undefined`] |
| **sort** | `string` |  | [Optional] [Defaults to `&#39;created_at_desc&#39;`] |
| **limit** | `number` |  | [Optional] [Defaults to `50`] |
| **offset** | `number` |  | [Optional] [Defaults to `0`] |
| **xAdminKey** | `string` |  | [Optional] [Defaults to `&#39;&#39;`] |
| **xAdminActor** | `string` |  | [Optional] [Defaults to `undefined`] |

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


## listAuditLogsAdminAuditLogsGet

> Array&lt;AdminAuditLogSchema&gt; listAuditLogsAdminAuditLogsGet(actorFilter, action, limit, offset, xAdminKey, xAdminActor)

List Audit Logs

### Example

```ts
import {
  Configuration,
  AdminApi,
} from '@xr7/sdk';
import type { ListAuditLogsAdminAuditLogsGetRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new AdminApi();

  const body = {
    // string (optional)
    actorFilter: actorFilter_example,
    // string (optional)
    action: action_example,
    // number (optional)
    limit: 56,
    // number (optional)
    offset: 56,
    // string (optional)
    xAdminKey: xAdminKey_example,
    // string (optional)
    xAdminActor: xAdminActor_example,
  } satisfies ListAuditLogsAdminAuditLogsGetRequest;

  try {
    const data = await api.listAuditLogsAdminAuditLogsGet(body);
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
| **actorFilter** | `string` |  | [Optional] [Defaults to `undefined`] |
| **action** | `string` |  | [Optional] [Defaults to `undefined`] |
| **limit** | `number` |  | [Optional] [Defaults to `100`] |
| **offset** | `number` |  | [Optional] [Defaults to `0`] |
| **xAdminKey** | `string` |  | [Optional] [Defaults to `&#39;&#39;`] |
| **xAdminActor** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

[**Array&lt;AdminAuditLogSchema&gt;**](AdminAuditLogSchema.md)

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


## listClaimsAdminClaimsGet

> any listClaimsAdminClaimsGet(status, artistId, jurisdiction, sort, limit, offset, xAdminKey, xAdminActor)

List Claims

### Example

```ts
import {
  Configuration,
  AdminApi,
} from '@xr7/sdk';
import type { ListClaimsAdminClaimsGetRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new AdminApi();

  const body = {
    // string (optional)
    status: status_example,
    // string (optional)
    artistId: artistId_example,
    // string (optional)
    jurisdiction: jurisdiction_example,
    // string (optional)
    sort: sort_example,
    // number (optional)
    limit: 56,
    // number (optional)
    offset: 56,
    // string (optional)
    xAdminKey: xAdminKey_example,
    // string (optional)
    xAdminActor: xAdminActor_example,
  } satisfies ListClaimsAdminClaimsGetRequest;

  try {
    const data = await api.listClaimsAdminClaimsGet(body);
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
| **status** | `string` |  | [Optional] [Defaults to `undefined`] |
| **artistId** | `string` |  | [Optional] [Defaults to `undefined`] |
| **jurisdiction** | `string` |  | [Optional] [Defaults to `undefined`] |
| **sort** | `string` |  | [Optional] [Defaults to `&#39;updated_at_desc&#39;`] |
| **limit** | `number` |  | [Optional] [Defaults to `50`] |
| **offset** | `number` |  | [Optional] [Defaults to `0`] |
| **xAdminKey** | `string` |  | [Optional] [Defaults to `&#39;&#39;`] |
| **xAdminActor** | `string` |  | [Optional] [Defaults to `undefined`] |

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


## listReviewQueueAdminReviewQueueGet

> any listReviewQueueAdminReviewQueueGet(status, artistId, sourceType, limit, offset, xAdminKey, xAdminActor)

List Review Queue

### Example

```ts
import {
  Configuration,
  AdminApi,
} from '@xr7/sdk';
import type { ListReviewQueueAdminReviewQueueGetRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new AdminApi();

  const body = {
    // string (optional)
    status: status_example,
    // string (optional)
    artistId: artistId_example,
    // string (optional)
    sourceType: sourceType_example,
    // number (optional)
    limit: 56,
    // number (optional)
    offset: 56,
    // string (optional)
    xAdminKey: xAdminKey_example,
    // string (optional)
    xAdminActor: xAdminActor_example,
  } satisfies ListReviewQueueAdminReviewQueueGetRequest;

  try {
    const data = await api.listReviewQueueAdminReviewQueueGet(body);
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
| **status** | `string` |  | [Optional] [Defaults to `undefined`] |
| **artistId** | `string` |  | [Optional] [Defaults to `undefined`] |
| **sourceType** | `string` |  | [Optional] [Defaults to `undefined`] |
| **limit** | `number` |  | [Optional] [Defaults to `50`] |
| **offset** | `number` |  | [Optional] [Defaults to `0`] |
| **xAdminKey** | `string` |  | [Optional] [Defaults to `&#39;&#39;`] |
| **xAdminActor** | `string` |  | [Optional] [Defaults to `undefined`] |

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


## listTransactionsAdminTransactionsGet

> any listTransactionsAdminTransactionsGet(status, txType, artistId, limit, offset, xAdminKey, xAdminActor)

List Transactions

### Example

```ts
import {
  Configuration,
  AdminApi,
} from '@xr7/sdk';
import type { ListTransactionsAdminTransactionsGetRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new AdminApi();

  const body = {
    // string (optional)
    status: status_example,
    // string (optional)
    txType: txType_example,
    // string (optional)
    artistId: artistId_example,
    // number (optional)
    limit: 56,
    // number (optional)
    offset: 56,
    // string (optional)
    xAdminKey: xAdminKey_example,
    // string (optional)
    xAdminActor: xAdminActor_example,
  } satisfies ListTransactionsAdminTransactionsGetRequest;

  try {
    const data = await api.listTransactionsAdminTransactionsGet(body);
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
| **status** | `string` |  | [Optional] [Defaults to `undefined`] |
| **txType** | `string` |  | [Optional] [Defaults to `undefined`] |
| **artistId** | `string` |  | [Optional] [Defaults to `undefined`] |
| **limit** | `number` |  | [Optional] [Defaults to `50`] |
| **offset** | `number` |  | [Optional] [Defaults to `0`] |
| **xAdminKey** | `string` |  | [Optional] [Defaults to `&#39;&#39;`] |
| **xAdminActor** | `string` |  | [Optional] [Defaults to `undefined`] |

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


## solRiskReportAdminReportsSolRiskGet

> any solRiskReportAdminReportsSolRiskGet(jurisdiction, xAdminKey, xAdminActor)

Sol Risk Report

### Example

```ts
import {
  Configuration,
  AdminApi,
} from '@xr7/sdk';
import type { SolRiskReportAdminReportsSolRiskGetRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new AdminApi();

  const body = {
    // string (optional)
    jurisdiction: jurisdiction_example,
    // string (optional)
    xAdminKey: xAdminKey_example,
    // string (optional)
    xAdminActor: xAdminActor_example,
  } satisfies SolRiskReportAdminReportsSolRiskGetRequest;

  try {
    const data = await api.solRiskReportAdminReportsSolRiskGet(body);
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
| **jurisdiction** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAdminKey** | `string` |  | [Optional] [Defaults to `&#39;&#39;`] |
| **xAdminActor** | `string` |  | [Optional] [Defaults to `undefined`] |

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


## updateFounderCohortLimitAdminFounderCohortLimitPut

> any updateFounderCohortLimitAdminFounderCohortLimitPut(founderCohortLimitUpdateRequest, xAdminKey, xAdminActor)

Update Founder Cohort Limit

### Example

```ts
import {
  Configuration,
  AdminApi,
} from '@xr7/sdk';
import type { UpdateFounderCohortLimitAdminFounderCohortLimitPutRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new AdminApi();

  const body = {
    // FounderCohortLimitUpdateRequest
    founderCohortLimitUpdateRequest: ...,
    // string (optional)
    xAdminKey: xAdminKey_example,
    // string (optional)
    xAdminActor: xAdminActor_example,
  } satisfies UpdateFounderCohortLimitAdminFounderCohortLimitPutRequest;

  try {
    const data = await api.updateFounderCohortLimitAdminFounderCohortLimitPut(body);
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
| **founderCohortLimitUpdateRequest** | [FounderCohortLimitUpdateRequest](FounderCohortLimitUpdateRequest.md) |  | |
| **xAdminKey** | `string` |  | [Optional] [Defaults to `&#39;&#39;`] |
| **xAdminActor** | `string` |  | [Optional] [Defaults to `undefined`] |

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

