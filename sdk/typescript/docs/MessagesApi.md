# MessagesApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**businessManagerChatArtistsArtistIdMessagesChatPost**](MessagesApi.md#businessmanagerchatartistsartistidmessageschatpost) | **POST** /artists/{artist_id}/messages/chat | Business Manager Chat |
| [**createWeeklyStoryArtistsArtistIdMessagesWeeklyStoryPost**](MessagesApi.md#createweeklystoryartistsartistidmessagesweeklystorypost) | **POST** /artists/{artist_id}/messages/weekly-story | Create Weekly Story |
| [**getFeedArtistsArtistIdMessagesFeedGet**](MessagesApi.md#getfeedartistsartistidmessagesfeedget) | **GET** /artists/{artist_id}/messages/feed | Get Feed |



## businessManagerChatArtistsArtistIdMessagesChatPost

> { [key: string]: any; } businessManagerChatArtistsArtistIdMessagesChatPost(artistId, chatRequest)

Business Manager Chat

Natural-language business manager.  Accepts a question like \&quot;Why was my YouTube lower?\&quot; and returns a plain-English answer grounded in this artist\&#39;s anomaly + earnings data.

### Example

```ts
import {
  Configuration,
  MessagesApi,
} from '@xr7/sdk';
import type { BusinessManagerChatArtistsArtistIdMessagesChatPostRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const config = new Configuration({ 
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new MessagesApi(config);

  const body = {
    // string
    artistId: artistId_example,
    // ChatRequest
    chatRequest: ...,
  } satisfies BusinessManagerChatArtistsArtistIdMessagesChatPostRequest;

  try {
    const data = await api.businessManagerChatArtistsArtistIdMessagesChatPost(body);
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
| **chatRequest** | [ChatRequest](ChatRequest.md) |  | |

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


## createWeeklyStoryArtistsArtistIdMessagesWeeklyStoryPost

> { [key: string]: any; } createWeeklyStoryArtistsArtistIdMessagesWeeklyStoryPost(artistId, weeklyStoryRequest)

Create Weekly Story

Generate and persist a weekly earnings story for the artist.

### Example

```ts
import {
  Configuration,
  MessagesApi,
} from '@xr7/sdk';
import type { CreateWeeklyStoryArtistsArtistIdMessagesWeeklyStoryPostRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const config = new Configuration({ 
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new MessagesApi(config);

  const body = {
    // string
    artistId: artistId_example,
    // WeeklyStoryRequest
    weeklyStoryRequest: ...,
  } satisfies CreateWeeklyStoryArtistsArtistIdMessagesWeeklyStoryPostRequest;

  try {
    const data = await api.createWeeklyStoryArtistsArtistIdMessagesWeeklyStoryPost(body);
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
| **weeklyStoryRequest** | [WeeklyStoryRequest](WeeklyStoryRequest.md) |  | |

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


## getFeedArtistsArtistIdMessagesFeedGet

> { [key: string]: any; } getFeedArtistsArtistIdMessagesFeedGet(artistId, limit, unreadOnly)

Get Feed

Return the artist\&#39;s message feed (onboarding, comfort, claim, SOL, deposit, weekly story).

### Example

```ts
import {
  Configuration,
  MessagesApi,
} from '@xr7/sdk';
import type { GetFeedArtistsArtistIdMessagesFeedGetRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const config = new Configuration({ 
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new MessagesApi(config);

  const body = {
    // string
    artistId: artistId_example,
    // number (optional)
    limit: 56,
    // boolean (optional)
    unreadOnly: true,
  } satisfies GetFeedArtistsArtistIdMessagesFeedGetRequest;

  try {
    const data = await api.getFeedArtistsArtistIdMessagesFeedGet(body);
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
| **limit** | `number` |  | [Optional] [Defaults to `50`] |
| **unreadOnly** | `boolean` |  | [Optional] [Defaults to `false`] |

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

