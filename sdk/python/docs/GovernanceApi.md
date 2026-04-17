# xr7_sdk.GovernanceApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**erase_artist_data_artists_artist_id_privacy_erase_post**](GovernanceApi.md#erase_artist_data_artists_artist_id_privacy_erase_post) | **POST** /artists/{artist_id}/privacy/erase | Erase Artist Data
[**export_artist_data_artists_artist_id_privacy_export_post**](GovernanceApi.md#export_artist_data_artists_artist_id_privacy_export_post) | **POST** /artists/{artist_id}/privacy/export | Export Artist Data
[**list_admin_audit_events_admin_audit_events_get**](GovernanceApi.md#list_admin_audit_events_admin_audit_events_get) | **GET** /admin/audit/events | List Admin Audit Events


# **erase_artist_data_artists_artist_id_privacy_erase_post**
> Dict[str, object] erase_artist_data_artists_artist_id_privacy_erase_post(artist_id)

Erase Artist Data

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
    api_instance = xr7_sdk.GovernanceApi(api_client)
    artist_id = 'artist_id_example' # str |

    try:
        # Erase Artist Data
        api_response = api_instance.erase_artist_data_artists_artist_id_privacy_erase_post(artist_id)
        print("The response of GovernanceApi->erase_artist_data_artists_artist_id_privacy_erase_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling GovernanceApi->erase_artist_data_artists_artist_id_privacy_erase_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **artist_id** | **str**|  |

### Return type

**Dict[str, object]**

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

# **export_artist_data_artists_artist_id_privacy_export_post**
> Dict[str, object] export_artist_data_artists_artist_id_privacy_export_post(artist_id)

Export Artist Data

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
    api_instance = xr7_sdk.GovernanceApi(api_client)
    artist_id = 'artist_id_example' # str |

    try:
        # Export Artist Data
        api_response = api_instance.export_artist_data_artists_artist_id_privacy_export_post(artist_id)
        print("The response of GovernanceApi->export_artist_data_artists_artist_id_privacy_export_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling GovernanceApi->export_artist_data_artists_artist_id_privacy_export_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **artist_id** | **str**|  |

### Return type

**Dict[str, object]**

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

# **list_admin_audit_events_admin_audit_events_get**
> Dict[str, object] list_admin_audit_events_admin_audit_events_get(limit=limit)

List Admin Audit Events

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
    api_instance = xr7_sdk.GovernanceApi(api_client)
    limit = 100 # int |  (optional) (default to 100)

    try:
        # List Admin Audit Events
        api_response = api_instance.list_admin_audit_events_admin_audit_events_get(limit=limit)
        print("The response of GovernanceApi->list_admin_audit_events_admin_audit_events_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling GovernanceApi->list_admin_audit_events_admin_audit_events_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **limit** | **int**|  | [optional] [default to 100]

### Return type

**Dict[str, object]**

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
