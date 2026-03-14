# IntelligenceApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**createOutcomeFeedbackArtistsArtistIdIntelligenceFeedbackPost**](IntelligenceApi.md#createoutcomefeedbackartistsartistidintelligencefeedbackpost) | **POST** /artists/{artist_id}/intelligence/feedback | Create Outcome Feedback |
| [**extractContractTermsArtistsArtistIdIntelligenceContractsExtractPost**](IntelligenceApi.md#extractcontracttermsartistsartistidintelligencecontractsextractpost) | **POST** /artists/{artist_id}/intelligence/contracts/extract | Extract Contract Terms |
| [**extractContractTermsUploadArtistsArtistIdIntelligenceContractsExtractUploadPost**](IntelligenceApi.md#extractcontracttermsuploadartistsartistidintelligencecontractsextractuploadpost) | **POST** /artists/{artist_id}/intelligence/contracts/extract-upload | Extract Contract Terms Upload |
| [**getCalibrationHealthArtistsArtistIdIntelligenceCalibrationGet**](IntelligenceApi.md#getcalibrationhealthartistsartistidintelligencecalibrationget) | **GET** /artists/{artist_id}/intelligence/calibration | Get Calibration Health |
| [**ingestRoyaltyLedgerArtistsArtistIdIntelligenceLedgerIngestPost**](IntelligenceApi.md#ingestroyaltyledgerartistsartistidintelligenceledgeringestpost) | **POST** /artists/{artist_id}/intelligence/ledger/ingest | Ingest Royalty Ledger |
| [**listFeedbackEventsArtistsArtistIdIntelligenceFeedbackEventsGet**](IntelligenceApi.md#listfeedbackeventsartistsartistidintelligencefeedbackeventsget) | **GET** /artists/{artist_id}/intelligence/feedback/events | List Feedback Events |
| [**rankByExpectedUtilityArtistsArtistIdIntelligenceRankUtilityPost**](IntelligenceApi.md#rankbyexpectedutilityartistsartistidintelligencerankutilitypost) | **POST** /artists/{artist_id}/intelligence/rank-utility | Rank By Expected Utility |
| [**simulateExpectedPayoutArtistsArtistIdIntelligenceSimulateExpectedPayoutPost**](IntelligenceApi.md#simulateexpectedpayoutartistsartistidintelligencesimulateexpectedpayoutpost) | **POST** /artists/{artist_id}/intelligence/simulate-expected-payout | Simulate Expected Payout |



## createOutcomeFeedbackArtistsArtistIdIntelligenceFeedbackPost

> RecoveryOutcomeFeedbackSchema createOutcomeFeedbackArtistsArtistIdIntelligenceFeedbackPost(artistId, structuredFeedbackRequest)

Create Outcome Feedback

### Example

```ts
import {
  Configuration,
  IntelligenceApi,
} from '@xr7/sdk';
import type { CreateOutcomeFeedbackArtistsArtistIdIntelligenceFeedbackPostRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new IntelligenceApi();

  const body = {
    // string
    artistId: artistId_example,
    // StructuredFeedbackRequest
    structuredFeedbackRequest: ...,
  } satisfies CreateOutcomeFeedbackArtistsArtistIdIntelligenceFeedbackPostRequest;

  try {
    const data = await api.createOutcomeFeedbackArtistsArtistIdIntelligenceFeedbackPost(body);
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
| **structuredFeedbackRequest** | [StructuredFeedbackRequest](StructuredFeedbackRequest.md) |  | |

### Return type

[**RecoveryOutcomeFeedbackSchema**](RecoveryOutcomeFeedbackSchema.md)

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


## extractContractTermsArtistsArtistIdIntelligenceContractsExtractPost

> any extractContractTermsArtistsArtistIdIntelligenceContractsExtractPost(artistId, contractExtractRequest)

Extract Contract Terms

### Example

```ts
import {
  Configuration,
  IntelligenceApi,
} from '@xr7/sdk';
import type { ExtractContractTermsArtistsArtistIdIntelligenceContractsExtractPostRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new IntelligenceApi();

  const body = {
    // string
    artistId: artistId_example,
    // ContractExtractRequest
    contractExtractRequest: ...,
  } satisfies ExtractContractTermsArtistsArtistIdIntelligenceContractsExtractPostRequest;

  try {
    const data = await api.extractContractTermsArtistsArtistIdIntelligenceContractsExtractPost(body);
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
| **contractExtractRequest** | [ContractExtractRequest](ContractExtractRequest.md) |  | |

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


## extractContractTermsUploadArtistsArtistIdIntelligenceContractsExtractUploadPost

> any extractContractTermsUploadArtistsArtistIdIntelligenceContractsExtractUploadPost(artistId, file, contractId, effectiveStart, effectiveEnd, extractedFrom)

Extract Contract Terms Upload

### Example

```ts
import {
  Configuration,
  IntelligenceApi,
} from '@xr7/sdk';
import type { ExtractContractTermsUploadArtistsArtistIdIntelligenceContractsExtractUploadPostRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new IntelligenceApi();

  const body = {
    // string
    artistId: artistId_example,
    // string
    file: file_example,
    // string (optional)
    contractId: contractId_example,
    // string (optional)
    effectiveStart: effectiveStart_example,
    // string (optional)
    effectiveEnd: effectiveEnd_example,
    // string (optional)
    extractedFrom: extractedFrom_example,
  } satisfies ExtractContractTermsUploadArtistsArtistIdIntelligenceContractsExtractUploadPostRequest;

  try {
    const data = await api.extractContractTermsUploadArtistsArtistIdIntelligenceContractsExtractUploadPost(body);
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
| **file** | `string` |  | [Defaults to `undefined`] |
| **contractId** | `string` |  | [Optional] [Defaults to `undefined`] |
| **effectiveStart** | `string` |  | [Optional] [Defaults to `undefined`] |
| **effectiveEnd** | `string` |  | [Optional] [Defaults to `undefined`] |
| **extractedFrom** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

**any**

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: `multipart/form-data`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## getCalibrationHealthArtistsArtistIdIntelligenceCalibrationGet

> any getCalibrationHealthArtistsArtistIdIntelligenceCalibrationGet(artistId)

Get Calibration Health

### Example

```ts
import {
  Configuration,
  IntelligenceApi,
} from '@xr7/sdk';
import type { GetCalibrationHealthArtistsArtistIdIntelligenceCalibrationGetRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new IntelligenceApi();

  const body = {
    // string
    artistId: artistId_example,
  } satisfies GetCalibrationHealthArtistsArtistIdIntelligenceCalibrationGetRequest;

  try {
    const data = await api.getCalibrationHealthArtistsArtistIdIntelligenceCalibrationGet(body);
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


## ingestRoyaltyLedgerArtistsArtistIdIntelligenceLedgerIngestPost

> any ingestRoyaltyLedgerArtistsArtistIdIntelligenceLedgerIngestPost(artistId, ledgerIngestRequest)

Ingest Royalty Ledger

### Example

```ts
import {
  Configuration,
  IntelligenceApi,
} from '@xr7/sdk';
import type { IngestRoyaltyLedgerArtistsArtistIdIntelligenceLedgerIngestPostRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new IntelligenceApi();

  const body = {
    // string
    artistId: artistId_example,
    // LedgerIngestRequest
    ledgerIngestRequest: ...,
  } satisfies IngestRoyaltyLedgerArtistsArtistIdIntelligenceLedgerIngestPostRequest;

  try {
    const data = await api.ingestRoyaltyLedgerArtistsArtistIdIntelligenceLedgerIngestPost(body);
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
| **ledgerIngestRequest** | [LedgerIngestRequest](LedgerIngestRequest.md) |  | |

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


## listFeedbackEventsArtistsArtistIdIntelligenceFeedbackEventsGet

> Array&lt;MLFeedbackEventSchema&gt; listFeedbackEventsArtistsArtistIdIntelligenceFeedbackEventsGet(artistId)

List Feedback Events

### Example

```ts
import {
  Configuration,
  IntelligenceApi,
} from '@xr7/sdk';
import type { ListFeedbackEventsArtistsArtistIdIntelligenceFeedbackEventsGetRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new IntelligenceApi();

  const body = {
    // string
    artistId: artistId_example,
  } satisfies ListFeedbackEventsArtistsArtistIdIntelligenceFeedbackEventsGetRequest;

  try {
    const data = await api.listFeedbackEventsArtistsArtistIdIntelligenceFeedbackEventsGet(body);
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

[**Array&lt;MLFeedbackEventSchema&gt;**](MLFeedbackEventSchema.md)

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


## rankByExpectedUtilityArtistsArtistIdIntelligenceRankUtilityPost

> any rankByExpectedUtilityArtistsArtistIdIntelligenceRankUtilityPost(artistId, utilityRankRequest)

Rank By Expected Utility

### Example

```ts
import {
  Configuration,
  IntelligenceApi,
} from '@xr7/sdk';
import type { RankByExpectedUtilityArtistsArtistIdIntelligenceRankUtilityPostRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new IntelligenceApi();

  const body = {
    // string
    artistId: artistId_example,
    // UtilityRankRequest
    utilityRankRequest: ...,
  } satisfies RankByExpectedUtilityArtistsArtistIdIntelligenceRankUtilityPostRequest;

  try {
    const data = await api.rankByExpectedUtilityArtistsArtistIdIntelligenceRankUtilityPost(body);
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
| **utilityRankRequest** | [UtilityRankRequest](UtilityRankRequest.md) |  | |

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


## simulateExpectedPayoutArtistsArtistIdIntelligenceSimulateExpectedPayoutPost

> any simulateExpectedPayoutArtistsArtistIdIntelligenceSimulateExpectedPayoutPost(artistId, simulatePayoutRequest)

Simulate Expected Payout

### Example

```ts
import {
  Configuration,
  IntelligenceApi,
} from '@xr7/sdk';
import type { SimulateExpectedPayoutArtistsArtistIdIntelligenceSimulateExpectedPayoutPostRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new IntelligenceApi();

  const body = {
    // string
    artistId: artistId_example,
    // SimulatePayoutRequest
    simulatePayoutRequest: ...,
  } satisfies SimulateExpectedPayoutArtistsArtistIdIntelligenceSimulateExpectedPayoutPostRequest;

  try {
    const data = await api.simulateExpectedPayoutArtistsArtistIdIntelligenceSimulateExpectedPayoutPost(body);
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
| **simulatePayoutRequest** | [SimulatePayoutRequest](SimulatePayoutRequest.md) |  | |

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

