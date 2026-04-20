# xr7_sdk.FetchersApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**fetch_global_social_artists_artist_id_fetchers_global_social_post**](FetchersApi.md#fetch_global_social_artists_artist_id_fetchers_global_social_post) | **POST** /artists/{artist_id}/fetchers/global-social | Fetch Global Social


# **fetch_global_social_artists_artist_id_fetchers_global_social_post**
> object fetch_global_social_artists_artist_id_fetchers_global_social_post(artist_id)

Fetch Global Social

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
    api_instance = xr7_sdk.FetchersApi(api_client)
    artist_id = 'artist_id_example' # str |

    try:
        # Fetch Global Social
        api_response = api_instance.fetch_global_social_artists_artist_id_fetchers_global_social_post(artist_id)
        print("The response of FetchersApi->fetch_global_social_artists_artist_id_fetchers_global_social_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling FetchersApi->fetch_global_social_artists_artist_id_fetchers_global_social_post: %s\n" % e)
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
