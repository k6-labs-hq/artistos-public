# xr7_sdk.AdminApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**admin_overview_admin_overview_get**](AdminApi.md#admin_overview_admin_overview_get) | **GET** /admin/overview | Admin Overview
[**assign_founder_manually_admin_artists_artist_id_founder_assign_post**](AdminApi.md#assign_founder_manually_admin_artists_artist_id_founder_assign_post) | **POST** /admin/artists/{artist_id}/founder/assign | Assign Founder Manually
[**founder_cohort_report_admin_reports_founder_cohort_get**](AdminApi.md#founder_cohort_report_admin_reports_founder_cohort_get) | **GET** /admin/reports/founder-cohort | Founder Cohort Report
[**founder_roster_admin_founders_get**](AdminApi.md#founder_roster_admin_founders_get) | **GET** /admin/founders | Founder Roster
[**list_anomalies_admin_anomalies_get**](AdminApi.md#list_anomalies_admin_anomalies_get) | **GET** /admin/anomalies | List Anomalies
[**list_artists_admin_artists_get**](AdminApi.md#list_artists_admin_artists_get) | **GET** /admin/artists | List Artists
[**list_audit_logs_admin_audit_logs_get**](AdminApi.md#list_audit_logs_admin_audit_logs_get) | **GET** /admin/audit-logs | List Audit Logs
[**list_claims_admin_claims_get**](AdminApi.md#list_claims_admin_claims_get) | **GET** /admin/claims | List Claims
[**list_review_queue_admin_review_queue_get**](AdminApi.md#list_review_queue_admin_review_queue_get) | **GET** /admin/review-queue | List Review Queue
[**list_transactions_admin_transactions_get**](AdminApi.md#list_transactions_admin_transactions_get) | **GET** /admin/transactions | List Transactions
[**sol_risk_report_admin_reports_sol_risk_get**](AdminApi.md#sol_risk_report_admin_reports_sol_risk_get) | **GET** /admin/reports/sol-risk | Sol Risk Report
[**update_founder_cohort_limit_admin_founder_cohort_limit_put**](AdminApi.md#update_founder_cohort_limit_admin_founder_cohort_limit_put) | **PUT** /admin/founder/cohort-limit | Update Founder Cohort Limit


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

# **assign_founder_manually_admin_artists_artist_id_founder_assign_post**
> object assign_founder_manually_admin_artists_artist_id_founder_assign_post(artist_id, founder_assign_request, x_admin_key=x_admin_key, x_admin_actor=x_admin_actor)

Assign Founder Manually

### Example


```python
import xr7_sdk
from xr7_sdk.models.founder_assign_request import FounderAssignRequest
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
    artist_id = 'artist_id_example' # str |
    founder_assign_request = xr7_sdk.FounderAssignRequest() # FounderAssignRequest |
    x_admin_key = '' # str |  (optional) (default to '')
    x_admin_actor = 'x_admin_actor_example' # str |  (optional)

    try:
        # Assign Founder Manually
        api_response = api_instance.assign_founder_manually_admin_artists_artist_id_founder_assign_post(artist_id, founder_assign_request, x_admin_key=x_admin_key, x_admin_actor=x_admin_actor)
        print("The response of AdminApi->assign_founder_manually_admin_artists_artist_id_founder_assign_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AdminApi->assign_founder_manually_admin_artists_artist_id_founder_assign_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **artist_id** | **str**|  |
 **founder_assign_request** | [**FounderAssignRequest**](FounderAssignRequest.md)|  |
 **x_admin_key** | **str**|  | [optional] [default to &#39;&#39;]
 **x_admin_actor** | **str**|  | [optional]

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

# **founder_cohort_report_admin_reports_founder_cohort_get**
> object founder_cohort_report_admin_reports_founder_cohort_get(x_admin_key=x_admin_key, x_admin_actor=x_admin_actor)

Founder Cohort Report

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
        # Founder Cohort Report
        api_response = api_instance.founder_cohort_report_admin_reports_founder_cohort_get(x_admin_key=x_admin_key, x_admin_actor=x_admin_actor)
        print("The response of AdminApi->founder_cohort_report_admin_reports_founder_cohort_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AdminApi->founder_cohort_report_admin_reports_founder_cohort_get: %s\n" % e)
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

# **founder_roster_admin_founders_get**
> object founder_roster_admin_founders_get(limit=limit, offset=offset, x_admin_key=x_admin_key, x_admin_actor=x_admin_actor)

Founder Roster

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
    limit = 200 # int |  (optional) (default to 200)
    offset = 0 # int |  (optional) (default to 0)
    x_admin_key = '' # str |  (optional) (default to '')
    x_admin_actor = 'x_admin_actor_example' # str |  (optional)

    try:
        # Founder Roster
        api_response = api_instance.founder_roster_admin_founders_get(limit=limit, offset=offset, x_admin_key=x_admin_key, x_admin_actor=x_admin_actor)
        print("The response of AdminApi->founder_roster_admin_founders_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AdminApi->founder_roster_admin_founders_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **limit** | **int**|  | [optional] [default to 200]
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
> object list_claims_admin_claims_get(status=status, artist_id=artist_id, jurisdiction=jurisdiction, sort=sort, limit=limit, offset=offset, x_admin_key=x_admin_key, x_admin_actor=x_admin_actor)

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
    jurisdiction = 'jurisdiction_example' # str |  (optional)
    sort = 'updated_at_desc' # str |  (optional) (default to 'updated_at_desc')
    limit = 50 # int |  (optional) (default to 50)
    offset = 0 # int |  (optional) (default to 0)
    x_admin_key = '' # str |  (optional) (default to '')
    x_admin_actor = 'x_admin_actor_example' # str |  (optional)

    try:
        # List Claims
        api_response = api_instance.list_claims_admin_claims_get(status=status, artist_id=artist_id, jurisdiction=jurisdiction, sort=sort, limit=limit, offset=offset, x_admin_key=x_admin_key, x_admin_actor=x_admin_actor)
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
 **jurisdiction** | **str**|  | [optional]
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

# **sol_risk_report_admin_reports_sol_risk_get**
> object sol_risk_report_admin_reports_sol_risk_get(jurisdiction=jurisdiction, x_admin_key=x_admin_key, x_admin_actor=x_admin_actor)

Sol Risk Report

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
    jurisdiction = 'jurisdiction_example' # str |  (optional)
    x_admin_key = '' # str |  (optional) (default to '')
    x_admin_actor = 'x_admin_actor_example' # str |  (optional)

    try:
        # Sol Risk Report
        api_response = api_instance.sol_risk_report_admin_reports_sol_risk_get(jurisdiction=jurisdiction, x_admin_key=x_admin_key, x_admin_actor=x_admin_actor)
        print("The response of AdminApi->sol_risk_report_admin_reports_sol_risk_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AdminApi->sol_risk_report_admin_reports_sol_risk_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **jurisdiction** | **str**|  | [optional]
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

# **update_founder_cohort_limit_admin_founder_cohort_limit_put**
> object update_founder_cohort_limit_admin_founder_cohort_limit_put(founder_cohort_limit_update_request, x_admin_key=x_admin_key, x_admin_actor=x_admin_actor)

Update Founder Cohort Limit

### Example


```python
import xr7_sdk
from xr7_sdk.models.founder_cohort_limit_update_request import FounderCohortLimitUpdateRequest
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
    founder_cohort_limit_update_request = xr7_sdk.FounderCohortLimitUpdateRequest() # FounderCohortLimitUpdateRequest |
    x_admin_key = '' # str |  (optional) (default to '')
    x_admin_actor = 'x_admin_actor_example' # str |  (optional)

    try:
        # Update Founder Cohort Limit
        api_response = api_instance.update_founder_cohort_limit_admin_founder_cohort_limit_put(founder_cohort_limit_update_request, x_admin_key=x_admin_key, x_admin_actor=x_admin_actor)
        print("The response of AdminApi->update_founder_cohort_limit_admin_founder_cohort_limit_put:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AdminApi->update_founder_cohort_limit_admin_founder_cohort_limit_put: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **founder_cohort_limit_update_request** | [**FounderCohortLimitUpdateRequest**](FounderCohortLimitUpdateRequest.md)|  |
 **x_admin_key** | **str**|  | [optional] [default to &#39;&#39;]
 **x_admin_actor** | **str**|  | [optional]

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
