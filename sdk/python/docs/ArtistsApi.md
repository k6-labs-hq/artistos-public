# xr7_sdk.ArtistsApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**artist_summary_artists_artist_id_summary_get**](ArtistsApi.md#artist_summary_artists_artist_id_summary_get) | **GET** /artists/{artist_id}/summary | Artist Summary
[**catalog_health_artists_artist_id_ml_catalog_health_get**](ArtistsApi.md#catalog_health_artists_artist_id_ml_catalog_health_get) | **GET** /artists/{artist_id}/ml/catalog-health | Catalog Health
[**connect_artist_artists_artist_id_connect_post**](ArtistsApi.md#connect_artist_artists_artist_id_connect_post) | **POST** /artists/{artist_id}/connect | Connect Artist
[**create_artist_artists_post**](ArtistsApi.md#create_artist_artists_post) | **POST** /artists/ | Create Artist
[**get_artist_artists_artist_id_get**](ArtistsApi.md#get_artist_artists_artist_id_get) | **GET** /artists/{artist_id} | Get Artist


# **artist_summary_artists_artist_id_summary_get**
> object artist_summary_artists_artist_id_summary_get(artist_id)

Artist Summary

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
    api_instance = xr7_sdk.ArtistsApi(api_client)
    artist_id = 'artist_id_example' # str | 

    try:
        # Artist Summary
        api_response = api_instance.artist_summary_artists_artist_id_summary_get(artist_id)
        print("The response of ArtistsApi->artist_summary_artists_artist_id_summary_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ArtistsApi->artist_summary_artists_artist_id_summary_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **artist_id** | **str**|  | 

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

# **catalog_health_artists_artist_id_ml_catalog_health_get**
> object catalog_health_artists_artist_id_ml_catalog_health_get(artist_id)

Catalog Health

Return an ML-derived catalog health score (0–100) and grade for the artist.

Combines metadata completeness, payment regularity, anomaly density,
recovery rate, and earnings accuracy into a single composite score.

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
    api_instance = xr7_sdk.ArtistsApi(api_client)
    artist_id = 'artist_id_example' # str | 

    try:
        # Catalog Health
        api_response = api_instance.catalog_health_artists_artist_id_ml_catalog_health_get(artist_id)
        print("The response of ArtistsApi->catalog_health_artists_artist_id_ml_catalog_health_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ArtistsApi->catalog_health_artists_artist_id_ml_catalog_health_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **artist_id** | **str**|  | 

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

# **connect_artist_artists_artist_id_connect_post**
> object connect_artist_artists_artist_id_connect_post(artist_id)

Connect Artist

Check which data connectors are configured for this artist and return
their credential status.

This endpoint validates that the required environment variables are set
for each connector.  It does NOT make real API calls — it only confirms
that the credentials are present and the connector is ready to use.

For connectors that are not yet configured, use the statement file upload
workflow: POST /artists/{artist_id}/statements/upload

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
    api_instance = xr7_sdk.ArtistsApi(api_client)
    artist_id = 'artist_id_example' # str | 

    try:
        # Connect Artist
        api_response = api_instance.connect_artist_artists_artist_id_connect_post(artist_id)
        print("The response of ArtistsApi->connect_artist_artists_artist_id_connect_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ArtistsApi->connect_artist_artists_artist_id_connect_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **artist_id** | **str**|  | 

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

# **create_artist_artists_post**
> ArtistSchema create_artist_artists_post(artist_create)

Create Artist

### Example


```python
import xr7_sdk
from xr7_sdk.models.artist_create import ArtistCreate
from xr7_sdk.models.artist_schema import ArtistSchema
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
    api_instance = xr7_sdk.ArtistsApi(api_client)
    artist_create = xr7_sdk.ArtistCreate() # ArtistCreate | 

    try:
        # Create Artist
        api_response = api_instance.create_artist_artists_post(artist_create)
        print("The response of ArtistsApi->create_artist_artists_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ArtistsApi->create_artist_artists_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **artist_create** | [**ArtistCreate**](ArtistCreate.md)|  | 

### Return type

[**ArtistSchema**](ArtistSchema.md)

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

# **get_artist_artists_artist_id_get**
> ArtistSchema get_artist_artists_artist_id_get(artist_id)

Get Artist

### Example


```python
import xr7_sdk
from xr7_sdk.models.artist_schema import ArtistSchema
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
    api_instance = xr7_sdk.ArtistsApi(api_client)
    artist_id = 'artist_id_example' # str | 

    try:
        # Get Artist
        api_response = api_instance.get_artist_artists_artist_id_get(artist_id)
        print("The response of ArtistsApi->get_artist_artists_artist_id_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ArtistsApi->get_artist_artists_artist_id_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **artist_id** | **str**|  | 

### Return type

[**ArtistSchema**](ArtistSchema.md)

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

