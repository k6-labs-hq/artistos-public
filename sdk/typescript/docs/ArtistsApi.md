# ArtistsApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**artistSummaryArtistsArtistIdSummaryGet**](ArtistsApi.md#artistsummaryartistsartistidsummaryget) | **GET** /artists/{artist_id}/summary | Artist Summary |
| [**catalogHealthArtistsArtistIdMlCatalogHealthGet**](ArtistsApi.md#cataloghealthartistsartistidmlcataloghealthget) | **GET** /artists/{artist_id}/ml/catalog-health | Catalog Health |
| [**connectArtistArtistsArtistIdConnectPost**](ArtistsApi.md#connectartistartistsartistidconnectpost) | **POST** /artists/{artist_id}/connect | Connect Artist |
| [**createArtistArtistsPost**](ArtistsApi.md#createartistartistspost) | **POST** /artists/ | Create Artist |
| [**getArtistArtistsArtistIdGet**](ArtistsApi.md#getartistartistsartistidget) | **GET** /artists/{artist_id} | Get Artist |



## artistSummaryArtistsArtistIdSummaryGet

> any artistSummaryArtistsArtistIdSummaryGet(artistId)

Artist Summary

### Example

```ts
import {
  Configuration,
  ArtistsApi,
} from '@xr7/sdk';
import type { ArtistSummaryArtistsArtistIdSummaryGetRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new ArtistsApi();

  const body = {
    // string
    artistId: artistId_example,
  } satisfies ArtistSummaryArtistsArtistIdSummaryGetRequest;

  try {
    const data = await api.artistSummaryArtistsArtistIdSummaryGet(body);
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


## catalogHealthArtistsArtistIdMlCatalogHealthGet

> any catalogHealthArtistsArtistIdMlCatalogHealthGet(artistId)

Catalog Health

Return an ML-derived catalog health score (0–100) and grade for the artist.  Combines metadata completeness, payment regularity, anomaly density, recovery rate, and earnings accuracy into a single composite score.

### Example

```ts
import {
  Configuration,
  ArtistsApi,
} from '@xr7/sdk';
import type { CatalogHealthArtistsArtistIdMlCatalogHealthGetRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new ArtistsApi();

  const body = {
    // string
    artistId: artistId_example,
  } satisfies CatalogHealthArtistsArtistIdMlCatalogHealthGetRequest;

  try {
    const data = await api.catalogHealthArtistsArtistIdMlCatalogHealthGet(body);
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


## connectArtistArtistsArtistIdConnectPost

> any connectArtistArtistsArtistIdConnectPost(artistId)

Connect Artist

Check which data connectors are configured for this artist and return their credential status.  This endpoint validates that the required environment variables are set for each connector.  It does NOT make real API calls — it only confirms that the credentials are present and the connector is ready to use.  For connectors that are not yet configured, use the statement file upload workflow: POST /artists/{artist_id}/statements/upload

### Example

```ts
import {
  Configuration,
  ArtistsApi,
} from '@xr7/sdk';
import type { ConnectArtistArtistsArtistIdConnectPostRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new ArtistsApi();

  const body = {
    // string
    artistId: artistId_example,
  } satisfies ConnectArtistArtistsArtistIdConnectPostRequest;

  try {
    const data = await api.connectArtistArtistsArtistIdConnectPost(body);
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


## createArtistArtistsPost

> ArtistSchema createArtistArtistsPost(artistCreate)

Create Artist

### Example

```ts
import {
  Configuration,
  ArtistsApi,
} from '@xr7/sdk';
import type { CreateArtistArtistsPostRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new ArtistsApi();

  const body = {
    // ArtistCreate
    artistCreate: ...,
  } satisfies CreateArtistArtistsPostRequest;

  try {
    const data = await api.createArtistArtistsPost(body);
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
| **artistCreate** | [ArtistCreate](ArtistCreate.md) |  | |

### Return type

[**ArtistSchema**](ArtistSchema.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **201** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## getArtistArtistsArtistIdGet

> ArtistSchema getArtistArtistsArtistIdGet(artistId)

Get Artist

### Example

```ts
import {
  Configuration,
  ArtistsApi,
} from '@xr7/sdk';
import type { GetArtistArtistsArtistIdGetRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new ArtistsApi();

  const body = {
    // string
    artistId: artistId_example,
  } satisfies GetArtistArtistsArtistIdGetRequest;

  try {
    const data = await api.getArtistArtistsArtistIdGet(body);
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

[**ArtistSchema**](ArtistSchema.md)

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

