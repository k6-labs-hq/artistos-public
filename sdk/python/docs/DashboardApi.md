# xr7_sdk.DashboardApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_artist_dashboard_artists_artist_id_dashboard_get**](DashboardApi.md#get_artist_dashboard_artists_artist_id_dashboard_get) | **GET** /artists/{artist_id}/dashboard | Get Artist Dashboard
[**get_dashboard_ui_dashboard_ui_get**](DashboardApi.md#get_dashboard_ui_dashboard_ui_get) | **GET** /dashboard/ui | Get Dashboard Ui


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
- ``total_deposited`` — sum of all Celero disbursements received
- ``deposits`` — per-deposit log with Celero transaction IDs

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
> object get_dashboard_ui_dashboard_ui_get()

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

    try:
        # Get Dashboard Ui
        api_response = api_instance.get_dashboard_ui_dashboard_ui_get()
        print("The response of DashboardApi->get_dashboard_ui_dashboard_ui_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DashboardApi->get_dashboard_ui_dashboard_ui_get: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

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

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

