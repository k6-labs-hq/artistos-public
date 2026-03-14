# ClaimsApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**advanceClaimClaimsClaimIdAdvancePost**](ClaimsApi.md#advanceclaimclaimsclaimidadvancepost) | **POST** /claims/{claim_id}/advance | Advance Claim |
| [**exportEvidencePacketClaimsClaimIdEvidenceExportGet**](ClaimsApi.md#exportevidencepacketclaimsclaimidevidenceexportget) | **GET** /claims/{claim_id}/evidence/export | Export Evidence Packet |
| [**generateEvidenceClaimsClaimIdEvidencePost**](ClaimsApi.md#generateevidenceclaimsclaimidevidencepost) | **POST** /claims/{claim_id}/evidence | Generate Evidence |
| [**getClaimClaimsClaimIdGet**](ClaimsApi.md#getclaimclaimsclaimidget) | **GET** /claims/{claim_id} | Get Claim |
| [**listClaimsArtistsArtistIdClaimsGet**](ClaimsApi.md#listclaimsartistsartistidclaimsget) | **GET** /artists/{artist_id}/claims | List Claims |
| [**reconcileClaimClaimsClaimIdReconcilePost**](ClaimsApi.md#reconcileclaimclaimsclaimidreconcilepost) | **POST** /claims/{claim_id}/reconcile | Reconcile Claim |
| [**verifyEvidencePacketClaimsClaimIdEvidenceVerifyGet**](ClaimsApi.md#verifyevidencepacketclaimsclaimidevidenceverifyget) | **GET** /claims/{claim_id}/evidence/verify | Verify Evidence Packet |



## advanceClaimClaimsClaimIdAdvancePost

> ClaimSchema advanceClaimClaimsClaimIdAdvancePost(claimId)

Advance Claim

### Example

```ts
import {
  Configuration,
  ClaimsApi,
} from '@xr7/sdk';
import type { AdvanceClaimClaimsClaimIdAdvancePostRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new ClaimsApi();

  const body = {
    // string
    claimId: claimId_example,
  } satisfies AdvanceClaimClaimsClaimIdAdvancePostRequest;

  try {
    const data = await api.advanceClaimClaimsClaimIdAdvancePost(body);
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

[**ClaimSchema**](ClaimSchema.md)

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


## exportEvidencePacketClaimsClaimIdEvidenceExportGet

> any exportEvidencePacketClaimsClaimIdEvidenceExportGet(claimId, format, refresh)

Export Evidence Packet

### Example

```ts
import {
  Configuration,
  ClaimsApi,
} from '@xr7/sdk';
import type { ExportEvidencePacketClaimsClaimIdEvidenceExportGetRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new ClaimsApi();

  const body = {
    // string
    claimId: claimId_example,
    // string (optional)
    format: format_example,
    // boolean (optional)
    refresh: true,
  } satisfies ExportEvidencePacketClaimsClaimIdEvidenceExportGetRequest;

  try {
    const data = await api.exportEvidencePacketClaimsClaimIdEvidenceExportGet(body);
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
| **format** | `string` |  | [Optional] [Defaults to `&#39;zip&#39;`] |
| **refresh** | `boolean` |  | [Optional] [Defaults to `false`] |

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


## generateEvidenceClaimsClaimIdEvidencePost

> any generateEvidenceClaimsClaimIdEvidencePost(claimId)

Generate Evidence

### Example

```ts
import {
  Configuration,
  ClaimsApi,
} from '@xr7/sdk';
import type { GenerateEvidenceClaimsClaimIdEvidencePostRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new ClaimsApi();

  const body = {
    // string
    claimId: claimId_example,
  } satisfies GenerateEvidenceClaimsClaimIdEvidencePostRequest;

  try {
    const data = await api.generateEvidenceClaimsClaimIdEvidencePost(body);
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


## getClaimClaimsClaimIdGet

> ClaimSchema getClaimClaimsClaimIdGet(claimId)

Get Claim

### Example

```ts
import {
  Configuration,
  ClaimsApi,
} from '@xr7/sdk';
import type { GetClaimClaimsClaimIdGetRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new ClaimsApi();

  const body = {
    // string
    claimId: claimId_example,
  } satisfies GetClaimClaimsClaimIdGetRequest;

  try {
    const data = await api.getClaimClaimsClaimIdGet(body);
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

[**ClaimSchema**](ClaimSchema.md)

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


## listClaimsArtistsArtistIdClaimsGet

> any listClaimsArtistsArtistIdClaimsGet(artistId)

List Claims

### Example

```ts
import {
  Configuration,
  ClaimsApi,
} from '@xr7/sdk';
import type { ListClaimsArtistsArtistIdClaimsGetRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new ClaimsApi();

  const body = {
    // string
    artistId: artistId_example,
  } satisfies ListClaimsArtistsArtistIdClaimsGetRequest;

  try {
    const data = await api.listClaimsArtistsArtistIdClaimsGet(body);
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


## reconcileClaimClaimsClaimIdReconcilePost

> ClaimSchema reconcileClaimClaimsClaimIdReconcilePost(claimId, reconcileRequest)

Reconcile Claim

### Example

```ts
import {
  Configuration,
  ClaimsApi,
} from '@xr7/sdk';
import type { ReconcileClaimClaimsClaimIdReconcilePostRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new ClaimsApi();

  const body = {
    // string
    claimId: claimId_example,
    // ReconcileRequest
    reconcileRequest: ...,
  } satisfies ReconcileClaimClaimsClaimIdReconcilePostRequest;

  try {
    const data = await api.reconcileClaimClaimsClaimIdReconcilePost(body);
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
| **reconcileRequest** | [ReconcileRequest](ReconcileRequest.md) |  | |

### Return type

[**ClaimSchema**](ClaimSchema.md)

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


## verifyEvidencePacketClaimsClaimIdEvidenceVerifyGet

> any verifyEvidencePacketClaimsClaimIdEvidenceVerifyGet(claimId, expectedPriorPacketHash)

Verify Evidence Packet

### Example

```ts
import {
  Configuration,
  ClaimsApi,
} from '@xr7/sdk';
import type { VerifyEvidencePacketClaimsClaimIdEvidenceVerifyGetRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new ClaimsApi();

  const body = {
    // string
    claimId: claimId_example,
    // string (optional)
    expectedPriorPacketHash: expectedPriorPacketHash_example,
  } satisfies VerifyEvidencePacketClaimsClaimIdEvidenceVerifyGetRequest;

  try {
    const data = await api.verifyEvidencePacketClaimsClaimIdEvidenceVerifyGet(body);
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
| **expectedPriorPacketHash** | `string` |  | [Optional] [Defaults to `undefined`] |

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

