# xr7_sdk.TrolleyApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_trolley_recipient_artists_artist_id_trolley_recipient_post**](TrolleyApi.md#create_trolley_recipient_artists_artist_id_trolley_recipient_post) | **POST** /artists/{artist_id}/trolley/recipient | Create Trolley Recipient
[**disburse_claim_claims_claim_id_disburse_post**](TrolleyApi.md#disburse_claim_claims_claim_id_disburse_post) | **POST** /claims/{claim_id}/disburse | Disburse Claim
[**get_trolley_status_artists_artist_id_trolley_status_get**](TrolleyApi.md#get_trolley_status_artists_artist_id_trolley_status_get) | **GET** /artists/{artist_id}/trolley/status | Get Trolley Status
[**get_trolley_widget_url_artists_artist_id_trolley_widget_url_get**](TrolleyApi.md#get_trolley_widget_url_artists_artist_id_trolley_widget_url_get) | **GET** /artists/{artist_id}/trolley/widget-url | Get Trolley Widget Url
[**manual_remittance_artists_artist_id_claims_claim_id_manual_remittance_post**](TrolleyApi.md#manual_remittance_artists_artist_id_claims_claim_id_manual_remittance_post) | **POST** /artists/{artist_id}/claims/{claim_id}/manual-remittance | Manual Remittance
[**trolley_webhook_webhooks_trolley_post**](TrolleyApi.md#trolley_webhook_webhooks_trolley_post) | **POST** /webhooks/trolley | Trolley Webhook


# **create_trolley_recipient_artists_artist_id_trolley_recipient_post**
> object create_trolley_recipient_artists_artist_id_trolley_recipient_post(artist_id)

Create Trolley Recipient

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
    api_instance = xr7_sdk.TrolleyApi(api_client)
    artist_id = 'artist_id_example' # str |

    try:
        # Create Trolley Recipient
        api_response = api_instance.create_trolley_recipient_artists_artist_id_trolley_recipient_post(artist_id)
        print("The response of TrolleyApi->create_trolley_recipient_artists_artist_id_trolley_recipient_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TrolleyApi->create_trolley_recipient_artists_artist_id_trolley_recipient_post: %s\n" % e)
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

# **disburse_claim_claims_claim_id_disburse_post**
> TrolleyTransactionSchema disburse_claim_claims_claim_id_disburse_post(claim_id)

Disburse Claim

### Example


```python
import xr7_sdk
from xr7_sdk.models.trolley_transaction_schema import TrolleyTransactionSchema
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
    api_instance = xr7_sdk.TrolleyApi(api_client)
    claim_id = 'claim_id_example' # str |

    try:
        # Disburse Claim
        api_response = api_instance.disburse_claim_claims_claim_id_disburse_post(claim_id)
        print("The response of TrolleyApi->disburse_claim_claims_claim_id_disburse_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TrolleyApi->disburse_claim_claims_claim_id_disburse_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **claim_id** | **str**|  |

### Return type

[**TrolleyTransactionSchema**](TrolleyTransactionSchema.md)

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

# **get_trolley_status_artists_artist_id_trolley_status_get**
> object get_trolley_status_artists_artist_id_trolley_status_get(artist_id)

Get Trolley Status

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
    api_instance = xr7_sdk.TrolleyApi(api_client)
    artist_id = 'artist_id_example' # str |

    try:
        # Get Trolley Status
        api_response = api_instance.get_trolley_status_artists_artist_id_trolley_status_get(artist_id)
        print("The response of TrolleyApi->get_trolley_status_artists_artist_id_trolley_status_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TrolleyApi->get_trolley_status_artists_artist_id_trolley_status_get: %s\n" % e)
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

# **get_trolley_widget_url_artists_artist_id_trolley_widget_url_get**
> object get_trolley_widget_url_artists_artist_id_trolley_widget_url_get(artist_id)

Get Trolley Widget Url

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
    api_instance = xr7_sdk.TrolleyApi(api_client)
    artist_id = 'artist_id_example' # str |

    try:
        # Get Trolley Widget Url
        api_response = api_instance.get_trolley_widget_url_artists_artist_id_trolley_widget_url_get(artist_id)
        print("The response of TrolleyApi->get_trolley_widget_url_artists_artist_id_trolley_widget_url_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TrolleyApi->get_trolley_widget_url_artists_artist_id_trolley_widget_url_get: %s\n" % e)
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

# **manual_remittance_artists_artist_id_claims_claim_id_manual_remittance_post**
> object manual_remittance_artists_artist_id_claims_claim_id_manual_remittance_post(artist_id, claim_id, manual_remittance_request)

Manual Remittance

### Example


```python
import xr7_sdk
from xr7_sdk.models.manual_remittance_request import ManualRemittanceRequest
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
    api_instance = xr7_sdk.TrolleyApi(api_client)
    artist_id = 'artist_id_example' # str |
    claim_id = 'claim_id_example' # str |
    manual_remittance_request = xr7_sdk.ManualRemittanceRequest() # ManualRemittanceRequest |

    try:
        # Manual Remittance
        api_response = api_instance.manual_remittance_artists_artist_id_claims_claim_id_manual_remittance_post(artist_id, claim_id, manual_remittance_request)
        print("The response of TrolleyApi->manual_remittance_artists_artist_id_claims_claim_id_manual_remittance_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TrolleyApi->manual_remittance_artists_artist_id_claims_claim_id_manual_remittance_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **artist_id** | **str**|  |
 **claim_id** | **str**|  |
 **manual_remittance_request** | [**ManualRemittanceRequest**](ManualRemittanceRequest.md)|  |

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

# **trolley_webhook_webhooks_trolley_post**
> object trolley_webhook_webhooks_trolley_post()

Trolley Webhook

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
    api_instance = xr7_sdk.TrolleyApi(api_client)

    try:
        # Trolley Webhook
        api_response = api_instance.trolley_webhook_webhooks_trolley_post()
        print("The response of TrolleyApi->trolley_webhook_webhooks_trolley_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TrolleyApi->trolley_webhook_webhooks_trolley_post: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

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

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)
