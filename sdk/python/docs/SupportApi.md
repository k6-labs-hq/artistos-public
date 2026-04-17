# xr7_sdk.SupportApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**support_action_artists_artist_id_support_action_post**](SupportApi.md#support_action_artists_artist_id_support_action_post) | **POST** /artists/{artist_id}/support/action | Support Action
[**support_chat_artists_artist_id_support_chat_post**](SupportApi.md#support_chat_artists_artist_id_support_chat_post) | **POST** /artists/{artist_id}/support/chat | Support Chat
[**support_history_artists_artist_id_support_history_get**](SupportApi.md#support_history_artists_artist_id_support_history_get) | **GET** /artists/{artist_id}/support/history | Support History
[**support_suggestions_artists_artist_id_support_suggestions_get**](SupportApi.md#support_suggestions_artists_artist_id_support_suggestions_get) | **GET** /artists/{artist_id}/support/suggestions | Support Suggestions


# **support_action_artists_artist_id_support_action_post**
> SupportActionResponse support_action_artists_artist_id_support_action_post(artist_id, support_action_request, x_actor_email=x_actor_email, x_actor_role=x_actor_role)

Support Action

### Example


```python
import xr7_sdk
from xr7_sdk.models.support_action_request import SupportActionRequest
from xr7_sdk.models.support_action_response import SupportActionResponse
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
    api_instance = xr7_sdk.SupportApi(api_client)
    artist_id = 'artist_id_example' # str |
    support_action_request = xr7_sdk.SupportActionRequest() # SupportActionRequest |
    x_actor_email = 'x_actor_email_example' # str |  (optional)
    x_actor_role = 'x_actor_role_example' # str |  (optional)

    try:
        # Support Action
        api_response = api_instance.support_action_artists_artist_id_support_action_post(artist_id, support_action_request, x_actor_email=x_actor_email, x_actor_role=x_actor_role)
        print("The response of SupportApi->support_action_artists_artist_id_support_action_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling SupportApi->support_action_artists_artist_id_support_action_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **artist_id** | **str**|  |
 **support_action_request** | [**SupportActionRequest**](SupportActionRequest.md)|  |
 **x_actor_email** | **str**|  | [optional]
 **x_actor_role** | **str**|  | [optional]

### Return type

[**SupportActionResponse**](SupportActionResponse.md)

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

# **support_chat_artists_artist_id_support_chat_post**
> SupportChatResponse support_chat_artists_artist_id_support_chat_post(artist_id, support_chat_request, x_actor_email=x_actor_email, x_actor_role=x_actor_role)

Support Chat

### Example


```python
import xr7_sdk
from xr7_sdk.models.support_chat_request import SupportChatRequest
from xr7_sdk.models.support_chat_response import SupportChatResponse
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
    api_instance = xr7_sdk.SupportApi(api_client)
    artist_id = 'artist_id_example' # str |
    support_chat_request = xr7_sdk.SupportChatRequest() # SupportChatRequest |
    x_actor_email = 'x_actor_email_example' # str |  (optional)
    x_actor_role = 'x_actor_role_example' # str |  (optional)

    try:
        # Support Chat
        api_response = api_instance.support_chat_artists_artist_id_support_chat_post(artist_id, support_chat_request, x_actor_email=x_actor_email, x_actor_role=x_actor_role)
        print("The response of SupportApi->support_chat_artists_artist_id_support_chat_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling SupportApi->support_chat_artists_artist_id_support_chat_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **artist_id** | **str**|  |
 **support_chat_request** | [**SupportChatRequest**](SupportChatRequest.md)|  |
 **x_actor_email** | **str**|  | [optional]
 **x_actor_role** | **str**|  | [optional]

### Return type

[**SupportChatResponse**](SupportChatResponse.md)

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

# **support_history_artists_artist_id_support_history_get**
> SupportHistoryResponse support_history_artists_artist_id_support_history_get(artist_id, page=page, page_size=page_size, cursor=cursor, thread_id=thread_id, x_actor_email=x_actor_email, x_actor_role=x_actor_role)

Support History

### Example


```python
import xr7_sdk
from xr7_sdk.models.support_history_response import SupportHistoryResponse
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
    api_instance = xr7_sdk.SupportApi(api_client)
    artist_id = 'artist_id_example' # str |
    page = 1 # int |  (optional) (default to 1)
    page_size = 20 # int |  (optional) (default to 20)
    cursor = 'cursor_example' # str |  (optional)
    thread_id = 'thread_id_example' # str |  (optional)
    x_actor_email = 'x_actor_email_example' # str |  (optional)
    x_actor_role = 'x_actor_role_example' # str |  (optional)

    try:
        # Support History
        api_response = api_instance.support_history_artists_artist_id_support_history_get(artist_id, page=page, page_size=page_size, cursor=cursor, thread_id=thread_id, x_actor_email=x_actor_email, x_actor_role=x_actor_role)
        print("The response of SupportApi->support_history_artists_artist_id_support_history_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling SupportApi->support_history_artists_artist_id_support_history_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **artist_id** | **str**|  |
 **page** | **int**|  | [optional] [default to 1]
 **page_size** | **int**|  | [optional] [default to 20]
 **cursor** | **str**|  | [optional]
 **thread_id** | **str**|  | [optional]
 **x_actor_email** | **str**|  | [optional]
 **x_actor_role** | **str**|  | [optional]

### Return type

[**SupportHistoryResponse**](SupportHistoryResponse.md)

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

# **support_suggestions_artists_artist_id_support_suggestions_get**
> SupportSuggestionResponse support_suggestions_artists_artist_id_support_suggestions_get(artist_id, x_actor_email=x_actor_email, x_actor_role=x_actor_role)

Support Suggestions

### Example


```python
import xr7_sdk
from xr7_sdk.models.support_suggestion_response import SupportSuggestionResponse
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
    api_instance = xr7_sdk.SupportApi(api_client)
    artist_id = 'artist_id_example' # str |
    x_actor_email = 'x_actor_email_example' # str |  (optional)
    x_actor_role = 'x_actor_role_example' # str |  (optional)

    try:
        # Support Suggestions
        api_response = api_instance.support_suggestions_artists_artist_id_support_suggestions_get(artist_id, x_actor_email=x_actor_email, x_actor_role=x_actor_role)
        print("The response of SupportApi->support_suggestions_artists_artist_id_support_suggestions_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling SupportApi->support_suggestions_artists_artist_id_support_suggestions_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **artist_id** | **str**|  |
 **x_actor_email** | **str**|  | [optional]
 **x_actor_role** | **str**|  | [optional]

### Return type

[**SupportSuggestionResponse**](SupportSuggestionResponse.md)

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
