# xr7_sdk.BillingApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_billing_summary_artists_artist_id_billing_get**](BillingApi.md#get_billing_summary_artists_artist_id_billing_get) | **GET** /artists/{artist_id}/billing | Get Billing Summary
[**list_invoices_artists_artist_id_invoices_get**](BillingApi.md#list_invoices_artists_artist_id_invoices_get) | **GET** /artists/{artist_id}/invoices | List Invoices


# **get_billing_summary_artists_artist_id_billing_get**
> object get_billing_summary_artists_artist_id_billing_get(artist_id)

Get Billing Summary

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
    api_instance = xr7_sdk.BillingApi(api_client)
    artist_id = 'artist_id_example' # str | 

    try:
        # Get Billing Summary
        api_response = api_instance.get_billing_summary_artists_artist_id_billing_get(artist_id)
        print("The response of BillingApi->get_billing_summary_artists_artist_id_billing_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling BillingApi->get_billing_summary_artists_artist_id_billing_get: %s\n" % e)
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

# **list_invoices_artists_artist_id_invoices_get**
> object list_invoices_artists_artist_id_invoices_get(artist_id)

List Invoices

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
    api_instance = xr7_sdk.BillingApi(api_client)
    artist_id = 'artist_id_example' # str | 

    try:
        # List Invoices
        api_response = api_instance.list_invoices_artists_artist_id_invoices_get(artist_id)
        print("The response of BillingApi->list_invoices_artists_artist_id_invoices_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling BillingApi->list_invoices_artists_artist_id_invoices_get: %s\n" % e)
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

