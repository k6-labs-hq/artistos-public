# PublicApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**advocacyKitArtistsArtistIdAdvocacyKitPost**](PublicApi.md#advocacykitartistsartistidadvocacykitpost) | **POST** /artists/{artist_id}/advocacy/kit | Advocacy Kit |
| [**publicAggregatesStatsPublicAggregatesGet**](PublicApi.md#publicaggregatesstatspublicaggregatesget) | **GET** /stats/public/aggregates | Public Aggregates |
| [**publicLeaderboardStatsPublicLeaderboardGet**](PublicApi.md#publicleaderboardstatspublicleaderboardget) | **GET** /stats/public/leaderboard | Public Leaderboard |
| [**publicSuccessStoriesStatsPublicSuccessStoriesGet**](PublicApi.md#publicsuccessstoriesstatspublicsuccessstoriesget) | **GET** /stats/public/success-stories | Public Success Stories |



## advocacyKitArtistsArtistIdAdvocacyKitPost

> any advocacyKitArtistsArtistIdAdvocacyKitPost(artistId)

Advocacy Kit

### Example

```ts
import {
  Configuration,
  PublicApi,
} from '@xr7/sdk';
import type { AdvocacyKitArtistsArtistIdAdvocacyKitPostRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new PublicApi();

  const body = {
    // string
    artistId: artistId_example,
  } satisfies AdvocacyKitArtistsArtistIdAdvocacyKitPostRequest;

  try {
    const data = await api.advocacyKitArtistsArtistIdAdvocacyKitPost(body);
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


## publicAggregatesStatsPublicAggregatesGet

> any publicAggregatesStatsPublicAggregatesGet()

Public Aggregates

### Example

```ts
import {
  Configuration,
  PublicApi,
} from '@xr7/sdk';
import type { PublicAggregatesStatsPublicAggregatesGetRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new PublicApi();

  try {
    const data = await api.publicAggregatesStatsPublicAggregatesGet();
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


## publicLeaderboardStatsPublicLeaderboardGet

> any publicLeaderboardStatsPublicLeaderboardGet()

Public Leaderboard

### Example

```ts
import {
  Configuration,
  PublicApi,
} from '@xr7/sdk';
import type { PublicLeaderboardStatsPublicLeaderboardGetRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new PublicApi();

  try {
    const data = await api.publicLeaderboardStatsPublicLeaderboardGet();
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


## publicSuccessStoriesStatsPublicSuccessStoriesGet

> any publicSuccessStoriesStatsPublicSuccessStoriesGet()

Public Success Stories

### Example

```ts
import {
  Configuration,
  PublicApi,
} from '@xr7/sdk';
import type { PublicSuccessStoriesStatsPublicSuccessStoriesGetRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new PublicApi();

  try {
    const data = await api.publicSuccessStoriesStatsPublicSuccessStoriesGet();
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
