# AnomaliesApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**anomalyRecoveryProbabilityEndpointAnomaliesAnomalyIdRecoveryProbabilityGet**](AnomaliesApi.md#anomalyrecoveryprobabilityendpointanomaliesanomalyidrecoveryprobabilityget) | **GET** /anomalies/{anomaly_id}/recovery-probability | Anomaly Recovery Probability Endpoint |
| [**detectAnomaliesArtistsArtistIdAnomaliesDetectPost**](AnomaliesApi.md#detectanomaliesartistsartistidanomaliesdetectpost) | **POST** /artists/{artist_id}/anomalies/detect | Detect Anomalies |
| [**fraudScanArtistsArtistIdAnomaliesFraudScanPost**](AnomaliesApi.md#fraudscanartistsartistidanomaliesfraudscanpost) | **POST** /artists/{artist_id}/anomalies/fraud-scan | Fraud Scan |
| [**getAnomalyAnomaliesAnomalyIdGet**](AnomaliesApi.md#getanomalyanomaliesanomalyidget) | **GET** /anomalies/{anomaly_id} | Get Anomaly |
| [**listAnomaliesArtistsArtistIdAnomaliesGet**](AnomaliesApi.md#listanomaliesartistsartistidanomaliesget) | **GET** /artists/{artist_id}/anomalies | List Anomalies |
| [**scanAiInfluenceArtistsArtistIdAiMusicScanInfluencePost**](AnomaliesApi.md#scanaiinfluenceartistsartistidaimusicscaninfluencepost) | **POST** /artists/{artist_id}/ai-music/scan-influence | Scan Ai Influence |



## anomalyRecoveryProbabilityEndpointAnomaliesAnomalyIdRecoveryProbabilityGet

> any anomalyRecoveryProbabilityEndpointAnomaliesAnomalyIdRecoveryProbabilityGet(anomalyId)

Anomaly Recovery Probability Endpoint

### Example

```ts
import {
  Configuration,
  AnomaliesApi,
} from '@xr7/sdk';
import type { AnomalyRecoveryProbabilityEndpointAnomaliesAnomalyIdRecoveryProbabilityGetRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new AnomaliesApi();

  const body = {
    // string
    anomalyId: anomalyId_example,
  } satisfies AnomalyRecoveryProbabilityEndpointAnomaliesAnomalyIdRecoveryProbabilityGetRequest;

  try {
    const data = await api.anomalyRecoveryProbabilityEndpointAnomaliesAnomalyIdRecoveryProbabilityGet(body);
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


## fraudScanArtistsArtistIdAnomaliesFraudScanPost

> any fraudScanArtistsArtistIdAnomaliesFraudScanPost(artistId)

Fraud Scan

### Example

```ts
import {
  Configuration,
  AnomaliesApi,
} from '@xr7/sdk';
import type { FraudScanArtistsArtistIdAnomaliesFraudScanPostRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new AnomaliesApi();

  const body = {
    // string
    artistId: artistId_example,
  } satisfies FraudScanArtistsArtistIdAnomaliesFraudScanPostRequest;

  try {
    const data = await api.fraudScanArtistsArtistIdAnomaliesFraudScanPost(body);
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

> any listAnomaliesArtistsArtistIdAnomaliesGet(artistId, status, debug)

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
  const config = new Configuration({ 
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new AnomaliesApi(config);

  const body = {
    // string
    artistId: artistId_example,
    // string (optional)
    status: status_example,
    // boolean (optional)
    debug: true,
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
| **debug** | `boolean` |  | [Optional] [Defaults to `false`] |

### Return type

**any**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## scanAiInfluenceArtistsArtistIdAiMusicScanInfluencePost

> any scanAiInfluenceArtistsArtistIdAiMusicScanInfluencePost(artistId)

Scan Ai Influence

### Example

```ts
import {
  Configuration,
  AnomaliesApi,
} from '@xr7/sdk';
import type { ScanAiInfluenceArtistsArtistIdAiMusicScanInfluencePostRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new AnomaliesApi();

  const body = {
    // string
    artistId: artistId_example,
  } satisfies ScanAiInfluenceArtistsArtistIdAiMusicScanInfluencePostRequest;

  try {
    const data = await api.scanAiInfluenceArtistsArtistIdAiMusicScanInfluencePost(body);
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

