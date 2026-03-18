# IdentityApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**autoMatchIdentityArtistsArtistIdIdentityAutoMatchPost**](IdentityApi.md#automatchidentityartistsartistididentityautomatchpost) | **POST** /artists/{artist_id}/identity/auto-match | Auto Match Identity |
| [**decideIdentityMatchArtistsArtistIdIdentityMatchesMatchIdDecisionPost**](IdentityApi.md#decideidentitymatchartistsartistididentitymatchesmatchiddecisionpost) | **POST** /artists/{artist_id}/identity/matches/{match_id}/decision | Decide Identity Match |
| [**getIdentityMatchAuditArtistsArtistIdIdentityMatchesMatchIdAuditGet**](IdentityApi.md#getidentitymatchauditartistsartistididentitymatchesmatchidauditget) | **GET** /artists/{artist_id}/identity/matches/{match_id}/audit | Get Identity Match Audit |
| [**listIdentityMatchesArtistsArtistIdIdentityMatchesGet**](IdentityApi.md#listidentitymatchesartistsartistididentitymatchesget) | **GET** /artists/{artist_id}/identity/matches | List Identity Matches |



## autoMatchIdentityArtistsArtistIdIdentityAutoMatchPost

> ArtistIdentityMatchSchema autoMatchIdentityArtistsArtistIdIdentityAutoMatchPost(artistId, identityMatchRequest, authorization)

Auto Match Identity

### Example

```ts
import {
  Configuration,
  IdentityApi,
} from '@xr7/sdk';
import type { AutoMatchIdentityArtistsArtistIdIdentityAutoMatchPostRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new IdentityApi();

  const body = {
    // string
    artistId: artistId_example,
    // IdentityMatchRequest
    identityMatchRequest: ...,
    // string (optional)
    authorization: authorization_example,
  } satisfies AutoMatchIdentityArtistsArtistIdIdentityAutoMatchPostRequest;

  try {
    const data = await api.autoMatchIdentityArtistsArtistIdIdentityAutoMatchPost(body);
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
| **identityMatchRequest** | [IdentityMatchRequest](IdentityMatchRequest.md) |  | |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

[**ArtistIdentityMatchSchema**](ArtistIdentityMatchSchema.md)

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


## decideIdentityMatchArtistsArtistIdIdentityMatchesMatchIdDecisionPost

> ArtistIdentityMatchSchema decideIdentityMatchArtistsArtistIdIdentityMatchesMatchIdDecisionPost(artistId, matchId, identityDecisionRequest, authorization)

Decide Identity Match

### Example

```ts
import {
  Configuration,
  IdentityApi,
} from '@xr7/sdk';
import type { DecideIdentityMatchArtistsArtistIdIdentityMatchesMatchIdDecisionPostRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new IdentityApi();

  const body = {
    // string
    artistId: artistId_example,
    // string
    matchId: matchId_example,
    // IdentityDecisionRequest
    identityDecisionRequest: ...,
    // string (optional)
    authorization: authorization_example,
  } satisfies DecideIdentityMatchArtistsArtistIdIdentityMatchesMatchIdDecisionPostRequest;

  try {
    const data = await api.decideIdentityMatchArtistsArtistIdIdentityMatchesMatchIdDecisionPost(body);
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
| **matchId** | `string` |  | [Defaults to `undefined`] |
| **identityDecisionRequest** | [IdentityDecisionRequest](IdentityDecisionRequest.md) |  | |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

[**ArtistIdentityMatchSchema**](ArtistIdentityMatchSchema.md)

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


## getIdentityMatchAuditArtistsArtistIdIdentityMatchesMatchIdAuditGet

> { [key: string]: any; } getIdentityMatchAuditArtistsArtistIdIdentityMatchesMatchIdAuditGet(artistId, matchId, authorization)

Get Identity Match Audit

### Example

```ts
import {
  Configuration,
  IdentityApi,
} from '@xr7/sdk';
import type { GetIdentityMatchAuditArtistsArtistIdIdentityMatchesMatchIdAuditGetRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new IdentityApi();

  const body = {
    // string
    artistId: artistId_example,
    // string
    matchId: matchId_example,
    // string (optional)
    authorization: authorization_example,
  } satisfies GetIdentityMatchAuditArtistsArtistIdIdentityMatchesMatchIdAuditGetRequest;

  try {
    const data = await api.getIdentityMatchAuditArtistsArtistIdIdentityMatchesMatchIdAuditGet(body);
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
| **matchId** | `string` |  | [Defaults to `undefined`] |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

**{ [key: string]: any; }**

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


## listIdentityMatchesArtistsArtistIdIdentityMatchesGet

> { [key: string]: any; } listIdentityMatchesArtistsArtistIdIdentityMatchesGet(artistId, authorization)

List Identity Matches

### Example

```ts
import {
  Configuration,
  IdentityApi,
} from '@xr7/sdk';
import type { ListIdentityMatchesArtistsArtistIdIdentityMatchesGetRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new IdentityApi();

  const body = {
    // string
    artistId: artistId_example,
    // string (optional)
    authorization: authorization_example,
  } satisfies ListIdentityMatchesArtistsArtistIdIdentityMatchesGetRequest;

  try {
    const data = await api.listIdentityMatchesArtistsArtistIdIdentityMatchesGet(body);
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
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

**{ [key: string]: any; }**

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

