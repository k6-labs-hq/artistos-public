# xr7_sdk.EarningsApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**forecast_earnings_artists_artist_id_ml_forecast_post**](EarningsApi.md#forecast_earnings_artists_artist_id_ml_forecast_post) | **POST** /artists/{artist_id}/ml/forecast | Forecast Earnings
[**get_earnings_history_artists_artist_id_earnings_history_get**](EarningsApi.md#get_earnings_history_artists_artist_id_earnings_history_get) | **GET** /artists/{artist_id}/earnings/history | Get Earnings History
[**get_earnings_summary_artists_artist_id_earnings_get**](EarningsApi.md#get_earnings_summary_artists_artist_id_earnings_get) | **GET** /artists/{artist_id}/earnings | Get Earnings Summary
[**get_post_repair_forecast_artists_artist_id_earnings_forecast_get**](EarningsApi.md#get_post_repair_forecast_artists_artist_id_earnings_forecast_get) | **GET** /artists/{artist_id}/earnings/forecast | Get Post Repair Forecast
[**reconstruct_earnings_artists_artist_id_earnings_reconstruct_post**](EarningsApi.md#reconstruct_earnings_artists_artist_id_earnings_reconstruct_post) | **POST** /artists/{artist_id}/earnings/reconstruct | Reconstruct Earnings


# **forecast_earnings_artists_artist_id_ml_forecast_post**
> object forecast_earnings_artists_artist_id_ml_forecast_post(artist_id, xr7_api_routers_earnings_forecast_request)

Forecast Earnings

Use a linear-regression trend model to forecast the artist's earnings for
the next *horizon_days* days.

Set ``by_category=true`` to receive a per-event-type breakdown.

### Example


```python
import xr7_sdk
from xr7_sdk.models.xr7_api_routers_earnings_forecast_request import XR7ApiRoutersEarningsForecastRequest
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
    api_instance = xr7_sdk.EarningsApi(api_client)
    artist_id = 'artist_id_example' # str |
    xr7_api_routers_earnings_forecast_request = xr7_sdk.XR7ApiRoutersEarningsForecastRequest() # XR7ApiRoutersEarningsForecastRequest |

    try:
        # Forecast Earnings
        api_response = api_instance.forecast_earnings_artists_artist_id_ml_forecast_post(artist_id, xr7_api_routers_earnings_forecast_request)
        print("The response of EarningsApi->forecast_earnings_artists_artist_id_ml_forecast_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling EarningsApi->forecast_earnings_artists_artist_id_ml_forecast_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **artist_id** | **str**|  |
 **xr7_api_routers_earnings_forecast_request** | [**XR7ApiRoutersEarningsForecastRequest**](XR7ApiRoutersEarningsForecastRequest.md)|  |

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

# **get_earnings_history_artists_artist_id_earnings_history_get**
> object get_earnings_history_artists_artist_id_earnings_history_get(artist_id)

Get Earnings History

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
    api_instance = xr7_sdk.EarningsApi(api_client)
    artist_id = 'artist_id_example' # str |

    try:
        # Get Earnings History
        api_response = api_instance.get_earnings_history_artists_artist_id_earnings_history_get(artist_id)
        print("The response of EarningsApi->get_earnings_history_artists_artist_id_earnings_history_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling EarningsApi->get_earnings_history_artists_artist_id_earnings_history_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **artist_id** | **str**|  |

### Return type

**object**

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

# **get_earnings_summary_artists_artist_id_earnings_get**
> object get_earnings_summary_artists_artist_id_earnings_get(artist_id)

Get Earnings Summary

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
    api_instance = xr7_sdk.EarningsApi(api_client)
    artist_id = 'artist_id_example' # str |

    try:
        # Get Earnings Summary
        api_response = api_instance.get_earnings_summary_artists_artist_id_earnings_get(artist_id)
        print("The response of EarningsApi->get_earnings_summary_artists_artist_id_earnings_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling EarningsApi->get_earnings_summary_artists_artist_id_earnings_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **artist_id** | **str**|  |

### Return type

**object**

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

# **get_post_repair_forecast_artists_artist_id_earnings_forecast_get**
> object get_post_repair_forecast_artists_artist_id_earnings_forecast_get(artist_id)

Get Post Repair Forecast

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
    api_instance = xr7_sdk.EarningsApi(api_client)
    artist_id = 'artist_id_example' # str |

    try:
        # Get Post Repair Forecast
        api_response = api_instance.get_post_repair_forecast_artists_artist_id_earnings_forecast_get(artist_id)
        print("The response of EarningsApi->get_post_repair_forecast_artists_artist_id_earnings_forecast_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling EarningsApi->get_post_repair_forecast_artists_artist_id_earnings_forecast_get: %s\n" % e)
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

# **reconstruct_earnings_artists_artist_id_earnings_reconstruct_post**
> object reconstruct_earnings_artists_artist_id_earnings_reconstruct_post(artist_id, reconstruct_request)

Reconstruct Earnings

### Example


```python
import xr7_sdk
from xr7_sdk.models.reconstruct_request import ReconstructRequest
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
    api_instance = xr7_sdk.EarningsApi(api_client)
    artist_id = 'artist_id_example' # str |
    reconstruct_request = xr7_sdk.ReconstructRequest() # ReconstructRequest |

    try:
        # Reconstruct Earnings
        api_response = api_instance.reconstruct_earnings_artists_artist_id_earnings_reconstruct_post(artist_id, reconstruct_request)
        print("The response of EarningsApi->reconstruct_earnings_artists_artist_id_earnings_reconstruct_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling EarningsApi->reconstruct_earnings_artists_artist_id_earnings_reconstruct_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **artist_id** | **str**|  |
 **reconstruct_request** | [**ReconstructRequest**](ReconstructRequest.md)|  |

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
