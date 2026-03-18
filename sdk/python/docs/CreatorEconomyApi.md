# xr7_sdk.CreatorEconomyApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**ingest_creator_data_artists_artist_id_creator_ingest_post**](CreatorEconomyApi.md#ingest_creator_data_artists_artist_id_creator_ingest_post) | **POST** /artists/{artist_id}/creator/ingest | Ingest Creator Data
[**list_creator_platforms_artists_artist_id_creator_platforms_get**](CreatorEconomyApi.md#list_creator_platforms_artists_artist_id_creator_platforms_get) | **GET** /artists/{artist_id}/creator/platforms | List Creator Platforms


# **ingest_creator_data_artists_artist_id_creator_ingest_post**
> Dict[str, object] ingest_creator_data_artists_artist_id_creator_ingest_post(artist_id, creator_ingest_request)

Ingest Creator Data

Parse and anomaly-scan creator-economy platform data.

Accepts raw export rows from YouTube Studio, TikTok, Instagram Reels,
Twitch, Patreon, or Shopify. Returns parsed events and detected anomalies.

### Example

* Bearer Authentication (HTTPBearer):

```python
import xr7_sdk
from xr7_sdk.models.creator_ingest_request import CreatorIngestRequest
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
    api_instance = xr7_sdk.CreatorEconomyApi(api_client)
    artist_id = 'artist_id_example' # str | 
    creator_ingest_request = xr7_sdk.CreatorIngestRequest() # CreatorIngestRequest | 

    try:
        # Ingest Creator Data
        api_response = api_instance.ingest_creator_data_artists_artist_id_creator_ingest_post(artist_id, creator_ingest_request)
        print("The response of CreatorEconomyApi->ingest_creator_data_artists_artist_id_creator_ingest_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling CreatorEconomyApi->ingest_creator_data_artists_artist_id_creator_ingest_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **artist_id** | **str**|  | 
 **creator_ingest_request** | [**CreatorIngestRequest**](CreatorIngestRequest.md)|  | 

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

# **list_creator_platforms_artists_artist_id_creator_platforms_get**
> Dict[str, object] list_creator_platforms_artists_artist_id_creator_platforms_get(artist_id)

List Creator Platforms

List all supported creator-economy platforms.

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
    api_instance = xr7_sdk.CreatorEconomyApi(api_client)
    artist_id = 'artist_id_example' # str | 

    try:
        # List Creator Platforms
        api_response = api_instance.list_creator_platforms_artists_artist_id_creator_platforms_get(artist_id)
        print("The response of CreatorEconomyApi->list_creator_platforms_artists_artist_id_creator_platforms_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling CreatorEconomyApi->list_creator_platforms_artists_artist_id_creator_platforms_get: %s\n" % e)
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

