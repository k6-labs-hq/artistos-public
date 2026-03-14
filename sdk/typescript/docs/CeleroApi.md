# CeleroApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**celeroWebhookCeleroWebhookPost**](CeleroApi.md#celerowebhookcelerowebhookpost) | **POST** /celero/webhook | Celero Webhook |
| [**chargeContingencyFeeArtistsArtistIdCeleroChargePost**](CeleroApi.md#chargecontingencyfeeartistsartistidcelerochargepost) | **POST** /artists/{artist_id}/celero/charge | Charge Contingency Fee |
| [**disburseToArtistArtistsArtistIdCeleroDisbursePost**](CeleroApi.md#disbursetoartistartistsartistidcelerodisbursepost) | **POST** /artists/{artist_id}/celero/disburse | Disburse To Artist |
| [**getCeleroStatusArtistsArtistIdCeleroStatusGet**](CeleroApi.md#getcelerostatusartistsartistidcelerostatusget) | **GET** /artists/{artist_id}/celero/status | Get Celero Status |
| [**getCeleroTransactionArtistsArtistIdCeleroTransactionsTransactionIdGet**](CeleroApi.md#getcelerotransactionartistsartistidcelerotransactionstransactionidget) | **GET** /artists/{artist_id}/celero/transactions/{transaction_id} | Get Celero Transaction |
| [**listCeleroTransactionsArtistsArtistIdCeleroTransactionsGet**](CeleroApi.md#listcelerotransactionsartistsartistidcelerotransactionsget) | **GET** /artists/{artist_id}/celero/transactions | List Celero Transactions |
| [**refundTransactionArtistsArtistIdCeleroTransactionsTransactionIdRefundPost**](CeleroApi.md#refundtransactionartistsartistidcelerotransactionstransactionidrefundpost) | **POST** /artists/{artist_id}/celero/transactions/{transaction_id}/refund | Refund Transaction |
| [**registerArtistWithCeleroArtistsArtistIdCeleroRegisterPost**](CeleroApi.md#registerartistwithceleroartistsartistidceleroregisterpost) | **POST** /artists/{artist_id}/celero/register | Register Artist With Celero |
| [**updateCeleroCustomerArtistsArtistIdCeleroCustomerPut**](CeleroApi.md#updatecelerocustomerartistsartistidcelerocustomerput) | **PUT** /artists/{artist_id}/celero/customer | Update Celero Customer |
| [**voidTransactionArtistsArtistIdCeleroTransactionsTransactionIdVoidPost**](CeleroApi.md#voidtransactionartistsartistidcelerotransactionstransactionidvoidpost) | **POST** /artists/{artist_id}/celero/transactions/{transaction_id}/void | Void Transaction |



## celeroWebhookCeleroWebhookPost

> any celeroWebhookCeleroWebhookPost(xCeleroSignature)

Celero Webhook

Receive and process real-time event notifications from Celero Commerce.  Configure this URL in the Celero merchant dashboard:   Settings → Webhooks → Add Endpoint → &#x60;&#x60;https://your-domain/celero/webhook&#x60;&#x60;  Supported events: &#x60;&#x60;transaction.approved&#x60;&#x60;, &#x60;&#x60;transaction.declined&#x60;&#x60;, &#x60;&#x60;transaction.void&#x60;&#x60;, &#x60;&#x60;transaction.refund&#x60;&#x60;, &#x60;&#x60;disbursement.settled&#x60;&#x60;, &#x60;&#x60;disbursement.failed&#x60;&#x60;.  Every request is validated against the HMAC-SHA256 signature in the &#x60;&#x60;X-Celero-Signature&#x60;&#x60; header using &#x60;&#x60;CELERO_WEBHOOK_SECRET&#x60;&#x60;.

### Example

```ts
import {
  Configuration,
  CeleroApi,
} from '@xr7/sdk';
import type { CeleroWebhookCeleroWebhookPostRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new CeleroApi();

  const body = {
    // string (optional)
    xCeleroSignature: xCeleroSignature_example,
  } satisfies CeleroWebhookCeleroWebhookPostRequest;

  try {
    const data = await api.celeroWebhookCeleroWebhookPost(body);
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
| **xCeleroSignature** | `string` |  | [Optional] [Defaults to `&#39;&#39;`] |

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


## chargeContingencyFeeArtistsArtistIdCeleroChargePost

> CeleroTransactionSchema chargeContingencyFeeArtistsArtistIdCeleroChargePost(artistId, celeroChargeRequest)

Charge Contingency Fee

Charge the artist\&#39;s Celero-vaulted payment method for XR7\&#39;s 10% contingency fee on a reconciled claim.  The claim must be in &#x60;&#x60;PAID&#x60;&#x60; status with a &#x60;&#x60;recovered_amount&#x60;&#x60; set. The charge amount is calculated as &#x60;&#x60;recovered_amount × 10%&#x60;&#x60;.  Requires: - The artist to be registered with Celero (&#x60;&#x60;celero_customer_vault_id&#x60;&#x60; set). - &#x60;&#x60;CELERO_SECURITY_KEY&#x60;&#x60; to be configured.

### Example

```ts
import {
  Configuration,
  CeleroApi,
} from '@xr7/sdk';
import type { ChargeContingencyFeeArtistsArtistIdCeleroChargePostRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new CeleroApi();

  const body = {
    // string
    artistId: artistId_example,
    // CeleroChargeRequest
    celeroChargeRequest: ...,
  } satisfies ChargeContingencyFeeArtistsArtistIdCeleroChargePostRequest;

  try {
    const data = await api.chargeContingencyFeeArtistsArtistIdCeleroChargePost(body);
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
| **celeroChargeRequest** | [CeleroChargeRequest](CeleroChargeRequest.md) |  | |

### Return type

[**CeleroTransactionSchema**](CeleroTransactionSchema.md)

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


## disburseToArtistArtistsArtistIdCeleroDisbursePost

> CeleroTransactionSchema disburseToArtistArtistsArtistIdCeleroDisbursePost(artistId, celeroDisburseRequest)

Disburse To Artist

Disburse the artist\&#39;s net recovery amount via ACH credit through Celero.  The &#x60;&#x60;amount&#x60;&#x60; should be the gross recovery minus XR7\&#39;s contingency fee.  Celero will credit the artist\&#39;s bank account stored in their vault.  Requires: - The artist to have a bank account on file in their Celero vault. - Celero ACH payout capability to be enabled on the XR7 merchant account. - &#x60;&#x60;CELERO_SECURITY_KEY&#x60;&#x60; to be configured.

### Example

```ts
import {
  Configuration,
  CeleroApi,
} from '@xr7/sdk';
import type { DisburseToArtistArtistsArtistIdCeleroDisbursePostRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new CeleroApi();

  const body = {
    // string
    artistId: artistId_example,
    // CeleroDisburseRequest
    celeroDisburseRequest: ...,
  } satisfies DisburseToArtistArtistsArtistIdCeleroDisbursePostRequest;

  try {
    const data = await api.disburseToArtistArtistsArtistIdCeleroDisbursePost(body);
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
| **celeroDisburseRequest** | [CeleroDisburseRequest](CeleroDisburseRequest.md) |  | |

### Return type

[**CeleroTransactionSchema**](CeleroTransactionSchema.md)

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


## getCeleroStatusArtistsArtistIdCeleroStatusGet

> any getCeleroStatusArtistsArtistIdCeleroStatusGet(artistId)

Get Celero Status

Return the Celero Commerce integration status for an artist.  Shows whether the artist has been registered in the Celero vault and a summary of their transaction history.

### Example

```ts
import {
  Configuration,
  CeleroApi,
} from '@xr7/sdk';
import type { GetCeleroStatusArtistsArtistIdCeleroStatusGetRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new CeleroApi();

  const body = {
    // string
    artistId: artistId_example,
  } satisfies GetCeleroStatusArtistsArtistIdCeleroStatusGetRequest;

  try {
    const data = await api.getCeleroStatusArtistsArtistIdCeleroStatusGet(body);
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


## getCeleroTransactionArtistsArtistIdCeleroTransactionsTransactionIdGet

> CeleroTransactionSchema getCeleroTransactionArtistsArtistIdCeleroTransactionsTransactionIdGet(artistId, transactionId)

Get Celero Transaction

Return a single Celero transaction record.

### Example

```ts
import {
  Configuration,
  CeleroApi,
} from '@xr7/sdk';
import type { GetCeleroTransactionArtistsArtistIdCeleroTransactionsTransactionIdGetRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new CeleroApi();

  const body = {
    // string
    artistId: artistId_example,
    // string
    transactionId: transactionId_example,
  } satisfies GetCeleroTransactionArtistsArtistIdCeleroTransactionsTransactionIdGetRequest;

  try {
    const data = await api.getCeleroTransactionArtistsArtistIdCeleroTransactionsTransactionIdGet(body);
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
| **transactionId** | `string` |  | [Defaults to `undefined`] |

### Return type

[**CeleroTransactionSchema**](CeleroTransactionSchema.md)

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


## listCeleroTransactionsArtistsArtistIdCeleroTransactionsGet

> Array&lt;CeleroTransactionSchema&gt; listCeleroTransactionsArtistsArtistIdCeleroTransactionsGet(artistId)

List Celero Transactions

Return all Celero transactions for an artist, newest first.

### Example

```ts
import {
  Configuration,
  CeleroApi,
} from '@xr7/sdk';
import type { ListCeleroTransactionsArtistsArtistIdCeleroTransactionsGetRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new CeleroApi();

  const body = {
    // string
    artistId: artistId_example,
  } satisfies ListCeleroTransactionsArtistsArtistIdCeleroTransactionsGetRequest;

  try {
    const data = await api.listCeleroTransactionsArtistsArtistIdCeleroTransactionsGet(body);
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

[**Array&lt;CeleroTransactionSchema&gt;**](CeleroTransactionSchema.md)

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


## refundTransactionArtistsArtistIdCeleroTransactionsTransactionIdRefundPost

> CeleroTransactionSchema refundTransactionArtistsArtistIdCeleroTransactionsTransactionIdRefundPost(artistId, transactionId, celeroRefundRequest)

Refund Transaction

Issue a partial or full refund for a previous CHARGE transaction.  If &#x60;&#x60;amount&#x60;&#x60; is omitted, the full transaction amount is refunded.

### Example

```ts
import {
  Configuration,
  CeleroApi,
} from '@xr7/sdk';
import type { RefundTransactionArtistsArtistIdCeleroTransactionsTransactionIdRefundPostRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new CeleroApi();

  const body = {
    // string
    artistId: artistId_example,
    // string
    transactionId: transactionId_example,
    // CeleroRefundRequest
    celeroRefundRequest: ...,
  } satisfies RefundTransactionArtistsArtistIdCeleroTransactionsTransactionIdRefundPostRequest;

  try {
    const data = await api.refundTransactionArtistsArtistIdCeleroTransactionsTransactionIdRefundPost(body);
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
| **transactionId** | `string` |  | [Defaults to `undefined`] |
| **celeroRefundRequest** | [CeleroRefundRequest](CeleroRefundRequest.md) |  | |

### Return type

[**CeleroTransactionSchema**](CeleroTransactionSchema.md)

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


## registerArtistWithCeleroArtistsArtistIdCeleroRegisterPost

> ArtistSchema registerArtistWithCeleroArtistsArtistIdCeleroRegisterPost(artistId, celeroRegisterRequest)

Register Artist With Celero

Register an artist in the Celero Commerce Customer Vault.  Creates a new vault record with the artist\&#39;s contact details.  The returned &#x60;&#x60;celero_customer_vault_id&#x60;&#x60; is stored on the Artist and used for all subsequent charges and disbursements.  The artist\&#39;s actual payment credentials (card number / bank account) are added separately using Celero\&#39;s **Collect.js** or **Collect Checkout** hosted form — XR7 never handles raw payment data.  Requires &#x60;&#x60;CELERO_SECURITY_KEY&#x60;&#x60; to be configured.

### Example

```ts
import {
  Configuration,
  CeleroApi,
} from '@xr7/sdk';
import type { RegisterArtistWithCeleroArtistsArtistIdCeleroRegisterPostRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new CeleroApi();

  const body = {
    // string
    artistId: artistId_example,
    // CeleroRegisterRequest
    celeroRegisterRequest: ...,
  } satisfies RegisterArtistWithCeleroArtistsArtistIdCeleroRegisterPostRequest;

  try {
    const data = await api.registerArtistWithCeleroArtistsArtistIdCeleroRegisterPost(body);
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
| **celeroRegisterRequest** | [CeleroRegisterRequest](CeleroRegisterRequest.md) |  | |

### Return type

[**ArtistSchema**](ArtistSchema.md)

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


## updateCeleroCustomerArtistsArtistIdCeleroCustomerPut

> ArtistSchema updateCeleroCustomerArtistsArtistIdCeleroCustomerPut(artistId, celeroRegisterRequest)

Update Celero Customer

Update an artist\&#39;s contact details in the Celero Customer Vault.

### Example

```ts
import {
  Configuration,
  CeleroApi,
} from '@xr7/sdk';
import type { UpdateCeleroCustomerArtistsArtistIdCeleroCustomerPutRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new CeleroApi();

  const body = {
    // string
    artistId: artistId_example,
    // CeleroRegisterRequest
    celeroRegisterRequest: ...,
  } satisfies UpdateCeleroCustomerArtistsArtistIdCeleroCustomerPutRequest;

  try {
    const data = await api.updateCeleroCustomerArtistsArtistIdCeleroCustomerPut(body);
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
| **celeroRegisterRequest** | [CeleroRegisterRequest](CeleroRegisterRequest.md) |  | |

### Return type

[**ArtistSchema**](ArtistSchema.md)

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


## voidTransactionArtistsArtistIdCeleroTransactionsTransactionIdVoidPost

> CeleroTransactionSchema voidTransactionArtistsArtistIdCeleroTransactionsTransactionIdVoidPost(artistId, transactionId)

Void Transaction

Void an unsettled CHARGE transaction (typically same-day).  Use &#x60;&#x60;refund&#x60;&#x60; for transactions that have already settled.

### Example

```ts
import {
  Configuration,
  CeleroApi,
} from '@xr7/sdk';
import type { VoidTransactionArtistsArtistIdCeleroTransactionsTransactionIdVoidPostRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new CeleroApi();

  const body = {
    // string
    artistId: artistId_example,
    // string
    transactionId: transactionId_example,
  } satisfies VoidTransactionArtistsArtistIdCeleroTransactionsTransactionIdVoidPostRequest;

  try {
    const data = await api.voidTransactionArtistsArtistIdCeleroTransactionsTransactionIdVoidPost(body);
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
| **transactionId** | `string` |  | [Defaults to `undefined`] |

### Return type

[**CeleroTransactionSchema**](CeleroTransactionSchema.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **201** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

