# xr7_sdk.RecoveryApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**audit_eligibility_artists_artist_id_recovery_audit_eligibility_get**](RecoveryApi.md#audit_eligibility_artists_artist_id_recovery_audit_eligibility_get) | **GET** /artists/{artist_id}/recovery/audit-eligibility | Audit Eligibility
[**priority_queue_artists_artist_id_recovery_priority_queue_get**](RecoveryApi.md#priority_queue_artists_artist_id_recovery_priority_queue_get) | **GET** /artists/{artist_id}/recovery/priority-queue | Priority Queue
[**rate_benchmark_artists_artist_id_recovery_rate_benchmark_get**](RecoveryApi.md#rate_benchmark_artists_artist_id_recovery_rate_benchmark_get) | **GET** /artists/{artist_id}/recovery/rate-benchmark | Rate Benchmark
[**recoupment_artists_artist_id_recovery_recoupment_get**](RecoveryApi.md#recoupment_artists_artist_id_recovery_recoupment_get) | **GET** /artists/{artist_id}/recovery/recoupment | Recoupment
[**sol_status_artists_artist_id_recovery_sol_status_get**](RecoveryApi.md#sol_status_artists_artist_id_recovery_sol_status_get) | **GET** /artists/{artist_id}/recovery/sol-status | Sol Status


# **audit_eligibility_artists_artist_id_recovery_audit_eligibility_get**
> object audit_eligibility_artists_artist_id_recovery_audit_eligibility_get(artist_id)

Audit Eligibility

Return audit-rights eligibility for all contracts.

Contracts are ranked by estimated potential recovery and eligibility
status (NEVER_AUDITED, ELIGIBLE, ELIGIBLE_SOON, NOT_YET_ELIGIBLE).

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
    api_instance = xr7_sdk.RecoveryApi(api_client)
    artist_id = 'artist_id_example' # str | 

    try:
        # Audit Eligibility
        api_response = api_instance.audit_eligibility_artists_artist_id_recovery_audit_eligibility_get(artist_id)
        print("The response of RecoveryApi->audit_eligibility_artists_artist_id_recovery_audit_eligibility_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling RecoveryApi->audit_eligibility_artists_artist_id_recovery_audit_eligibility_get: %s\n" % e)
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

# **priority_queue_artists_artist_id_recovery_priority_queue_get**
> object priority_queue_artists_artist_id_recovery_priority_queue_get(artist_id)

Priority Queue

Return a unified, prioritised action queue for the artist.

Merges open anomalies and in-flight claims into a single ranked list,
scoring each item by (estimated_recoverable × confidence × urgency) / age.
The artist (or their representative) should work through this list
top-to-bottom to maximise recovery.

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
    api_instance = xr7_sdk.RecoveryApi(api_client)
    artist_id = 'artist_id_example' # str | 

    try:
        # Priority Queue
        api_response = api_instance.priority_queue_artists_artist_id_recovery_priority_queue_get(artist_id)
        print("The response of RecoveryApi->priority_queue_artists_artist_id_recovery_priority_queue_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling RecoveryApi->priority_queue_artists_artist_id_recovery_priority_queue_get: %s\n" % e)
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

# **rate_benchmark_artists_artist_id_recovery_rate_benchmark_get**
> object rate_benchmark_artists_artist_id_recovery_rate_benchmark_get(artist_id)

Rate Benchmark

Compare the artist's actual payment rates against industry benchmarks.

Returns a full report including per-event-type comparisons, estimated
underpayment amounts, and a tier classification
(ABOVE_MARKET, AT_MARKET, BELOW_MARKET, CRITICAL).

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
    api_instance = xr7_sdk.RecoveryApi(api_client)
    artist_id = 'artist_id_example' # str | 

    try:
        # Rate Benchmark
        api_response = api_instance.rate_benchmark_artists_artist_id_recovery_rate_benchmark_get(artist_id)
        print("The response of RecoveryApi->rate_benchmark_artists_artist_id_recovery_rate_benchmark_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling RecoveryApi->rate_benchmark_artists_artist_id_recovery_rate_benchmark_get: %s\n" % e)
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

# **recoupment_artists_artist_id_recovery_recoupment_get**
> object recoupment_artists_artist_id_recovery_recoupment_get(artist_id)

Recoupment

Return recoupment position and any discrepancy flags for all contracts
with advance/recoupment provisions.

Flags RECOUPMENT_DISCREPANCY when the calculated balance differs from
the counterparty-reported balance, and EXCESS_RECOUPMENT when more than
the advance has been recouped.

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
    api_instance = xr7_sdk.RecoveryApi(api_client)
    artist_id = 'artist_id_example' # str | 

    try:
        # Recoupment
        api_response = api_instance.recoupment_artists_artist_id_recovery_recoupment_get(artist_id)
        print("The response of RecoveryApi->recoupment_artists_artist_id_recovery_recoupment_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling RecoveryApi->recoupment_artists_artist_id_recovery_recoupment_get: %s\n" % e)
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

# **sol_status_artists_artist_id_recovery_sol_status_get**
> object sol_status_artists_artist_id_recovery_sol_status_get(artist_id)

Sol Status

Return statute-of-limitations classification for all open anomalies.

Each anomaly is classified as EXPIRED, URGENT (<90 days), AT_RISK
(90–180 days), or OK (>180 days remaining), sorted most-urgent first.
Also returns an overall SOL exposure summary.

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
    api_instance = xr7_sdk.RecoveryApi(api_client)
    artist_id = 'artist_id_example' # str | 

    try:
        # Sol Status
        api_response = api_instance.sol_status_artists_artist_id_recovery_sol_status_get(artist_id)
        print("The response of RecoveryApi->sol_status_artists_artist_id_recovery_sol_status_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling RecoveryApi->sol_status_artists_artist_id_recovery_sol_status_get: %s\n" % e)
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

