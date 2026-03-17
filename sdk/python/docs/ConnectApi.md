# xr7_sdk.ConnectApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**connect_global_social_artists_artist_id_connect_global_social_post**](ConnectApi.md#connect_global_social_artists_artist_id_connect_global_social_post) | **POST** /artists/{artist_id}/connect/global-social | Connect Global Social
[**connect_global_social_status_artists_artist_id_connect_global_social_status_get**](ConnectApi.md#connect_global_social_status_artists_artist_id_connect_global_social_status_get) | **GET** /artists/{artist_id}/connect/global-social/status | Connect Global Social Status
[**connect_soundcloud_artists_artist_id_connect_soundcloud_post**](ConnectApi.md#connect_soundcloud_artists_artist_id_connect_soundcloud_post) | **POST** /artists/{artist_id}/connect/soundcloud | Connect Soundcloud
[**connect_soundcloud_status_artists_artist_id_connect_soundcloud_status_get**](ConnectApi.md#connect_soundcloud_status_artists_artist_id_connect_soundcloud_status_get) | **GET** /artists/{artist_id}/connect/soundcloud/status | Connect Soundcloud Status


# **connect_global_social_artists_artist_id_connect_global_social_post**
> object connect_global_social_artists_artist_id_connect_global_social_post(artist_id, platform)

Connect Global Social

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
    api_instance = xr7_sdk.ConnectApi(api_client)
    artist_id = 'artist_id_example' # str | 
    platform = 'platform_example' # str | 

    try:
        # Connect Global Social
        api_response = api_instance.connect_global_social_artists_artist_id_connect_global_social_post(artist_id, platform)
        print("The response of ConnectApi->connect_global_social_artists_artist_id_connect_global_social_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ConnectApi->connect_global_social_artists_artist_id_connect_global_social_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **artist_id** | **str**|  | 
 **platform** | **str**|  | 

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

# **connect_global_social_status_artists_artist_id_connect_global_social_status_get**
> object connect_global_social_status_artists_artist_id_connect_global_social_status_get(artist_id)

Connect Global Social Status

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
    api_instance = xr7_sdk.ConnectApi(api_client)
    artist_id = 'artist_id_example' # str | 

    try:
        # Connect Global Social Status
        api_response = api_instance.connect_global_social_status_artists_artist_id_connect_global_social_status_get(artist_id)
        print("The response of ConnectApi->connect_global_social_status_artists_artist_id_connect_global_social_status_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ConnectApi->connect_global_social_status_artists_artist_id_connect_global_social_status_get: %s\n" % e)
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

# **connect_soundcloud_artists_artist_id_connect_soundcloud_post**
> object connect_soundcloud_artists_artist_id_connect_soundcloud_post(artist_id)

Connect Soundcloud

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
    api_instance = xr7_sdk.ConnectApi(api_client)
    artist_id = 'artist_id_example' # str | 

    try:
        # Connect Soundcloud
        api_response = api_instance.connect_soundcloud_artists_artist_id_connect_soundcloud_post(artist_id)
        print("The response of ConnectApi->connect_soundcloud_artists_artist_id_connect_soundcloud_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ConnectApi->connect_soundcloud_artists_artist_id_connect_soundcloud_post: %s\n" % e)
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

# **connect_soundcloud_status_artists_artist_id_connect_soundcloud_status_get**
> object connect_soundcloud_status_artists_artist_id_connect_soundcloud_status_get(artist_id)

Connect Soundcloud Status

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
    api_instance = xr7_sdk.ConnectApi(api_client)
    artist_id = 'artist_id_example' # str | 

    try:
        # Connect Soundcloud Status
        api_response = api_instance.connect_soundcloud_status_artists_artist_id_connect_soundcloud_status_get(artist_id)
        print("The response of ConnectApi->connect_soundcloud_status_artists_artist_id_connect_soundcloud_status_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ConnectApi->connect_soundcloud_status_artists_artist_id_connect_soundcloud_status_get: %s\n" % e)
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

