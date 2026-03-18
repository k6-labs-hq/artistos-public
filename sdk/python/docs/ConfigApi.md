# xr7_sdk.ConfigApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_founder_status_config_founder_status_get**](ConfigApi.md#get_founder_status_config_founder_status_get) | **GET** /config/founder-status | Get Founder Status


# **get_founder_status_config_founder_status_get**
> object get_founder_status_config_founder_status_get()

Get Founder Status

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
    api_instance = xr7_sdk.ConfigApi(api_client)

    try:
        # Get Founder Status
        api_response = api_instance.get_founder_status_config_founder_status_get()
        print("The response of ConfigApi->get_founder_status_config_founder_status_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ConfigApi->get_founder_status_config_founder_status_get: %s\n" % e)
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

