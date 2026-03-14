# xr7_sdk.AnomaliesApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**detect_anomalies_artists_artist_id_anomalies_detect_post**](AnomaliesApi.md#detect_anomalies_artists_artist_id_anomalies_detect_post) | **POST** /artists/{artist_id}/anomalies/detect | Detect Anomalies
[**get_anomaly_anomalies_anomaly_id_get**](AnomaliesApi.md#get_anomaly_anomalies_anomaly_id_get) | **GET** /anomalies/{anomaly_id} | Get Anomaly
[**list_anomalies_artists_artist_id_anomalies_get**](AnomaliesApi.md#list_anomalies_artists_artist_id_anomalies_get) | **GET** /artists/{artist_id}/anomalies | List Anomalies


# **detect_anomalies_artists_artist_id_anomalies_detect_post**
> object detect_anomalies_artists_artist_id_anomalies_detect_post(artist_id)

Detect Anomalies

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
    api_instance = xr7_sdk.AnomaliesApi(api_client)
    artist_id = 'artist_id_example' # str | 

    try:
        # Detect Anomalies
        api_response = api_instance.detect_anomalies_artists_artist_id_anomalies_detect_post(artist_id)
        print("The response of AnomaliesApi->detect_anomalies_artists_artist_id_anomalies_detect_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AnomaliesApi->detect_anomalies_artists_artist_id_anomalies_detect_post: %s\n" % e)
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

# **get_anomaly_anomalies_anomaly_id_get**
> AnomalySchema get_anomaly_anomalies_anomaly_id_get(anomaly_id)

Get Anomaly

### Example


```python
import xr7_sdk
from xr7_sdk.models.anomaly_schema import AnomalySchema
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
    api_instance = xr7_sdk.AnomaliesApi(api_client)
    anomaly_id = 'anomaly_id_example' # str | 

    try:
        # Get Anomaly
        api_response = api_instance.get_anomaly_anomalies_anomaly_id_get(anomaly_id)
        print("The response of AnomaliesApi->get_anomaly_anomalies_anomaly_id_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AnomaliesApi->get_anomaly_anomalies_anomaly_id_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **anomaly_id** | **str**|  | 

### Return type

[**AnomalySchema**](AnomalySchema.md)

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

# **list_anomalies_artists_artist_id_anomalies_get**
> object list_anomalies_artists_artist_id_anomalies_get(artist_id, status=status)

List Anomalies

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
    api_instance = xr7_sdk.AnomaliesApi(api_client)
    artist_id = 'artist_id_example' # str | 
    status = 'status_example' # str |  (optional)

    try:
        # List Anomalies
        api_response = api_instance.list_anomalies_artists_artist_id_anomalies_get(artist_id, status=status)
        print("The response of AnomaliesApi->list_anomalies_artists_artist_id_anomalies_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AnomaliesApi->list_anomalies_artists_artist_id_anomalies_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **artist_id** | **str**|  | 
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

