# EarningsApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**forecastEarningsArtistsArtistIdMlForecastPost**](EarningsApi.md#forecastearningsartistsartistidmlforecastpost) | **POST** /artists/{artist_id}/ml/forecast | Forecast Earnings |
| [**getEarningsHistoryArtistsArtistIdEarningsHistoryGet**](EarningsApi.md#getearningshistoryartistsartistidearningshistoryget) | **GET** /artists/{artist_id}/earnings/history | Get Earnings History |
| [**getEarningsSummaryArtistsArtistIdEarningsGet**](EarningsApi.md#getearningssummaryartistsartistidearningsget) | **GET** /artists/{artist_id}/earnings | Get Earnings Summary |
| [**getPostRepairForecastArtistsArtistIdEarningsForecastGet**](EarningsApi.md#getpostrepairforecastartistsartistidearningsforecastget) | **GET** /artists/{artist_id}/earnings/forecast | Get Post Repair Forecast |
| [**reconstructEarningsArtistsArtistIdEarningsReconstructPost**](EarningsApi.md#reconstructearningsartistsartistidearningsreconstructpost) | **POST** /artists/{artist_id}/earnings/reconstruct | Reconstruct Earnings |



## forecastEarningsArtistsArtistIdMlForecastPost

> any forecastEarningsArtistsArtistIdMlForecastPost(artistId, xR7ApiRoutersEarningsForecastRequest)

Forecast Earnings

Use a linear-regression trend model to forecast the artist\&#39;s earnings for the next *horizon_days* days.  Set &#x60;&#x60;by_category&#x3D;true&#x60;&#x60; to receive a per-event-type breakdown.

### Example

```ts
import {
  Configuration,
  EarningsApi,
} from '@xr7/sdk';
import type { ForecastEarningsArtistsArtistIdMlForecastPostRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new EarningsApi();

  const body = {
    // string
    artistId: artistId_example,
    // XR7ApiRoutersEarningsForecastRequest
    xR7ApiRoutersEarningsForecastRequest: ...,
  } satisfies ForecastEarningsArtistsArtistIdMlForecastPostRequest;

  try {
    const data = await api.forecastEarningsArtistsArtistIdMlForecastPost(body);
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
| **xR7ApiRoutersEarningsForecastRequest** | [XR7ApiRoutersEarningsForecastRequest](XR7ApiRoutersEarningsForecastRequest.md) |  | |

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


## getEarningsHistoryArtistsArtistIdEarningsHistoryGet

> any getEarningsHistoryArtistsArtistIdEarningsHistoryGet(artistId)

Get Earnings History

### Example

```ts
import {
  Configuration,
  EarningsApi,
} from '@xr7/sdk';
import type { GetEarningsHistoryArtistsArtistIdEarningsHistoryGetRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const config = new Configuration({
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new EarningsApi(config);

  const body = {
    // string
    artistId: artistId_example,
  } satisfies GetEarningsHistoryArtistsArtistIdEarningsHistoryGetRequest;

  try {
    const data = await api.getEarningsHistoryArtistsArtistIdEarningsHistoryGet(body);
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


## getEarningsSummaryArtistsArtistIdEarningsGet

> any getEarningsSummaryArtistsArtistIdEarningsGet(artistId)

Get Earnings Summary

### Example

```ts
import {
  Configuration,
  EarningsApi,
} from '@xr7/sdk';
import type { GetEarningsSummaryArtistsArtistIdEarningsGetRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const config = new Configuration({
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new EarningsApi(config);

  const body = {
    // string
    artistId: artistId_example,
  } satisfies GetEarningsSummaryArtistsArtistIdEarningsGetRequest;

  try {
    const data = await api.getEarningsSummaryArtistsArtistIdEarningsGet(body);
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


## getPostRepairForecastArtistsArtistIdEarningsForecastGet

> any getPostRepairForecastArtistsArtistIdEarningsForecastGet(artistId)

Get Post Repair Forecast

### Example

```ts
import {
  Configuration,
  EarningsApi,
} from '@xr7/sdk';
import type { GetPostRepairForecastArtistsArtistIdEarningsForecastGetRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new EarningsApi();

  const body = {
    // string
    artistId: artistId_example,
  } satisfies GetPostRepairForecastArtistsArtistIdEarningsForecastGetRequest;

  try {
    const data = await api.getPostRepairForecastArtistsArtistIdEarningsForecastGet(body);
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


## reconstructEarningsArtistsArtistIdEarningsReconstructPost

> any reconstructEarningsArtistsArtistIdEarningsReconstructPost(artistId, reconstructRequest)

Reconstruct Earnings

### Example

```ts
import {
  Configuration,
  EarningsApi,
} from '@xr7/sdk';
import type { ReconstructEarningsArtistsArtistIdEarningsReconstructPostRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new EarningsApi();

  const body = {
    // string
    artistId: artistId_example,
    // ReconstructRequest
    reconstructRequest: ...,
  } satisfies ReconstructEarningsArtistsArtistIdEarningsReconstructPostRequest;

  try {
    const data = await api.reconstructEarningsArtistsArtistIdEarningsReconstructPost(body);
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
| **reconstructRequest** | [ReconstructRequest](ReconstructRequest.md) |  | |

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
