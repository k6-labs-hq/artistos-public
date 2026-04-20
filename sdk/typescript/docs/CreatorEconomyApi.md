# CreatorEconomyApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**ingestCreatorDataArtistsArtistIdCreatorIngestPost**](CreatorEconomyApi.md#ingestcreatordataartistsartistidcreatoringestpost) | **POST** /artists/{artist_id}/creator/ingest | Ingest Creator Data |
| [**listCreatorPlatformsArtistsArtistIdCreatorPlatformsGet**](CreatorEconomyApi.md#listcreatorplatformsartistsartistidcreatorplatformsget) | **GET** /artists/{artist_id}/creator/platforms | List Creator Platforms |



## ingestCreatorDataArtistsArtistIdCreatorIngestPost

> { [key: string]: any; } ingestCreatorDataArtistsArtistIdCreatorIngestPost(artistId, creatorIngestRequest)

Ingest Creator Data

Parse and anomaly-scan creator-economy platform data.  Accepts raw export rows from YouTube Studio, TikTok, Instagram Reels, Twitch, Patreon, or Shopify. Returns parsed events and detected anomalies.

### Example

```ts
import {
  Configuration,
  CreatorEconomyApi,
} from '@xr7/sdk';
import type { IngestCreatorDataArtistsArtistIdCreatorIngestPostRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const config = new Configuration({
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new CreatorEconomyApi(config);

  const body = {
    // string
    artistId: artistId_example,
    // CreatorIngestRequest
    creatorIngestRequest: ...,
  } satisfies IngestCreatorDataArtistsArtistIdCreatorIngestPostRequest;

  try {
    const data = await api.ingestCreatorDataArtistsArtistIdCreatorIngestPost(body);
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
| **creatorIngestRequest** | [CreatorIngestRequest](CreatorIngestRequest.md) |  | |

### Return type

**{ [key: string]: any; }**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## listCreatorPlatformsArtistsArtistIdCreatorPlatformsGet

> { [key: string]: any; } listCreatorPlatformsArtistsArtistIdCreatorPlatformsGet(artistId)

List Creator Platforms

List all supported creator-economy platforms.

### Example

```ts
import {
  Configuration,
  CreatorEconomyApi,
} from '@xr7/sdk';
import type { ListCreatorPlatformsArtistsArtistIdCreatorPlatformsGetRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const config = new Configuration({
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new CreatorEconomyApi(config);

  const body = {
    // string
    artistId: artistId_example,
  } satisfies ListCreatorPlatformsArtistsArtistIdCreatorPlatformsGetRequest;

  try {
    const data = await api.listCreatorPlatformsArtistsArtistIdCreatorPlatformsGet(body);
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
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)
