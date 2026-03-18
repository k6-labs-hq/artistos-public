# xr7_sdk.IdentityApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**auto_match_identity_artists_artist_id_identity_auto_match_post**](IdentityApi.md#auto_match_identity_artists_artist_id_identity_auto_match_post) | **POST** /artists/{artist_id}/identity/auto-match | Auto Match Identity
[**decide_identity_match_artists_artist_id_identity_matches_match_id_decision_post**](IdentityApi.md#decide_identity_match_artists_artist_id_identity_matches_match_id_decision_post) | **POST** /artists/{artist_id}/identity/matches/{match_id}/decision | Decide Identity Match
[**get_identity_match_audit_artists_artist_id_identity_matches_match_id_audit_get**](IdentityApi.md#get_identity_match_audit_artists_artist_id_identity_matches_match_id_audit_get) | **GET** /artists/{artist_id}/identity/matches/{match_id}/audit | Get Identity Match Audit
[**list_identity_matches_artists_artist_id_identity_matches_get**](IdentityApi.md#list_identity_matches_artists_artist_id_identity_matches_get) | **GET** /artists/{artist_id}/identity/matches | List Identity Matches


# **auto_match_identity_artists_artist_id_identity_auto_match_post**
> ArtistIdentityMatchSchema auto_match_identity_artists_artist_id_identity_auto_match_post(artist_id, identity_match_request)

Auto Match Identity

### Example

* Bearer Authentication (HTTPBearer):

```python
import xr7_sdk
from xr7_sdk.models.artist_identity_match_schema import ArtistIdentityMatchSchema
from xr7_sdk.models.identity_match_request import IdentityMatchRequest
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
    api_instance = xr7_sdk.IdentityApi(api_client)
    artist_id = 'artist_id_example' # str | 
    identity_match_request = xr7_sdk.IdentityMatchRequest() # IdentityMatchRequest | 

    try:
        # Auto Match Identity
        api_response = api_instance.auto_match_identity_artists_artist_id_identity_auto_match_post(artist_id, identity_match_request)
        print("The response of IdentityApi->auto_match_identity_artists_artist_id_identity_auto_match_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling IdentityApi->auto_match_identity_artists_artist_id_identity_auto_match_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **artist_id** | **str**|  | 
 **identity_match_request** | [**IdentityMatchRequest**](IdentityMatchRequest.md)|  | 

### Return type

[**ArtistIdentityMatchSchema**](ArtistIdentityMatchSchema.md)

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

# **decide_identity_match_artists_artist_id_identity_matches_match_id_decision_post**
> ArtistIdentityMatchSchema decide_identity_match_artists_artist_id_identity_matches_match_id_decision_post(artist_id, match_id, identity_decision_request)

Decide Identity Match

### Example

* Bearer Authentication (HTTPBearer):

```python
import xr7_sdk
from xr7_sdk.models.artist_identity_match_schema import ArtistIdentityMatchSchema
from xr7_sdk.models.identity_decision_request import IdentityDecisionRequest
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
    api_instance = xr7_sdk.IdentityApi(api_client)
    artist_id = 'artist_id_example' # str | 
    match_id = 'match_id_example' # str | 
    identity_decision_request = xr7_sdk.IdentityDecisionRequest() # IdentityDecisionRequest | 

    try:
        # Decide Identity Match
        api_response = api_instance.decide_identity_match_artists_artist_id_identity_matches_match_id_decision_post(artist_id, match_id, identity_decision_request)
        print("The response of IdentityApi->decide_identity_match_artists_artist_id_identity_matches_match_id_decision_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling IdentityApi->decide_identity_match_artists_artist_id_identity_matches_match_id_decision_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **artist_id** | **str**|  | 
 **match_id** | **str**|  | 
 **identity_decision_request** | [**IdentityDecisionRequest**](IdentityDecisionRequest.md)|  | 

### Return type

[**ArtistIdentityMatchSchema**](ArtistIdentityMatchSchema.md)

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

# **get_identity_match_audit_artists_artist_id_identity_matches_match_id_audit_get**
> Dict[str, object] get_identity_match_audit_artists_artist_id_identity_matches_match_id_audit_get(artist_id, match_id)

Get Identity Match Audit

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
    api_instance = xr7_sdk.IdentityApi(api_client)
    artist_id = 'artist_id_example' # str | 
    match_id = 'match_id_example' # str | 

    try:
        # Get Identity Match Audit
        api_response = api_instance.get_identity_match_audit_artists_artist_id_identity_matches_match_id_audit_get(artist_id, match_id)
        print("The response of IdentityApi->get_identity_match_audit_artists_artist_id_identity_matches_match_id_audit_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling IdentityApi->get_identity_match_audit_artists_artist_id_identity_matches_match_id_audit_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **artist_id** | **str**|  | 
 **match_id** | **str**|  | 

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

# **list_identity_matches_artists_artist_id_identity_matches_get**
> Dict[str, object] list_identity_matches_artists_artist_id_identity_matches_get(artist_id)

List Identity Matches

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
    api_instance = xr7_sdk.IdentityApi(api_client)
    artist_id = 'artist_id_example' # str | 

    try:
        # List Identity Matches
        api_response = api_instance.list_identity_matches_artists_artist_id_identity_matches_get(artist_id)
        print("The response of IdentityApi->list_identity_matches_artists_artist_id_identity_matches_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling IdentityApi->list_identity_matches_artists_artist_id_identity_matches_get: %s\n" % e)
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

