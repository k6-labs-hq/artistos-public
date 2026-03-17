# TrolleyApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**createTrolleyRecipientArtistsArtistIdTrolleyRecipientPost**](TrolleyApi.md#createtrolleyrecipientartistsartistidtrolleyrecipientpost) | **POST** /artists/{artist_id}/trolley/recipient | Create Trolley Recipient |
| [**disburseClaimClaimsClaimIdDisbursePost**](TrolleyApi.md#disburseclaimclaimsclaimiddisbursepost) | **POST** /claims/{claim_id}/disburse | Disburse Claim |
| [**getTrolleyStatusArtistsArtistIdTrolleyStatusGet**](TrolleyApi.md#gettrolleystatusartistsartistidtrolleystatusget) | **GET** /artists/{artist_id}/trolley/status | Get Trolley Status |
| [**getTrolleyWidgetUrlArtistsArtistIdTrolleyWidgetUrlGet**](TrolleyApi.md#gettrolleywidgeturlartistsartistidtrolleywidgeturlget) | **GET** /artists/{artist_id}/trolley/widget-url | Get Trolley Widget Url |
| [**manualRemittanceArtistsArtistIdClaimsClaimIdManualRemittancePost**](TrolleyApi.md#manualremittanceartistsartistidclaimsclaimidmanualremittancepost) | **POST** /artists/{artist_id}/claims/{claim_id}/manual-remittance | Manual Remittance |
| [**trolleyWebhookWebhooksTrolleyPost**](TrolleyApi.md#trolleywebhookwebhookstrolleypost) | **POST** /webhooks/trolley | Trolley Webhook |



## createTrolleyRecipientArtistsArtistIdTrolleyRecipientPost

> any createTrolleyRecipientArtistsArtistIdTrolleyRecipientPost(artistId)

Create Trolley Recipient

### Example

```ts
import {
  Configuration,
  TrolleyApi,
} from '@xr7/sdk';
import type { CreateTrolleyRecipientArtistsArtistIdTrolleyRecipientPostRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new TrolleyApi();

  const body = {
    // string
    artistId: artistId_example,
  } satisfies CreateTrolleyRecipientArtistsArtistIdTrolleyRecipientPostRequest;

  try {
    const data = await api.createTrolleyRecipientArtistsArtistIdTrolleyRecipientPost(body);
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


## disburseClaimClaimsClaimIdDisbursePost

> TrolleyTransactionSchema disburseClaimClaimsClaimIdDisbursePost(claimId)

Disburse Claim

### Example

```ts
import {
  Configuration,
  TrolleyApi,
} from '@xr7/sdk';
import type { DisburseClaimClaimsClaimIdDisbursePostRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new TrolleyApi();

  const body = {
    // string
    claimId: claimId_example,
  } satisfies DisburseClaimClaimsClaimIdDisbursePostRequest;

  try {
    const data = await api.disburseClaimClaimsClaimIdDisbursePost(body);
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

[**TrolleyTransactionSchema**](TrolleyTransactionSchema.md)

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


## getTrolleyStatusArtistsArtistIdTrolleyStatusGet

> any getTrolleyStatusArtistsArtistIdTrolleyStatusGet(artistId)

Get Trolley Status

### Example

```ts
import {
  Configuration,
  TrolleyApi,
} from '@xr7/sdk';
import type { GetTrolleyStatusArtistsArtistIdTrolleyStatusGetRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new TrolleyApi();

  const body = {
    // string
    artistId: artistId_example,
  } satisfies GetTrolleyStatusArtistsArtistIdTrolleyStatusGetRequest;

  try {
    const data = await api.getTrolleyStatusArtistsArtistIdTrolleyStatusGet(body);
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


## getTrolleyWidgetUrlArtistsArtistIdTrolleyWidgetUrlGet

> any getTrolleyWidgetUrlArtistsArtistIdTrolleyWidgetUrlGet(artistId)

Get Trolley Widget Url

### Example

```ts
import {
  Configuration,
  TrolleyApi,
} from '@xr7/sdk';
import type { GetTrolleyWidgetUrlArtistsArtistIdTrolleyWidgetUrlGetRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new TrolleyApi();

  const body = {
    // string
    artistId: artistId_example,
  } satisfies GetTrolleyWidgetUrlArtistsArtistIdTrolleyWidgetUrlGetRequest;

  try {
    const data = await api.getTrolleyWidgetUrlArtistsArtistIdTrolleyWidgetUrlGet(body);
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


## manualRemittanceArtistsArtistIdClaimsClaimIdManualRemittancePost

> any manualRemittanceArtistsArtistIdClaimsClaimIdManualRemittancePost(artistId, claimId, manualRemittanceRequest)

Manual Remittance

### Example

```ts
import {
  Configuration,
  TrolleyApi,
} from '@xr7/sdk';
import type { ManualRemittanceArtistsArtistIdClaimsClaimIdManualRemittancePostRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new TrolleyApi();

  const body = {
    // string
    artistId: artistId_example,
    // string
    claimId: claimId_example,
    // ManualRemittanceRequest
    manualRemittanceRequest: ...,
  } satisfies ManualRemittanceArtistsArtistIdClaimsClaimIdManualRemittancePostRequest;

  try {
    const data = await api.manualRemittanceArtistsArtistIdClaimsClaimIdManualRemittancePost(body);
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
| **claimId** | `string` |  | [Defaults to `undefined`] |
| **manualRemittanceRequest** | [ManualRemittanceRequest](ManualRemittanceRequest.md) |  | |

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


## trolleyWebhookWebhooksTrolleyPost

> any trolleyWebhookWebhooksTrolleyPost()

Trolley Webhook

### Example

```ts
import {
  Configuration,
  TrolleyApi,
} from '@xr7/sdk';
import type { TrolleyWebhookWebhooksTrolleyPostRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new TrolleyApi();

  try {
    const data = await api.trolleyWebhookWebhooksTrolleyPost();
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

