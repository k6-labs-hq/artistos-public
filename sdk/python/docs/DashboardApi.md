# xr7_sdk.DashboardApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**agent_trace_artists_artist_id_agent_trace_run_id_get**](DashboardApi.md#agent_trace_artists_artist_id_agent_trace_run_id_get) | **GET** /artists/{artist_id}/agent-trace/{run_id} | Agent Trace
[**chat_royalties_artists_artist_id_chat_royalties_post**](DashboardApi.md#chat_royalties_artists_artist_id_chat_royalties_post) | **POST** /artists/{artist_id}/chat/royalties | Chat Royalties
[**dashboard_benchmarks_artists_artist_id_benchmarks_get**](DashboardApi.md#dashboard_benchmarks_artists_artist_id_benchmarks_get) | **GET** /artists/{artist_id}/benchmarks | Dashboard Benchmarks
[**dashboard_flow_artists_artist_id_dashboard_flow_get**](DashboardApi.md#dashboard_flow_artists_artist_id_dashboard_flow_get) | **GET** /artists/{artist_id}/dashboard/flow | Dashboard Flow
[**export_full_transparency_artists_artist_id_export_full_transparency_get**](DashboardApi.md#export_full_transparency_artists_artist_id_export_full_transparency_get) | **GET** /artists/{artist_id}/export/full-transparency | Export Full Transparency
[**export_guidance_artists_artist_id_dashboard_export_guidance_get**](DashboardApi.md#export_guidance_artists_artist_id_dashboard_export_guidance_get) | **GET** /artists/{artist_id}/dashboard/export-guidance | Export Guidance
[**get_agents_status_artists_artist_id_agents_status_get**](DashboardApi.md#get_agents_status_artists_artist_id_agents_status_get) | **GET** /artists/{artist_id}/agents/status | Get Agents Status
[**get_artist_dashboard_artists_artist_id_dashboard_get**](DashboardApi.md#get_artist_dashboard_artists_artist_id_dashboard_get) | **GET** /artists/{artist_id}/dashboard | Get Artist Dashboard
[**get_dashboard_ui_dashboard_ui_get**](DashboardApi.md#get_dashboard_ui_dashboard_ui_get) | **GET** /dashboard/ui | Get Dashboard Ui


# **agent_trace_artists_artist_id_agent_trace_run_id_get**
> object agent_trace_artists_artist_id_agent_trace_run_id_get(artist_id, run_id)

Agent Trace

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
    api_instance = xr7_sdk.DashboardApi(api_client)
    artist_id = 'artist_id_example' # str | 
    run_id = 'run_id_example' # str | 

    try:
        # Agent Trace
        api_response = api_instance.agent_trace_artists_artist_id_agent_trace_run_id_get(artist_id, run_id)
        print("The response of DashboardApi->agent_trace_artists_artist_id_agent_trace_run_id_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DashboardApi->agent_trace_artists_artist_id_agent_trace_run_id_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **artist_id** | **str**|  | 
 **run_id** | **str**|  | 

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

# **chat_royalties_artists_artist_id_chat_royalties_post**
> object chat_royalties_artists_artist_id_chat_royalties_post(artist_id, question)

Chat Royalties

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
    api_instance = xr7_sdk.DashboardApi(api_client)
    artist_id = 'artist_id_example' # str | 
    question = 'question_example' # str | 

    try:
        # Chat Royalties
        api_response = api_instance.chat_royalties_artists_artist_id_chat_royalties_post(artist_id, question)
        print("The response of DashboardApi->chat_royalties_artists_artist_id_chat_royalties_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DashboardApi->chat_royalties_artists_artist_id_chat_royalties_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **artist_id** | **str**|  | 
 **question** | **str**|  | 

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

# **dashboard_benchmarks_artists_artist_id_benchmarks_get**
> object dashboard_benchmarks_artists_artist_id_benchmarks_get(artist_id)

Dashboard Benchmarks

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
    api_instance = xr7_sdk.DashboardApi(api_client)
    artist_id = 'artist_id_example' # str | 

    try:
        # Dashboard Benchmarks
        api_response = api_instance.dashboard_benchmarks_artists_artist_id_benchmarks_get(artist_id)
        print("The response of DashboardApi->dashboard_benchmarks_artists_artist_id_benchmarks_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DashboardApi->dashboard_benchmarks_artists_artist_id_benchmarks_get: %s\n" % e)
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

# **dashboard_flow_artists_artist_id_dashboard_flow_get**
> object dashboard_flow_artists_artist_id_dashboard_flow_get(artist_id)

Dashboard Flow

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
    api_instance = xr7_sdk.DashboardApi(api_client)
    artist_id = 'artist_id_example' # str | 

    try:
        # Dashboard Flow
        api_response = api_instance.dashboard_flow_artists_artist_id_dashboard_flow_get(artist_id)
        print("The response of DashboardApi->dashboard_flow_artists_artist_id_dashboard_flow_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DashboardApi->dashboard_flow_artists_artist_id_dashboard_flow_get: %s\n" % e)
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

# **export_full_transparency_artists_artist_id_export_full_transparency_get**
> object export_full_transparency_artists_artist_id_export_full_transparency_get(artist_id)

Export Full Transparency

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
    api_instance = xr7_sdk.DashboardApi(api_client)
    artist_id = 'artist_id_example' # str | 

    try:
        # Export Full Transparency
        api_response = api_instance.export_full_transparency_artists_artist_id_export_full_transparency_get(artist_id)
        print("The response of DashboardApi->export_full_transparency_artists_artist_id_export_full_transparency_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DashboardApi->export_full_transparency_artists_artist_id_export_full_transparency_get: %s\n" % e)
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

# **export_guidance_artists_artist_id_dashboard_export_guidance_get**
> object export_guidance_artists_artist_id_dashboard_export_guidance_get(artist_id, platform=platform)

Export Guidance

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
    api_instance = xr7_sdk.DashboardApi(api_client)
    artist_id = 'artist_id_example' # str | 
    platform = 'youtube' # str |  (optional) (default to 'youtube')

    try:
        # Export Guidance
        api_response = api_instance.export_guidance_artists_artist_id_dashboard_export_guidance_get(artist_id, platform=platform)
        print("The response of DashboardApi->export_guidance_artists_artist_id_dashboard_export_guidance_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DashboardApi->export_guidance_artists_artist_id_dashboard_export_guidance_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **artist_id** | **str**|  | 
 **platform** | **str**|  | [optional] [default to &#39;youtube&#39;]

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

# **get_agents_status_artists_artist_id_agents_status_get**
> object get_agents_status_artists_artist_id_agents_status_get(artist_id, authorization=authorization)

Get Agents Status

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
    api_instance = xr7_sdk.DashboardApi(api_client)
    artist_id = 'artist_id_example' # str | 
    authorization = 'authorization_example' # str |  (optional)

    try:
        # Get Agents Status
        api_response = api_instance.get_agents_status_artists_artist_id_agents_status_get(artist_id, authorization=authorization)
        print("The response of DashboardApi->get_agents_status_artists_artist_id_agents_status_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DashboardApi->get_agents_status_artists_artist_id_agents_status_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **artist_id** | **str**|  | 
 **authorization** | **str**|  | [optional] 

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

# **get_artist_dashboard_artists_artist_id_dashboard_get**
> object get_artist_dashboard_artists_artist_id_dashboard_get(artist_id)

Get Artist Dashboard

Return the artist's full recovery dashboard.

**leakage_discovered**
- ``total_anomalies`` — total number of anomalies detected
- ``total_estimated_recoverable`` — sum of estimated recoverable amounts
- ``by_category`` — breakdown by revenue category (ROYALTY, TOURING, etc.)
- ``by_severity`` — breakdown by severity (LOW / MEDIUM / HIGH / CRITICAL)
- ``recent_discoveries`` — last 10 newly detected anomalies

**in_pursuit**
- ``active_claim_count`` — number of open claims
- ``total_amount_in_pursuit`` — total dollar value of active claims
- ``total_gross_recovered`` — total recovered across all closed/paid claims
- ``total_net_recovered`` — gross minus XR7 contingency fees

**recovered_and_deposited**
- ``total_deposited`` — sum of all Trolley disbursements received
- ``deposits`` — per-deposit log with Trolley payment IDs

**balance_still_pursuing**
- ``balance_still_pursuing`` — the key number: money we are still chasing
- ``total_pending_deposit`` — approved but not yet ACH-settled

**deadlines**
- ``expired_count`` — anomalies whose SOL window has already closed
- ``urgent_count`` — anomalies with <90 days remaining on their SOL window
- ``at_risk_count`` — anomalies with 90–180 days remaining
- ``top_urgent_items`` — up to 5 most time-sensitive anomalies with days_remaining

**priority_actions**
- ``top_10_actions`` — ranked action items (anomalies + claims) by ROI × urgency
- ``total_open_items`` — total items in the priority queue

**catalog_health**
- ``health_score`` — ML composite score 0–100
- ``grade`` — letter grade A–F
- ``signals`` — per-signal breakdown (metadata, payment regularity, etc.)
- ``recommendations`` — list of actionable improvement suggestions

**earnings_trend**
- ``trend`` — GROWING / FLAT / DECLINING / INSUFFICIENT_DATA
- ``predicted_total`` — predicted earnings over next 90 days
- ``predicted_low`` / ``predicted_high`` — 95% confidence interval

**activity_feed**
- Up to 50 timestamped events: leakage discoveries, claim updates,
  and payment deposits, newest first.

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
    api_instance = xr7_sdk.DashboardApi(api_client)
    artist_id = 'artist_id_example' # str | 

    try:
        # Get Artist Dashboard
        api_response = api_instance.get_artist_dashboard_artists_artist_id_dashboard_get(artist_id)
        print("The response of DashboardApi->get_artist_dashboard_artists_artist_id_dashboard_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DashboardApi->get_artist_dashboard_artists_artist_id_dashboard_get: %s\n" % e)
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

# **get_dashboard_ui_dashboard_ui_get**
> object get_dashboard_ui_dashboard_ui_get(org_id=org_id)

Get Dashboard Ui

Serve the standalone artist recovery dashboard UI page.

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
    api_instance = xr7_sdk.DashboardApi(api_client)
    org_id = 'org_id_example' # str |  (optional)

    try:
        # Get Dashboard Ui
        api_response = api_instance.get_dashboard_ui_dashboard_ui_get(org_id=org_id)
        print("The response of DashboardApi->get_dashboard_ui_dashboard_ui_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DashboardApi->get_dashboard_ui_dashboard_ui_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **org_id** | **str**|  | [optional] 

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

