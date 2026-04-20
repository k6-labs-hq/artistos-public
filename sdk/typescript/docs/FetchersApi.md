# FetchersApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**fetchGlobalSocialArtistsArtistIdFetchersGlobalSocialPost**](FetchersApi.md#fetchglobalsocialartistsartistidfetchersglobalsocialpost) | **POST** /artists/{artist_id}/fetchers/global-social | Fetch Global Social |



## fetchGlobalSocialArtistsArtistIdFetchersGlobalSocialPost

> any fetchGlobalSocialArtistsArtistIdFetchersGlobalSocialPost(artistId)

Fetch Global Social

### Example

```ts
import {
  Configuration,
  FetchersApi,
} from '@xr7/sdk';
import type { FetchGlobalSocialArtistsArtistIdFetchersGlobalSocialPostRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new FetchersApi();

  const body = {
    // string
    artistId: artistId_example,
  } satisfies FetchGlobalSocialArtistsArtistIdFetchersGlobalSocialPostRequest;

  try {
    const data = await api.fetchGlobalSocialArtistsArtistIdFetchersGlobalSocialPost(body);
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
