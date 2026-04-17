# ConfigApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**getFounderStatusConfigFounderStatusGet**](ConfigApi.md#getfounderstatusconfigfounderstatusget) | **GET** /config/founder-status | Get Founder Status |



## getFounderStatusConfigFounderStatusGet

> any getFounderStatusConfigFounderStatusGet()

Get Founder Status

### Example

```ts
import {
  Configuration,
  ConfigApi,
} from '@xr7/sdk';
import type { GetFounderStatusConfigFounderStatusGetRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new ConfigApi();

  try {
    const data = await api.getFounderStatusConfigFounderStatusGet();
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
