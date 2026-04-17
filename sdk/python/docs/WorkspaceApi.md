# xr7_sdk.WorkspaceApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**workspace_artists_workspace_artists_get**](WorkspaceApi.md#workspace_artists_workspace_artists_get) | **GET** /workspace/artists | Workspace Artists
[**workspace_claims_workspace_claims_get**](WorkspaceApi.md#workspace_claims_workspace_claims_get) | **GET** /workspace/claims | Workspace Claims
[**workspace_deadlines_workspace_deadlines_get**](WorkspaceApi.md#workspace_deadlines_workspace_deadlines_get) | **GET** /workspace/deadlines | Workspace Deadlines
[**workspace_overview_workspace_overview_get**](WorkspaceApi.md#workspace_overview_workspace_overview_get) | **GET** /workspace/overview | Workspace Overview


# **workspace_artists_workspace_artists_get**
> object workspace_artists_workspace_artists_get(x_workspace_key=x_workspace_key, x_workspace_role=x_workspace_role)

Workspace Artists

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
    api_instance = xr7_sdk.WorkspaceApi(api_client)
    x_workspace_key = '' # str |  (optional) (default to '')
    x_workspace_role = '' # str |  (optional) (default to '')

    try:
        # Workspace Artists
        api_response = api_instance.workspace_artists_workspace_artists_get(x_workspace_key=x_workspace_key, x_workspace_role=x_workspace_role)
        print("The response of WorkspaceApi->workspace_artists_workspace_artists_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WorkspaceApi->workspace_artists_workspace_artists_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **x_workspace_key** | **str**|  | [optional] [default to &#39;&#39;]
 **x_workspace_role** | **str**|  | [optional] [default to &#39;&#39;]

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

# **workspace_claims_workspace_claims_get**
> object workspace_claims_workspace_claims_get(x_workspace_key=x_workspace_key, x_workspace_role=x_workspace_role)

Workspace Claims

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
    api_instance = xr7_sdk.WorkspaceApi(api_client)
    x_workspace_key = '' # str |  (optional) (default to '')
    x_workspace_role = '' # str |  (optional) (default to '')

    try:
        # Workspace Claims
        api_response = api_instance.workspace_claims_workspace_claims_get(x_workspace_key=x_workspace_key, x_workspace_role=x_workspace_role)
        print("The response of WorkspaceApi->workspace_claims_workspace_claims_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WorkspaceApi->workspace_claims_workspace_claims_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **x_workspace_key** | **str**|  | [optional] [default to &#39;&#39;]
 **x_workspace_role** | **str**|  | [optional] [default to &#39;&#39;]

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

# **workspace_deadlines_workspace_deadlines_get**
> object workspace_deadlines_workspace_deadlines_get(x_workspace_key=x_workspace_key, x_workspace_role=x_workspace_role)

Workspace Deadlines

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
    api_instance = xr7_sdk.WorkspaceApi(api_client)
    x_workspace_key = '' # str |  (optional) (default to '')
    x_workspace_role = '' # str |  (optional) (default to '')

    try:
        # Workspace Deadlines
        api_response = api_instance.workspace_deadlines_workspace_deadlines_get(x_workspace_key=x_workspace_key, x_workspace_role=x_workspace_role)
        print("The response of WorkspaceApi->workspace_deadlines_workspace_deadlines_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WorkspaceApi->workspace_deadlines_workspace_deadlines_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **x_workspace_key** | **str**|  | [optional] [default to &#39;&#39;]
 **x_workspace_role** | **str**|  | [optional] [default to &#39;&#39;]

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

# **workspace_overview_workspace_overview_get**
> object workspace_overview_workspace_overview_get(x_workspace_key=x_workspace_key, x_workspace_role=x_workspace_role)

Workspace Overview

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
    api_instance = xr7_sdk.WorkspaceApi(api_client)
    x_workspace_key = '' # str |  (optional) (default to '')
    x_workspace_role = '' # str |  (optional) (default to '')

    try:
        # Workspace Overview
        api_response = api_instance.workspace_overview_workspace_overview_get(x_workspace_key=x_workspace_key, x_workspace_role=x_workspace_role)
        print("The response of WorkspaceApi->workspace_overview_workspace_overview_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WorkspaceApi->workspace_overview_workspace_overview_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **x_workspace_key** | **str**|  | [optional] [default to &#39;&#39;]
 **x_workspace_role** | **str**|  | [optional] [default to &#39;&#39;]

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
