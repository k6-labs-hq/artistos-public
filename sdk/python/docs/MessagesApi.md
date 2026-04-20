# xr7_sdk.MessagesApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**business_manager_chat_artists_artist_id_messages_chat_post**](MessagesApi.md#business_manager_chat_artists_artist_id_messages_chat_post) | **POST** /artists/{artist_id}/messages/chat | Business Manager Chat
[**create_weekly_story_artists_artist_id_messages_weekly_story_post**](MessagesApi.md#create_weekly_story_artists_artist_id_messages_weekly_story_post) | **POST** /artists/{artist_id}/messages/weekly-story | Create Weekly Story
[**get_feed_artists_artist_id_messages_feed_get**](MessagesApi.md#get_feed_artists_artist_id_messages_feed_get) | **GET** /artists/{artist_id}/messages/feed | Get Feed


# **business_manager_chat_artists_artist_id_messages_chat_post**
> Dict[str, object] business_manager_chat_artists_artist_id_messages_chat_post(artist_id, chat_request)

Business Manager Chat

Natural-language business manager.

Accepts a question like "Why was my YouTube lower?" and returns a
plain-English answer grounded in this artist's anomaly + earnings data.

### Example

* Bearer Authentication (HTTPBearer):

```python
import xr7_sdk
from xr7_sdk.models.chat_request import ChatRequest
from xr7_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = xr7_sdk.Configuration(
    host = "http://localhost"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization: HTTPBearer
configuration = xr7_sdk.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with xr7_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = xr7_sdk.MessagesApi(api_client)
    artist_id = 'artist_id_example' # str |
    chat_request = xr7_sdk.ChatRequest() # ChatRequest |

    try:
        # Business Manager Chat
        api_response = api_instance.business_manager_chat_artists_artist_id_messages_chat_post(artist_id, chat_request)
        print("The response of MessagesApi->business_manager_chat_artists_artist_id_messages_chat_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling MessagesApi->business_manager_chat_artists_artist_id_messages_chat_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **artist_id** | **str**|  |
 **chat_request** | [**ChatRequest**](ChatRequest.md)|  |

### Return type

**Dict[str, object]**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **create_weekly_story_artists_artist_id_messages_weekly_story_post**
> Dict[str, object] create_weekly_story_artists_artist_id_messages_weekly_story_post(artist_id, weekly_story_request)

Create Weekly Story

Generate and persist a weekly earnings story for the artist.

### Example

* Bearer Authentication (HTTPBearer):

```python
import xr7_sdk
from xr7_sdk.models.weekly_story_request import WeeklyStoryRequest
from xr7_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = xr7_sdk.Configuration(
    host = "http://localhost"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization: HTTPBearer
configuration = xr7_sdk.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with xr7_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = xr7_sdk.MessagesApi(api_client)
    artist_id = 'artist_id_example' # str |
    weekly_story_request = xr7_sdk.WeeklyStoryRequest() # WeeklyStoryRequest |

    try:
        # Create Weekly Story
        api_response = api_instance.create_weekly_story_artists_artist_id_messages_weekly_story_post(artist_id, weekly_story_request)
        print("The response of MessagesApi->create_weekly_story_artists_artist_id_messages_weekly_story_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling MessagesApi->create_weekly_story_artists_artist_id_messages_weekly_story_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **artist_id** | **str**|  |
 **weekly_story_request** | [**WeeklyStoryRequest**](WeeklyStoryRequest.md)|  |

### Return type

**Dict[str, object]**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_feed_artists_artist_id_messages_feed_get**
> Dict[str, object] get_feed_artists_artist_id_messages_feed_get(artist_id, limit=limit, unread_only=unread_only)

Get Feed

Return the artist's message feed (onboarding, comfort, claim, SOL, deposit, weekly story).

### Example

* Bearer Authentication (HTTPBearer):

```python
import xr7_sdk
from xr7_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = xr7_sdk.Configuration(
    host = "http://localhost"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization: HTTPBearer
configuration = xr7_sdk.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with xr7_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = xr7_sdk.MessagesApi(api_client)
    artist_id = 'artist_id_example' # str |
    limit = 50 # int |  (optional) (default to 50)
    unread_only = False # bool |  (optional) (default to False)

    try:
        # Get Feed
        api_response = api_instance.get_feed_artists_artist_id_messages_feed_get(artist_id, limit=limit, unread_only=unread_only)
        print("The response of MessagesApi->get_feed_artists_artist_id_messages_feed_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling MessagesApi->get_feed_artists_artist_id_messages_feed_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **artist_id** | **str**|  |
 **limit** | **int**|  | [optional] [default to 50]
 **unread_only** | **bool**|  | [optional] [default to False]

### Return type

**Dict[str, object]**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)
