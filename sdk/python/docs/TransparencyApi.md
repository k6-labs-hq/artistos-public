# xr7_sdk.TransparencyApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**explain_anomaly_artists_artist_id_anomalies_anomaly_id_explain_get**](TransparencyApi.md#explain_anomaly_artists_artist_id_anomalies_anomaly_id_explain_get) | **GET** /artists/{artist_id}/anomalies/{anomaly_id}/explain | Explain Anomaly
[**full_ledger_artists_artist_id_ledger_full_get**](TransparencyApi.md#full_ledger_artists_artist_id_ledger_full_get) | **GET** /artists/{artist_id}/ledger/full | Full Ledger


# **explain_anomaly_artists_artist_id_anomalies_anomaly_id_explain_get**
> object explain_anomaly_artists_artist_id_anomalies_anomaly_id_explain_get(artist_id, anomaly_id)

Explain Anomaly

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
    api_instance = xr7_sdk.TransparencyApi(api_client)
    artist_id = 'artist_id_example' # str |
    anomaly_id = 'anomaly_id_example' # str |

    try:
        # Explain Anomaly
        api_response = api_instance.explain_anomaly_artists_artist_id_anomalies_anomaly_id_explain_get(artist_id, anomaly_id)
        print("The response of TransparencyApi->explain_anomaly_artists_artist_id_anomalies_anomaly_id_explain_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TransparencyApi->explain_anomaly_artists_artist_id_anomalies_anomaly_id_explain_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **artist_id** | **str**|  |
 **anomaly_id** | **str**|  |

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

# **full_ledger_artists_artist_id_ledger_full_get**
> object full_ledger_artists_artist_id_ledger_full_get(artist_id, include_raw_statements=include_raw_statements)

Full Ledger

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
    api_instance = xr7_sdk.TransparencyApi(api_client)
    artist_id = 'artist_id_example' # str |
    include_raw_statements = True # bool |  (optional) (default to True)

    try:
        # Full Ledger
        api_response = api_instance.full_ledger_artists_artist_id_ledger_full_get(artist_id, include_raw_statements=include_raw_statements)
        print("The response of TransparencyApi->full_ledger_artists_artist_id_ledger_full_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TransparencyApi->full_ledger_artists_artist_id_ledger_full_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **artist_id** | **str**|  |
 **include_raw_statements** | **bool**|  | [optional] [default to True]

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
