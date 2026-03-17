# IntelligenceApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**catalogValuationArtistsArtistIdMlCatalogValuationPost**](IntelligenceApi.md#catalogvaluationartistsartistidmlcatalogvaluationpost) | **POST** /artists/{artist_id}/ml/catalog-valuation | Catalog Valuation |
| [**createOutcomeFeedbackArtistsArtistIdIntelligenceFeedbackPost**](IntelligenceApi.md#createoutcomefeedbackartistsartistidintelligencefeedbackpost) | **POST** /artists/{artist_id}/intelligence/feedback | Create Outcome Feedback |
| [**extractContractTermsArtistsArtistIdIntelligenceContractsExtractPost**](IntelligenceApi.md#extractcontracttermsartistsartistidintelligencecontractsextractpost) | **POST** /artists/{artist_id}/intelligence/contracts/extract | Extract Contract Terms |
| [**extractContractTermsUploadArtistsArtistIdIntelligenceContractsExtractUploadPost**](IntelligenceApi.md#extractcontracttermsuploadartistsartistidintelligencecontractsextractuploadpost) | **POST** /artists/{artist_id}/intelligence/contracts/extract-upload | Extract Contract Terms Upload |
| [**financingMatchesArtistsArtistIdMlFinancingMatchesPost**](IntelligenceApi.md#financingmatchesartistsartistidmlfinancingmatchespost) | **POST** /artists/{artist_id}/ml/financing-matches | Financing Matches |
| [**getCalibrationHealthArtistsArtistIdIntelligenceCalibrationGet**](IntelligenceApi.md#getcalibrationhealthartistsartistidintelligencecalibrationget) | **GET** /artists/{artist_id}/intelligence/calibration | Get Calibration Health |
| [**ingestRoyaltyLedgerArtistsArtistIdIntelligenceLedgerIngestPost**](IntelligenceApi.md#ingestroyaltyledgerartistsartistidintelligenceledgeringestpost) | **POST** /artists/{artist_id}/intelligence/ledger/ingest | Ingest Royalty Ledger |
| [**listFeedbackEventsArtistsArtistIdIntelligenceFeedbackEventsGet**](IntelligenceApi.md#listfeedbackeventsartistsartistidintelligencefeedbackeventsget) | **GET** /artists/{artist_id}/intelligence/feedback/events | List Feedback Events |
| [**preSignatureContractReviewArtistsArtistIdIntelligenceContractsPreSignatureReviewPost**](IntelligenceApi.md#presignaturecontractreviewartistsartistidintelligencecontractspresignaturereviewpost) | **POST** /artists/{artist_id}/intelligence/contracts/pre-signature-review | Pre Signature Contract Review |
| [**rankByExpectedUtilityArtistsArtistIdIntelligenceRankUtilityPost**](IntelligenceApi.md#rankbyexpectedutilityartistsartistidintelligencerankutilitypost) | **POST** /artists/{artist_id}/intelligence/rank-utility | Rank By Expected Utility |
| [**registrationAutoFixArtistsArtistIdRegistrationAutoFixPost**](IntelligenceApi.md#registrationautofixartistsartistidregistrationautofixpost) | **POST** /artists/{artist_id}/registration/auto-fix | Registration Auto Fix |
| [**registrationStatusArtistsArtistIdRegistrationStatusGet**](IntelligenceApi.md#registrationstatusartistsartistidregistrationstatusget) | **GET** /artists/{artist_id}/registration/status | Registration Status |
| [**runCatalogAuditOnDemandArtistsArtistIdMlCatalogAuditPost**](IntelligenceApi.md#runcatalogauditondemandartistsartistidmlcatalogauditpost) | **POST** /artists/{artist_id}/ml/catalog-audit | Run Catalog Audit On Demand |
| [**runTaxOptimizerArtistsArtistIdIntelligenceTaxOptimizerPost**](IntelligenceApi.md#runtaxoptimizerartistsartistidintelligencetaxoptimizerpost) | **POST** /artists/{artist_id}/intelligence/tax-optimizer | Run Tax Optimizer |
| [**simulateExpectedPayoutArtistsArtistIdIntelligenceSimulateExpectedPayoutPost**](IntelligenceApi.md#simulateexpectedpayoutartistsartistidintelligencesimulateexpectedpayoutpost) | **POST** /artists/{artist_id}/intelligence/simulate-expected-payout | Simulate Expected Payout |
| [**simulateOptimizationArtistsArtistIdMlSimulateOptimizationPost**](IntelligenceApi.md#simulateoptimizationartistsartistidmlsimulateoptimizationpost) | **POST** /artists/{artist_id}/ml/simulate-optimization | Simulate Optimization |



## catalogValuationArtistsArtistIdMlCatalogValuationPost

> any catalogValuationArtistsArtistIdMlCatalogValuationPost(artistId)

Catalog Valuation

### Example

```ts
import {
  Configuration,
  IntelligenceApi,
} from '@xr7/sdk';
import type { CatalogValuationArtistsArtistIdMlCatalogValuationPostRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new IntelligenceApi();

  const body = {
    // string
    artistId: artistId_example,
  } satisfies CatalogValuationArtistsArtistIdMlCatalogValuationPostRequest;

  try {
    const data = await api.catalogValuationArtistsArtistIdMlCatalogValuationPost(body);
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


## financingMatchesArtistsArtistIdMlFinancingMatchesPost

> any financingMatchesArtistsArtistIdMlFinancingMatchesPost(artistId)

Financing Matches

### Example

```ts
import {
  Configuration,
  IntelligenceApi,
} from '@xr7/sdk';
import type { FinancingMatchesArtistsArtistIdMlFinancingMatchesPostRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new IntelligenceApi();

  const body = {
    // string
    artistId: artistId_example,
  } satisfies FinancingMatchesArtistsArtistIdMlFinancingMatchesPostRequest;

  try {
    const data = await api.financingMatchesArtistsArtistIdMlFinancingMatchesPost(body);
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


## preSignatureContractReviewArtistsArtistIdIntelligenceContractsPreSignatureReviewPost

> any preSignatureContractReviewArtistsArtistIdIntelligenceContractsPreSignatureReviewPost(artistId, preSignatureContractReviewRequest)

Pre Signature Contract Review

### Example

```ts
import {
  Configuration,
  IntelligenceApi,
} from '@xr7/sdk';
import type { PreSignatureContractReviewArtistsArtistIdIntelligenceContractsPreSignatureReviewPostRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new IntelligenceApi();

  const body = {
    // string
    artistId: artistId_example,
    // PreSignatureContractReviewRequest
    preSignatureContractReviewRequest: ...,
  } satisfies PreSignatureContractReviewArtistsArtistIdIntelligenceContractsPreSignatureReviewPostRequest;

  try {
    const data = await api.preSignatureContractReviewArtistsArtistIdIntelligenceContractsPreSignatureReviewPost(body);
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
| **preSignatureContractReviewRequest** | [PreSignatureContractReviewRequest](PreSignatureContractReviewRequest.md) |  | |

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


## registrationAutoFixArtistsArtistIdRegistrationAutoFixPost

> any registrationAutoFixArtistsArtistIdRegistrationAutoFixPost(artistId)

Registration Auto Fix

### Example

```ts
import {
  Configuration,
  IntelligenceApi,
} from '@xr7/sdk';
import type { RegistrationAutoFixArtistsArtistIdRegistrationAutoFixPostRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new IntelligenceApi();

  const body = {
    // string
    artistId: artistId_example,
  } satisfies RegistrationAutoFixArtistsArtistIdRegistrationAutoFixPostRequest;

  try {
    const data = await api.registrationAutoFixArtistsArtistIdRegistrationAutoFixPost(body);
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


## registrationStatusArtistsArtistIdRegistrationStatusGet

> any registrationStatusArtistsArtistIdRegistrationStatusGet(artistId)

Registration Status

### Example

```ts
import {
  Configuration,
  IntelligenceApi,
} from '@xr7/sdk';
import type { RegistrationStatusArtistsArtistIdRegistrationStatusGetRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new IntelligenceApi();

  const body = {
    // string
    artistId: artistId_example,
  } satisfies RegistrationStatusArtistsArtistIdRegistrationStatusGetRequest;

  try {
    const data = await api.registrationStatusArtistsArtistIdRegistrationStatusGet(body);
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


## runCatalogAuditOnDemandArtistsArtistIdMlCatalogAuditPost

> any runCatalogAuditOnDemandArtistsArtistIdMlCatalogAuditPost(artistId)

Run Catalog Audit On Demand

### Example

```ts
import {
  Configuration,
  IntelligenceApi,
} from '@xr7/sdk';
import type { RunCatalogAuditOnDemandArtistsArtistIdMlCatalogAuditPostRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new IntelligenceApi();

  const body = {
    // string
    artistId: artistId_example,
  } satisfies RunCatalogAuditOnDemandArtistsArtistIdMlCatalogAuditPostRequest;

  try {
    const data = await api.runCatalogAuditOnDemandArtistsArtistIdMlCatalogAuditPost(body);
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


## runTaxOptimizerArtistsArtistIdIntelligenceTaxOptimizerPost

> any runTaxOptimizerArtistsArtistIdIntelligenceTaxOptimizerPost(artistId, taxOptimizerRequest)

Run Tax Optimizer

### Example

```ts
import {
  Configuration,
  IntelligenceApi,
} from '@xr7/sdk';
import type { RunTaxOptimizerArtistsArtistIdIntelligenceTaxOptimizerPostRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new IntelligenceApi();

  const body = {
    // string
    artistId: artistId_example,
    // TaxOptimizerRequest
    taxOptimizerRequest: ...,
  } satisfies RunTaxOptimizerArtistsArtistIdIntelligenceTaxOptimizerPostRequest;

  try {
    const data = await api.runTaxOptimizerArtistsArtistIdIntelligenceTaxOptimizerPost(body);
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
| **taxOptimizerRequest** | [TaxOptimizerRequest](TaxOptimizerRequest.md) |  | |

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


## simulateOptimizationArtistsArtistIdMlSimulateOptimizationPost

> any simulateOptimizationArtistsArtistIdMlSimulateOptimizationPost(artistId, optimizationSimulationRequest)

Simulate Optimization

### Example

```ts
import {
  Configuration,
  IntelligenceApi,
} from '@xr7/sdk';
import type { SimulateOptimizationArtistsArtistIdMlSimulateOptimizationPostRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new IntelligenceApi();

  const body = {
    // string
    artistId: artistId_example,
    // OptimizationSimulationRequest
    optimizationSimulationRequest: ...,
  } satisfies SimulateOptimizationArtistsArtistIdMlSimulateOptimizationPostRequest;

  try {
    const data = await api.simulateOptimizationArtistsArtistIdMlSimulateOptimizationPost(body);
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
| **optimizationSimulationRequest** | [OptimizationSimulationRequest](OptimizationSimulationRequest.md) |  | |

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

