# xr7_sdk.IdentityApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**auto_match_identity_artists_artist_id_identity_auto_match_post**](IdentityApi.md#auto_match_identity_artists_artist_id_identity_auto_match_post) | **POST** /artists/{artist_id}/identity/auto-match | Auto Match Identity
[**decide_identity_match_artists_artist_id_identity_matches_match_id_decision_post**](IdentityApi.md#decide_identity_match_artists_artist_id_identity_matches_match_id_decision_post) | **POST** /artists/{artist_id}/identity/matches/{match_id}/decision | Decide Identity Match
[**get_identity_match_audit_artists_artist_id_identity_matches_match_id_audit_get**](IdentityApi.md#get_identity_match_audit_artists_artist_id_identity_matches_match_id_audit_get) | **GET** /artists/{artist_id}/identity/matches/{match_id}/audit | Get Identity Match Audit
[**list_identity_matches_artists_artist_id_identity_matches_get**](IdentityApi.md#list_identity_matches_artists_artist_id_identity_matches_get) | **GET** /artists/{artist_id}/identity/matches | List Identity Matches


# **auto_match_identity_artists_artist_id_identity_auto_match_post**
> ArtistIdentityMatchSchema auto_match_identity_artists_artist_id_identity_auto_match_post(artist_id, identity_match_request, authorization=authorization)

Auto Match Identity

### Example


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


# Enter a context with an instance of the API client
with xr7_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = xr7_sdk.IdentityApi(api_client)
    artist_id = 'artist_id_example' # str | 
    identity_match_request = xr7_sdk.IdentityMatchRequest() # IdentityMatchRequest | 
    authorization = 'authorization_example' # str |  (optional)

    try:
        # Auto Match Identity
        api_response = api_instance.auto_match_identity_artists_artist_id_identity_auto_match_post(artist_id, identity_match_request, authorization=authorization)
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
 **authorization** | **str**|  | [optional] 

### Return type

[**ArtistIdentityMatchSchema**](ArtistIdentityMatchSchema.md)

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

# **decide_identity_match_artists_artist_id_identity_matches_match_id_decision_post**
> ArtistIdentityMatchSchema decide_identity_match_artists_artist_id_identity_matches_match_id_decision_post(artist_id, match_id, identity_decision_request, authorization=authorization)

Decide Identity Match

### Example


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


# Enter a context with an instance of the API client
with xr7_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = xr7_sdk.IdentityApi(api_client)
    artist_id = 'artist_id_example' # str | 
    match_id = 'match_id_example' # str | 
    identity_decision_request = xr7_sdk.IdentityDecisionRequest() # IdentityDecisionRequest | 
    authorization = 'authorization_example' # str |  (optional)

    try:
        # Decide Identity Match
        api_response = api_instance.decide_identity_match_artists_artist_id_identity_matches_match_id_decision_post(artist_id, match_id, identity_decision_request, authorization=authorization)
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
 **authorization** | **str**|  | [optional] 

### Return type

[**ArtistIdentityMatchSchema**](ArtistIdentityMatchSchema.md)

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

# **get_identity_match_audit_artists_artist_id_identity_matches_match_id_audit_get**
> Dict[str, object] get_identity_match_audit_artists_artist_id_identity_matches_match_id_audit_get(artist_id, match_id, authorization=authorization)

Get Identity Match Audit

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
    api_instance = xr7_sdk.IdentityApi(api_client)
    artist_id = 'artist_id_example' # str | 
    match_id = 'match_id_example' # str | 
    authorization = 'authorization_example' # str |  (optional)

    try:
        # Get Identity Match Audit
        api_response = api_instance.get_identity_match_audit_artists_artist_id_identity_matches_match_id_audit_get(artist_id, match_id, authorization=authorization)
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
 **authorization** | **str**|  | [optional] 

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

# **list_identity_matches_artists_artist_id_identity_matches_get**
> Dict[str, object] list_identity_matches_artists_artist_id_identity_matches_get(artist_id, authorization=authorization)

List Identity Matches

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
    api_instance = xr7_sdk.IdentityApi(api_client)
    artist_id = 'artist_id_example' # str | 
    authorization = 'authorization_example' # str |  (optional)

    try:
        # List Identity Matches
        api_response = api_instance.list_identity_matches_artists_artist_id_identity_matches_get(artist_id, authorization=authorization)
        print("The response of IdentityApi->list_identity_matches_artists_artist_id_identity_matches_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling IdentityApi->list_identity_matches_artists_artist_id_identity_matches_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **artist_id** | **str**|  | 
 **authorization** | **str**|  | [optional] 

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

