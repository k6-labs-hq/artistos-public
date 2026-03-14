# xr7_sdk.ClaimsApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**advance_claim_claims_claim_id_advance_post**](ClaimsApi.md#advance_claim_claims_claim_id_advance_post) | **POST** /claims/{claim_id}/advance | Advance Claim
[**export_evidence_packet_claims_claim_id_evidence_export_get**](ClaimsApi.md#export_evidence_packet_claims_claim_id_evidence_export_get) | **GET** /claims/{claim_id}/evidence/export | Export Evidence Packet
[**generate_evidence_claims_claim_id_evidence_post**](ClaimsApi.md#generate_evidence_claims_claim_id_evidence_post) | **POST** /claims/{claim_id}/evidence | Generate Evidence
[**get_claim_claims_claim_id_get**](ClaimsApi.md#get_claim_claims_claim_id_get) | **GET** /claims/{claim_id} | Get Claim
[**list_claims_artists_artist_id_claims_get**](ClaimsApi.md#list_claims_artists_artist_id_claims_get) | **GET** /artists/{artist_id}/claims | List Claims
[**reconcile_claim_claims_claim_id_reconcile_post**](ClaimsApi.md#reconcile_claim_claims_claim_id_reconcile_post) | **POST** /claims/{claim_id}/reconcile | Reconcile Claim
[**verify_evidence_packet_claims_claim_id_evidence_verify_get**](ClaimsApi.md#verify_evidence_packet_claims_claim_id_evidence_verify_get) | **GET** /claims/{claim_id}/evidence/verify | Verify Evidence Packet


# **advance_claim_claims_claim_id_advance_post**
> ClaimSchema advance_claim_claims_claim_id_advance_post(claim_id)

Advance Claim

### Example


```python
import xr7_sdk
from xr7_sdk.models.claim_schema import ClaimSchema
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
    api_instance = xr7_sdk.ClaimsApi(api_client)
    claim_id = 'claim_id_example' # str | 

    try:
        # Advance Claim
        api_response = api_instance.advance_claim_claims_claim_id_advance_post(claim_id)
        print("The response of ClaimsApi->advance_claim_claims_claim_id_advance_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ClaimsApi->advance_claim_claims_claim_id_advance_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **claim_id** | **str**|  | 

### Return type

[**ClaimSchema**](ClaimSchema.md)

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

# **export_evidence_packet_claims_claim_id_evidence_export_get**
> object export_evidence_packet_claims_claim_id_evidence_export_get(claim_id, format=format, refresh=refresh)

Export Evidence Packet

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
    api_instance = xr7_sdk.ClaimsApi(api_client)
    claim_id = 'claim_id_example' # str | 
    format = 'zip' # str |  (optional) (default to 'zip')
    refresh = False # bool |  (optional) (default to False)

    try:
        # Export Evidence Packet
        api_response = api_instance.export_evidence_packet_claims_claim_id_evidence_export_get(claim_id, format=format, refresh=refresh)
        print("The response of ClaimsApi->export_evidence_packet_claims_claim_id_evidence_export_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ClaimsApi->export_evidence_packet_claims_claim_id_evidence_export_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **claim_id** | **str**|  | 
 **format** | **str**|  | [optional] [default to &#39;zip&#39;]
 **refresh** | **bool**|  | [optional] [default to False]

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

# **generate_evidence_claims_claim_id_evidence_post**
> object generate_evidence_claims_claim_id_evidence_post(claim_id)

Generate Evidence

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
    api_instance = xr7_sdk.ClaimsApi(api_client)
    claim_id = 'claim_id_example' # str | 

    try:
        # Generate Evidence
        api_response = api_instance.generate_evidence_claims_claim_id_evidence_post(claim_id)
        print("The response of ClaimsApi->generate_evidence_claims_claim_id_evidence_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ClaimsApi->generate_evidence_claims_claim_id_evidence_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **claim_id** | **str**|  | 

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

# **get_claim_claims_claim_id_get**
> ClaimSchema get_claim_claims_claim_id_get(claim_id)

Get Claim

### Example


```python
import xr7_sdk
from xr7_sdk.models.claim_schema import ClaimSchema
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
    api_instance = xr7_sdk.ClaimsApi(api_client)
    claim_id = 'claim_id_example' # str | 

    try:
        # Get Claim
        api_response = api_instance.get_claim_claims_claim_id_get(claim_id)
        print("The response of ClaimsApi->get_claim_claims_claim_id_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ClaimsApi->get_claim_claims_claim_id_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **claim_id** | **str**|  | 

### Return type

[**ClaimSchema**](ClaimSchema.md)

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

# **list_claims_artists_artist_id_claims_get**
> object list_claims_artists_artist_id_claims_get(artist_id)

List Claims

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
    api_instance = xr7_sdk.ClaimsApi(api_client)
    artist_id = 'artist_id_example' # str | 

    try:
        # List Claims
        api_response = api_instance.list_claims_artists_artist_id_claims_get(artist_id)
        print("The response of ClaimsApi->list_claims_artists_artist_id_claims_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ClaimsApi->list_claims_artists_artist_id_claims_get: %s\n" % e)
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

# **reconcile_claim_claims_claim_id_reconcile_post**
> ClaimSchema reconcile_claim_claims_claim_id_reconcile_post(claim_id, reconcile_request)

Reconcile Claim

### Example


```python
import xr7_sdk
from xr7_sdk.models.claim_schema import ClaimSchema
from xr7_sdk.models.reconcile_request import ReconcileRequest
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
    api_instance = xr7_sdk.ClaimsApi(api_client)
    claim_id = 'claim_id_example' # str | 
    reconcile_request = xr7_sdk.ReconcileRequest() # ReconcileRequest | 

    try:
        # Reconcile Claim
        api_response = api_instance.reconcile_claim_claims_claim_id_reconcile_post(claim_id, reconcile_request)
        print("The response of ClaimsApi->reconcile_claim_claims_claim_id_reconcile_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ClaimsApi->reconcile_claim_claims_claim_id_reconcile_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **claim_id** | **str**|  | 
 **reconcile_request** | [**ReconcileRequest**](ReconcileRequest.md)|  | 

### Return type

[**ClaimSchema**](ClaimSchema.md)

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

# **verify_evidence_packet_claims_claim_id_evidence_verify_get**
> object verify_evidence_packet_claims_claim_id_evidence_verify_get(claim_id, expected_prior_packet_hash=expected_prior_packet_hash)

Verify Evidence Packet

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
    api_instance = xr7_sdk.ClaimsApi(api_client)
    claim_id = 'claim_id_example' # str | 
    expected_prior_packet_hash = 'expected_prior_packet_hash_example' # str |  (optional)

    try:
        # Verify Evidence Packet
        api_response = api_instance.verify_evidence_packet_claims_claim_id_evidence_verify_get(claim_id, expected_prior_packet_hash=expected_prior_packet_hash)
        print("The response of ClaimsApi->verify_evidence_packet_claims_claim_id_evidence_verify_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ClaimsApi->verify_evidence_packet_claims_claim_id_evidence_verify_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **claim_id** | **str**|  | 
 **expected_prior_packet_hash** | **str**|  | [optional] 

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

