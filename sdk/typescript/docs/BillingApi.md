# BillingApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**getBillingSummaryArtistsArtistIdBillingGet**](BillingApi.md#getbillingsummaryartistsartistidbillingget) | **GET** /artists/{artist_id}/billing | Get Billing Summary |
| [**listInvoicesArtistsArtistIdInvoicesGet**](BillingApi.md#listinvoicesartistsartistidinvoicesget) | **GET** /artists/{artist_id}/invoices | List Invoices |



## getBillingSummaryArtistsArtistIdBillingGet

> any getBillingSummaryArtistsArtistIdBillingGet(artistId)

Get Billing Summary

### Example

```ts
import {
  Configuration,
  BillingApi,
} from '@xr7/sdk';
import type { GetBillingSummaryArtistsArtistIdBillingGetRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new BillingApi();

  const body = {
    // string
    artistId: artistId_example,
  } satisfies GetBillingSummaryArtistsArtistIdBillingGetRequest;

  try {
    const data = await api.getBillingSummaryArtistsArtistIdBillingGet(body);
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


## listInvoicesArtistsArtistIdInvoicesGet

> any listInvoicesArtistsArtistIdInvoicesGet(artistId)

List Invoices

### Example

```ts
import {
  Configuration,
  BillingApi,
} from '@xr7/sdk';
import type { ListInvoicesArtistsArtistIdInvoicesGetRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new BillingApi();

  const body = {
    // string
    artistId: artistId_example,
  } satisfies ListInvoicesArtistsArtistIdInvoicesGetRequest;

  try {
    const data = await api.listInvoicesArtistsArtistIdInvoicesGet(body);
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
