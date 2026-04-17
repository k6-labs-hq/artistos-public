# xr7_sdk.Xr7ForensicsApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_gap_report_artists_artist_id_xr7_reconciliation_gaps_get**](Xr7ForensicsApi.md#get_gap_report_artists_artist_id_xr7_reconciliation_gaps_get) | **GET** /artists/{artist_id}/xr7/reconciliation/gaps | Get Gap Report
[**queue_api_ingestion_artists_artist_id_xr7_queue_api_ingestion_post**](Xr7ForensicsApi.md#queue_api_ingestion_artists_artist_id_xr7_queue_api_ingestion_post) | **POST** /artists/{artist_id}/xr7/queue/api-ingestion | Queue Api Ingestion
[**queue_black_box_artists_artist_id_xr7_queue_black_box_detection_post**](Xr7ForensicsApi.md#queue_black_box_artists_artist_id_xr7_queue_black_box_detection_post) | **POST** /artists/{artist_id}/xr7/queue/black-box-detection | Queue Black Box
[**queue_file_ingestion_artists_artist_id_xr7_queue_file_ingestion_post**](Xr7ForensicsApi.md#queue_file_ingestion_artists_artist_id_xr7_queue_file_ingestion_post) | **POST** /artists/{artist_id}/xr7/queue/file-ingestion | Queue File Ingestion
[**queue_fingerprinting_artists_artist_id_xr7_queue_fingerprinting_post**](Xr7ForensicsApi.md#queue_fingerprinting_artists_artist_id_xr7_queue_fingerprinting_post) | **POST** /artists/{artist_id}/xr7/queue/fingerprinting | Queue Fingerprinting
[**queue_reconciliation_artists_artist_id_xr7_queue_reconciliation_post**](Xr7ForensicsApi.md#queue_reconciliation_artists_artist_id_xr7_queue_reconciliation_post) | **POST** /artists/{artist_id}/xr7/queue/reconciliation | Queue Reconciliation
[**run_api_ingestion_artists_artist_id_xr7_pipelines_api_ingestion_post**](Xr7ForensicsApi.md#run_api_ingestion_artists_artist_id_xr7_pipelines_api_ingestion_post) | **POST** /artists/{artist_id}/xr7/pipelines/api-ingestion | Run Api Ingestion
[**run_black_box_artists_artist_id_xr7_pipelines_black_box_detection_post**](Xr7ForensicsApi.md#run_black_box_artists_artist_id_xr7_pipelines_black_box_detection_post) | **POST** /artists/{artist_id}/xr7/pipelines/black-box-detection | Run Black Box
[**run_file_ingestion_artists_artist_id_xr7_pipelines_file_ingestion_post**](Xr7ForensicsApi.md#run_file_ingestion_artists_artist_id_xr7_pipelines_file_ingestion_post) | **POST** /artists/{artist_id}/xr7/pipelines/file-ingestion | Run File Ingestion
[**run_fingerprinting_artists_artist_id_xr7_pipelines_fingerprinting_post**](Xr7ForensicsApi.md#run_fingerprinting_artists_artist_id_xr7_pipelines_fingerprinting_post) | **POST** /artists/{artist_id}/xr7/pipelines/fingerprinting | Run Fingerprinting
[**run_reconciliation_artists_artist_id_xr7_pipelines_reconciliation_post**](Xr7ForensicsApi.md#run_reconciliation_artists_artist_id_xr7_pipelines_reconciliation_post) | **POST** /artists/{artist_id}/xr7/pipelines/reconciliation | Run Reconciliation
[**upsert_xr7_credentials_artists_artist_id_xr7_credentials_post**](Xr7ForensicsApi.md#upsert_xr7_credentials_artists_artist_id_xr7_credentials_post) | **POST** /artists/{artist_id}/xr7/credentials | Upsert Xr7 Credentials


# **get_gap_report_artists_artist_id_xr7_reconciliation_gaps_get**
> object get_gap_report_artists_artist_id_xr7_reconciliation_gaps_get(artist_id, tenant_id=tenant_id)

Get Gap Report

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
    api_instance = xr7_sdk.Xr7ForensicsApi(api_client)
    artist_id = 'artist_id_example' # str |
    tenant_id = 'default' # str |  (optional) (default to 'default')

    try:
        # Get Gap Report
        api_response = api_instance.get_gap_report_artists_artist_id_xr7_reconciliation_gaps_get(artist_id, tenant_id=tenant_id)
        print("The response of Xr7ForensicsApi->get_gap_report_artists_artist_id_xr7_reconciliation_gaps_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling Xr7ForensicsApi->get_gap_report_artists_artist_id_xr7_reconciliation_gaps_get: %s\n" % e)
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

# **queue_api_ingestion_artists_artist_id_xr7_queue_api_ingestion_post**
> object queue_api_ingestion_artists_artist_id_xr7_queue_api_ingestion_post(artist_id, api_ingestion_request)

Queue Api Ingestion

### Example


```python
import xr7_sdk
from xr7_sdk.models.api_ingestion_request import APIIngestionRequest
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
    api_instance = xr7_sdk.Xr7ForensicsApi(api_client)
    artist_id = 'artist_id_example' # str |
    api_ingestion_request = xr7_sdk.APIIngestionRequest() # APIIngestionRequest |

    try:
        # Queue Api Ingestion
        api_response = api_instance.queue_api_ingestion_artists_artist_id_xr7_queue_api_ingestion_post(artist_id, api_ingestion_request)
        print("The response of Xr7ForensicsApi->queue_api_ingestion_artists_artist_id_xr7_queue_api_ingestion_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling Xr7ForensicsApi->queue_api_ingestion_artists_artist_id_xr7_queue_api_ingestion_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **artist_id** | **str**|  |
 **api_ingestion_request** | [**APIIngestionRequest**](APIIngestionRequest.md)|  |

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

# **queue_black_box_artists_artist_id_xr7_queue_black_box_detection_post**
> object queue_black_box_artists_artist_id_xr7_queue_black_box_detection_post(artist_id, black_box_request)

Queue Black Box

### Example


```python
import xr7_sdk
from xr7_sdk.models.black_box_request import BlackBoxRequest
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
    api_instance = xr7_sdk.Xr7ForensicsApi(api_client)
    artist_id = 'artist_id_example' # str |
    black_box_request = xr7_sdk.BlackBoxRequest() # BlackBoxRequest |

    try:
        # Queue Black Box
        api_response = api_instance.queue_black_box_artists_artist_id_xr7_queue_black_box_detection_post(artist_id, black_box_request)
        print("The response of Xr7ForensicsApi->queue_black_box_artists_artist_id_xr7_queue_black_box_detection_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling Xr7ForensicsApi->queue_black_box_artists_artist_id_xr7_queue_black_box_detection_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **artist_id** | **str**|  |
 **black_box_request** | [**BlackBoxRequest**](BlackBoxRequest.md)|  |

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

# **queue_file_ingestion_artists_artist_id_xr7_queue_file_ingestion_post**
> object queue_file_ingestion_artists_artist_id_xr7_queue_file_ingestion_post(artist_id, source_system, file, tenant_id=tenant_id, queue_backend=queue_backend)

Queue File Ingestion

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
    api_instance = xr7_sdk.Xr7ForensicsApi(api_client)
    artist_id = 'artist_id_example' # str |
    source_system = 'source_system_example' # str |
    file = 'file_example' # str |
    tenant_id = 'default' # str |  (optional) (default to 'default')
    queue_backend = 'celery' # str |  (optional) (default to 'celery')

    try:
        # Queue File Ingestion
        api_response = api_instance.queue_file_ingestion_artists_artist_id_xr7_queue_file_ingestion_post(artist_id, source_system, file, tenant_id=tenant_id, queue_backend=queue_backend)
        print("The response of Xr7ForensicsApi->queue_file_ingestion_artists_artist_id_xr7_queue_file_ingestion_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling Xr7ForensicsApi->queue_file_ingestion_artists_artist_id_xr7_queue_file_ingestion_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **artist_id** | **str**|  |
 **source_system** | **str**|  |
 **file** | **str**|  |
 **tenant_id** | **str**|  | [optional] [default to &#39;default&#39;]
 **queue_backend** | **str**|  | [optional] [default to &#39;celery&#39;]

### Return type

**object**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: multipart/form-data
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **queue_fingerprinting_artists_artist_id_xr7_queue_fingerprinting_post**
> object queue_fingerprinting_artists_artist_id_xr7_queue_fingerprinting_post(artist_id, fingerprinting_request)

Queue Fingerprinting

### Example


```python
import xr7_sdk
from xr7_sdk.models.fingerprinting_request import FingerprintingRequest
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
    api_instance = xr7_sdk.Xr7ForensicsApi(api_client)
    artist_id = 'artist_id_example' # str |
    fingerprinting_request = xr7_sdk.FingerprintingRequest() # FingerprintingRequest |

    try:
        # Queue Fingerprinting
        api_response = api_instance.queue_fingerprinting_artists_artist_id_xr7_queue_fingerprinting_post(artist_id, fingerprinting_request)
        print("The response of Xr7ForensicsApi->queue_fingerprinting_artists_artist_id_xr7_queue_fingerprinting_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling Xr7ForensicsApi->queue_fingerprinting_artists_artist_id_xr7_queue_fingerprinting_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **artist_id** | **str**|  |
 **fingerprinting_request** | [**FingerprintingRequest**](FingerprintingRequest.md)|  |

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

# **queue_reconciliation_artists_artist_id_xr7_queue_reconciliation_post**
> object queue_reconciliation_artists_artist_id_xr7_queue_reconciliation_post(artist_id, reconciliation_request)

Queue Reconciliation

### Example


```python
import xr7_sdk
from xr7_sdk.models.reconciliation_request import ReconciliationRequest
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
    api_instance = xr7_sdk.Xr7ForensicsApi(api_client)
    artist_id = 'artist_id_example' # str |
    reconciliation_request = xr7_sdk.ReconciliationRequest() # ReconciliationRequest |

    try:
        # Queue Reconciliation
        api_response = api_instance.queue_reconciliation_artists_artist_id_xr7_queue_reconciliation_post(artist_id, reconciliation_request)
        print("The response of Xr7ForensicsApi->queue_reconciliation_artists_artist_id_xr7_queue_reconciliation_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling Xr7ForensicsApi->queue_reconciliation_artists_artist_id_xr7_queue_reconciliation_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **artist_id** | **str**|  |
 **reconciliation_request** | [**ReconciliationRequest**](ReconciliationRequest.md)|  |

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

# **run_api_ingestion_artists_artist_id_xr7_pipelines_api_ingestion_post**
> object run_api_ingestion_artists_artist_id_xr7_pipelines_api_ingestion_post(artist_id, api_ingestion_request)

Run Api Ingestion

### Example


```python
import xr7_sdk
from xr7_sdk.models.api_ingestion_request import APIIngestionRequest
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
    api_instance = xr7_sdk.Xr7ForensicsApi(api_client)
    artist_id = 'artist_id_example' # str |
    api_ingestion_request = xr7_sdk.APIIngestionRequest() # APIIngestionRequest |

    try:
        # Run Api Ingestion
        api_response = api_instance.run_api_ingestion_artists_artist_id_xr7_pipelines_api_ingestion_post(artist_id, api_ingestion_request)
        print("The response of Xr7ForensicsApi->run_api_ingestion_artists_artist_id_xr7_pipelines_api_ingestion_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling Xr7ForensicsApi->run_api_ingestion_artists_artist_id_xr7_pipelines_api_ingestion_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **artist_id** | **str**|  |
 **api_ingestion_request** | [**APIIngestionRequest**](APIIngestionRequest.md)|  |

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

# **run_black_box_artists_artist_id_xr7_pipelines_black_box_detection_post**
> object run_black_box_artists_artist_id_xr7_pipelines_black_box_detection_post(artist_id, black_box_request)

Run Black Box

### Example


```python
import xr7_sdk
from xr7_sdk.models.black_box_request import BlackBoxRequest
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
    api_instance = xr7_sdk.Xr7ForensicsApi(api_client)
    artist_id = 'artist_id_example' # str |
    black_box_request = xr7_sdk.BlackBoxRequest() # BlackBoxRequest |

    try:
        # Run Black Box
        api_response = api_instance.run_black_box_artists_artist_id_xr7_pipelines_black_box_detection_post(artist_id, black_box_request)
        print("The response of Xr7ForensicsApi->run_black_box_artists_artist_id_xr7_pipelines_black_box_detection_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling Xr7ForensicsApi->run_black_box_artists_artist_id_xr7_pipelines_black_box_detection_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **artist_id** | **str**|  |
 **black_box_request** | [**BlackBoxRequest**](BlackBoxRequest.md)|  |

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

# **run_file_ingestion_artists_artist_id_xr7_pipelines_file_ingestion_post**
> object run_file_ingestion_artists_artist_id_xr7_pipelines_file_ingestion_post(artist_id, source_system, file, tenant_id=tenant_id)

Run File Ingestion

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
    api_instance = xr7_sdk.Xr7ForensicsApi(api_client)
    artist_id = 'artist_id_example' # str |
    source_system = 'source_system_example' # str |
    file = 'file_example' # str |
    tenant_id = 'default' # str |  (optional) (default to 'default')

    try:
        # Run File Ingestion
        api_response = api_instance.run_file_ingestion_artists_artist_id_xr7_pipelines_file_ingestion_post(artist_id, source_system, file, tenant_id=tenant_id)
        print("The response of Xr7ForensicsApi->run_file_ingestion_artists_artist_id_xr7_pipelines_file_ingestion_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling Xr7ForensicsApi->run_file_ingestion_artists_artist_id_xr7_pipelines_file_ingestion_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **artist_id** | **str**|  |
 **source_system** | **str**|  |
 **file** | **str**|  |
 **tenant_id** | **str**|  | [optional] [default to &#39;default&#39;]

### Return type

**object**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: multipart/form-data
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **run_fingerprinting_artists_artist_id_xr7_pipelines_fingerprinting_post**
> object run_fingerprinting_artists_artist_id_xr7_pipelines_fingerprinting_post(artist_id, fingerprinting_request)

Run Fingerprinting

### Example


```python
import xr7_sdk
from xr7_sdk.models.fingerprinting_request import FingerprintingRequest
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
    api_instance = xr7_sdk.Xr7ForensicsApi(api_client)
    artist_id = 'artist_id_example' # str |
    fingerprinting_request = xr7_sdk.FingerprintingRequest() # FingerprintingRequest |

    try:
        # Run Fingerprinting
        api_response = api_instance.run_fingerprinting_artists_artist_id_xr7_pipelines_fingerprinting_post(artist_id, fingerprinting_request)
        print("The response of Xr7ForensicsApi->run_fingerprinting_artists_artist_id_xr7_pipelines_fingerprinting_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling Xr7ForensicsApi->run_fingerprinting_artists_artist_id_xr7_pipelines_fingerprinting_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **artist_id** | **str**|  |
 **fingerprinting_request** | [**FingerprintingRequest**](FingerprintingRequest.md)|  |

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

# **run_reconciliation_artists_artist_id_xr7_pipelines_reconciliation_post**
> object run_reconciliation_artists_artist_id_xr7_pipelines_reconciliation_post(artist_id, reconciliation_request)

Run Reconciliation

### Example


```python
import xr7_sdk
from xr7_sdk.models.reconciliation_request import ReconciliationRequest
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
    api_instance = xr7_sdk.Xr7ForensicsApi(api_client)
    artist_id = 'artist_id_example' # str |
    reconciliation_request = xr7_sdk.ReconciliationRequest() # ReconciliationRequest |

    try:
        # Run Reconciliation
        api_response = api_instance.run_reconciliation_artists_artist_id_xr7_pipelines_reconciliation_post(artist_id, reconciliation_request)
        print("The response of Xr7ForensicsApi->run_reconciliation_artists_artist_id_xr7_pipelines_reconciliation_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling Xr7ForensicsApi->run_reconciliation_artists_artist_id_xr7_pipelines_reconciliation_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **artist_id** | **str**|  |
 **reconciliation_request** | [**ReconciliationRequest**](ReconciliationRequest.md)|  |

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

# **upsert_xr7_credentials_artists_artist_id_xr7_credentials_post**
> object upsert_xr7_credentials_artists_artist_id_xr7_credentials_post(artist_id, xr7_connector_credential_upsert)

Upsert Xr7 Credentials

### Example


```python
import xr7_sdk
from xr7_sdk.models.xr7_connector_credential_upsert import XR7ConnectorCredentialUpsert
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
    api_instance = xr7_sdk.Xr7ForensicsApi(api_client)
    artist_id = 'artist_id_example' # str |
    xr7_connector_credential_upsert = xr7_sdk.XR7ConnectorCredentialUpsert() # XR7ConnectorCredentialUpsert |

    try:
        # Upsert Xr7 Credentials
        api_response = api_instance.upsert_xr7_credentials_artists_artist_id_xr7_credentials_post(artist_id, xr7_connector_credential_upsert)
        print("The response of Xr7ForensicsApi->upsert_xr7_credentials_artists_artist_id_xr7_credentials_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling Xr7ForensicsApi->upsert_xr7_credentials_artists_artist_id_xr7_credentials_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **artist_id** | **str**|  |
 **xr7_connector_credential_upsert** | [**XR7ConnectorCredentialUpsert**](XR7ConnectorCredentialUpsert.md)|  |

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
