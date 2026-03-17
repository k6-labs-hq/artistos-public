# xr7_sdk.TeamApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**network_invite_artists_artist_id_network_invite_post**](TeamApi.md#network_invite_artists_artist_id_network_invite_post) | **POST** /artists/{artist_id}/network/invite | Network Invite


# **network_invite_artists_artist_id_network_invite_post**
> object network_invite_artists_artist_id_network_invite_post(artist_id, invite_request)

Network Invite

### Example


```python
import xr7_sdk
from xr7_sdk.models.invite_request import InviteRequest
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
    api_instance = xr7_sdk.TeamApi(api_client)
    artist_id = 'artist_id_example' # str | 
    invite_request = xr7_sdk.InviteRequest() # InviteRequest | 

    try:
        # Network Invite
        api_response = api_instance.network_invite_artists_artist_id_network_invite_post(artist_id, invite_request)
        print("The response of TeamApi->network_invite_artists_artist_id_network_invite_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TeamApi->network_invite_artists_artist_id_network_invite_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **artist_id** | **str**|  | 
 **invite_request** | [**InviteRequest**](InviteRequest.md)|  | 

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

