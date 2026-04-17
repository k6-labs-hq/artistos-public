# ArtistsApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**artistSummaryArtistsArtistIdSummaryGet**](ArtistsApi.md#artistsummaryartistsartistidsummaryget) | **GET** /artists/{artist_id}/summary | Artist Summary |
| [**catalogHealthArtistsArtistIdMlCatalogHealthGet**](ArtistsApi.md#cataloghealthartistsartistidmlcataloghealthget) | **GET** /artists/{artist_id}/ml/catalog-health | Catalog Health |
| [**connectArtistArtistsArtistIdConnectPost**](ArtistsApi.md#connectartistartistsartistidconnectpost) | **POST** /artists/{artist_id}/connect | Connect Artist |
| [**connectProviderArtistsArtistIdConnectProviderPost**](ArtistsApi.md#connectproviderartistsartistidconnectproviderpost) | **POST** /artists/{artist_id}/connect/{provider} | Connect Provider |
| [**createArtistArtistsPost**](ArtistsApi.md#createartistartistspost) | **POST** /artists/ | Create Artist |
| [**getArtistArtistsArtistIdGet**](ArtistsApi.md#getartistartistsartistidget) | **GET** /artists/{artist_id} | Get Artist |
| [**getArtistPreferencesArtistsArtistIdPreferencesGet**](ArtistsApi.md#getartistpreferencesartistsartistidpreferencesget) | **GET** /artists/{artist_id}/preferences | Get Artist Preferences |
| [**providerConnectionStatusArtistsArtistIdConnectProviderStatusGet**](ArtistsApi.md#providerconnectionstatusartistsartistidconnectproviderstatusget) | **GET** /artists/{artist_id}/connect/{provider}/status | Provider Connection Status |
| [**updateArtistPreferencesArtistsArtistIdPreferencesPut**](ArtistsApi.md#updateartistpreferencesartistsartistidpreferencesput) | **PUT** /artists/{artist_id}/preferences | Update Artist Preferences |
| [**weeklyDigestArtistsArtistIdDigestWeeklyGet**](ArtistsApi.md#weeklydigestartistsartistiddigestweeklyget) | **GET** /artists/{artist_id}/digest/weekly | Weekly Digest |



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


## connectProviderArtistsArtistIdConnectProviderPost

> any connectProviderArtistsArtistIdConnectProviderPost(artistId, provider)

Connect Provider

### Example

```ts
import {
  Configuration,
  ArtistsApi,
} from '@xr7/sdk';
import type { ConnectProviderArtistsArtistIdConnectProviderPostRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new ArtistsApi();

  const body = {
    // string
    artistId: artistId_example,
    // string
    provider: provider_example,
  } satisfies ConnectProviderArtistsArtistIdConnectProviderPostRequest;

  try {
    const data = await api.connectProviderArtistsArtistIdConnectProviderPost(body);
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
| **provider** | `string` |  | [Defaults to `undefined`] |

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


## getArtistPreferencesArtistsArtistIdPreferencesGet

> any getArtistPreferencesArtistsArtistIdPreferencesGet(artistId)

Get Artist Preferences

### Example

```ts
import {
  Configuration,
  ArtistsApi,
} from '@xr7/sdk';
import type { GetArtistPreferencesArtistsArtistIdPreferencesGetRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new ArtistsApi();

  const body = {
    // string
    artistId: artistId_example,
  } satisfies GetArtistPreferencesArtistsArtistIdPreferencesGetRequest;

  try {
    const data = await api.getArtistPreferencesArtistsArtistIdPreferencesGet(body);
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


## providerConnectionStatusArtistsArtistIdConnectProviderStatusGet

> any providerConnectionStatusArtistsArtistIdConnectProviderStatusGet(artistId, provider)

Provider Connection Status

### Example

```ts
import {
  Configuration,
  ArtistsApi,
} from '@xr7/sdk';
import type { ProviderConnectionStatusArtistsArtistIdConnectProviderStatusGetRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new ArtistsApi();

  const body = {
    // string
    artistId: artistId_example,
    // string
    provider: provider_example,
  } satisfies ProviderConnectionStatusArtistsArtistIdConnectProviderStatusGetRequest;

  try {
    const data = await api.providerConnectionStatusArtistsArtistIdConnectProviderStatusGet(body);
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
| **provider** | `string` |  | [Defaults to `undefined`] |

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


## updateArtistPreferencesArtistsArtistIdPreferencesPut

> any updateArtistPreferencesArtistsArtistIdPreferencesPut(artistId, artistPreferenceUpdateRequest)

Update Artist Preferences

### Example

```ts
import {
  Configuration,
  ArtistsApi,
} from '@xr7/sdk';
import type { UpdateArtistPreferencesArtistsArtistIdPreferencesPutRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new ArtistsApi();

  const body = {
    // string
    artistId: artistId_example,
    // ArtistPreferenceUpdateRequest
    artistPreferenceUpdateRequest: ...,
  } satisfies UpdateArtistPreferencesArtistsArtistIdPreferencesPutRequest;

  try {
    const data = await api.updateArtistPreferencesArtistsArtistIdPreferencesPut(body);
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
| **artistPreferenceUpdateRequest** | [ArtistPreferenceUpdateRequest](ArtistPreferenceUpdateRequest.md) |  | |

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


## weeklyDigestArtistsArtistIdDigestWeeklyGet

> any weeklyDigestArtistsArtistIdDigestWeeklyGet(artistId)

Weekly Digest

### Example

```ts
import {
  Configuration,
  ArtistsApi,
} from '@xr7/sdk';
import type { WeeklyDigestArtistsArtistIdDigestWeeklyGetRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new ArtistsApi();

  const body = {
    // string
    artistId: artistId_example,
  } satisfies WeeklyDigestArtistsArtistIdDigestWeeklyGetRequest;

  try {
    const data = await api.weeklyDigestArtistsArtistIdDigestWeeklyGet(body);
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
