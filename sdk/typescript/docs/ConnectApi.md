# ConnectApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**connectGlobalSocialArtistsArtistIdConnectGlobalSocialPost**](ConnectApi.md#connectglobalsocialartistsartistidconnectglobalsocialpost) | **POST** /artists/{artist_id}/connect/global-social | Connect Global Social |
| [**connectGlobalSocialStatusArtistsArtistIdConnectGlobalSocialStatusGet**](ConnectApi.md#connectglobalsocialstatusartistsartistidconnectglobalsocialstatusget) | **GET** /artists/{artist_id}/connect/global-social/status | Connect Global Social Status |
| [**connectSoundcloudArtistsArtistIdConnectSoundcloudPost**](ConnectApi.md#connectsoundcloudartistsartistidconnectsoundcloudpost) | **POST** /artists/{artist_id}/connect/soundcloud | Connect Soundcloud |
| [**connectSoundcloudStatusArtistsArtistIdConnectSoundcloudStatusGet**](ConnectApi.md#connectsoundcloudstatusartistsartistidconnectsoundcloudstatusget) | **GET** /artists/{artist_id}/connect/soundcloud/status | Connect Soundcloud Status |



## connectGlobalSocialArtistsArtistIdConnectGlobalSocialPost

> any connectGlobalSocialArtistsArtistIdConnectGlobalSocialPost(artistId, platform)

Connect Global Social

### Example

```ts
import {
  Configuration,
  ConnectApi,
} from '@xr7/sdk';
import type { ConnectGlobalSocialArtistsArtistIdConnectGlobalSocialPostRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new ConnectApi();

  const body = {
    // string
    artistId: artistId_example,
    // string
    platform: platform_example,
  } satisfies ConnectGlobalSocialArtistsArtistIdConnectGlobalSocialPostRequest;

  try {
    const data = await api.connectGlobalSocialArtistsArtistIdConnectGlobalSocialPost(body);
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
| **platform** | `string` |  | [Defaults to `undefined`] |

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


## connectGlobalSocialStatusArtistsArtistIdConnectGlobalSocialStatusGet

> any connectGlobalSocialStatusArtistsArtistIdConnectGlobalSocialStatusGet(artistId)

Connect Global Social Status

### Example

```ts
import {
  Configuration,
  ConnectApi,
} from '@xr7/sdk';
import type { ConnectGlobalSocialStatusArtistsArtistIdConnectGlobalSocialStatusGetRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new ConnectApi();

  const body = {
    // string
    artistId: artistId_example,
  } satisfies ConnectGlobalSocialStatusArtistsArtistIdConnectGlobalSocialStatusGetRequest;

  try {
    const data = await api.connectGlobalSocialStatusArtistsArtistIdConnectGlobalSocialStatusGet(body);
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


## connectSoundcloudArtistsArtistIdConnectSoundcloudPost

> any connectSoundcloudArtistsArtistIdConnectSoundcloudPost(artistId)

Connect Soundcloud

### Example

```ts
import {
  Configuration,
  ConnectApi,
} from '@xr7/sdk';
import type { ConnectSoundcloudArtistsArtistIdConnectSoundcloudPostRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new ConnectApi();

  const body = {
    // string
    artistId: artistId_example,
  } satisfies ConnectSoundcloudArtistsArtistIdConnectSoundcloudPostRequest;

  try {
    const data = await api.connectSoundcloudArtistsArtistIdConnectSoundcloudPost(body);
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


## connectSoundcloudStatusArtistsArtistIdConnectSoundcloudStatusGet

> any connectSoundcloudStatusArtistsArtistIdConnectSoundcloudStatusGet(artistId)

Connect Soundcloud Status

### Example

```ts
import {
  Configuration,
  ConnectApi,
} from '@xr7/sdk';
import type { ConnectSoundcloudStatusArtistsArtistIdConnectSoundcloudStatusGetRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new ConnectApi();

  const body = {
    // string
    artistId: artistId_example,
  } satisfies ConnectSoundcloudStatusArtistsArtistIdConnectSoundcloudStatusGetRequest;

  try {
    const data = await api.connectSoundcloudStatusArtistsArtistIdConnectSoundcloudStatusGet(body);
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
