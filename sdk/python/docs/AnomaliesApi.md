# xr7_sdk.AnomaliesApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**anomaly_recovery_probability_endpoint_anomalies_anomaly_id_recovery_probability_get**](AnomaliesApi.md#anomaly_recovery_probability_endpoint_anomalies_anomaly_id_recovery_probability_get) | **GET** /anomalies/{anomaly_id}/recovery-probability | Anomaly Recovery Probability Endpoint
[**detect_anomalies_artists_artist_id_anomalies_detect_post**](AnomaliesApi.md#detect_anomalies_artists_artist_id_anomalies_detect_post) | **POST** /artists/{artist_id}/anomalies/detect | Detect Anomalies
[**fraud_scan_artists_artist_id_anomalies_fraud_scan_post**](AnomaliesApi.md#fraud_scan_artists_artist_id_anomalies_fraud_scan_post) | **POST** /artists/{artist_id}/anomalies/fraud-scan | Fraud Scan
[**get_anomaly_anomalies_anomaly_id_get**](AnomaliesApi.md#get_anomaly_anomalies_anomaly_id_get) | **GET** /anomalies/{anomaly_id} | Get Anomaly
[**list_anomalies_artists_artist_id_anomalies_get**](AnomaliesApi.md#list_anomalies_artists_artist_id_anomalies_get) | **GET** /artists/{artist_id}/anomalies | List Anomalies
[**scan_ai_influence_artists_artist_id_ai_music_scan_influence_post**](AnomaliesApi.md#scan_ai_influence_artists_artist_id_ai_music_scan_influence_post) | **POST** /artists/{artist_id}/ai-music/scan-influence | Scan Ai Influence


# **anomaly_recovery_probability_endpoint_anomalies_anomaly_id_recovery_probability_get**
> object anomaly_recovery_probability_endpoint_anomalies_anomaly_id_recovery_probability_get(anomaly_id)

Anomaly Recovery Probability Endpoint

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
    anomaly_id = 'anomaly_id_example' # str | 

    try:
        # Anomaly Recovery Probability Endpoint
        api_response = api_instance.anomaly_recovery_probability_endpoint_anomalies_anomaly_id_recovery_probability_get(anomaly_id)
        print("The response of AnomaliesApi->anomaly_recovery_probability_endpoint_anomalies_anomaly_id_recovery_probability_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AnomaliesApi->anomaly_recovery_probability_endpoint_anomalies_anomaly_id_recovery_probability_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
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

# **fraud_scan_artists_artist_id_anomalies_fraud_scan_post**
> object fraud_scan_artists_artist_id_anomalies_fraud_scan_post(artist_id)

Fraud Scan

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
        # Fraud Scan
        api_response = api_instance.fraud_scan_artists_artist_id_anomalies_fraud_scan_post(artist_id)
        print("The response of AnomaliesApi->fraud_scan_artists_artist_id_anomalies_fraud_scan_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AnomaliesApi->fraud_scan_artists_artist_id_anomalies_fraud_scan_post: %s\n" % e)
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
> object list_anomalies_artists_artist_id_anomalies_get(artist_id, status=status, debug=debug)

List Anomalies

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
    api_instance = xr7_sdk.AnomaliesApi(api_client)
    artist_id = 'artist_id_example' # str | 
    status = 'status_example' # str |  (optional)
    debug = False # bool |  (optional) (default to False)

    try:
        # List Anomalies
        api_response = api_instance.list_anomalies_artists_artist_id_anomalies_get(artist_id, status=status, debug=debug)
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
 **debug** | **bool**|  | [optional] [default to False]

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

# **scan_ai_influence_artists_artist_id_ai_music_scan_influence_post**
> object scan_ai_influence_artists_artist_id_ai_music_scan_influence_post(artist_id)

Scan Ai Influence

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
        # Scan Ai Influence
        api_response = api_instance.scan_ai_influence_artists_artist_id_ai_music_scan_influence_post(artist_id)
        print("The response of AnomaliesApi->scan_ai_influence_artists_artist_id_ai_music_scan_influence_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AnomaliesApi->scan_ai_influence_artists_artist_id_ai_music_scan_influence_post: %s\n" % e)
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

