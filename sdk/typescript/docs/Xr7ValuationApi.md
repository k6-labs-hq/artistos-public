# Xr7ValuationApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**catalogHealthArtistsArtistIdXr7CatalogHealthGet**](Xr7ValuationApi.md#cataloghealthartistsartistidxr7cataloghealthget) | **GET** /artists/{artist_id}/xr7/catalog/health | Catalog Health |
| [**recoveryForecastArtistsArtistIdXr7ForecastRecoveryPost**](Xr7ValuationApi.md#recoveryforecastartistsartistidxr7forecastrecoverypost) | **POST** /artists/{artist_id}/xr7/forecast/recovery | Recovery Forecast |
| [**simulationArtistsArtistIdXr7SimulationsWhatIfPost**](Xr7ValuationApi.md#simulationartistsartistidxr7simulationswhatifpost) | **POST** /artists/{artist_id}/xr7/simulations/what-if | Simulation |
| [**valuationSnapshotArtistsArtistIdXr7ValuationSnapshotGet**](Xr7ValuationApi.md#valuationsnapshotartistsartistidxr7valuationsnapshotget) | **GET** /artists/{artist_id}/xr7/valuation/snapshot | Valuation Snapshot |



## catalogHealthArtistsArtistIdXr7CatalogHealthGet

> any catalogHealthArtistsArtistIdXr7CatalogHealthGet(artistId, tenantId)

Catalog Health

### Example

```ts
import {
  Configuration,
  Xr7ValuationApi,
} from '@xr7/sdk';
import type { CatalogHealthArtistsArtistIdXr7CatalogHealthGetRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new Xr7ValuationApi();

  const body = {
    // string
    artistId: artistId_example,
    // string (optional)
    tenantId: tenantId_example,
  } satisfies CatalogHealthArtistsArtistIdXr7CatalogHealthGetRequest;

  try {
    const data = await api.catalogHealthArtistsArtistIdXr7CatalogHealthGet(body);
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
| **tenantId** | `string` |  | [Optional] [Defaults to `&#39;default&#39;`] |

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


## recoveryForecastArtistsArtistIdXr7ForecastRecoveryPost

> any recoveryForecastArtistsArtistIdXr7ForecastRecoveryPost(artistId, xR7ApiRoutersXr7ValuationForecastRequest)

Recovery Forecast

### Example

```ts
import {
  Configuration,
  Xr7ValuationApi,
} from '@xr7/sdk';
import type { RecoveryForecastArtistsArtistIdXr7ForecastRecoveryPostRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new Xr7ValuationApi();

  const body = {
    // string
    artistId: artistId_example,
    // XR7ApiRoutersXr7ValuationForecastRequest
    xR7ApiRoutersXr7ValuationForecastRequest: ...,
  } satisfies RecoveryForecastArtistsArtistIdXr7ForecastRecoveryPostRequest;

  try {
    const data = await api.recoveryForecastArtistsArtistIdXr7ForecastRecoveryPost(body);
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
| **xR7ApiRoutersXr7ValuationForecastRequest** | [XR7ApiRoutersXr7ValuationForecastRequest](XR7ApiRoutersXr7ValuationForecastRequest.md) |  | |

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


## simulationArtistsArtistIdXr7SimulationsWhatIfPost

> any simulationArtistsArtistIdXr7SimulationsWhatIfPost(artistId, simulationRequest)

Simulation

### Example

```ts
import {
  Configuration,
  Xr7ValuationApi,
} from '@xr7/sdk';
import type { SimulationArtistsArtistIdXr7SimulationsWhatIfPostRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new Xr7ValuationApi();

  const body = {
    // string
    artistId: artistId_example,
    // SimulationRequest
    simulationRequest: ...,
  } satisfies SimulationArtistsArtistIdXr7SimulationsWhatIfPostRequest;

  try {
    const data = await api.simulationArtistsArtistIdXr7SimulationsWhatIfPost(body);
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
| **simulationRequest** | [SimulationRequest](SimulationRequest.md) |  | |

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


## valuationSnapshotArtistsArtistIdXr7ValuationSnapshotGet

> any valuationSnapshotArtistsArtistIdXr7ValuationSnapshotGet(artistId, tenantId, asOf)

Valuation Snapshot

### Example

```ts
import {
  Configuration,
  Xr7ValuationApi,
} from '@xr7/sdk';
import type { ValuationSnapshotArtistsArtistIdXr7ValuationSnapshotGetRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new Xr7ValuationApi();

  const body = {
    // string
    artistId: artistId_example,
    // string (optional)
    tenantId: tenantId_example,
    // Date (optional)
    asOf: 2013-10-20,
  } satisfies ValuationSnapshotArtistsArtistIdXr7ValuationSnapshotGetRequest;

  try {
    const data = await api.valuationSnapshotArtistsArtistIdXr7ValuationSnapshotGet(body);
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
| **tenantId** | `string` |  | [Optional] [Defaults to `&#39;default&#39;`] |
| **asOf** | `Date` |  | [Optional] [Defaults to `undefined`] |

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
