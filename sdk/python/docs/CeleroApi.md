# xr7_sdk.CeleroApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**celero_webhook_celero_webhook_post**](CeleroApi.md#celero_webhook_celero_webhook_post) | **POST** /celero/webhook | Celero Webhook
[**charge_contingency_fee_artists_artist_id_celero_charge_post**](CeleroApi.md#charge_contingency_fee_artists_artist_id_celero_charge_post) | **POST** /artists/{artist_id}/celero/charge | Charge Contingency Fee
[**disburse_to_artist_artists_artist_id_celero_disburse_post**](CeleroApi.md#disburse_to_artist_artists_artist_id_celero_disburse_post) | **POST** /artists/{artist_id}/celero/disburse | Disburse To Artist
[**get_celero_status_artists_artist_id_celero_status_get**](CeleroApi.md#get_celero_status_artists_artist_id_celero_status_get) | **GET** /artists/{artist_id}/celero/status | Get Celero Status
[**get_celero_transaction_artists_artist_id_celero_transactions_transaction_id_get**](CeleroApi.md#get_celero_transaction_artists_artist_id_celero_transactions_transaction_id_get) | **GET** /artists/{artist_id}/celero/transactions/{transaction_id} | Get Celero Transaction
[**list_celero_transactions_artists_artist_id_celero_transactions_get**](CeleroApi.md#list_celero_transactions_artists_artist_id_celero_transactions_get) | **GET** /artists/{artist_id}/celero/transactions | List Celero Transactions
[**refund_transaction_artists_artist_id_celero_transactions_transaction_id_refund_post**](CeleroApi.md#refund_transaction_artists_artist_id_celero_transactions_transaction_id_refund_post) | **POST** /artists/{artist_id}/celero/transactions/{transaction_id}/refund | Refund Transaction
[**register_artist_with_celero_artists_artist_id_celero_register_post**](CeleroApi.md#register_artist_with_celero_artists_artist_id_celero_register_post) | **POST** /artists/{artist_id}/celero/register | Register Artist With Celero
[**update_celero_customer_artists_artist_id_celero_customer_put**](CeleroApi.md#update_celero_customer_artists_artist_id_celero_customer_put) | **PUT** /artists/{artist_id}/celero/customer | Update Celero Customer
[**void_transaction_artists_artist_id_celero_transactions_transaction_id_void_post**](CeleroApi.md#void_transaction_artists_artist_id_celero_transactions_transaction_id_void_post) | **POST** /artists/{artist_id}/celero/transactions/{transaction_id}/void | Void Transaction


# **celero_webhook_celero_webhook_post**
> object celero_webhook_celero_webhook_post(x_celero_signature=x_celero_signature)

Celero Webhook

Receive and process real-time event notifications from Celero Commerce.

Configure this URL in the Celero merchant dashboard:
  Settings → Webhooks → Add Endpoint → ``https://your-domain/celero/webhook``

Supported events: ``transaction.approved``, ``transaction.declined``,
``transaction.void``, ``transaction.refund``, ``disbursement.settled``,
``disbursement.failed``.

Every request is validated against the HMAC-SHA256 signature in the
``X-Celero-Signature`` header using ``CELERO_WEBHOOK_SECRET``.

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
    api_instance = xr7_sdk.CeleroApi(api_client)
    x_celero_signature = '' # str |  (optional) (default to '')

    try:
        # Celero Webhook
        api_response = api_instance.celero_webhook_celero_webhook_post(x_celero_signature=x_celero_signature)
        print("The response of CeleroApi->celero_webhook_celero_webhook_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling CeleroApi->celero_webhook_celero_webhook_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **x_celero_signature** | **str**|  | [optional] [default to &#39;&#39;]

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

# **charge_contingency_fee_artists_artist_id_celero_charge_post**
> CeleroTransactionSchema charge_contingency_fee_artists_artist_id_celero_charge_post(artist_id, celero_charge_request)

Charge Contingency Fee

Charge the artist's Celero-vaulted payment method for XR7's
10% contingency fee on a reconciled claim.

The claim must be in ``PAID`` status with a ``recovered_amount`` set.
The charge amount is calculated as ``recovered_amount × 10%``.

Requires:
- The artist to be registered with Celero (``celero_customer_vault_id`` set).
- ``CELERO_SECURITY_KEY`` to be configured.

### Example


```python
import xr7_sdk
from xr7_sdk.models.celero_charge_request import CeleroChargeRequest
from xr7_sdk.models.celero_transaction_schema import CeleroTransactionSchema
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
    api_instance = xr7_sdk.CeleroApi(api_client)
    artist_id = 'artist_id_example' # str | 
    celero_charge_request = xr7_sdk.CeleroChargeRequest() # CeleroChargeRequest | 

    try:
        # Charge Contingency Fee
        api_response = api_instance.charge_contingency_fee_artists_artist_id_celero_charge_post(artist_id, celero_charge_request)
        print("The response of CeleroApi->charge_contingency_fee_artists_artist_id_celero_charge_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling CeleroApi->charge_contingency_fee_artists_artist_id_celero_charge_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **artist_id** | **str**|  | 
 **celero_charge_request** | [**CeleroChargeRequest**](CeleroChargeRequest.md)|  | 

### Return type

[**CeleroTransactionSchema**](CeleroTransactionSchema.md)

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

# **disburse_to_artist_artists_artist_id_celero_disburse_post**
> CeleroTransactionSchema disburse_to_artist_artists_artist_id_celero_disburse_post(artist_id, celero_disburse_request)

Disburse To Artist

Disburse the artist's net recovery amount via ACH credit through Celero.

The ``amount`` should be the gross recovery minus XR7's contingency
fee.  Celero will credit the artist's bank account stored in their vault.

Requires:
- The artist to have a bank account on file in their Celero vault.
- Celero ACH payout capability to be enabled on the XR7 merchant account.
- ``CELERO_SECURITY_KEY`` to be configured.

### Example


```python
import xr7_sdk
from xr7_sdk.models.celero_disburse_request import CeleroDisburseRequest
from xr7_sdk.models.celero_transaction_schema import CeleroTransactionSchema
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
    api_instance = xr7_sdk.CeleroApi(api_client)
    artist_id = 'artist_id_example' # str | 
    celero_disburse_request = xr7_sdk.CeleroDisburseRequest() # CeleroDisburseRequest | 

    try:
        # Disburse To Artist
        api_response = api_instance.disburse_to_artist_artists_artist_id_celero_disburse_post(artist_id, celero_disburse_request)
        print("The response of CeleroApi->disburse_to_artist_artists_artist_id_celero_disburse_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling CeleroApi->disburse_to_artist_artists_artist_id_celero_disburse_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **artist_id** | **str**|  | 
 **celero_disburse_request** | [**CeleroDisburseRequest**](CeleroDisburseRequest.md)|  | 

### Return type

[**CeleroTransactionSchema**](CeleroTransactionSchema.md)

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

# **get_celero_status_artists_artist_id_celero_status_get**
> object get_celero_status_artists_artist_id_celero_status_get(artist_id)

Get Celero Status

Return the Celero Commerce integration status for an artist.

Shows whether the artist has been registered in the Celero vault and
a summary of their transaction history.

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
    api_instance = xr7_sdk.CeleroApi(api_client)
    artist_id = 'artist_id_example' # str | 

    try:
        # Get Celero Status
        api_response = api_instance.get_celero_status_artists_artist_id_celero_status_get(artist_id)
        print("The response of CeleroApi->get_celero_status_artists_artist_id_celero_status_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling CeleroApi->get_celero_status_artists_artist_id_celero_status_get: %s\n" % e)
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

# **get_celero_transaction_artists_artist_id_celero_transactions_transaction_id_get**
> CeleroTransactionSchema get_celero_transaction_artists_artist_id_celero_transactions_transaction_id_get(artist_id, transaction_id)

Get Celero Transaction

Return a single Celero transaction record.

### Example


```python
import xr7_sdk
from xr7_sdk.models.celero_transaction_schema import CeleroTransactionSchema
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
    api_instance = xr7_sdk.CeleroApi(api_client)
    artist_id = 'artist_id_example' # str | 
    transaction_id = 'transaction_id_example' # str | 

    try:
        # Get Celero Transaction
        api_response = api_instance.get_celero_transaction_artists_artist_id_celero_transactions_transaction_id_get(artist_id, transaction_id)
        print("The response of CeleroApi->get_celero_transaction_artists_artist_id_celero_transactions_transaction_id_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling CeleroApi->get_celero_transaction_artists_artist_id_celero_transactions_transaction_id_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **artist_id** | **str**|  | 
 **transaction_id** | **str**|  | 

### Return type

[**CeleroTransactionSchema**](CeleroTransactionSchema.md)

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

# **list_celero_transactions_artists_artist_id_celero_transactions_get**
> List[CeleroTransactionSchema] list_celero_transactions_artists_artist_id_celero_transactions_get(artist_id)

List Celero Transactions

Return all Celero transactions for an artist, newest first.

### Example


```python
import xr7_sdk
from xr7_sdk.models.celero_transaction_schema import CeleroTransactionSchema
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
    api_instance = xr7_sdk.CeleroApi(api_client)
    artist_id = 'artist_id_example' # str | 

    try:
        # List Celero Transactions
        api_response = api_instance.list_celero_transactions_artists_artist_id_celero_transactions_get(artist_id)
        print("The response of CeleroApi->list_celero_transactions_artists_artist_id_celero_transactions_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling CeleroApi->list_celero_transactions_artists_artist_id_celero_transactions_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **artist_id** | **str**|  | 

### Return type

[**List[CeleroTransactionSchema]**](CeleroTransactionSchema.md)

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

# **refund_transaction_artists_artist_id_celero_transactions_transaction_id_refund_post**
> CeleroTransactionSchema refund_transaction_artists_artist_id_celero_transactions_transaction_id_refund_post(artist_id, transaction_id, celero_refund_request)

Refund Transaction

Issue a partial or full refund for a previous CHARGE transaction.

If ``amount`` is omitted, the full transaction amount is refunded.

### Example


```python
import xr7_sdk
from xr7_sdk.models.celero_refund_request import CeleroRefundRequest
from xr7_sdk.models.celero_transaction_schema import CeleroTransactionSchema
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
    api_instance = xr7_sdk.CeleroApi(api_client)
    artist_id = 'artist_id_example' # str | 
    transaction_id = 'transaction_id_example' # str | 
    celero_refund_request = xr7_sdk.CeleroRefundRequest() # CeleroRefundRequest | 

    try:
        # Refund Transaction
        api_response = api_instance.refund_transaction_artists_artist_id_celero_transactions_transaction_id_refund_post(artist_id, transaction_id, celero_refund_request)
        print("The response of CeleroApi->refund_transaction_artists_artist_id_celero_transactions_transaction_id_refund_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling CeleroApi->refund_transaction_artists_artist_id_celero_transactions_transaction_id_refund_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **artist_id** | **str**|  | 
 **transaction_id** | **str**|  | 
 **celero_refund_request** | [**CeleroRefundRequest**](CeleroRefundRequest.md)|  | 

### Return type

[**CeleroTransactionSchema**](CeleroTransactionSchema.md)

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

# **register_artist_with_celero_artists_artist_id_celero_register_post**
> ArtistSchema register_artist_with_celero_artists_artist_id_celero_register_post(artist_id, celero_register_request)

Register Artist With Celero

Register an artist in the Celero Commerce Customer Vault.

Creates a new vault record with the artist's contact details.  The
returned ``celero_customer_vault_id`` is stored on the Artist and used
for all subsequent charges and disbursements.

The artist's actual payment credentials (card number / bank account)
are added separately using Celero's **Collect.js** or **Collect Checkout**
hosted form — XR7 never handles raw payment data.

Requires ``CELERO_SECURITY_KEY`` to be configured.

### Example


```python
import xr7_sdk
from xr7_sdk.models.artist_schema import ArtistSchema
from xr7_sdk.models.celero_register_request import CeleroRegisterRequest
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
    api_instance = xr7_sdk.CeleroApi(api_client)
    artist_id = 'artist_id_example' # str | 
    celero_register_request = xr7_sdk.CeleroRegisterRequest() # CeleroRegisterRequest | 

    try:
        # Register Artist With Celero
        api_response = api_instance.register_artist_with_celero_artists_artist_id_celero_register_post(artist_id, celero_register_request)
        print("The response of CeleroApi->register_artist_with_celero_artists_artist_id_celero_register_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling CeleroApi->register_artist_with_celero_artists_artist_id_celero_register_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **artist_id** | **str**|  | 
 **celero_register_request** | [**CeleroRegisterRequest**](CeleroRegisterRequest.md)|  | 

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
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **update_celero_customer_artists_artist_id_celero_customer_put**
> ArtistSchema update_celero_customer_artists_artist_id_celero_customer_put(artist_id, celero_register_request)

Update Celero Customer

Update an artist's contact details in the Celero Customer Vault.

### Example


```python
import xr7_sdk
from xr7_sdk.models.artist_schema import ArtistSchema
from xr7_sdk.models.celero_register_request import CeleroRegisterRequest
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
    api_instance = xr7_sdk.CeleroApi(api_client)
    artist_id = 'artist_id_example' # str | 
    celero_register_request = xr7_sdk.CeleroRegisterRequest() # CeleroRegisterRequest | 

    try:
        # Update Celero Customer
        api_response = api_instance.update_celero_customer_artists_artist_id_celero_customer_put(artist_id, celero_register_request)
        print("The response of CeleroApi->update_celero_customer_artists_artist_id_celero_customer_put:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling CeleroApi->update_celero_customer_artists_artist_id_celero_customer_put: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **artist_id** | **str**|  | 
 **celero_register_request** | [**CeleroRegisterRequest**](CeleroRegisterRequest.md)|  | 

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
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **void_transaction_artists_artist_id_celero_transactions_transaction_id_void_post**
> CeleroTransactionSchema void_transaction_artists_artist_id_celero_transactions_transaction_id_void_post(artist_id, transaction_id)

Void Transaction

Void an unsettled CHARGE transaction (typically same-day).

Use ``refund`` for transactions that have already settled.

### Example


```python
import xr7_sdk
from xr7_sdk.models.celero_transaction_schema import CeleroTransactionSchema
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
    api_instance = xr7_sdk.CeleroApi(api_client)
    artist_id = 'artist_id_example' # str | 
    transaction_id = 'transaction_id_example' # str | 

    try:
        # Void Transaction
        api_response = api_instance.void_transaction_artists_artist_id_celero_transactions_transaction_id_void_post(artist_id, transaction_id)
        print("The response of CeleroApi->void_transaction_artists_artist_id_celero_transactions_transaction_id_void_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling CeleroApi->void_transaction_artists_artist_id_celero_transactions_transaction_id_void_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **artist_id** | **str**|  | 
 **transaction_id** | **str**|  | 

### Return type

[**CeleroTransactionSchema**](CeleroTransactionSchema.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

