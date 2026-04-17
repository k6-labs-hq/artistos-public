# xr7_sdk.MlSuiteApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**ml_calibration_dashboard_artists_artist_id_ml_calibration_dashboard_get**](MlSuiteApi.md#ml_calibration_dashboard_artists_artist_id_ml_calibration_dashboard_get) | **GET** /artists/{artist_id}/ml/calibration-dashboard | Ml Calibration Dashboard
[**ml_explain_artists_artist_id_ml_explain_get**](MlSuiteApi.md#ml_explain_artists_artist_id_ml_explain_get) | **GET** /artists/{artist_id}/ml/explain | Ml Explain


# **ml_calibration_dashboard_artists_artist_id_ml_calibration_dashboard_get**
> Dict[str, object] ml_calibration_dashboard_artists_artist_id_ml_calibration_dashboard_get(artist_id)

Ml Calibration Dashboard

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
    api_instance = xr7_sdk.MlSuiteApi(api_client)
    artist_id = 'artist_id_example' # str |

    try:
        # Ml Calibration Dashboard
        api_response = api_instance.ml_calibration_dashboard_artists_artist_id_ml_calibration_dashboard_get(artist_id)
        print("The response of MlSuiteApi->ml_calibration_dashboard_artists_artist_id_ml_calibration_dashboard_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling MlSuiteApi->ml_calibration_dashboard_artists_artist_id_ml_calibration_dashboard_get: %s\n" % e)
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

# **ml_explain_artists_artist_id_ml_explain_get**
> Dict[str, object] ml_explain_artists_artist_id_ml_explain_get(artist_id)

Ml Explain

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
    api_instance = xr7_sdk.MlSuiteApi(api_client)
    artist_id = 'artist_id_example' # str |

    try:
        # Ml Explain
        api_response = api_instance.ml_explain_artists_artist_id_ml_explain_get(artist_id)
        print("The response of MlSuiteApi->ml_explain_artists_artist_id_ml_explain_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling MlSuiteApi->ml_explain_artists_artist_id_ml_explain_get: %s\n" % e)
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
