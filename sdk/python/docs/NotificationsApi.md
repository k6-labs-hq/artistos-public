# xr7_sdk.NotificationsApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**dispatch_notifications_artists_artist_id_notifications_dispatch_post**](NotificationsApi.md#dispatch_notifications_artists_artist_id_notifications_dispatch_post) | **POST** /artists/{artist_id}/notifications/dispatch | Dispatch Notifications
[**push_register_artists_artist_id_notifications_push_register_post**](NotificationsApi.md#push_register_artists_artist_id_notifications_push_register_post) | **POST** /artists/{artist_id}/notifications/push-register | Push Register
[**set_notification_preferences_artists_artist_id_notifications_preferences_post**](NotificationsApi.md#set_notification_preferences_artists_artist_id_notifications_preferences_post) | **POST** /artists/{artist_id}/notifications/preferences | Set Notification Preferences
[**voice_query_artists_artist_id_notifications_voice_query_post**](NotificationsApi.md#voice_query_artists_artist_id_notifications_voice_query_post) | **POST** /artists/{artist_id}/notifications/voice-query | Voice Query


# **dispatch_notifications_artists_artist_id_notifications_dispatch_post**
> object dispatch_notifications_artists_artist_id_notifications_dispatch_post(artist_id)

Dispatch Notifications

### Example


```python
import xr7_sdk
from xr7_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = xr7_sdk.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with xr7_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = xr7_sdk.NotificationsApi(api_client)
    artist_id = 'artist_id_example' # str |

    try:
        # Dispatch Notifications
        api_response = api_instance.dispatch_notifications_artists_artist_id_notifications_dispatch_post(artist_id)
        print("The response of NotificationsApi->dispatch_notifications_artists_artist_id_notifications_dispatch_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling NotificationsApi->dispatch_notifications_artists_artist_id_notifications_dispatch_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **artist_id** | **str**|  |

### Return type

**object**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **push_register_artists_artist_id_notifications_push_register_post**
> object push_register_artists_artist_id_notifications_push_register_post(artist_id, token, platform=platform)

Push Register

### Example


```python
import xr7_sdk
from xr7_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = xr7_sdk.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with xr7_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = xr7_sdk.NotificationsApi(api_client)
    artist_id = 'artist_id_example' # str |
    token = 'token_example' # str |
    platform = 'firebase' # str |  (optional) (default to 'firebase')

    try:
        # Push Register
        api_response = api_instance.push_register_artists_artist_id_notifications_push_register_post(artist_id, token, platform=platform)
        print("The response of NotificationsApi->push_register_artists_artist_id_notifications_push_register_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling NotificationsApi->push_register_artists_artist_id_notifications_push_register_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **artist_id** | **str**|  |
 **token** | **str**|  |
 **platform** | **str**|  | [optional] [default to &#39;firebase&#39;]

### Return type

**object**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **set_notification_preferences_artists_artist_id_notifications_preferences_post**
> NotificationPreferenceSchema set_notification_preferences_artists_artist_id_notifications_preferences_post(artist_id, notification_preference_request)

Set Notification Preferences

### Example


```python
import xr7_sdk
from xr7_sdk.models.notification_preference_request import NotificationPreferenceRequest
from xr7_sdk.models.notification_preference_schema import NotificationPreferenceSchema
from xr7_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = xr7_sdk.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with xr7_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = xr7_sdk.NotificationsApi(api_client)
    artist_id = 'artist_id_example' # str |
    notification_preference_request = xr7_sdk.NotificationPreferenceRequest() # NotificationPreferenceRequest |

    try:
        # Set Notification Preferences
        api_response = api_instance.set_notification_preferences_artists_artist_id_notifications_preferences_post(artist_id, notification_preference_request)
        print("The response of NotificationsApi->set_notification_preferences_artists_artist_id_notifications_preferences_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling NotificationsApi->set_notification_preferences_artists_artist_id_notifications_preferences_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **artist_id** | **str**|  |
 **notification_preference_request** | [**NotificationPreferenceRequest**](NotificationPreferenceRequest.md)|  |

### Return type

[**NotificationPreferenceSchema**](NotificationPreferenceSchema.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **voice_query_artists_artist_id_notifications_voice_query_post**
> object voice_query_artists_artist_id_notifications_voice_query_post(artist_id, question)

Voice Query

### Example


```python
import xr7_sdk
from xr7_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = xr7_sdk.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with xr7_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = xr7_sdk.NotificationsApi(api_client)
    artist_id = 'artist_id_example' # str |
    question = 'question_example' # str |

    try:
        # Voice Query
        api_response = api_instance.voice_query_artists_artist_id_notifications_voice_query_post(artist_id, question)
        print("The response of NotificationsApi->voice_query_artists_artist_id_notifications_voice_query_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling NotificationsApi->voice_query_artists_artist_id_notifications_voice_query_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **artist_id** | **str**|  |
 **question** | **str**|  |

### Return type

**object**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)
