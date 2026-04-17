# ClassActionApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**listClassActionSignalsAdminClassActionSignalsGet**](ClassActionApi.md#listclassactionsignalsadminclassactionsignalsget) | **GET** /admin/class-action/signals | List Class Action Signals |
| [**runClassActionAggregationAdminClassActionAggregatePost**](ClassActionApi.md#runclassactionaggregationadminclassactionaggregatepost) | **POST** /admin/class-action/aggregate | Run Class Action Aggregation |



## listClassActionSignalsAdminClassActionSignalsGet

> { [key: string]: any; } listClassActionSignalsAdminClassActionSignalsGet()

List Class Action Signals

Return all active class-action evidence signals.

### Example

```ts
import {
  Configuration,
  ClassActionApi,
} from '@xr7/sdk';
import type { ListClassActionSignalsAdminClassActionSignalsGetRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const config = new Configuration({
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new ClassActionApi(config);

  try {
    const data = await api.listClassActionSignalsAdminClassActionSignalsGet();
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

**{ [key: string]: any; }**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## runClassActionAggregationAdminClassActionAggregatePost

> { [key: string]: any; } runClassActionAggregationAdminClassActionAggregatePost()

Run Class Action Aggregation

Re-run the class-action signal aggregator across all open anomalies.  Requires admin role. Returns created/updated signal records.

### Example

```ts
import {
  Configuration,
  ClassActionApi,
} from '@xr7/sdk';
import type { RunClassActionAggregationAdminClassActionAggregatePostRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const config = new Configuration({
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new ClassActionApi(config);

  try {
    const data = await api.runClassActionAggregationAdminClassActionAggregatePost();
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

**{ [key: string]: any; }**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)
