# xr7_sdk.Xr7ValuationApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**catalog_health_artists_artist_id_xr7_catalog_health_get**](Xr7ValuationApi.md#catalog_health_artists_artist_id_xr7_catalog_health_get) | **GET** /artists/{artist_id}/xr7/catalog/health | Catalog Health
[**recovery_forecast_artists_artist_id_xr7_forecast_recovery_post**](Xr7ValuationApi.md#recovery_forecast_artists_artist_id_xr7_forecast_recovery_post) | **POST** /artists/{artist_id}/xr7/forecast/recovery | Recovery Forecast
[**simulation_artists_artist_id_xr7_simulations_what_if_post**](Xr7ValuationApi.md#simulation_artists_artist_id_xr7_simulations_what_if_post) | **POST** /artists/{artist_id}/xr7/simulations/what-if | Simulation
[**valuation_snapshot_artists_artist_id_xr7_valuation_snapshot_get**](Xr7ValuationApi.md#valuation_snapshot_artists_artist_id_xr7_valuation_snapshot_get) | **GET** /artists/{artist_id}/xr7/valuation/snapshot | Valuation Snapshot


# **catalog_health_artists_artist_id_xr7_catalog_health_get**
> object catalog_health_artists_artist_id_xr7_catalog_health_get(artist_id, tenant_id=tenant_id)

Catalog Health

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
    api_instance = xr7_sdk.Xr7ValuationApi(api_client)
    artist_id = 'artist_id_example' # str |
    tenant_id = 'default' # str |  (optional) (default to 'default')

    try:
        # Catalog Health
        api_response = api_instance.catalog_health_artists_artist_id_xr7_catalog_health_get(artist_id, tenant_id=tenant_id)
        print("The response of Xr7ValuationApi->catalog_health_artists_artist_id_xr7_catalog_health_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling Xr7ValuationApi->catalog_health_artists_artist_id_xr7_catalog_health_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **artist_id** | **str**|  |
 **tenant_id** | **str**|  | [optional] [default to &#39;default&#39;]

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

# **recovery_forecast_artists_artist_id_xr7_forecast_recovery_post**
> object recovery_forecast_artists_artist_id_xr7_forecast_recovery_post(artist_id, xr7_api_routers_xr7_valuation_forecast_request)

Recovery Forecast

### Example


```python
import xr7_sdk
from xr7_sdk.models.xr7_api_routers_xr7_valuation_forecast_request import XR7ApiRoutersXr7ValuationForecastRequest
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
    api_instance = xr7_sdk.Xr7ValuationApi(api_client)
    artist_id = 'artist_id_example' # str |
    xr7_api_routers_xr7_valuation_forecast_request = xr7_sdk.XR7ApiRoutersXr7ValuationForecastRequest() # XR7ApiRoutersXr7ValuationForecastRequest |

    try:
        # Recovery Forecast
        api_response = api_instance.recovery_forecast_artists_artist_id_xr7_forecast_recovery_post(artist_id, xr7_api_routers_xr7_valuation_forecast_request)
        print("The response of Xr7ValuationApi->recovery_forecast_artists_artist_id_xr7_forecast_recovery_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling Xr7ValuationApi->recovery_forecast_artists_artist_id_xr7_forecast_recovery_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **artist_id** | **str**|  |
 **xr7_api_routers_xr7_valuation_forecast_request** | [**XR7ApiRoutersXr7ValuationForecastRequest**](XR7ApiRoutersXr7ValuationForecastRequest.md)|  |

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

# **simulation_artists_artist_id_xr7_simulations_what_if_post**
> object simulation_artists_artist_id_xr7_simulations_what_if_post(artist_id, simulation_request)

Simulation

### Example


```python
import xr7_sdk
from xr7_sdk.models.simulation_request import SimulationRequest
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
    api_instance = xr7_sdk.Xr7ValuationApi(api_client)
    artist_id = 'artist_id_example' # str |
    simulation_request = xr7_sdk.SimulationRequest() # SimulationRequest |

    try:
        # Simulation
        api_response = api_instance.simulation_artists_artist_id_xr7_simulations_what_if_post(artist_id, simulation_request)
        print("The response of Xr7ValuationApi->simulation_artists_artist_id_xr7_simulations_what_if_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling Xr7ValuationApi->simulation_artists_artist_id_xr7_simulations_what_if_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **artist_id** | **str**|  |
 **simulation_request** | [**SimulationRequest**](SimulationRequest.md)|  |

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

# **valuation_snapshot_artists_artist_id_xr7_valuation_snapshot_get**
> object valuation_snapshot_artists_artist_id_xr7_valuation_snapshot_get(artist_id, tenant_id=tenant_id, as_of=as_of)

Valuation Snapshot

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
    api_instance = xr7_sdk.Xr7ValuationApi(api_client)
    artist_id = 'artist_id_example' # str |
    tenant_id = 'default' # str |  (optional) (default to 'default')
    as_of = '2013-10-20' # date |  (optional)

    try:
        # Valuation Snapshot
        api_response = api_instance.valuation_snapshot_artists_artist_id_xr7_valuation_snapshot_get(artist_id, tenant_id=tenant_id, as_of=as_of)
        print("The response of Xr7ValuationApi->valuation_snapshot_artists_artist_id_xr7_valuation_snapshot_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling Xr7ValuationApi->valuation_snapshot_artists_artist_id_xr7_valuation_snapshot_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **artist_id** | **str**|  |
 **tenant_id** | **str**|  | [optional] [default to &#39;default&#39;]
 **as_of** | **date**|  | [optional]

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
