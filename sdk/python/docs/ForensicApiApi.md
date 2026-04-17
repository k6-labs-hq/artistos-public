# xr7_sdk.ForensicApiApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**auth_connect_auth_connect_provider_post**](ForensicApiApi.md#auth_connect_auth_connect_provider_post) | **POST** /auth/connect/{provider} | Auth Connect
[**auth_providers_auth_providers_get**](ForensicApiApi.md#auth_providers_auth_providers_get) | **GET** /auth/providers | Auth Providers
[**confirm_catalog_catalog_confirm_post**](ForensicApiApi.md#confirm_catalog_catalog_confirm_post) | **POST** /catalog/confirm | Confirm Catalog
[**get_catalog_catalog_get**](ForensicApiApi.md#get_catalog_catalog_get) | **GET** /catalog | Get Catalog
[**get_ledger_entry_ledger_entry_id_get**](ForensicApiApi.md#get_ledger_entry_ledger_entry_id_get) | **GET** /ledger/{entry_id} | Get Ledger Entry
[**list_ledger_ledger_get**](ForensicApiApi.md#list_ledger_ledger_get) | **GET** /ledger | List Ledger
[**list_variance_variance_get**](ForensicApiApi.md#list_variance_variance_get) | **GET** /variance | List Variance
[**recovery_submit_recovery_claim_id_submit_post**](ForensicApiApi.md#recovery_submit_recovery_claim_id_submit_post) | **POST** /recovery/{claim_id}/submit | Recovery Submit
[**statements_status_statements_statement_id_status_get**](ForensicApiApi.md#statements_status_statements_statement_id_status_get) | **GET** /statements/{statement_id}/status | Statements Status
[**statements_upload_statements_upload_post**](ForensicApiApi.md#statements_upload_statements_upload_post) | **POST** /statements/upload | Statements Upload
[**variance_evidence_variance_variance_id_evidence_get**](ForensicApiApi.md#variance_evidence_variance_variance_id_evidence_get) | **GET** /variance/{variance_id}/evidence | Variance Evidence


# **auth_connect_auth_connect_provider_post**
> AuthConnectResponse auth_connect_auth_connect_provider_post(provider, redirect_uri)

Auth Connect

### Example


```python
import xr7_sdk
from xr7_sdk.models.auth_connect_response import AuthConnectResponse
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
    api_instance = xr7_sdk.ForensicApiApi(api_client)
    provider = 'provider_example' # str |
    redirect_uri = 'redirect_uri_example' # str |

    try:
        # Auth Connect
        api_response = api_instance.auth_connect_auth_connect_provider_post(provider, redirect_uri)
        print("The response of ForensicApiApi->auth_connect_auth_connect_provider_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ForensicApiApi->auth_connect_auth_connect_provider_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **provider** | **str**|  |
 **redirect_uri** | **str**|  |

### Return type

[**AuthConnectResponse**](AuthConnectResponse.md)

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

# **auth_providers_auth_providers_get**
> Dict[str, List[Dict[str, object]]] auth_providers_auth_providers_get()

Auth Providers

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
    api_instance = xr7_sdk.ForensicApiApi(api_client)

    try:
        # Auth Providers
        api_response = api_instance.auth_providers_auth_providers_get()
        print("The response of ForensicApiApi->auth_providers_auth_providers_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ForensicApiApi->auth_providers_auth_providers_get: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

**Dict[str, List[Dict[str, object]]]**

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

# **confirm_catalog_catalog_confirm_post**
> object confirm_catalog_catalog_confirm_post(xr7_api_routers_forensic_catalog_confirm_request)

Confirm Catalog

### Example


```python
import xr7_sdk
from xr7_sdk.models.xr7_api_routers_forensic_catalog_confirm_request import XR7ApiRoutersForensicCatalogConfirmRequest
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
    api_instance = xr7_sdk.ForensicApiApi(api_client)
    xr7_api_routers_forensic_catalog_confirm_request = xr7_sdk.XR7ApiRoutersForensicCatalogConfirmRequest() # XR7ApiRoutersForensicCatalogConfirmRequest |

    try:
        # Confirm Catalog
        api_response = api_instance.confirm_catalog_catalog_confirm_post(xr7_api_routers_forensic_catalog_confirm_request)
        print("The response of ForensicApiApi->confirm_catalog_catalog_confirm_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ForensicApiApi->confirm_catalog_catalog_confirm_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **xr7_api_routers_forensic_catalog_confirm_request** | [**XR7ApiRoutersForensicCatalogConfirmRequest**](XR7ApiRoutersForensicCatalogConfirmRequest.md)|  |

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

# **get_catalog_catalog_get**
> object get_catalog_catalog_get(artist_id)

Get Catalog

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
    api_instance = xr7_sdk.ForensicApiApi(api_client)
    artist_id = 'artist_id_example' # str |

    try:
        # Get Catalog
        api_response = api_instance.get_catalog_catalog_get(artist_id)
        print("The response of ForensicApiApi->get_catalog_catalog_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ForensicApiApi->get_catalog_catalog_get: %s\n" % e)
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

# **get_ledger_entry_ledger_entry_id_get**
> ImmutableLedgerEntrySchema get_ledger_entry_ledger_entry_id_get(entry_id)

Get Ledger Entry

### Example


```python
import xr7_sdk
from xr7_sdk.models.immutable_ledger_entry_schema import ImmutableLedgerEntrySchema
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
    api_instance = xr7_sdk.ForensicApiApi(api_client)
    entry_id = 'entry_id_example' # str |

    try:
        # Get Ledger Entry
        api_response = api_instance.get_ledger_entry_ledger_entry_id_get(entry_id)
        print("The response of ForensicApiApi->get_ledger_entry_ledger_entry_id_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ForensicApiApi->get_ledger_entry_ledger_entry_id_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **entry_id** | **str**|  |

### Return type

[**ImmutableLedgerEntrySchema**](ImmutableLedgerEntrySchema.md)

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

# **list_ledger_ledger_get**
> List[ImmutableLedgerEntrySchema] list_ledger_ledger_get(artist_id)

List Ledger

### Example


```python
import xr7_sdk
from xr7_sdk.models.immutable_ledger_entry_schema import ImmutableLedgerEntrySchema
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
    api_instance = xr7_sdk.ForensicApiApi(api_client)
    artist_id = 'artist_id_example' # str |

    try:
        # List Ledger
        api_response = api_instance.list_ledger_ledger_get(artist_id)
        print("The response of ForensicApiApi->list_ledger_ledger_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ForensicApiApi->list_ledger_ledger_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **artist_id** | **str**|  |

### Return type

[**List[ImmutableLedgerEntrySchema]**](ImmutableLedgerEntrySchema.md)

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

# **list_variance_variance_get**
> object list_variance_variance_get(artist_id)

List Variance

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
    api_instance = xr7_sdk.ForensicApiApi(api_client)
    artist_id = 'artist_id_example' # str |

    try:
        # List Variance
        api_response = api_instance.list_variance_variance_get(artist_id)
        print("The response of ForensicApiApi->list_variance_variance_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ForensicApiApi->list_variance_variance_get: %s\n" % e)
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

# **recovery_submit_recovery_claim_id_submit_post**
> RecoverySubmitResponse recovery_submit_recovery_claim_id_submit_post(claim_id)

Recovery Submit

### Example


```python
import xr7_sdk
from xr7_sdk.models.recovery_submit_response import RecoverySubmitResponse
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
    api_instance = xr7_sdk.ForensicApiApi(api_client)
    claim_id = 'claim_id_example' # str |

    try:
        # Recovery Submit
        api_response = api_instance.recovery_submit_recovery_claim_id_submit_post(claim_id)
        print("The response of ForensicApiApi->recovery_submit_recovery_claim_id_submit_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ForensicApiApi->recovery_submit_recovery_claim_id_submit_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **claim_id** | **str**|  |

### Return type

[**RecoverySubmitResponse**](RecoverySubmitResponse.md)

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

# **statements_status_statements_statement_id_status_get**
> object statements_status_statements_statement_id_status_get(statement_id)

Statements Status

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
    api_instance = xr7_sdk.ForensicApiApi(api_client)
    statement_id = 'statement_id_example' # str |

    try:
        # Statements Status
        api_response = api_instance.statements_status_statements_statement_id_status_get(statement_id)
        print("The response of ForensicApiApi->statements_status_statements_statement_id_status_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ForensicApiApi->statements_status_statements_statement_id_status_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **statement_id** | **str**|  |

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

# **statements_upload_statements_upload_post**
> ForensicUniversalRoyaltyEventSchema statements_upload_statements_upload_post(forensic_universal_royalty_event_create)

Statements Upload

Minimal statement upload endpoint that stores a normalized universal event row.

### Example


```python
import xr7_sdk
from xr7_sdk.models.forensic_universal_royalty_event_create import ForensicUniversalRoyaltyEventCreate
from xr7_sdk.models.forensic_universal_royalty_event_schema import ForensicUniversalRoyaltyEventSchema
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
    api_instance = xr7_sdk.ForensicApiApi(api_client)
    forensic_universal_royalty_event_create = xr7_sdk.ForensicUniversalRoyaltyEventCreate() # ForensicUniversalRoyaltyEventCreate |

    try:
        # Statements Upload
        api_response = api_instance.statements_upload_statements_upload_post(forensic_universal_royalty_event_create)
        print("The response of ForensicApiApi->statements_upload_statements_upload_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ForensicApiApi->statements_upload_statements_upload_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **forensic_universal_royalty_event_create** | [**ForensicUniversalRoyaltyEventCreate**](ForensicUniversalRoyaltyEventCreate.md)|  |

### Return type

[**ForensicUniversalRoyaltyEventSchema**](ForensicUniversalRoyaltyEventSchema.md)

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

# **variance_evidence_variance_variance_id_evidence_get**
> object variance_evidence_variance_variance_id_evidence_get(variance_id)

Variance Evidence

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
    api_instance = xr7_sdk.ForensicApiApi(api_client)
    variance_id = 'variance_id_example' # str |

    try:
        # Variance Evidence
        api_response = api_instance.variance_evidence_variance_variance_id_evidence_get(variance_id)
        print("The response of ForensicApiApi->variance_evidence_variance_variance_id_evidence_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ForensicApiApi->variance_evidence_variance_variance_id_evidence_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **variance_id** | **str**|  |

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
