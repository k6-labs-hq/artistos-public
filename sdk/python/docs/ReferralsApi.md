# xr7_sdk.ReferralsApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_referrals_artists_artist_id_referrals_get**](ReferralsApi.md#get_referrals_artists_artist_id_referrals_get) | **GET** /artists/{artist_id}/referrals | Get Referrals
[**register_referral_artists_artist_id_referrals_post**](ReferralsApi.md#register_referral_artists_artist_id_referrals_post) | **POST** /artists/{artist_id}/referrals | Register Referral


# **get_referrals_artists_artist_id_referrals_get**
> Dict[str, object] get_referrals_artists_artist_id_referrals_get(artist_id)

Get Referrals

Return the referral tree and lifetime earnings for this artist.

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
    api_instance = xr7_sdk.ReferralsApi(api_client)
    artist_id = 'artist_id_example' # str | 

    try:
        # Get Referrals
        api_response = api_instance.get_referrals_artists_artist_id_referrals_get(artist_id)
        print("The response of ReferralsApi->get_referrals_artists_artist_id_referrals_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ReferralsApi->get_referrals_artists_artist_id_referrals_get: %s\n" % e)
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

# **register_referral_artists_artist_id_referrals_post**
> Dict[str, object] register_referral_artists_artist_id_referrals_post(artist_id, referral_request)

Register Referral

Register a new artist referral link.

The referrer earns a percentage of the referred artist's net recoveries.

### Example

* Bearer Authentication (HTTPBearer):

```python
import xr7_sdk
from xr7_sdk.models.referral_request import ReferralRequest
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
    api_instance = xr7_sdk.ReferralsApi(api_client)
    artist_id = 'artist_id_example' # str | 
    referral_request = xr7_sdk.ReferralRequest() # ReferralRequest | 

    try:
        # Register Referral
        api_response = api_instance.register_referral_artists_artist_id_referrals_post(artist_id, referral_request)
        print("The response of ReferralsApi->register_referral_artists_artist_id_referrals_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ReferralsApi->register_referral_artists_artist_id_referrals_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **artist_id** | **str**|  | 
 **referral_request** | [**ReferralRequest**](ReferralRequest.md)|  | 

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

