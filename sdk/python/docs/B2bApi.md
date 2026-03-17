# xr7_sdk.B2bApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**b2b_dashboard_b2b_org_org_id_dashboard_get**](B2bApi.md#b2b_dashboard_b2b_org_org_id_dashboard_get) | **GET** /b2b/org/{org_id}/dashboard | B2B Dashboard
[**bulk_onboard_b2b_org_org_id_artists_bulk_onboard_post**](B2bApi.md#bulk_onboard_b2b_org_org_id_artists_bulk_onboard_post) | **POST** /b2b/org/{org_id}/artists/bulk-onboard | Bulk Onboard
[**management_anomalies_drilldown_management_org_id_anomalies_get**](B2bApi.md#management_anomalies_drilldown_management_org_id_anomalies_get) | **GET** /management/{org_id}/anomalies | Management Anomalies Drilldown
[**management_artist_drilldown_management_org_id_artists_artist_id_get**](B2bApi.md#management_artist_drilldown_management_org_id_artists_artist_id_get) | **GET** /management/{org_id}/artists/{artist_id} | Management Artist Drilldown
[**management_catalog_drilldown_management_org_id_catalog_get**](B2bApi.md#management_catalog_drilldown_management_org_id_catalog_get) | **GET** /management/{org_id}/catalog | Management Catalog Drilldown
[**management_claims_drilldown_management_org_id_claims_get**](B2bApi.md#management_claims_drilldown_management_org_id_claims_get) | **GET** /management/{org_id}/claims | Management Claims Drilldown
[**management_dashboard_management_org_id_dashboard_get**](B2bApi.md#management_dashboard_management_org_id_dashboard_get) | **GET** /management/{org_id}/dashboard | Management Dashboard
[**management_forecast_management_org_id_forecast_get**](B2bApi.md#management_forecast_management_org_id_forecast_get) | **GET** /management/{org_id}/forecast | Management Forecast
[**org_portfolio_org_org_id_portfolio_get**](B2bApi.md#org_portfolio_org_org_id_portfolio_get) | **GET** /org/{org_id}/portfolio | Org Portfolio
[**xr7_operator_dashboard_xr7_operator_dashboard_get**](B2bApi.md#xr7_operator_dashboard_xr7_operator_dashboard_get) | **GET** /xr7/operator/dashboard | Xr7 Operator Dashboard


# **b2b_dashboard_b2b_org_org_id_dashboard_get**
> object b2b_dashboard_b2b_org_org_id_dashboard_get(org_id, x_org_key=x_org_key, x_org_role=x_org_role, x_org_actor=x_org_actor)

B2B Dashboard

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
    api_instance = xr7_sdk.B2bApi(api_client)
    org_id = 'org_id_example' # str | 
    x_org_key = '' # str |  (optional) (default to '')
    x_org_role = '' # str |  (optional) (default to '')
    x_org_actor = '' # str |  (optional) (default to '')

    try:
        # B2B Dashboard
        api_response = api_instance.b2b_dashboard_b2b_org_org_id_dashboard_get(org_id, x_org_key=x_org_key, x_org_role=x_org_role, x_org_actor=x_org_actor)
        print("The response of B2bApi->b2b_dashboard_b2b_org_org_id_dashboard_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling B2bApi->b2b_dashboard_b2b_org_org_id_dashboard_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **org_id** | **str**|  | 
 **x_org_key** | **str**|  | [optional] [default to &#39;&#39;]
 **x_org_role** | **str**|  | [optional] [default to &#39;&#39;]
 **x_org_actor** | **str**|  | [optional] [default to &#39;&#39;]

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

# **bulk_onboard_b2b_org_org_id_artists_bulk_onboard_post**
> object bulk_onboard_b2b_org_org_id_artists_bulk_onboard_post(org_id, bulk_onboard_request, x_org_key=x_org_key, x_org_role=x_org_role, x_org_actor=x_org_actor)

Bulk Onboard

### Example


```python
import xr7_sdk
from xr7_sdk.models.bulk_onboard_request import BulkOnboardRequest
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
    api_instance = xr7_sdk.B2bApi(api_client)
    org_id = 'org_id_example' # str | 
    bulk_onboard_request = xr7_sdk.BulkOnboardRequest() # BulkOnboardRequest | 
    x_org_key = '' # str |  (optional) (default to '')
    x_org_role = '' # str |  (optional) (default to '')
    x_org_actor = '' # str |  (optional) (default to '')

    try:
        # Bulk Onboard
        api_response = api_instance.bulk_onboard_b2b_org_org_id_artists_bulk_onboard_post(org_id, bulk_onboard_request, x_org_key=x_org_key, x_org_role=x_org_role, x_org_actor=x_org_actor)
        print("The response of B2bApi->bulk_onboard_b2b_org_org_id_artists_bulk_onboard_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling B2bApi->bulk_onboard_b2b_org_org_id_artists_bulk_onboard_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **org_id** | **str**|  | 
 **bulk_onboard_request** | [**BulkOnboardRequest**](BulkOnboardRequest.md)|  | 
 **x_org_key** | **str**|  | [optional] [default to &#39;&#39;]
 **x_org_role** | **str**|  | [optional] [default to &#39;&#39;]
 **x_org_actor** | **str**|  | [optional] [default to &#39;&#39;]

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

# **management_anomalies_drilldown_management_org_id_anomalies_get**
> object management_anomalies_drilldown_management_org_id_anomalies_get(org_id, severity=severity, status=status, category=category, limit=limit, x_org_key=x_org_key, x_org_role=x_org_role, x_org_actor=x_org_actor)

Management Anomalies Drilldown

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
    api_instance = xr7_sdk.B2bApi(api_client)
    org_id = 'org_id_example' # str | 
    severity = 'severity_example' # str |  (optional)
    status = 'status_example' # str |  (optional)
    category = 'category_example' # str |  (optional)
    limit = 100 # int |  (optional) (default to 100)
    x_org_key = '' # str |  (optional) (default to '')
    x_org_role = '' # str |  (optional) (default to '')
    x_org_actor = '' # str |  (optional) (default to '')

    try:
        # Management Anomalies Drilldown
        api_response = api_instance.management_anomalies_drilldown_management_org_id_anomalies_get(org_id, severity=severity, status=status, category=category, limit=limit, x_org_key=x_org_key, x_org_role=x_org_role, x_org_actor=x_org_actor)
        print("The response of B2bApi->management_anomalies_drilldown_management_org_id_anomalies_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling B2bApi->management_anomalies_drilldown_management_org_id_anomalies_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **org_id** | **str**|  | 
 **severity** | **str**|  | [optional] 
 **status** | **str**|  | [optional] 
 **category** | **str**|  | [optional] 
 **limit** | **int**|  | [optional] [default to 100]
 **x_org_key** | **str**|  | [optional] [default to &#39;&#39;]
 **x_org_role** | **str**|  | [optional] [default to &#39;&#39;]
 **x_org_actor** | **str**|  | [optional] [default to &#39;&#39;]

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

# **management_artist_drilldown_management_org_id_artists_artist_id_get**
> object management_artist_drilldown_management_org_id_artists_artist_id_get(org_id, artist_id, x_org_key=x_org_key, x_org_role=x_org_role, x_org_actor=x_org_actor)

Management Artist Drilldown

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
    api_instance = xr7_sdk.B2bApi(api_client)
    org_id = 'org_id_example' # str | 
    artist_id = 'artist_id_example' # str | 
    x_org_key = '' # str |  (optional) (default to '')
    x_org_role = '' # str |  (optional) (default to '')
    x_org_actor = '' # str |  (optional) (default to '')

    try:
        # Management Artist Drilldown
        api_response = api_instance.management_artist_drilldown_management_org_id_artists_artist_id_get(org_id, artist_id, x_org_key=x_org_key, x_org_role=x_org_role, x_org_actor=x_org_actor)
        print("The response of B2bApi->management_artist_drilldown_management_org_id_artists_artist_id_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling B2bApi->management_artist_drilldown_management_org_id_artists_artist_id_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **org_id** | **str**|  | 
 **artist_id** | **str**|  | 
 **x_org_key** | **str**|  | [optional] [default to &#39;&#39;]
 **x_org_role** | **str**|  | [optional] [default to &#39;&#39;]
 **x_org_actor** | **str**|  | [optional] [default to &#39;&#39;]

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

# **management_catalog_drilldown_management_org_id_catalog_get**
> object management_catalog_drilldown_management_org_id_catalog_get(org_id, x_org_key=x_org_key, x_org_role=x_org_role, x_org_actor=x_org_actor)

Management Catalog Drilldown

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
    api_instance = xr7_sdk.B2bApi(api_client)
    org_id = 'org_id_example' # str | 
    x_org_key = '' # str |  (optional) (default to '')
    x_org_role = '' # str |  (optional) (default to '')
    x_org_actor = '' # str |  (optional) (default to '')

    try:
        # Management Catalog Drilldown
        api_response = api_instance.management_catalog_drilldown_management_org_id_catalog_get(org_id, x_org_key=x_org_key, x_org_role=x_org_role, x_org_actor=x_org_actor)
        print("The response of B2bApi->management_catalog_drilldown_management_org_id_catalog_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling B2bApi->management_catalog_drilldown_management_org_id_catalog_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **org_id** | **str**|  | 
 **x_org_key** | **str**|  | [optional] [default to &#39;&#39;]
 **x_org_role** | **str**|  | [optional] [default to &#39;&#39;]
 **x_org_actor** | **str**|  | [optional] [default to &#39;&#39;]

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

# **management_claims_drilldown_management_org_id_claims_get**
> object management_claims_drilldown_management_org_id_claims_get(org_id, status=status, sol_window_days=sol_window_days, limit=limit, x_org_key=x_org_key, x_org_role=x_org_role, x_org_actor=x_org_actor)

Management Claims Drilldown

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
    api_instance = xr7_sdk.B2bApi(api_client)
    org_id = 'org_id_example' # str | 
    status = 'status_example' # str |  (optional)
    sol_window_days = 30 # int |  (optional) (default to 30)
    limit = 100 # int |  (optional) (default to 100)
    x_org_key = '' # str |  (optional) (default to '')
    x_org_role = '' # str |  (optional) (default to '')
    x_org_actor = '' # str |  (optional) (default to '')

    try:
        # Management Claims Drilldown
        api_response = api_instance.management_claims_drilldown_management_org_id_claims_get(org_id, status=status, sol_window_days=sol_window_days, limit=limit, x_org_key=x_org_key, x_org_role=x_org_role, x_org_actor=x_org_actor)
        print("The response of B2bApi->management_claims_drilldown_management_org_id_claims_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling B2bApi->management_claims_drilldown_management_org_id_claims_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **org_id** | **str**|  | 
 **status** | **str**|  | [optional] 
 **sol_window_days** | **int**|  | [optional] [default to 30]
 **limit** | **int**|  | [optional] [default to 100]
 **x_org_key** | **str**|  | [optional] [default to &#39;&#39;]
 **x_org_role** | **str**|  | [optional] [default to &#39;&#39;]
 **x_org_actor** | **str**|  | [optional] [default to &#39;&#39;]

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

# **management_dashboard_management_org_id_dashboard_get**
> object management_dashboard_management_org_id_dashboard_get(org_id, x_org_key=x_org_key, x_org_role=x_org_role, x_org_actor=x_org_actor)

Management Dashboard

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
    api_instance = xr7_sdk.B2bApi(api_client)
    org_id = 'org_id_example' # str | 
    x_org_key = '' # str |  (optional) (default to '')
    x_org_role = '' # str |  (optional) (default to '')
    x_org_actor = '' # str |  (optional) (default to '')

    try:
        # Management Dashboard
        api_response = api_instance.management_dashboard_management_org_id_dashboard_get(org_id, x_org_key=x_org_key, x_org_role=x_org_role, x_org_actor=x_org_actor)
        print("The response of B2bApi->management_dashboard_management_org_id_dashboard_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling B2bApi->management_dashboard_management_org_id_dashboard_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **org_id** | **str**|  | 
 **x_org_key** | **str**|  | [optional] [default to &#39;&#39;]
 **x_org_role** | **str**|  | [optional] [default to &#39;&#39;]
 **x_org_actor** | **str**|  | [optional] [default to &#39;&#39;]

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

# **management_forecast_management_org_id_forecast_get**
> object management_forecast_management_org_id_forecast_get(org_id, x_org_key=x_org_key, x_org_role=x_org_role, x_org_actor=x_org_actor)

Management Forecast

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
    api_instance = xr7_sdk.B2bApi(api_client)
    org_id = 'org_id_example' # str | 
    x_org_key = '' # str |  (optional) (default to '')
    x_org_role = '' # str |  (optional) (default to '')
    x_org_actor = '' # str |  (optional) (default to '')

    try:
        # Management Forecast
        api_response = api_instance.management_forecast_management_org_id_forecast_get(org_id, x_org_key=x_org_key, x_org_role=x_org_role, x_org_actor=x_org_actor)
        print("The response of B2bApi->management_forecast_management_org_id_forecast_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling B2bApi->management_forecast_management_org_id_forecast_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **org_id** | **str**|  | 
 **x_org_key** | **str**|  | [optional] [default to &#39;&#39;]
 **x_org_role** | **str**|  | [optional] [default to &#39;&#39;]
 **x_org_actor** | **str**|  | [optional] [default to &#39;&#39;]

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

# **org_portfolio_org_org_id_portfolio_get**
> object org_portfolio_org_org_id_portfolio_get(org_id, x_org_key=x_org_key, x_org_role=x_org_role, x_org_actor=x_org_actor)

Org Portfolio

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
    api_instance = xr7_sdk.B2bApi(api_client)
    org_id = 'org_id_example' # str | 
    x_org_key = '' # str |  (optional) (default to '')
    x_org_role = '' # str |  (optional) (default to '')
    x_org_actor = '' # str |  (optional) (default to '')

    try:
        # Org Portfolio
        api_response = api_instance.org_portfolio_org_org_id_portfolio_get(org_id, x_org_key=x_org_key, x_org_role=x_org_role, x_org_actor=x_org_actor)
        print("The response of B2bApi->org_portfolio_org_org_id_portfolio_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling B2bApi->org_portfolio_org_org_id_portfolio_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **org_id** | **str**|  | 
 **x_org_key** | **str**|  | [optional] [default to &#39;&#39;]
 **x_org_role** | **str**|  | [optional] [default to &#39;&#39;]
 **x_org_actor** | **str**|  | [optional] [default to &#39;&#39;]

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

# **xr7_operator_dashboard_xr7_operator_dashboard_get**
> object xr7_operator_dashboard_xr7_operator_dashboard_get(org_id=org_id, x_org_key=x_org_key, x_org_role=x_org_role, x_org_actor=x_org_actor)

Xr7 Operator Dashboard

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
    api_instance = xr7_sdk.B2bApi(api_client)
    org_id = 'org_id_example' # str |  (optional)
    x_org_key = '' # str |  (optional) (default to '')
    x_org_role = '' # str |  (optional) (default to '')
    x_org_actor = '' # str |  (optional) (default to '')

    try:
        # Xr7 Operator Dashboard
        api_response = api_instance.xr7_operator_dashboard_xr7_operator_dashboard_get(org_id=org_id, x_org_key=x_org_key, x_org_role=x_org_role, x_org_actor=x_org_actor)
        print("The response of B2bApi->xr7_operator_dashboard_xr7_operator_dashboard_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling B2bApi->xr7_operator_dashboard_xr7_operator_dashboard_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **org_id** | **str**|  | [optional] 
 **x_org_key** | **str**|  | [optional] [default to &#39;&#39;]
 **x_org_role** | **str**|  | [optional] [default to &#39;&#39;]
 **x_org_actor** | **str**|  | [optional] [default to &#39;&#39;]

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

