# DefaultApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**healthHealthGet**](DefaultApi.md#healthhealthget) | **GET** /health | Health |
| [**readinessHealthReadinessGet**](DefaultApi.md#readinesshealthreadinessget) | **GET** /health/readiness | Readiness |



## healthHealthGet

> any healthHealthGet()

Health

### Example

```ts
import {
  Configuration,
  DefaultApi,
} from '@xr7/sdk';
import type { HealthHealthGetRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new DefaultApi();

  try {
    const data = await api.healthHealthGet();
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


## readinessHealthReadinessGet

> any readinessHealthReadinessGet()

Readiness

Return the platform readiness status for every integration point.  Operators can call this endpoint to see exactly which connectors are configured (credentials present) vs. which require additional setup.  &#x60;&#x60;ready&#x60;&#x60; is &#x60;&#x60;True&#x60;&#x60; only when the core platform components are functional.  Individual connector status reflects whether the required environment variables are set — it does NOT make real network connections.

### Example

```ts
import {
  Configuration,
  DefaultApi,
} from '@xr7/sdk';
import type { ReadinessHealthReadinessGetRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new DefaultApi();

  try {
    const data = await api.readinessHealthReadinessGet();
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
