# xr7_sdk.ClassActionApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**list_class_action_signals_admin_class_action_signals_get**](ClassActionApi.md#list_class_action_signals_admin_class_action_signals_get) | **GET** /admin/class-action/signals | List Class Action Signals
[**run_class_action_aggregation_admin_class_action_aggregate_post**](ClassActionApi.md#run_class_action_aggregation_admin_class_action_aggregate_post) | **POST** /admin/class-action/aggregate | Run Class Action Aggregation


# **list_class_action_signals_admin_class_action_signals_get**
> Dict[str, object] list_class_action_signals_admin_class_action_signals_get()

List Class Action Signals

Return all active class-action evidence signals.

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
    api_instance = xr7_sdk.ClassActionApi(api_client)

    try:
        # List Class Action Signals
        api_response = api_instance.list_class_action_signals_admin_class_action_signals_get()
        print("The response of ClassActionApi->list_class_action_signals_admin_class_action_signals_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ClassActionApi->list_class_action_signals_admin_class_action_signals_get: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

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

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **run_class_action_aggregation_admin_class_action_aggregate_post**
> Dict[str, object] run_class_action_aggregation_admin_class_action_aggregate_post()

Run Class Action Aggregation

Re-run the class-action signal aggregator across all open anomalies.

Requires admin role. Returns created/updated signal records.

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
    api_instance = xr7_sdk.ClassActionApi(api_client)

    try:
        # Run Class Action Aggregation
        api_response = api_instance.run_class_action_aggregation_admin_class_action_aggregate_post()
        print("The response of ClassActionApi->run_class_action_aggregation_admin_class_action_aggregate_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ClassActionApi->run_class_action_aggregation_admin_class_action_aggregate_post: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

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

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)
