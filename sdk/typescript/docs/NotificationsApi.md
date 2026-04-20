# NotificationsApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**dispatchNotificationsArtistsArtistIdNotificationsDispatchPost**](NotificationsApi.md#dispatchnotificationsartistsartistidnotificationsdispatchpost) | **POST** /artists/{artist_id}/notifications/dispatch | Dispatch Notifications |
| [**pushRegisterArtistsArtistIdNotificationsPushRegisterPost**](NotificationsApi.md#pushregisterartistsartistidnotificationspushregisterpost) | **POST** /artists/{artist_id}/notifications/push-register | Push Register |
| [**setNotificationPreferencesArtistsArtistIdNotificationsPreferencesPost**](NotificationsApi.md#setnotificationpreferencesartistsartistidnotificationspreferencespost) | **POST** /artists/{artist_id}/notifications/preferences | Set Notification Preferences |
| [**voiceQueryArtistsArtistIdNotificationsVoiceQueryPost**](NotificationsApi.md#voicequeryartistsartistidnotificationsvoicequerypost) | **POST** /artists/{artist_id}/notifications/voice-query | Voice Query |



## dispatchNotificationsArtistsArtistIdNotificationsDispatchPost

> any dispatchNotificationsArtistsArtistIdNotificationsDispatchPost(artistId)

Dispatch Notifications

### Example

```ts
import {
  Configuration,
  NotificationsApi,
} from '@xr7/sdk';
import type { DispatchNotificationsArtistsArtistIdNotificationsDispatchPostRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new NotificationsApi();

  const body = {
    // string
    artistId: artistId_example,
  } satisfies DispatchNotificationsArtistsArtistIdNotificationsDispatchPostRequest;

  try {
    const data = await api.dispatchNotificationsArtistsArtistIdNotificationsDispatchPost(body);
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


## pushRegisterArtistsArtistIdNotificationsPushRegisterPost

> any pushRegisterArtistsArtistIdNotificationsPushRegisterPost(artistId, token, platform)

Push Register

### Example

```ts
import {
  Configuration,
  NotificationsApi,
} from '@xr7/sdk';
import type { PushRegisterArtistsArtistIdNotificationsPushRegisterPostRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new NotificationsApi();

  const body = {
    // string
    artistId: artistId_example,
    // string
    token: token_example,
    // string (optional)
    platform: platform_example,
  } satisfies PushRegisterArtistsArtistIdNotificationsPushRegisterPostRequest;

  try {
    const data = await api.pushRegisterArtistsArtistIdNotificationsPushRegisterPost(body);
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
| **token** | `string` |  | [Defaults to `undefined`] |
| **platform** | `string` |  | [Optional] [Defaults to `&#39;firebase&#39;`] |

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


## setNotificationPreferencesArtistsArtistIdNotificationsPreferencesPost

> NotificationPreferenceSchema setNotificationPreferencesArtistsArtistIdNotificationsPreferencesPost(artistId, notificationPreferenceRequest)

Set Notification Preferences

### Example

```ts
import {
  Configuration,
  NotificationsApi,
} from '@xr7/sdk';
import type { SetNotificationPreferencesArtistsArtistIdNotificationsPreferencesPostRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new NotificationsApi();

  const body = {
    // string
    artistId: artistId_example,
    // NotificationPreferenceRequest
    notificationPreferenceRequest: ...,
  } satisfies SetNotificationPreferencesArtistsArtistIdNotificationsPreferencesPostRequest;

  try {
    const data = await api.setNotificationPreferencesArtistsArtistIdNotificationsPreferencesPost(body);
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
| **notificationPreferenceRequest** | [NotificationPreferenceRequest](NotificationPreferenceRequest.md) |  | |

### Return type

[**NotificationPreferenceSchema**](NotificationPreferenceSchema.md)

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


## voiceQueryArtistsArtistIdNotificationsVoiceQueryPost

> any voiceQueryArtistsArtistIdNotificationsVoiceQueryPost(artistId, question)

Voice Query

### Example

```ts
import {
  Configuration,
  NotificationsApi,
} from '@xr7/sdk';
import type { VoiceQueryArtistsArtistIdNotificationsVoiceQueryPostRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new NotificationsApi();

  const body = {
    // string
    artistId: artistId_example,
    // string
    question: question_example,
  } satisfies VoiceQueryArtistsArtistIdNotificationsVoiceQueryPostRequest;

  try {
    const data = await api.voiceQueryArtistsArtistIdNotificationsVoiceQueryPost(body);
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
| **question** | `string` |  | [Defaults to `undefined`] |

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
