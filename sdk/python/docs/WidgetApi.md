# xr7_sdk.WidgetApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**claim_widget_claim_post**](WidgetApi.md#claim_widget_claim_post) | **POST** /widget/claim | Claim
[**estimate_widget_estimate_post**](WidgetApi.md#estimate_widget_estimate_post) | **POST** /widget/estimate | Estimate
[**list_leads_widget_leads_get**](WidgetApi.md#list_leads_widget_leads_get) | **GET** /widget/leads | List Leads
[**register_widget_register_post**](WidgetApi.md#register_widget_register_post) | **POST** /widget/register | Register
[**verify_widget_verify_post**](WidgetApi.md#verify_widget_verify_post) | **POST** /widget/verify | Verify


# **claim_widget_claim_post**
> object claim_widget_claim_post(claim_request)

Claim

Mark a lead as "claimed" when the artist clicks the recovery CTA.

The ``lead_id`` returned by ``POST /widget/estimate`` is required.
Idempotent — calling this multiple times on the same lead is safe.

### Example


```python
import xr7_sdk
from xr7_sdk.models.claim_request import ClaimRequest
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
    api_instance = xr7_sdk.WidgetApi(api_client)
    claim_request = xr7_sdk.ClaimRequest() # ClaimRequest | 

    try:
        # Claim
        api_response = api_instance.claim_widget_claim_post(claim_request)
        print("The response of WidgetApi->claim_widget_claim_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WidgetApi->claim_widget_claim_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **claim_request** | [**ClaimRequest**](ClaimRequest.md)|  | 

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

# **estimate_widget_estimate_post**
> object estimate_widget_estimate_post(estimate_request)

Estimate

Step 3 of the MFA flow.

Presents the estimate token obtained from ``POST /widget/verify`` along
with optional career profile information.  Saves a lead record to the
database, emails the estimate results to the artist, and returns the
full royalty owed estimate.

### Example


```python
import xr7_sdk
from xr7_sdk.models.estimate_request import EstimateRequest
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
    api_instance = xr7_sdk.WidgetApi(api_client)
    estimate_request = xr7_sdk.EstimateRequest() # EstimateRequest | 

    try:
        # Estimate
        api_response = api_instance.estimate_widget_estimate_post(estimate_request)
        print("The response of WidgetApi->estimate_widget_estimate_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WidgetApi->estimate_widget_estimate_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **estimate_request** | [**EstimateRequest**](EstimateRequest.md)|  | 

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

# **list_leads_widget_leads_get**
> List[WidgetLeadSchema] list_leads_widget_leads_get(x_admin_key=x_admin_key)

List Leads

Return all widget leads in reverse-chronological order.

Requires the ``X-Admin-Key`` request header to equal the
``WIDGET_ADMIN_KEY`` environment variable.

### Example


```python
import xr7_sdk
from xr7_sdk.models.widget_lead_schema import WidgetLeadSchema
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
    api_instance = xr7_sdk.WidgetApi(api_client)
    x_admin_key = '' # str |  (optional) (default to '')

    try:
        # List Leads
        api_response = api_instance.list_leads_widget_leads_get(x_admin_key=x_admin_key)
        print("The response of WidgetApi->list_leads_widget_leads_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WidgetApi->list_leads_widget_leads_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **x_admin_key** | **str**|  | [optional] [default to &#39;&#39;]

### Return type

[**List[WidgetLeadSchema]**](WidgetLeadSchema.md)

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

# **register_widget_register_post**
> RegisterResponse register_widget_register_post(register_request)

Register

Step 1 of the MFA flow.

Validates the artist's identity details, creates a verification session,
and dispatches a 6-digit OTP to both the provided phone number and email
address.

In **development** environments (``XR7_ENV`` ≠ ``production``), the
OTPs are also returned in the response body under ``dev_phone_otp`` and
``dev_email_otp`` so that local testing requires no external credentials.
These fields are **absent** in production.

### Example


```python
import xr7_sdk
from xr7_sdk.models.register_request import RegisterRequest
from xr7_sdk.models.register_response import RegisterResponse
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
    api_instance = xr7_sdk.WidgetApi(api_client)
    register_request = xr7_sdk.RegisterRequest() # RegisterRequest | 

    try:
        # Register
        api_response = api_instance.register_widget_register_post(register_request)
        print("The response of WidgetApi->register_widget_register_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WidgetApi->register_widget_register_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **register_request** | [**RegisterRequest**](RegisterRequest.md)|  | 

### Return type

[**RegisterResponse**](RegisterResponse.md)

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

# **verify_widget_verify_post**
> VerifyResponse verify_widget_verify_post(verify_request)

Verify

Step 2 of the MFA flow.

Both the phone OTP and email OTP must be correct.  On success, a
short-lived estimate token is returned.  This token must be presented
to ``POST /widget/estimate`` to retrieve the royalty estimate.

### Example


```python
import xr7_sdk
from xr7_sdk.models.verify_request import VerifyRequest
from xr7_sdk.models.verify_response import VerifyResponse
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
    api_instance = xr7_sdk.WidgetApi(api_client)
    verify_request = xr7_sdk.VerifyRequest() # VerifyRequest | 

    try:
        # Verify
        api_response = api_instance.verify_widget_verify_post(verify_request)
        print("The response of WidgetApi->verify_widget_verify_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WidgetApi->verify_widget_verify_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **verify_request** | [**VerifyRequest**](VerifyRequest.md)|  | 

### Return type

[**VerifyResponse**](VerifyResponse.md)

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

