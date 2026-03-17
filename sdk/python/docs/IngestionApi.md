# xr7_sdk.IngestionApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**connect_regional_global_artists_artist_id_connect_regional_global_post**](IngestionApi.md#connect_regional_global_artists_artist_id_connect_regional_global_post) | **POST** /artists/{artist_id}/connect/regional-global | Connect Regional Global
[**connect_soundexchange_mlc_artists_artist_id_connect_soundexchange_mlc_post**](IngestionApi.md#connect_soundexchange_mlc_artists_artist_id_connect_soundexchange_mlc_post) | **POST** /artists/{artist_id}/connect/soundexchange-mlc | Connect Soundexchange Mlc
[**get_statement_artists_artist_id_statements_statement_id_get**](IngestionApi.md#get_statement_artists_artist_id_statements_statement_id_get) | **GET** /artists/{artist_id}/statements/{statement_id} | Get Statement
[**list_statements_artists_artist_id_statements_get**](IngestionApi.md#list_statements_artists_artist_id_statements_get) | **GET** /artists/{artist_id}/statements | List Statements
[**regional_global_status_artists_artist_id_connect_regional_global_status_get**](IngestionApi.md#regional_global_status_artists_artist_id_connect_regional_global_status_get) | **GET** /artists/{artist_id}/connect/regional-global/status | Regional Global Status
[**soundexchange_mlc_status_artists_artist_id_connect_soundexchange_mlc_status_get**](IngestionApi.md#soundexchange_mlc_status_artists_artist_id_connect_soundexchange_mlc_status_get) | **GET** /artists/{artist_id}/connect/soundexchange-mlc/status | Soundexchange Mlc Status
[**supported_formats_ingestion_supported_formats_get**](IngestionApi.md#supported_formats_ingestion_supported_formats_get) | **GET** /ingestion/supported-formats | Supported Formats
[**upload_statement_artists_artist_id_statements_upload_post**](IngestionApi.md#upload_statement_artists_artist_id_statements_upload_post) | **POST** /artists/{artist_id}/statements/upload | Upload Statement
[**upload_statement_batch_artists_artist_id_statements_upload_batch_post**](IngestionApi.md#upload_statement_batch_artists_artist_id_statements_upload_batch_post) | **POST** /artists/{artist_id}/statements/upload-batch | Upload Statement Batch


# **connect_regional_global_artists_artist_id_connect_regional_global_post**
> object connect_regional_global_artists_artist_id_connect_regional_global_post(artist_id, genre=genre, territory=territory)

Connect Regional Global

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
    api_instance = xr7_sdk.IngestionApi(api_client)
    artist_id = 'artist_id_example' # str | 
    genre = 'latin' # str |  (optional) (default to 'latin')
    territory = 'LATAM' # str |  (optional) (default to 'LATAM')

    try:
        # Connect Regional Global
        api_response = api_instance.connect_regional_global_artists_artist_id_connect_regional_global_post(artist_id, genre=genre, territory=territory)
        print("The response of IngestionApi->connect_regional_global_artists_artist_id_connect_regional_global_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling IngestionApi->connect_regional_global_artists_artist_id_connect_regional_global_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **artist_id** | **str**|  | 
 **genre** | **str**|  | [optional] [default to &#39;latin&#39;]
 **territory** | **str**|  | [optional] [default to &#39;LATAM&#39;]

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

# **connect_soundexchange_mlc_artists_artist_id_connect_soundexchange_mlc_post**
> object connect_soundexchange_mlc_artists_artist_id_connect_soundexchange_mlc_post(artist_id, years_back=years_back)

Connect Soundexchange Mlc

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
    api_instance = xr7_sdk.IngestionApi(api_client)
    artist_id = 'artist_id_example' # str | 
    years_back = 10 # int |  (optional) (default to 10)

    try:
        # Connect Soundexchange Mlc
        api_response = api_instance.connect_soundexchange_mlc_artists_artist_id_connect_soundexchange_mlc_post(artist_id, years_back=years_back)
        print("The response of IngestionApi->connect_soundexchange_mlc_artists_artist_id_connect_soundexchange_mlc_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling IngestionApi->connect_soundexchange_mlc_artists_artist_id_connect_soundexchange_mlc_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **artist_id** | **str**|  | 
 **years_back** | **int**|  | [optional] [default to 10]

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

# **get_statement_artists_artist_id_statements_statement_id_get**
> StatementSchema get_statement_artists_artist_id_statements_statement_id_get(artist_id, statement_id)

Get Statement

Return details of a single statement upload.

### Example


```python
import xr7_sdk
from xr7_sdk.models.statement_schema import StatementSchema
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
    api_instance = xr7_sdk.IngestionApi(api_client)
    artist_id = 'artist_id_example' # str | 
    statement_id = 'statement_id_example' # str | 

    try:
        # Get Statement
        api_response = api_instance.get_statement_artists_artist_id_statements_statement_id_get(artist_id, statement_id)
        print("The response of IngestionApi->get_statement_artists_artist_id_statements_statement_id_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling IngestionApi->get_statement_artists_artist_id_statements_statement_id_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **artist_id** | **str**|  | 
 **statement_id** | **str**|  | 

### Return type

[**StatementSchema**](StatementSchema.md)

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

# **list_statements_artists_artist_id_statements_get**
> List[StatementSchema] list_statements_artists_artist_id_statements_get(artist_id)

List Statements

Return all statement uploads for an artist, newest first.

### Example


```python
import xr7_sdk
from xr7_sdk.models.statement_schema import StatementSchema
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
    api_instance = xr7_sdk.IngestionApi(api_client)
    artist_id = 'artist_id_example' # str | 

    try:
        # List Statements
        api_response = api_instance.list_statements_artists_artist_id_statements_get(artist_id)
        print("The response of IngestionApi->list_statements_artists_artist_id_statements_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling IngestionApi->list_statements_artists_artist_id_statements_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **artist_id** | **str**|  | 

### Return type

[**List[StatementSchema]**](StatementSchema.md)

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

# **regional_global_status_artists_artist_id_connect_regional_global_status_get**
> object regional_global_status_artists_artist_id_connect_regional_global_status_get(artist_id)

Regional Global Status

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
    api_instance = xr7_sdk.IngestionApi(api_client)
    artist_id = 'artist_id_example' # str | 

    try:
        # Regional Global Status
        api_response = api_instance.regional_global_status_artists_artist_id_connect_regional_global_status_get(artist_id)
        print("The response of IngestionApi->regional_global_status_artists_artist_id_connect_regional_global_status_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling IngestionApi->regional_global_status_artists_artist_id_connect_regional_global_status_get: %s\n" % e)
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

# **soundexchange_mlc_status_artists_artist_id_connect_soundexchange_mlc_status_get**
> object soundexchange_mlc_status_artists_artist_id_connect_soundexchange_mlc_status_get(artist_id)

Soundexchange Mlc Status

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
    api_instance = xr7_sdk.IngestionApi(api_client)
    artist_id = 'artist_id_example' # str | 

    try:
        # Soundexchange Mlc Status
        api_response = api_instance.soundexchange_mlc_status_artists_artist_id_connect_soundexchange_mlc_status_get(artist_id)
        print("The response of IngestionApi->soundexchange_mlc_status_artists_artist_id_connect_soundexchange_mlc_status_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling IngestionApi->soundexchange_mlc_status_artists_artist_id_connect_soundexchange_mlc_status_get: %s\n" % e)
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

# **supported_formats_ingestion_supported_formats_get**
> Dict[str, object] supported_formats_ingestion_supported_formats_get()

Supported Formats

Return the complete list of explicitly supported royalty statement
formats, grouped by type (distributor, PRO, DSP, generic).

For each format the response includes:
- ``name`` — human-readable distributor/PRO name
- ``type`` — ``"distributor"`` | ``"pro"`` | ``"dsp"`` | ``"generic"``
- ``key_columns`` — representative column headers from that format's CSV
- ``description`` — how to obtain the file and what it covers

Any file that does not match an explicit format is handled by the
``"generic"`` fallback, which recognises any file with recognisable date,
source, quantity, and amount columns.  This covers distributors such as
Songtradr, Vydia, AWAL, Symphonic, INgrooves, Believe, Kobalt, and others.

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
    api_instance = xr7_sdk.IngestionApi(api_client)

    try:
        # Supported Formats
        api_response = api_instance.supported_formats_ingestion_supported_formats_get()
        print("The response of IngestionApi->supported_formats_ingestion_supported_formats_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling IngestionApi->supported_formats_ingestion_supported_formats_get: %s\n" % e)
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

# **upload_statement_artists_artist_id_statements_upload_post**
> StatementSchema upload_statement_artists_artist_id_statements_upload_post(artist_id, file)

Upload Statement

Upload a royalty statement file and ingest it into the database.

Supported formats are automatically detected from the column headers:
    **DistroKid**, **TuneCore**, **CD Baby**, **ASCAP**, **BMI**,
    **Spotify for Artists**, **SoundCloud**, and a **generic** fallback for any statement with
recognisable date / amount / quantity columns.

After ingestion, anomaly detection is run automatically so that any
under-payment issues are immediately flagged.

Returns a :class:`~XR7.models.statement.Statement` record summarising
what was parsed and saved.

**Requires prior acceptance of the Artist Recovery Services Agreement.**
Call ``GET /terms`` to read the agreement and
``POST /artists/{artist_id}/terms/accept`` to accept it.  This endpoint
returns HTTP 403 until the artist has agreed to the terms.

### Example


```python
import xr7_sdk
from xr7_sdk.models.statement_schema import StatementSchema
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
    api_instance = xr7_sdk.IngestionApi(api_client)
    artist_id = 'artist_id_example' # str | 
    file = 'file_example' # str | 

    try:
        # Upload Statement
        api_response = api_instance.upload_statement_artists_artist_id_statements_upload_post(artist_id, file)
        print("The response of IngestionApi->upload_statement_artists_artist_id_statements_upload_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling IngestionApi->upload_statement_artists_artist_id_statements_upload_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **artist_id** | **str**|  | 
 **file** | **str**|  | 

### Return type

[**StatementSchema**](StatementSchema.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: multipart/form-data
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **upload_statement_batch_artists_artist_id_statements_upload_batch_post**
> object upload_statement_batch_artists_artist_id_statements_upload_batch_post(artist_id, files)

Upload Statement Batch

Upload and process a batch of statement files (CSV/ZIP/PDF) with malware scanning and parallel parsing.

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
    api_instance = xr7_sdk.IngestionApi(api_client)
    artist_id = 'artist_id_example' # str | 
    files = ['files_example'] # List[str] | 

    try:
        # Upload Statement Batch
        api_response = api_instance.upload_statement_batch_artists_artist_id_statements_upload_batch_post(artist_id, files)
        print("The response of IngestionApi->upload_statement_batch_artists_artist_id_statements_upload_batch_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling IngestionApi->upload_statement_batch_artists_artist_id_statements_upload_batch_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **artist_id** | **str**|  | 
 **files** | [**List[str]**](str.md)|  | 

### Return type

**object**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: multipart/form-data
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

