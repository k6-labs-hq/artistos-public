# xr7_sdk.SovereigntyApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**accept_advance_offer_artists_artist_id_advance_accept_post**](SovereigntyApi.md#accept_advance_offer_artists_artist_id_advance_accept_post) | **POST** /artists/{artist_id}/advance/accept | Accept Advance Offer
[**create_advance_offer_artists_artist_id_advance_offer_post**](SovereigntyApi.md#create_advance_offer_artists_artist_id_advance_offer_post) | **POST** /artists/{artist_id}/advance/offer | Create Advance Offer
[**list_advance_history_artists_artist_id_advance_history_get**](SovereigntyApi.md#list_advance_history_artists_artist_id_advance_history_get) | **GET** /artists/{artist_id}/advance/history | List Advance History
[**list_rights_gaps_artists_artist_id_rights_gaps_get**](SovereigntyApi.md#list_rights_gaps_artists_artist_id_rights_gaps_get) | **GET** /artists/{artist_id}/rights/gaps | List Rights Gaps
[**register_rights_packets_artists_artist_id_rights_register_post**](SovereigntyApi.md#register_rights_packets_artists_artist_id_rights_register_post) | **POST** /artists/{artist_id}/rights/register | Register Rights Packets
[**scan_rights_artists_artist_id_rights_scan_get**](SovereigntyApi.md#scan_rights_artists_artist_id_rights_scan_get) | **GET** /artists/{artist_id}/rights/scan | Scan Rights


# **accept_advance_offer_artists_artist_id_advance_accept_post**
> Dict[str, object] accept_advance_offer_artists_artist_id_advance_accept_post(artist_id, advance_accept_request)

Accept Advance Offer

Accept a pending advance offer. Triggers Trolley disbursement queue.

### Example

* Bearer Authentication (HTTPBearer):

```python
import xr7_sdk
from xr7_sdk.models.advance_accept_request import AdvanceAcceptRequest
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
    api_instance = xr7_sdk.SovereigntyApi(api_client)
    artist_id = 'artist_id_example' # str |
    advance_accept_request = xr7_sdk.AdvanceAcceptRequest() # AdvanceAcceptRequest |

    try:
        # Accept Advance Offer
        api_response = api_instance.accept_advance_offer_artists_artist_id_advance_accept_post(artist_id, advance_accept_request)
        print("The response of SovereigntyApi->accept_advance_offer_artists_artist_id_advance_accept_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling SovereigntyApi->accept_advance_offer_artists_artist_id_advance_accept_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **artist_id** | **str**|  |
 **advance_accept_request** | [**AdvanceAcceptRequest**](AdvanceAcceptRequest.md)|  |

### Return type

**Dict[str, object]**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **create_advance_offer_artists_artist_id_advance_offer_post**
> Dict[str, object] create_advance_offer_artists_artist_id_advance_offer_post(artist_id, advance_offer_request)

Create Advance Offer

Compute and return a cash advance offer backed by predicted recovery.

Safe advance = 60% of the predicted-low earnings forecast; repaid
automatically when the recovery arrives.

### Example

* Bearer Authentication (HTTPBearer):

```python
import xr7_sdk
from xr7_sdk.models.advance_offer_request import AdvanceOfferRequest
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
    api_instance = xr7_sdk.SovereigntyApi(api_client)
    artist_id = 'artist_id_example' # str |
    advance_offer_request = xr7_sdk.AdvanceOfferRequest() # AdvanceOfferRequest |

    try:
        # Create Advance Offer
        api_response = api_instance.create_advance_offer_artists_artist_id_advance_offer_post(artist_id, advance_offer_request)
        print("The response of SovereigntyApi->create_advance_offer_artists_artist_id_advance_offer_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling SovereigntyApi->create_advance_offer_artists_artist_id_advance_offer_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **artist_id** | **str**|  |
 **advance_offer_request** | [**AdvanceOfferRequest**](AdvanceOfferRequest.md)|  |

### Return type

**Dict[str, object]**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_advance_history_artists_artist_id_advance_history_get**
> Dict[str, object] list_advance_history_artists_artist_id_advance_history_get(artist_id)

List Advance History

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
    api_instance = xr7_sdk.SovereigntyApi(api_client)
    artist_id = 'artist_id_example' # str |

    try:
        # List Advance History
        api_response = api_instance.list_advance_history_artists_artist_id_advance_history_get(artist_id)
        print("The response of SovereigntyApi->list_advance_history_artists_artist_id_advance_history_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling SovereigntyApi->list_advance_history_artists_artist_id_advance_history_get: %s\n" % e)
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

# **list_rights_gaps_artists_artist_id_rights_gaps_get**
> Dict[str, object] list_rights_gaps_artists_artist_id_rights_gaps_get(artist_id)

List Rights Gaps

List all persisted rights scan results for this artist.

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
    api_instance = xr7_sdk.SovereigntyApi(api_client)
    artist_id = 'artist_id_example' # str |

    try:
        # List Rights Gaps
        api_response = api_instance.list_rights_gaps_artists_artist_id_rights_gaps_get(artist_id)
        print("The response of SovereigntyApi->list_rights_gaps_artists_artist_id_rights_gaps_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling SovereigntyApi->list_rights_gaps_artists_artist_id_rights_gaps_get: %s\n" % e)
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

# **register_rights_packets_artists_artist_id_rights_register_post**
> Dict[str, object] register_rights_packets_artists_artist_id_rights_register_post(artist_id)

Register Rights Packets

Generate and persist auto-registration packets for all detected gaps.

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
    api_instance = xr7_sdk.SovereigntyApi(api_client)
    artist_id = 'artist_id_example' # str |

    try:
        # Register Rights Packets
        api_response = api_instance.register_rights_packets_artists_artist_id_rights_register_post(artist_id)
        print("The response of SovereigntyApi->register_rights_packets_artists_artist_id_rights_register_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling SovereigntyApi->register_rights_packets_artists_artist_id_rights_register_post: %s\n" % e)
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

# **scan_rights_artists_artist_id_rights_scan_get**
> Dict[str, object] scan_rights_artists_artist_id_rights_scan_get(artist_id)

Scan Rights

Scan catalog for missing ISRC/ISWC/UPC/PRO/foreign registrations.

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
    api_instance = xr7_sdk.SovereigntyApi(api_client)
    artist_id = 'artist_id_example' # str |

    try:
        # Scan Rights
        api_response = api_instance.scan_rights_artists_artist_id_rights_scan_get(artist_id)
        print("The response of SovereigntyApi->scan_rights_artists_artist_id_rights_scan_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling SovereigntyApi->scan_rights_artists_artist_id_rights_scan_get: %s\n" % e)
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
