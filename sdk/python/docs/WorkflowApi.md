# xr7_sdk.WorkflowApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**run_full_autonomous_workflow_artists_artist_id_workflow_run_full_autonomous_post**](WorkflowApi.md#run_full_autonomous_workflow_artists_artist_id_workflow_run_full_autonomous_post) | **POST** /artists/{artist_id}/workflow/run-full-autonomous | Run Full Autonomous Workflow
[**workflow_run_status_artists_artist_id_workflow_runs_run_id_get**](WorkflowApi.md#workflow_run_status_artists_artist_id_workflow_runs_run_id_get) | **GET** /artists/{artist_id}/workflow/runs/{run_id} | Workflow Run Status


# **run_full_autonomous_workflow_artists_artist_id_workflow_run_full_autonomous_post**
> WorkflowRunResponse run_full_autonomous_workflow_artists_artist_id_workflow_run_full_autonomous_post(artist_id)

Run Full Autonomous Workflow

### Example


```python
import xr7_sdk
from xr7_sdk.models.workflow_run_response import WorkflowRunResponse
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
    api_instance = xr7_sdk.WorkflowApi(api_client)
    artist_id = 'artist_id_example' # str |

    try:
        # Run Full Autonomous Workflow
        api_response = api_instance.run_full_autonomous_workflow_artists_artist_id_workflow_run_full_autonomous_post(artist_id)
        print("The response of WorkflowApi->run_full_autonomous_workflow_artists_artist_id_workflow_run_full_autonomous_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WorkflowApi->run_full_autonomous_workflow_artists_artist_id_workflow_run_full_autonomous_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **artist_id** | **str**|  |

### Return type

[**WorkflowRunResponse**](WorkflowRunResponse.md)

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

# **workflow_run_status_artists_artist_id_workflow_runs_run_id_get**
> object workflow_run_status_artists_artist_id_workflow_runs_run_id_get(artist_id, run_id)

Workflow Run Status

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
    api_instance = xr7_sdk.WorkflowApi(api_client)
    artist_id = 'artist_id_example' # str |
    run_id = 'run_id_example' # str |

    try:
        # Workflow Run Status
        api_response = api_instance.workflow_run_status_artists_artist_id_workflow_runs_run_id_get(artist_id, run_id)
        print("The response of WorkflowApi->workflow_run_status_artists_artist_id_workflow_runs_run_id_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WorkflowApi->workflow_run_status_artists_artist_id_workflow_runs_run_id_get: %s\n" % e)
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
