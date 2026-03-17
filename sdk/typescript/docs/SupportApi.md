# SupportApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**supportActionArtistsArtistIdSupportActionPost**](SupportApi.md#supportactionartistsartistidsupportactionpost) | **POST** /artists/{artist_id}/support/action | Support Action |
| [**supportChatArtistsArtistIdSupportChatPost**](SupportApi.md#supportchatartistsartistidsupportchatpost) | **POST** /artists/{artist_id}/support/chat | Support Chat |
| [**supportHistoryArtistsArtistIdSupportHistoryGet**](SupportApi.md#supporthistoryartistsartistidsupporthistoryget) | **GET** /artists/{artist_id}/support/history | Support History |
| [**supportSuggestionsArtistsArtistIdSupportSuggestionsGet**](SupportApi.md#supportsuggestionsartistsartistidsupportsuggestionsget) | **GET** /artists/{artist_id}/support/suggestions | Support Suggestions |



## supportActionArtistsArtistIdSupportActionPost

> SupportActionResponse supportActionArtistsArtistIdSupportActionPost(artistId, supportActionRequest, xActorEmail, xActorRole)

Support Action

### Example

```ts
import {
  Configuration,
  SupportApi,
} from '@xr7/sdk';
import type { SupportActionArtistsArtistIdSupportActionPostRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new SupportApi();

  const body = {
    // string
    artistId: artistId_example,
    // SupportActionRequest
    supportActionRequest: ...,
    // string (optional)
    xActorEmail: xActorEmail_example,
    // string (optional)
    xActorRole: xActorRole_example,
  } satisfies SupportActionArtistsArtistIdSupportActionPostRequest;

  try {
    const data = await api.supportActionArtistsArtistIdSupportActionPost(body);
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
| **supportActionRequest** | [SupportActionRequest](SupportActionRequest.md) |  | |
| **xActorEmail** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xActorRole** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

[**SupportActionResponse**](SupportActionResponse.md)

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


## supportChatArtistsArtistIdSupportChatPost

> SupportChatResponse supportChatArtistsArtistIdSupportChatPost(artistId, supportChatRequest, xActorEmail, xActorRole)

Support Chat

### Example

```ts
import {
  Configuration,
  SupportApi,
} from '@xr7/sdk';
import type { SupportChatArtistsArtistIdSupportChatPostRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new SupportApi();

  const body = {
    // string
    artistId: artistId_example,
    // SupportChatRequest
    supportChatRequest: ...,
    // string (optional)
    xActorEmail: xActorEmail_example,
    // string (optional)
    xActorRole: xActorRole_example,
  } satisfies SupportChatArtistsArtistIdSupportChatPostRequest;

  try {
    const data = await api.supportChatArtistsArtistIdSupportChatPost(body);
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
| **supportChatRequest** | [SupportChatRequest](SupportChatRequest.md) |  | |
| **xActorEmail** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xActorRole** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

[**SupportChatResponse**](SupportChatResponse.md)

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


## supportHistoryArtistsArtistIdSupportHistoryGet

> SupportHistoryResponse supportHistoryArtistsArtistIdSupportHistoryGet(artistId, page, pageSize, cursor, threadId, xActorEmail, xActorRole)

Support History

### Example

```ts
import {
  Configuration,
  SupportApi,
} from '@xr7/sdk';
import type { SupportHistoryArtistsArtistIdSupportHistoryGetRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new SupportApi();

  const body = {
    // string
    artistId: artistId_example,
    // number (optional)
    page: 56,
    // number (optional)
    pageSize: 56,
    // string (optional)
    cursor: cursor_example,
    // string (optional)
    threadId: threadId_example,
    // string (optional)
    xActorEmail: xActorEmail_example,
    // string (optional)
    xActorRole: xActorRole_example,
  } satisfies SupportHistoryArtistsArtistIdSupportHistoryGetRequest;

  try {
    const data = await api.supportHistoryArtistsArtistIdSupportHistoryGet(body);
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
| **page** | `number` |  | [Optional] [Defaults to `1`] |
| **pageSize** | `number` |  | [Optional] [Defaults to `20`] |
| **cursor** | `string` |  | [Optional] [Defaults to `undefined`] |
| **threadId** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xActorEmail** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xActorRole** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

[**SupportHistoryResponse**](SupportHistoryResponse.md)

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


## supportSuggestionsArtistsArtistIdSupportSuggestionsGet

> SupportSuggestionResponse supportSuggestionsArtistsArtistIdSupportSuggestionsGet(artistId, xActorEmail, xActorRole)

Support Suggestions

### Example

```ts
import {
  Configuration,
  SupportApi,
} from '@xr7/sdk';
import type { SupportSuggestionsArtistsArtistIdSupportSuggestionsGetRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new SupportApi();

  const body = {
    // string
    artistId: artistId_example,
    // string (optional)
    xActorEmail: xActorEmail_example,
    // string (optional)
    xActorRole: xActorRole_example,
  } satisfies SupportSuggestionsArtistsArtistIdSupportSuggestionsGetRequest;

  try {
    const data = await api.supportSuggestionsArtistsArtistIdSupportSuggestionsGet(body);
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
| **xActorEmail** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xActorRole** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

[**SupportSuggestionResponse**](SupportSuggestionResponse.md)

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

