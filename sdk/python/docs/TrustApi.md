# xr7_sdk.TrustApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_trust_trace_artists_artist_id_trust_trace_get**](TrustApi.md#get_trust_trace_artists_artist_id_trust_trace_get) | **GET** /artists/{artist_id}/trust/trace | Get Trust Trace


# **get_trust_trace_artists_artist_id_trust_trace_get**
> Dict[str, object] get_trust_trace_artists_artist_id_trust_trace_get(artist_id)

Get Trust Trace

Return the real-time pipeline trace feed for this artist.

Each entry contains stage, sub_stage, confidence (0-1), eta_seconds,
and a plain-English explanation of what XR7 is doing right now.

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
    api_instance = xr7_sdk.TrustApi(api_client)
    artist_id = 'artist_id_example' # str | 

    try:
        # Get Trust Trace
        api_response = api_instance.get_trust_trace_artists_artist_id_trust_trace_get(artist_id)
        print("The response of TrustApi->get_trust_trace_artists_artist_id_trust_trace_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TrustApi->get_trust_trace_artists_artist_id_trust_trace_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **artist_id** | **str**|  | 

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

