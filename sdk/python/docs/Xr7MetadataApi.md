# xr7_sdk.Xr7MetadataApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**apply_repairs_artists_artist_id_xr7_metadata_repair_apply_post**](Xr7MetadataApi.md#apply_repairs_artists_artist_id_xr7_metadata_repair_apply_post) | **POST** /artists/{artist_id}/xr7/metadata/repair/apply | Apply Repairs
[**suggest_repairs_artists_artist_id_xr7_metadata_repair_suggest_post**](Xr7MetadataApi.md#suggest_repairs_artists_artist_id_xr7_metadata_repair_suggest_post) | **POST** /artists/{artist_id}/xr7/metadata/repair/suggest | Suggest Repairs


# **apply_repairs_artists_artist_id_xr7_metadata_repair_apply_post**
> object apply_repairs_artists_artist_id_xr7_metadata_repair_apply_post(artist_id, metadata_repair_apply_request)

Apply Repairs

### Example


```python
import xr7_sdk
from xr7_sdk.models.metadata_repair_apply_request import MetadataRepairApplyRequest
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
    api_instance = xr7_sdk.Xr7MetadataApi(api_client)
    artist_id = 'artist_id_example' # str |
    metadata_repair_apply_request = xr7_sdk.MetadataRepairApplyRequest() # MetadataRepairApplyRequest |

    try:
        # Apply Repairs
        api_response = api_instance.apply_repairs_artists_artist_id_xr7_metadata_repair_apply_post(artist_id, metadata_repair_apply_request)
        print("The response of Xr7MetadataApi->apply_repairs_artists_artist_id_xr7_metadata_repair_apply_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling Xr7MetadataApi->apply_repairs_artists_artist_id_xr7_metadata_repair_apply_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **artist_id** | **str**|  |
 **metadata_repair_apply_request** | [**MetadataRepairApplyRequest**](MetadataRepairApplyRequest.md)|  |

### Return type

**object**

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

# **suggest_repairs_artists_artist_id_xr7_metadata_repair_suggest_post**
> object suggest_repairs_artists_artist_id_xr7_metadata_repair_suggest_post(artist_id, metadata_repair_suggest_request)

Suggest Repairs

### Example


```python
import xr7_sdk
from xr7_sdk.models.metadata_repair_suggest_request import MetadataRepairSuggestRequest
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
    api_instance = xr7_sdk.Xr7MetadataApi(api_client)
    artist_id = 'artist_id_example' # str |
    metadata_repair_suggest_request = xr7_sdk.MetadataRepairSuggestRequest() # MetadataRepairSuggestRequest |

    try:
        # Suggest Repairs
        api_response = api_instance.suggest_repairs_artists_artist_id_xr7_metadata_repair_suggest_post(artist_id, metadata_repair_suggest_request)
        print("The response of Xr7MetadataApi->suggest_repairs_artists_artist_id_xr7_metadata_repair_suggest_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling Xr7MetadataApi->suggest_repairs_artists_artist_id_xr7_metadata_repair_suggest_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **artist_id** | **str**|  |
 **metadata_repair_suggest_request** | [**MetadataRepairSuggestRequest**](MetadataRepairSuggestRequest.md)|  |

### Return type

**object**

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
