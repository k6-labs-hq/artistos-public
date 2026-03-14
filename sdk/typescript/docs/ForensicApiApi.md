# ForensicApiApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**authConnectAuthConnectProviderPost**](ForensicApiApi.md#authconnectauthconnectproviderpost) | **POST** /auth/connect/{provider} | Auth Connect |
| [**authProvidersAuthProvidersGet**](ForensicApiApi.md#authprovidersauthprovidersget) | **GET** /auth/providers | Auth Providers |
| [**confirmCatalogCatalogConfirmPost**](ForensicApiApi.md#confirmcatalogcatalogconfirmpost) | **POST** /catalog/confirm | Confirm Catalog |
| [**getCatalogCatalogGet**](ForensicApiApi.md#getcatalogcatalogget) | **GET** /catalog | Get Catalog |
| [**getLedgerEntryLedgerEntryIdGet**](ForensicApiApi.md#getledgerentryledgerentryidget) | **GET** /ledger/{entry_id} | Get Ledger Entry |
| [**listLedgerLedgerGet**](ForensicApiApi.md#listledgerledgerget) | **GET** /ledger | List Ledger |
| [**listVarianceVarianceGet**](ForensicApiApi.md#listvariancevarianceget) | **GET** /variance | List Variance |
| [**recoverySubmitRecoveryClaimIdSubmitPost**](ForensicApiApi.md#recoverysubmitrecoveryclaimidsubmitpost) | **POST** /recovery/{claim_id}/submit | Recovery Submit |
| [**statementsStatusStatementsStatementIdStatusGet**](ForensicApiApi.md#statementsstatusstatementsstatementidstatusget) | **GET** /statements/{statement_id}/status | Statements Status |
| [**statementsUploadStatementsUploadPost**](ForensicApiApi.md#statementsuploadstatementsuploadpost) | **POST** /statements/upload | Statements Upload |
| [**varianceEvidenceVarianceVarianceIdEvidenceGet**](ForensicApiApi.md#varianceevidencevariancevarianceidevidenceget) | **GET** /variance/{variance_id}/evidence | Variance Evidence |



## authConnectAuthConnectProviderPost

> AuthConnectResponse authConnectAuthConnectProviderPost(provider, redirectUri)

Auth Connect

### Example

```ts
import {
  Configuration,
  ForensicApiApi,
} from '@xr7/sdk';
import type { AuthConnectAuthConnectProviderPostRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new ForensicApiApi();

  const body = {
    // string
    provider: provider_example,
    // string
    redirectUri: redirectUri_example,
  } satisfies AuthConnectAuthConnectProviderPostRequest;

  try {
    const data = await api.authConnectAuthConnectProviderPost(body);
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
| **provider** | `string` |  | [Defaults to `undefined`] |
| **redirectUri** | `string` |  | [Defaults to `undefined`] |

### Return type

[**AuthConnectResponse**](AuthConnectResponse.md)

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


## authProvidersAuthProvidersGet

> { [key: string]: Array&lt;{ [key: string]: any; }&gt;; } authProvidersAuthProvidersGet()

Auth Providers

### Example

```ts
import {
  Configuration,
  ForensicApiApi,
} from '@xr7/sdk';
import type { AuthProvidersAuthProvidersGetRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new ForensicApiApi();

  try {
    const data = await api.authProvidersAuthProvidersGet();
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

**{ [key: string]: Array<{ [key: string]: any; }>; }**

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


## confirmCatalogCatalogConfirmPost

> any confirmCatalogCatalogConfirmPost(xR7ApiRoutersForensicCatalogConfirmRequest)

Confirm Catalog

### Example

```ts
import {
  Configuration,
  ForensicApiApi,
} from '@xr7/sdk';
import type { ConfirmCatalogCatalogConfirmPostRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new ForensicApiApi();

  const body = {
    // XR7ApiRoutersForensicCatalogConfirmRequest
    xR7ApiRoutersForensicCatalogConfirmRequest: ...,
  } satisfies ConfirmCatalogCatalogConfirmPostRequest;

  try {
    const data = await api.confirmCatalogCatalogConfirmPost(body);
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
| **xR7ApiRoutersForensicCatalogConfirmRequest** | [XR7ApiRoutersForensicCatalogConfirmRequest](XR7ApiRoutersForensicCatalogConfirmRequest.md) |  | |

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


## getCatalogCatalogGet

> any getCatalogCatalogGet(artistId)

Get Catalog

### Example

```ts
import {
  Configuration,
  ForensicApiApi,
} from '@xr7/sdk';
import type { GetCatalogCatalogGetRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new ForensicApiApi();

  const body = {
    // string
    artistId: artistId_example,
  } satisfies GetCatalogCatalogGetRequest;

  try {
    const data = await api.getCatalogCatalogGet(body);
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


## getLedgerEntryLedgerEntryIdGet

> ImmutableLedgerEntrySchema getLedgerEntryLedgerEntryIdGet(entryId)

Get Ledger Entry

### Example

```ts
import {
  Configuration,
  ForensicApiApi,
} from '@xr7/sdk';
import type { GetLedgerEntryLedgerEntryIdGetRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new ForensicApiApi();

  const body = {
    // string
    entryId: entryId_example,
  } satisfies GetLedgerEntryLedgerEntryIdGetRequest;

  try {
    const data = await api.getLedgerEntryLedgerEntryIdGet(body);
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
| **entryId** | `string` |  | [Defaults to `undefined`] |

### Return type

[**ImmutableLedgerEntrySchema**](ImmutableLedgerEntrySchema.md)

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


## listLedgerLedgerGet

> Array&lt;ImmutableLedgerEntrySchema&gt; listLedgerLedgerGet(artistId)

List Ledger

### Example

```ts
import {
  Configuration,
  ForensicApiApi,
} from '@xr7/sdk';
import type { ListLedgerLedgerGetRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new ForensicApiApi();

  const body = {
    // string
    artistId: artistId_example,
  } satisfies ListLedgerLedgerGetRequest;

  try {
    const data = await api.listLedgerLedgerGet(body);
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

[**Array&lt;ImmutableLedgerEntrySchema&gt;**](ImmutableLedgerEntrySchema.md)

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


## listVarianceVarianceGet

> any listVarianceVarianceGet(artistId)

List Variance

### Example

```ts
import {
  Configuration,
  ForensicApiApi,
} from '@xr7/sdk';
import type { ListVarianceVarianceGetRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new ForensicApiApi();

  const body = {
    // string
    artistId: artistId_example,
  } satisfies ListVarianceVarianceGetRequest;

  try {
    const data = await api.listVarianceVarianceGet(body);
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


## recoverySubmitRecoveryClaimIdSubmitPost

> RecoverySubmitResponse recoverySubmitRecoveryClaimIdSubmitPost(claimId)

Recovery Submit

### Example

```ts
import {
  Configuration,
  ForensicApiApi,
} from '@xr7/sdk';
import type { RecoverySubmitRecoveryClaimIdSubmitPostRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new ForensicApiApi();

  const body = {
    // string
    claimId: claimId_example,
  } satisfies RecoverySubmitRecoveryClaimIdSubmitPostRequest;

  try {
    const data = await api.recoverySubmitRecoveryClaimIdSubmitPost(body);
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

[**RecoverySubmitResponse**](RecoverySubmitResponse.md)

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


## statementsStatusStatementsStatementIdStatusGet

> any statementsStatusStatementsStatementIdStatusGet(statementId)

Statements Status

### Example

```ts
import {
  Configuration,
  ForensicApiApi,
} from '@xr7/sdk';
import type { StatementsStatusStatementsStatementIdStatusGetRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new ForensicApiApi();

  const body = {
    // string
    statementId: statementId_example,
  } satisfies StatementsStatusStatementsStatementIdStatusGetRequest;

  try {
    const data = await api.statementsStatusStatementsStatementIdStatusGet(body);
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
| **statementId** | `string` |  | [Defaults to `undefined`] |

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


## statementsUploadStatementsUploadPost

> ForensicUniversalRoyaltyEventSchema statementsUploadStatementsUploadPost(forensicUniversalRoyaltyEventCreate)

Statements Upload

Minimal statement upload endpoint that stores a normalized universal event row.

### Example

```ts
import {
  Configuration,
  ForensicApiApi,
} from '@xr7/sdk';
import type { StatementsUploadStatementsUploadPostRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new ForensicApiApi();

  const body = {
    // ForensicUniversalRoyaltyEventCreate
    forensicUniversalRoyaltyEventCreate: ...,
  } satisfies StatementsUploadStatementsUploadPostRequest;

  try {
    const data = await api.statementsUploadStatementsUploadPost(body);
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
| **forensicUniversalRoyaltyEventCreate** | [ForensicUniversalRoyaltyEventCreate](ForensicUniversalRoyaltyEventCreate.md) |  | |

### Return type

[**ForensicUniversalRoyaltyEventSchema**](ForensicUniversalRoyaltyEventSchema.md)

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


## varianceEvidenceVarianceVarianceIdEvidenceGet

> any varianceEvidenceVarianceVarianceIdEvidenceGet(varianceId)

Variance Evidence

### Example

```ts
import {
  Configuration,
  ForensicApiApi,
} from '@xr7/sdk';
import type { VarianceEvidenceVarianceVarianceIdEvidenceGetRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new ForensicApiApi();

  const body = {
    // string
    varianceId: varianceId_example,
  } satisfies VarianceEvidenceVarianceVarianceIdEvidenceGetRequest;

  try {
    const data = await api.varianceEvidenceVarianceVarianceIdEvidenceGet(body);
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
| **varianceId** | `string` |  | [Defaults to `undefined`] |

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

