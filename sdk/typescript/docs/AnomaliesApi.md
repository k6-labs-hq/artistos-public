# AnomaliesApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**detectAnomaliesArtistsArtistIdAnomaliesDetectPost**](AnomaliesApi.md#detectanomaliesartistsartistidanomaliesdetectpost) | **POST** /artists/{artist_id}/anomalies/detect | Detect Anomalies |
| [**getAnomalyAnomaliesAnomalyIdGet**](AnomaliesApi.md#getanomalyanomaliesanomalyidget) | **GET** /anomalies/{anomaly_id} | Get Anomaly |
| [**listAnomaliesArtistsArtistIdAnomaliesGet**](AnomaliesApi.md#listanomaliesartistsartistidanomaliesget) | **GET** /artists/{artist_id}/anomalies | List Anomalies |



## detectAnomaliesArtistsArtistIdAnomaliesDetectPost

> any detectAnomaliesArtistsArtistIdAnomaliesDetectPost(artistId)

Detect Anomalies

### Example

```ts
import {
  Configuration,
  AnomaliesApi,
} from '@xr7/sdk';
import type { DetectAnomaliesArtistsArtistIdAnomaliesDetectPostRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new AnomaliesApi();

  const body = {
    // string
    artistId: artistId_example,
  } satisfies DetectAnomaliesArtistsArtistIdAnomaliesDetectPostRequest;

  try {
    const data = await api.detectAnomaliesArtistsArtistIdAnomaliesDetectPost(body);
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


## getAnomalyAnomaliesAnomalyIdGet

> AnomalySchema getAnomalyAnomaliesAnomalyIdGet(anomalyId)

Get Anomaly

### Example

```ts
import {
  Configuration,
  AnomaliesApi,
} from '@xr7/sdk';
import type { GetAnomalyAnomaliesAnomalyIdGetRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new AnomaliesApi();

  const body = {
    // string
    anomalyId: anomalyId_example,
  } satisfies GetAnomalyAnomaliesAnomalyIdGetRequest;

  try {
    const data = await api.getAnomalyAnomaliesAnomalyIdGet(body);
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
| **anomalyId** | `string` |  | [Defaults to `undefined`] |

### Return type

[**AnomalySchema**](AnomalySchema.md)

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


## listAnomaliesArtistsArtistIdAnomaliesGet

> any listAnomaliesArtistsArtistIdAnomaliesGet(artistId, status)

List Anomalies

### Example

```ts
import {
  Configuration,
  AnomaliesApi,
} from '@xr7/sdk';
import type { ListAnomaliesArtistsArtistIdAnomaliesGetRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new AnomaliesApi();

  const body = {
    // string
    artistId: artistId_example,
    // string (optional)
    status: status_example,
  } satisfies ListAnomaliesArtistsArtistIdAnomaliesGetRequest;

  try {
    const data = await api.listAnomaliesArtistsArtistIdAnomaliesGet(body);
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
| **status** | `string` |  | [Optional] [Defaults to `undefined`] |

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

