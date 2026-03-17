# xr7_sdk.PublicApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**advocacy_kit_artists_artist_id_advocacy_kit_post**](PublicApi.md#advocacy_kit_artists_artist_id_advocacy_kit_post) | **POST** /artists/{artist_id}/advocacy/kit | Advocacy Kit
[**public_aggregates_stats_public_aggregates_get**](PublicApi.md#public_aggregates_stats_public_aggregates_get) | **GET** /stats/public/aggregates | Public Aggregates
[**public_leaderboard_stats_public_leaderboard_get**](PublicApi.md#public_leaderboard_stats_public_leaderboard_get) | **GET** /stats/public/leaderboard | Public Leaderboard
[**public_success_stories_stats_public_success_stories_get**](PublicApi.md#public_success_stories_stats_public_success_stories_get) | **GET** /stats/public/success-stories | Public Success Stories


# **advocacy_kit_artists_artist_id_advocacy_kit_post**
> object advocacy_kit_artists_artist_id_advocacy_kit_post(artist_id)

Advocacy Kit

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
    api_instance = xr7_sdk.PublicApi(api_client)
    artist_id = 'artist_id_example' # str | 

    try:
        # Advocacy Kit
        api_response = api_instance.advocacy_kit_artists_artist_id_advocacy_kit_post(artist_id)
        print("The response of PublicApi->advocacy_kit_artists_artist_id_advocacy_kit_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PublicApi->advocacy_kit_artists_artist_id_advocacy_kit_post: %s\n" % e)
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

# **public_aggregates_stats_public_aggregates_get**
> object public_aggregates_stats_public_aggregates_get()

Public Aggregates

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
    api_instance = xr7_sdk.PublicApi(api_client)

    try:
        # Public Aggregates
        api_response = api_instance.public_aggregates_stats_public_aggregates_get()
        print("The response of PublicApi->public_aggregates_stats_public_aggregates_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PublicApi->public_aggregates_stats_public_aggregates_get: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

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

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **public_leaderboard_stats_public_leaderboard_get**
> object public_leaderboard_stats_public_leaderboard_get()

Public Leaderboard

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
    api_instance = xr7_sdk.PublicApi(api_client)

    try:
        # Public Leaderboard
        api_response = api_instance.public_leaderboard_stats_public_leaderboard_get()
        print("The response of PublicApi->public_leaderboard_stats_public_leaderboard_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PublicApi->public_leaderboard_stats_public_leaderboard_get: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

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

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **public_success_stories_stats_public_success_stories_get**
> object public_success_stories_stats_public_success_stories_get()

Public Success Stories

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
    api_instance = xr7_sdk.PublicApi(api_client)

    try:
        # Public Success Stories
        api_response = api_instance.public_success_stories_stats_public_success_stories_get()
        print("The response of PublicApi->public_success_stories_stats_public_success_stories_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PublicApi->public_success_stories_stats_public_success_stories_get: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

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

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

