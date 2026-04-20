# xr7_sdk.DefaultApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**health_health_get**](DefaultApi.md#health_health_get) | **GET** /health | Health
[**readiness_health_readiness_get**](DefaultApi.md#readiness_health_readiness_get) | **GET** /health/readiness | Readiness


# **health_health_get**
> object health_health_get()

Health

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
    api_instance = xr7_sdk.DefaultApi(api_client)

    try:
        # Health
        api_response = api_instance.health_health_get()
        print("The response of DefaultApi->health_health_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->health_health_get: %s\n" % e)
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

# **readiness_health_readiness_get**
> object readiness_health_readiness_get()

Readiness

Return the platform readiness status for every integration point.

Operators can call this endpoint to see exactly which connectors are
configured (credentials present) vs. which require additional setup.

``ready`` is ``True`` only when the core platform components are
functional.  Individual connector status reflects whether the required
environment variables are set — it does NOT make real network connections.

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
    api_instance = xr7_sdk.DefaultApi(api_client)

    try:
        # Readiness
        api_response = api_instance.readiness_health_readiness_get()
        print("The response of DefaultApi->readiness_health_readiness_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->readiness_health_readiness_get: %s\n" % e)
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
