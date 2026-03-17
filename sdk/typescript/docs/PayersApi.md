# PayersApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**payerBehaviorPayersPayerIdBehaviorGet**](PayersApi.md#payerbehaviorpayerspayeridbehaviorget) | **GET** /payers/{payer_id}/behavior | Payer Behavior |
| [**payerRiskPayersPayerIdRiskGet**](PayersApi.md#payerriskpayerspayeridriskget) | **GET** /payers/{payer_id}/risk | Payer Risk |



## payerBehaviorPayersPayerIdBehaviorGet

> any payerBehaviorPayersPayerIdBehaviorGet(payerId)

Payer Behavior

### Example

```ts
import {
  Configuration,
  PayersApi,
} from '@xr7/sdk';
import type { PayerBehaviorPayersPayerIdBehaviorGetRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new PayersApi();

  const body = {
    // string
    payerId: payerId_example,
  } satisfies PayerBehaviorPayersPayerIdBehaviorGetRequest;

  try {
    const data = await api.payerBehaviorPayersPayerIdBehaviorGet(body);
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
| **payerId** | `string` |  | [Defaults to `undefined`] |

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


## payerRiskPayersPayerIdRiskGet

> any payerRiskPayersPayerIdRiskGet(payerId)

Payer Risk

### Example

```ts
import {
  Configuration,
  PayersApi,
} from '@xr7/sdk';
import type { PayerRiskPayersPayerIdRiskGetRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new PayersApi();

  const body = {
    // string
    payerId: payerId_example,
  } satisfies PayerRiskPayersPayerIdRiskGetRequest;

  try {
    const data = await api.payerRiskPayersPayerIdRiskGet(body);
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
| **payerId** | `string` |  | [Defaults to `undefined`] |

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

