# SovereigntyApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**acceptAdvanceOfferArtistsArtistIdAdvanceAcceptPost**](SovereigntyApi.md#acceptadvanceofferartistsartistidadvanceacceptpost) | **POST** /artists/{artist_id}/advance/accept | Accept Advance Offer |
| [**createAdvanceOfferArtistsArtistIdAdvanceOfferPost**](SovereigntyApi.md#createadvanceofferartistsartistidadvanceofferpost) | **POST** /artists/{artist_id}/advance/offer | Create Advance Offer |
| [**listAdvanceHistoryArtistsArtistIdAdvanceHistoryGet**](SovereigntyApi.md#listadvancehistoryartistsartistidadvancehistoryget) | **GET** /artists/{artist_id}/advance/history | List Advance History |
| [**listRightsGapsArtistsArtistIdRightsGapsGet**](SovereigntyApi.md#listrightsgapsartistsartistidrightsgapsget) | **GET** /artists/{artist_id}/rights/gaps | List Rights Gaps |
| [**registerRightsPacketsArtistsArtistIdRightsRegisterPost**](SovereigntyApi.md#registerrightspacketsartistsartistidrightsregisterpost) | **POST** /artists/{artist_id}/rights/register | Register Rights Packets |
| [**scanRightsArtistsArtistIdRightsScanGet**](SovereigntyApi.md#scanrightsartistsartistidrightsscanget) | **GET** /artists/{artist_id}/rights/scan | Scan Rights |



## acceptAdvanceOfferArtistsArtistIdAdvanceAcceptPost

> { [key: string]: any; } acceptAdvanceOfferArtistsArtistIdAdvanceAcceptPost(artistId, advanceAcceptRequest)

Accept Advance Offer

Accept a pending advance offer. Triggers Trolley disbursement queue.

### Example

```ts
import {
  Configuration,
  SovereigntyApi,
} from '@xr7/sdk';
import type { AcceptAdvanceOfferArtistsArtistIdAdvanceAcceptPostRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const config = new Configuration({
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new SovereigntyApi(config);

  const body = {
    // string
    artistId: artistId_example,
    // AdvanceAcceptRequest
    advanceAcceptRequest: ...,
  } satisfies AcceptAdvanceOfferArtistsArtistIdAdvanceAcceptPostRequest;

  try {
    const data = await api.acceptAdvanceOfferArtistsArtistIdAdvanceAcceptPost(body);
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
| **advanceAcceptRequest** | [AdvanceAcceptRequest](AdvanceAcceptRequest.md) |  | |

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


## createAdvanceOfferArtistsArtistIdAdvanceOfferPost

> { [key: string]: any; } createAdvanceOfferArtistsArtistIdAdvanceOfferPost(artistId, advanceOfferRequest)

Create Advance Offer

Compute and return a cash advance offer backed by predicted recovery.  Safe advance &#x3D; 60% of the predicted-low earnings forecast; repaid automatically when the recovery arrives.

### Example

```ts
import {
  Configuration,
  SovereigntyApi,
} from '@xr7/sdk';
import type { CreateAdvanceOfferArtistsArtistIdAdvanceOfferPostRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const config = new Configuration({
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new SovereigntyApi(config);

  const body = {
    // string
    artistId: artistId_example,
    // AdvanceOfferRequest
    advanceOfferRequest: ...,
  } satisfies CreateAdvanceOfferArtistsArtistIdAdvanceOfferPostRequest;

  try {
    const data = await api.createAdvanceOfferArtistsArtistIdAdvanceOfferPost(body);
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
| **advanceOfferRequest** | [AdvanceOfferRequest](AdvanceOfferRequest.md) |  | |

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


## listAdvanceHistoryArtistsArtistIdAdvanceHistoryGet

> { [key: string]: any; } listAdvanceHistoryArtistsArtistIdAdvanceHistoryGet(artistId)

List Advance History

### Example

```ts
import {
  Configuration,
  SovereigntyApi,
} from '@xr7/sdk';
import type { ListAdvanceHistoryArtistsArtistIdAdvanceHistoryGetRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const config = new Configuration({
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new SovereigntyApi(config);

  const body = {
    // string
    artistId: artistId_example,
  } satisfies ListAdvanceHistoryArtistsArtistIdAdvanceHistoryGetRequest;

  try {
    const data = await api.listAdvanceHistoryArtistsArtistIdAdvanceHistoryGet(body);
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


## listRightsGapsArtistsArtistIdRightsGapsGet

> { [key: string]: any; } listRightsGapsArtistsArtistIdRightsGapsGet(artistId)

List Rights Gaps

List all persisted rights scan results for this artist.

### Example

```ts
import {
  Configuration,
  SovereigntyApi,
} from '@xr7/sdk';
import type { ListRightsGapsArtistsArtistIdRightsGapsGetRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const config = new Configuration({
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new SovereigntyApi(config);

  const body = {
    // string
    artistId: artistId_example,
  } satisfies ListRightsGapsArtistsArtistIdRightsGapsGetRequest;

  try {
    const data = await api.listRightsGapsArtistsArtistIdRightsGapsGet(body);
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


## registerRightsPacketsArtistsArtistIdRightsRegisterPost

> { [key: string]: any; } registerRightsPacketsArtistsArtistIdRightsRegisterPost(artistId)

Register Rights Packets

Generate and persist auto-registration packets for all detected gaps.

### Example

```ts
import {
  Configuration,
  SovereigntyApi,
} from '@xr7/sdk';
import type { RegisterRightsPacketsArtistsArtistIdRightsRegisterPostRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const config = new Configuration({
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new SovereigntyApi(config);

  const body = {
    // string
    artistId: artistId_example,
  } satisfies RegisterRightsPacketsArtistsArtistIdRightsRegisterPostRequest;

  try {
    const data = await api.registerRightsPacketsArtistsArtistIdRightsRegisterPost(body);
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


## scanRightsArtistsArtistIdRightsScanGet

> { [key: string]: any; } scanRightsArtistsArtistIdRightsScanGet(artistId)

Scan Rights

Scan catalog for missing ISRC/ISWC/UPC/PRO/foreign registrations.

### Example

```ts
import {
  Configuration,
  SovereigntyApi,
} from '@xr7/sdk';
import type { ScanRightsArtistsArtistIdRightsScanGetRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const config = new Configuration({
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new SovereigntyApi(config);

  const body = {
    // string
    artistId: artistId_example,
  } satisfies ScanRightsArtistsArtistIdRightsScanGetRequest;

  try {
    const data = await api.scanRightsArtistsArtistIdRightsScanGet(body);
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
