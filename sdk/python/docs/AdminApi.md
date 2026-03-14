# xr7_sdk.AdminApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**admin_overview_admin_overview_get**](AdminApi.md#admin_overview_admin_overview_get) | **GET** /admin/overview | Admin Overview
[**list_anomalies_admin_anomalies_get**](AdminApi.md#list_anomalies_admin_anomalies_get) | **GET** /admin/anomalies | List Anomalies
[**list_artists_admin_artists_get**](AdminApi.md#list_artists_admin_artists_get) | **GET** /admin/artists | List Artists
[**list_audit_logs_admin_audit_logs_get**](AdminApi.md#list_audit_logs_admin_audit_logs_get) | **GET** /admin/audit-logs | List Audit Logs
[**list_claims_admin_claims_get**](AdminApi.md#list_claims_admin_claims_get) | **GET** /admin/claims | List Claims
[**list_review_queue_admin_review_queue_get**](AdminApi.md#list_review_queue_admin_review_queue_get) | **GET** /admin/review-queue | List Review Queue
[**list_transactions_admin_transactions_get**](AdminApi.md#list_transactions_admin_transactions_get) | **GET** /admin/transactions | List Transactions


# **admin_overview_admin_overview_get**
> object admin_overview_admin_overview_get(x_admin_key=x_admin_key, x_admin_actor=x_admin_actor)

Admin Overview

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
    api_instance = xr7_sdk.AdminApi(api_client)
    x_admin_key = '' # str |  (optional) (default to '')
    x_admin_actor = 'x_admin_actor_example' # str |  (optional)

    try:
        # Admin Overview
        api_response = api_instance.admin_overview_admin_overview_get(x_admin_key=x_admin_key, x_admin_actor=x_admin_actor)
        print("The response of AdminApi->admin_overview_admin_overview_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AdminApi->admin_overview_admin_overview_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **x_admin_key** | **str**|  | [optional] [default to &#39;&#39;]
 **x_admin_actor** | **str**|  | [optional] 

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

# **list_anomalies_admin_anomalies_get**
> object list_anomalies_admin_anomalies_get(status=status, severity=severity, artist_id=artist_id, limit=limit, offset=offset, x_admin_key=x_admin_key, x_admin_actor=x_admin_actor)

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
    api_instance = xr7_sdk.AdminApi(api_client)
    status = 'status_example' # str |  (optional)
    severity = 'severity_example' # str |  (optional)
    artist_id = 'artist_id_example' # str |  (optional)
    limit = 50 # int |  (optional) (default to 50)
    offset = 0 # int |  (optional) (default to 0)
    x_admin_key = '' # str |  (optional) (default to '')
    x_admin_actor = 'x_admin_actor_example' # str |  (optional)

    try:
        # List Anomalies
        api_response = api_instance.list_anomalies_admin_anomalies_get(status=status, severity=severity, artist_id=artist_id, limit=limit, offset=offset, x_admin_key=x_admin_key, x_admin_actor=x_admin_actor)
        print("The response of AdminApi->list_anomalies_admin_anomalies_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AdminApi->list_anomalies_admin_anomalies_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **status** | **str**|  | [optional] 
 **severity** | **str**|  | [optional] 
 **artist_id** | **str**|  | [optional] 
 **limit** | **int**|  | [optional] [default to 50]
 **offset** | **int**|  | [optional] [default to 0]
 **x_admin_key** | **str**|  | [optional] [default to &#39;&#39;]
 **x_admin_actor** | **str**|  | [optional] 

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

# **list_artists_admin_artists_get**
> object list_artists_admin_artists_get(status=status, q=q, sort=sort, limit=limit, offset=offset, x_admin_key=x_admin_key, x_admin_actor=x_admin_actor)

List Artists

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
    api_instance = xr7_sdk.AdminApi(api_client)
    status = 'status_example' # str |  (optional)
    q = 'q_example' # str |  (optional)
    sort = 'created_at_desc' # str |  (optional) (default to 'created_at_desc')
    limit = 50 # int |  (optional) (default to 50)
    offset = 0 # int |  (optional) (default to 0)
    x_admin_key = '' # str |  (optional) (default to '')
    x_admin_actor = 'x_admin_actor_example' # str |  (optional)

    try:
        # List Artists
        api_response = api_instance.list_artists_admin_artists_get(status=status, q=q, sort=sort, limit=limit, offset=offset, x_admin_key=x_admin_key, x_admin_actor=x_admin_actor)
        print("The response of AdminApi->list_artists_admin_artists_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AdminApi->list_artists_admin_artists_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **status** | **str**|  | [optional] 
 **q** | **str**|  | [optional] 
 **sort** | **str**|  | [optional] [default to &#39;created_at_desc&#39;]
 **limit** | **int**|  | [optional] [default to 50]
 **offset** | **int**|  | [optional] [default to 0]
 **x_admin_key** | **str**|  | [optional] [default to &#39;&#39;]
 **x_admin_actor** | **str**|  | [optional] 

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

# **list_audit_logs_admin_audit_logs_get**
> List[AdminAuditLogSchema] list_audit_logs_admin_audit_logs_get(actor_filter=actor_filter, action=action, limit=limit, offset=offset, x_admin_key=x_admin_key, x_admin_actor=x_admin_actor)

List Audit Logs

### Example


```python
import xr7_sdk
from xr7_sdk.models.admin_audit_log_schema import AdminAuditLogSchema
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
    api_instance = xr7_sdk.AdminApi(api_client)
    actor_filter = 'actor_filter_example' # str |  (optional)
    action = 'action_example' # str |  (optional)
    limit = 100 # int |  (optional) (default to 100)
    offset = 0 # int |  (optional) (default to 0)
    x_admin_key = '' # str |  (optional) (default to '')
    x_admin_actor = 'x_admin_actor_example' # str |  (optional)

    try:
        # List Audit Logs
        api_response = api_instance.list_audit_logs_admin_audit_logs_get(actor_filter=actor_filter, action=action, limit=limit, offset=offset, x_admin_key=x_admin_key, x_admin_actor=x_admin_actor)
        print("The response of AdminApi->list_audit_logs_admin_audit_logs_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AdminApi->list_audit_logs_admin_audit_logs_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **actor_filter** | **str**|  | [optional] 
 **action** | **str**|  | [optional] 
 **limit** | **int**|  | [optional] [default to 100]
 **offset** | **int**|  | [optional] [default to 0]
 **x_admin_key** | **str**|  | [optional] [default to &#39;&#39;]
 **x_admin_actor** | **str**|  | [optional] 

### Return type

[**List[AdminAuditLogSchema]**](AdminAuditLogSchema.md)

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

# **list_claims_admin_claims_get**
> object list_claims_admin_claims_get(status=status, artist_id=artist_id, sort=sort, limit=limit, offset=offset, x_admin_key=x_admin_key, x_admin_actor=x_admin_actor)

List Claims

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
    api_instance = xr7_sdk.AdminApi(api_client)
    status = 'status_example' # str |  (optional)
    artist_id = 'artist_id_example' # str |  (optional)
    sort = 'updated_at_desc' # str |  (optional) (default to 'updated_at_desc')
    limit = 50 # int |  (optional) (default to 50)
    offset = 0 # int |  (optional) (default to 0)
    x_admin_key = '' # str |  (optional) (default to '')
    x_admin_actor = 'x_admin_actor_example' # str |  (optional)

    try:
        # List Claims
        api_response = api_instance.list_claims_admin_claims_get(status=status, artist_id=artist_id, sort=sort, limit=limit, offset=offset, x_admin_key=x_admin_key, x_admin_actor=x_admin_actor)
        print("The response of AdminApi->list_claims_admin_claims_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AdminApi->list_claims_admin_claims_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **status** | **str**|  | [optional] 
 **artist_id** | **str**|  | [optional] 
 **sort** | **str**|  | [optional] [default to &#39;updated_at_desc&#39;]
 **limit** | **int**|  | [optional] [default to 50]
 **offset** | **int**|  | [optional] [default to 0]
 **x_admin_key** | **str**|  | [optional] [default to &#39;&#39;]
 **x_admin_actor** | **str**|  | [optional] 

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

# **list_review_queue_admin_review_queue_get**
> object list_review_queue_admin_review_queue_get(status=status, artist_id=artist_id, source_type=source_type, limit=limit, offset=offset, x_admin_key=x_admin_key, x_admin_actor=x_admin_actor)

List Review Queue

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
    api_instance = xr7_sdk.AdminApi(api_client)
    status = 'status_example' # str |  (optional)
    artist_id = 'artist_id_example' # str |  (optional)
    source_type = 'source_type_example' # str |  (optional)
    limit = 50 # int |  (optional) (default to 50)
    offset = 0 # int |  (optional) (default to 0)
    x_admin_key = '' # str |  (optional) (default to '')
    x_admin_actor = 'x_admin_actor_example' # str |  (optional)

    try:
        # List Review Queue
        api_response = api_instance.list_review_queue_admin_review_queue_get(status=status, artist_id=artist_id, source_type=source_type, limit=limit, offset=offset, x_admin_key=x_admin_key, x_admin_actor=x_admin_actor)
        print("The response of AdminApi->list_review_queue_admin_review_queue_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AdminApi->list_review_queue_admin_review_queue_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **status** | **str**|  | [optional] 
 **artist_id** | **str**|  | [optional] 
 **source_type** | **str**|  | [optional] 
 **limit** | **int**|  | [optional] [default to 50]
 **offset** | **int**|  | [optional] [default to 0]
 **x_admin_key** | **str**|  | [optional] [default to &#39;&#39;]
 **x_admin_actor** | **str**|  | [optional] 

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

# **list_transactions_admin_transactions_get**
> object list_transactions_admin_transactions_get(status=status, tx_type=tx_type, artist_id=artist_id, limit=limit, offset=offset, x_admin_key=x_admin_key, x_admin_actor=x_admin_actor)

List Transactions

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
    api_instance = xr7_sdk.AdminApi(api_client)
    status = 'status_example' # str |  (optional)
    tx_type = 'tx_type_example' # str |  (optional)
    artist_id = 'artist_id_example' # str |  (optional)
    limit = 50 # int |  (optional) (default to 50)
    offset = 0 # int |  (optional) (default to 0)
    x_admin_key = '' # str |  (optional) (default to '')
    x_admin_actor = 'x_admin_actor_example' # str |  (optional)

    try:
        # List Transactions
        api_response = api_instance.list_transactions_admin_transactions_get(status=status, tx_type=tx_type, artist_id=artist_id, limit=limit, offset=offset, x_admin_key=x_admin_key, x_admin_actor=x_admin_actor)
        print("The response of AdminApi->list_transactions_admin_transactions_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AdminApi->list_transactions_admin_transactions_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **status** | **str**|  | [optional] 
 **tx_type** | **str**|  | [optional] 
 **artist_id** | **str**|  | [optional] 
 **limit** | **int**|  | [optional] [default to 50]
 **offset** | **int**|  | [optional] [default to 0]
 **x_admin_key** | **str**|  | [optional] [default to &#39;&#39;]
 **x_admin_actor** | **str**|  | [optional] 

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

