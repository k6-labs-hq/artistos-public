# AdminApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**adminOverviewAdminOverviewGet**](AdminApi.md#adminoverviewadminoverviewget) | **GET** /admin/overview | Admin Overview |
| [**listAnomaliesAdminAnomaliesGet**](AdminApi.md#listanomaliesadminanomaliesget) | **GET** /admin/anomalies | List Anomalies |
| [**listArtistsAdminArtistsGet**](AdminApi.md#listartistsadminartistsget) | **GET** /admin/artists | List Artists |
| [**listAuditLogsAdminAuditLogsGet**](AdminApi.md#listauditlogsadminauditlogsget) | **GET** /admin/audit-logs | List Audit Logs |
| [**listClaimsAdminClaimsGet**](AdminApi.md#listclaimsadminclaimsget) | **GET** /admin/claims | List Claims |
| [**listReviewQueueAdminReviewQueueGet**](AdminApi.md#listreviewqueueadminreviewqueueget) | **GET** /admin/review-queue | List Review Queue |
| [**listTransactionsAdminTransactionsGet**](AdminApi.md#listtransactionsadmintransactionsget) | **GET** /admin/transactions | List Transactions |



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

> any listClaimsAdminClaimsGet(status, artistId, sort, limit, offset, xAdminKey, xAdminActor)

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

