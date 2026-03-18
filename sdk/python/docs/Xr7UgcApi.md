# xr7_sdk.Xr7UgcApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**ingest_signals_artists_artist_id_xr7_ugc_signals_ingest_post**](Xr7UgcApi.md#ingest_signals_artists_artist_id_xr7_ugc_signals_ingest_post) | **POST** /artists/{artist_id}/xr7/ugc/signals/ingest | Ingest Signals
[**ugc_opportunities_artists_artist_id_xr7_ugc_opportunities_get**](Xr7UgcApi.md#ugc_opportunities_artists_artist_id_xr7_ugc_opportunities_get) | **GET** /artists/{artist_id}/xr7/ugc/opportunities | Ugc Opportunities


# **ingest_signals_artists_artist_id_xr7_ugc_signals_ingest_post**
> object ingest_signals_artists_artist_id_xr7_ugc_signals_ingest_post(artist_id, ugc_signal_ingest_request)

Ingest Signals

### Example


```python
import xr7_sdk
from xr7_sdk.models.ugc_signal_ingest_request import UGCSignalIngestRequest
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
    api_instance = xr7_sdk.Xr7UgcApi(api_client)
    artist_id = 'artist_id_example' # str | 
    ugc_signal_ingest_request = xr7_sdk.UGCSignalIngestRequest() # UGCSignalIngestRequest | 

    try:
        # Ingest Signals
        api_response = api_instance.ingest_signals_artists_artist_id_xr7_ugc_signals_ingest_post(artist_id, ugc_signal_ingest_request)
        print("The response of Xr7UgcApi->ingest_signals_artists_artist_id_xr7_ugc_signals_ingest_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling Xr7UgcApi->ingest_signals_artists_artist_id_xr7_ugc_signals_ingest_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **artist_id** | **str**|  | 
 **ugc_signal_ingest_request** | [**UGCSignalIngestRequest**](UGCSignalIngestRequest.md)|  | 

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

# **ugc_opportunities_artists_artist_id_xr7_ugc_opportunities_get**
> object ugc_opportunities_artists_artist_id_xr7_ugc_opportunities_get(artist_id, tenant_id=tenant_id, min_confidence=min_confidence, min_estimated_value=min_estimated_value, status=status)

Ugc Opportunities

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
    api_instance = xr7_sdk.Xr7UgcApi(api_client)
    artist_id = 'artist_id_example' # str | 
    tenant_id = 'default' # str |  (optional) (default to 'default')
    min_confidence = 0.65 # float |  (optional) (default to 0.65)
    min_estimated_value = 0.0 # float |  (optional) (default to 0.0)
    status = 'status_example' # str |  (optional)

    try:
        # Ugc Opportunities
        api_response = api_instance.ugc_opportunities_artists_artist_id_xr7_ugc_opportunities_get(artist_id, tenant_id=tenant_id, min_confidence=min_confidence, min_estimated_value=min_estimated_value, status=status)
        print("The response of Xr7UgcApi->ugc_opportunities_artists_artist_id_xr7_ugc_opportunities_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling Xr7UgcApi->ugc_opportunities_artists_artist_id_xr7_ugc_opportunities_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **artist_id** | **str**|  | 
 **tenant_id** | **str**|  | [optional] [default to &#39;default&#39;]
 **min_confidence** | **float**|  | [optional] [default to 0.65]
 **min_estimated_value** | **float**|  | [optional] [default to 0.0]
 **status** | **str**|  | [optional] 

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

