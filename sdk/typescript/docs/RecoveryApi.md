# RecoveryApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**auditEligibilityArtistsArtistIdRecoveryAuditEligibilityGet**](RecoveryApi.md#auditeligibilityartistsartistidrecoveryauditeligibilityget) | **GET** /artists/{artist_id}/recovery/audit-eligibility | Audit Eligibility |
| [**priorityQueueArtistsArtistIdRecoveryPriorityQueueGet**](RecoveryApi.md#priorityqueueartistsartistidrecoverypriorityqueueget) | **GET** /artists/{artist_id}/recovery/priority-queue | Priority Queue |
| [**rateBenchmarkArtistsArtistIdRecoveryRateBenchmarkGet**](RecoveryApi.md#ratebenchmarkartistsartistidrecoveryratebenchmarkget) | **GET** /artists/{artist_id}/recovery/rate-benchmark | Rate Benchmark |
| [**recoupmentArtistsArtistIdRecoveryRecoupmentGet**](RecoveryApi.md#recoupmentartistsartistidrecoveryrecoupmentget) | **GET** /artists/{artist_id}/recovery/recoupment | Recoupment |
| [**solStatusArtistsArtistIdRecoverySolStatusGet**](RecoveryApi.md#solstatusartistsartistidrecoverysolstatusget) | **GET** /artists/{artist_id}/recovery/sol-status | Sol Status |



## auditEligibilityArtistsArtistIdRecoveryAuditEligibilityGet

> any auditEligibilityArtistsArtistIdRecoveryAuditEligibilityGet(artistId)

Audit Eligibility

Return audit-rights eligibility for all contracts.  Contracts are ranked by estimated potential recovery and eligibility status (NEVER_AUDITED, ELIGIBLE, ELIGIBLE_SOON, NOT_YET_ELIGIBLE).

### Example

```ts
import {
  Configuration,
  RecoveryApi,
} from '@xr7/sdk';
import type { AuditEligibilityArtistsArtistIdRecoveryAuditEligibilityGetRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new RecoveryApi();

  const body = {
    // string
    artistId: artistId_example,
  } satisfies AuditEligibilityArtistsArtistIdRecoveryAuditEligibilityGetRequest;

  try {
    const data = await api.auditEligibilityArtistsArtistIdRecoveryAuditEligibilityGet(body);
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


## priorityQueueArtistsArtistIdRecoveryPriorityQueueGet

> any priorityQueueArtistsArtistIdRecoveryPriorityQueueGet(artistId)

Priority Queue

Return a unified, prioritised action queue for the artist.  Merges open anomalies and in-flight claims into a single ranked list, scoring each item by (estimated_recoverable × confidence × urgency) / age. The artist (or their representative) should work through this list top-to-bottom to maximise recovery.

### Example

```ts
import {
  Configuration,
  RecoveryApi,
} from '@xr7/sdk';
import type { PriorityQueueArtistsArtistIdRecoveryPriorityQueueGetRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new RecoveryApi();

  const body = {
    // string
    artistId: artistId_example,
  } satisfies PriorityQueueArtistsArtistIdRecoveryPriorityQueueGetRequest;

  try {
    const data = await api.priorityQueueArtistsArtistIdRecoveryPriorityQueueGet(body);
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


## rateBenchmarkArtistsArtistIdRecoveryRateBenchmarkGet

> any rateBenchmarkArtistsArtistIdRecoveryRateBenchmarkGet(artistId)

Rate Benchmark

Compare the artist\&#39;s actual payment rates against industry benchmarks.  Returns a full report including per-event-type comparisons, estimated underpayment amounts, and a tier classification (ABOVE_MARKET, AT_MARKET, BELOW_MARKET, CRITICAL).

### Example

```ts
import {
  Configuration,
  RecoveryApi,
} from '@xr7/sdk';
import type { RateBenchmarkArtistsArtistIdRecoveryRateBenchmarkGetRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new RecoveryApi();

  const body = {
    // string
    artistId: artistId_example,
  } satisfies RateBenchmarkArtistsArtistIdRecoveryRateBenchmarkGetRequest;

  try {
    const data = await api.rateBenchmarkArtistsArtistIdRecoveryRateBenchmarkGet(body);
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


## recoupmentArtistsArtistIdRecoveryRecoupmentGet

> any recoupmentArtistsArtistIdRecoveryRecoupmentGet(artistId)

Recoupment

Return recoupment position and any discrepancy flags for all contracts with advance/recoupment provisions.  Flags RECOUPMENT_DISCREPANCY when the calculated balance differs from the counterparty-reported balance, and EXCESS_RECOUPMENT when more than the advance has been recouped.

### Example

```ts
import {
  Configuration,
  RecoveryApi,
} from '@xr7/sdk';
import type { RecoupmentArtistsArtistIdRecoveryRecoupmentGetRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new RecoveryApi();

  const body = {
    // string
    artistId: artistId_example,
  } satisfies RecoupmentArtistsArtistIdRecoveryRecoupmentGetRequest;

  try {
    const data = await api.recoupmentArtistsArtistIdRecoveryRecoupmentGet(body);
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


## solStatusArtistsArtistIdRecoverySolStatusGet

> any solStatusArtistsArtistIdRecoverySolStatusGet(artistId)

Sol Status

Return statute-of-limitations classification for all open anomalies.  Each anomaly is classified as EXPIRED, URGENT (&lt;90 days), AT_RISK (90–180 days), or OK (&gt;180 days remaining), sorted most-urgent first. Also returns an overall SOL exposure summary.

### Example

```ts
import {
  Configuration,
  RecoveryApi,
} from '@xr7/sdk';
import type { SolStatusArtistsArtistIdRecoverySolStatusGetRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new RecoveryApi();

  const body = {
    // string
    artistId: artistId_example,
  } satisfies SolStatusArtistsArtistIdRecoverySolStatusGetRequest;

  try {
    const data = await api.solStatusArtistsArtistIdRecoverySolStatusGet(body);
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

