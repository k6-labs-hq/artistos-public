# xr7_sdk.TermsApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**accept_terms_artists_artist_id_terms_accept_post**](TermsApi.md#accept_terms_artists_artist_id_terms_accept_post) | **POST** /artists/{artist_id}/terms/accept | Accept Terms
[**get_terms_terms_get**](TermsApi.md#get_terms_terms_get) | **GET** /terms | Get Terms
[**terms_status_artists_artist_id_terms_status_get**](TermsApi.md#terms_status_artists_artist_id_terms_status_get) | **GET** /artists/{artist_id}/terms/status | Terms Status


# **accept_terms_artists_artist_id_terms_accept_post**
> TermsAcceptanceSchema accept_terms_artists_artist_id_terms_accept_post(artist_id, terms_accept_request)

Accept Terms

Record the artist's acceptance of the current Artist Recovery Services
Agreement.

This endpoint:
1. Verifies the artist exists.
2. Verifies the version the artist was shown matches the live version
   (stale-page protection).
3. Verifies the ``agreed`` flag is ``true`` — a bare form POST cannot
   accidentally create an acceptance record.
4. Persists an immutable TermsAcceptance row with server-set timestamp,
   IP address, and User-Agent string.

Submitting again after the artist has already accepted the current version
is idempotent — the existing acceptance record is returned without creating
a duplicate.

### Example


```python
import xr7_sdk
from xr7_sdk.models.terms_accept_request import TermsAcceptRequest
from xr7_sdk.models.terms_acceptance_schema import TermsAcceptanceSchema
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
    api_instance = xr7_sdk.TermsApi(api_client)
    artist_id = 'artist_id_example' # str |
    terms_accept_request = xr7_sdk.TermsAcceptRequest() # TermsAcceptRequest |

    try:
        # Accept Terms
        api_response = api_instance.accept_terms_artists_artist_id_terms_accept_post(artist_id, terms_accept_request)
        print("The response of TermsApi->accept_terms_artists_artist_id_terms_accept_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TermsApi->accept_terms_artists_artist_id_terms_accept_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **artist_id** | **str**|  |
 **terms_accept_request** | [**TermsAcceptRequest**](TermsAcceptRequest.md)|  |

### Return type

[**TermsAcceptanceSchema**](TermsAcceptanceSchema.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_terms_terms_get**
> Dict[str, object] get_terms_terms_get()

Get Terms

Return the current Artist Recovery Services Agreement text, version
identifier, and SHA-256 hash.

The client should render the full ``text`` field for the artist to read
before presenting the acceptance checkbox.  The ``version`` and ``sha256``
values must be echoed back verbatim in POST /artists/{id}/terms/accept.

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
    api_instance = xr7_sdk.TermsApi(api_client)

    try:
        # Get Terms
        api_response = api_instance.get_terms_terms_get()
        print("The response of TermsApi->get_terms_terms_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TermsApi->get_terms_terms_get: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

**Dict[str, object]**

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

# **terms_status_artists_artist_id_terms_status_get**
> Dict[str, object] terms_status_artists_artist_id_terms_status_get(artist_id)

Terms Status

Return whether the artist has accepted the current version of the
Artist Recovery Services Agreement.

``accepted`` is ``True`` only if there is an acceptance record for the
*current* live version.  If the terms were updated since the artist last
agreed, ``accepted`` will be ``False`` and ``pending_version`` will
indicate the version the artist needs to accept.

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
    api_instance = xr7_sdk.TermsApi(api_client)
    artist_id = 'artist_id_example' # str |

    try:
        # Terms Status
        api_response = api_instance.terms_status_artists_artist_id_terms_status_get(artist_id)
        print("The response of TermsApi->terms_status_artists_artist_id_terms_status_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TermsApi->terms_status_artists_artist_id_terms_status_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **artist_id** | **str**|  |

### Return type

**Dict[str, object]**

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
