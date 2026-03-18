# xr7_sdk.AdvanceGovernanceApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**accept_artist_offer_artists_artist_id_advance_offers_offer_id_accept_post**](AdvanceGovernanceApi.md#accept_artist_offer_artists_artist_id_advance_offers_offer_id_accept_post) | **POST** /artists/{artist_id}/advance/offers/{offer_id}/accept | Accept Artist Offer
[**analyst_queue_admin_advances_queue_analyst_get**](AdvanceGovernanceApi.md#analyst_queue_admin_advances_queue_analyst_get) | **GET** /admin/advances/queue/analyst | Analyst Queue
[**approve_analyst_admin_advances_opportunities_opportunity_id_analyst_decision_post**](AdvanceGovernanceApi.md#approve_analyst_admin_advances_opportunities_opportunity_id_analyst_decision_post) | **POST** /admin/advances/opportunities/{opportunity_id}/analyst-decision | Approve Analyst
[**approve_executive_admin_advances_opportunities_opportunity_id_executive_decision_post**](AdvanceGovernanceApi.md#approve_executive_admin_advances_opportunities_opportunity_id_executive_decision_post) | **POST** /admin/advances/opportunities/{opportunity_id}/executive-decision | Approve Executive
[**create_failed_packet_admin_advances_offers_offer_id_failed_recovery_packet_post**](AdvanceGovernanceApi.md#create_failed_packet_admin_advances_offers_offer_id_failed_recovery_packet_post) | **POST** /admin/advances/offers/{offer_id}/failed-recovery-packet | Create Failed Packet
[**executive_queue_admin_advances_queue_executive_get**](AdvanceGovernanceApi.md#executive_queue_admin_advances_queue_executive_get) | **GET** /admin/advances/queue/executive | Executive Queue
[**list_artist_offers_artists_artist_id_advance_offers_get**](AdvanceGovernanceApi.md#list_artist_offers_artists_artist_id_advance_offers_get) | **GET** /artists/{artist_id}/advance/offers | List Artist Offers
[**publish_offer_admin_advances_opportunities_opportunity_id_publish_offer_post**](AdvanceGovernanceApi.md#publish_offer_admin_advances_opportunities_opportunity_id_publish_offer_post) | **POST** /admin/advances/opportunities/{opportunity_id}/publish-offer | Publish Offer
[**run_nightly_eval_admin_advances_run_nightly_eval_post**](AdvanceGovernanceApi.md#run_nightly_eval_admin_advances_run_nightly_eval_post) | **POST** /admin/advances/run-nightly-eval | Run Nightly Eval


# **accept_artist_offer_artists_artist_id_advance_offers_offer_id_accept_post**
> Dict[str, object] accept_artist_offer_artists_artist_id_advance_offers_offer_id_accept_post(artist_id, offer_id)

Accept Artist Offer

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
    api_instance = xr7_sdk.AdvanceGovernanceApi(api_client)
    artist_id = 'artist_id_example' # str | 
    offer_id = 'offer_id_example' # str | 

    try:
        # Accept Artist Offer
        api_response = api_instance.accept_artist_offer_artists_artist_id_advance_offers_offer_id_accept_post(artist_id, offer_id)
        print("The response of AdvanceGovernanceApi->accept_artist_offer_artists_artist_id_advance_offers_offer_id_accept_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AdvanceGovernanceApi->accept_artist_offer_artists_artist_id_advance_offers_offer_id_accept_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **artist_id** | **str**|  | 
 **offer_id** | **str**|  | 

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

# **analyst_queue_admin_advances_queue_analyst_get**
> Dict[str, object] analyst_queue_admin_advances_queue_analyst_get()

Analyst Queue

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
    api_instance = xr7_sdk.AdvanceGovernanceApi(api_client)

    try:
        # Analyst Queue
        api_response = api_instance.analyst_queue_admin_advances_queue_analyst_get()
        print("The response of AdvanceGovernanceApi->analyst_queue_admin_advances_queue_analyst_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AdvanceGovernanceApi->analyst_queue_admin_advances_queue_analyst_get: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

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

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **approve_analyst_admin_advances_opportunities_opportunity_id_analyst_decision_post**
> Dict[str, object] approve_analyst_admin_advances_opportunities_opportunity_id_analyst_decision_post(opportunity_id, approval_request)

Approve Analyst

### Example

* Bearer Authentication (HTTPBearer):

```python
import xr7_sdk
from xr7_sdk.models.approval_request import ApprovalRequest
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
    api_instance = xr7_sdk.AdvanceGovernanceApi(api_client)
    opportunity_id = 'opportunity_id_example' # str | 
    approval_request = xr7_sdk.ApprovalRequest() # ApprovalRequest | 

    try:
        # Approve Analyst
        api_response = api_instance.approve_analyst_admin_advances_opportunities_opportunity_id_analyst_decision_post(opportunity_id, approval_request)
        print("The response of AdvanceGovernanceApi->approve_analyst_admin_advances_opportunities_opportunity_id_analyst_decision_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AdvanceGovernanceApi->approve_analyst_admin_advances_opportunities_opportunity_id_analyst_decision_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **opportunity_id** | **str**|  | 
 **approval_request** | [**ApprovalRequest**](ApprovalRequest.md)|  | 

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

# **approve_executive_admin_advances_opportunities_opportunity_id_executive_decision_post**
> Dict[str, object] approve_executive_admin_advances_opportunities_opportunity_id_executive_decision_post(opportunity_id, approval_request)

Approve Executive

### Example

* Bearer Authentication (HTTPBearer):

```python
import xr7_sdk
from xr7_sdk.models.approval_request import ApprovalRequest
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
    api_instance = xr7_sdk.AdvanceGovernanceApi(api_client)
    opportunity_id = 'opportunity_id_example' # str | 
    approval_request = xr7_sdk.ApprovalRequest() # ApprovalRequest | 

    try:
        # Approve Executive
        api_response = api_instance.approve_executive_admin_advances_opportunities_opportunity_id_executive_decision_post(opportunity_id, approval_request)
        print("The response of AdvanceGovernanceApi->approve_executive_admin_advances_opportunities_opportunity_id_executive_decision_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AdvanceGovernanceApi->approve_executive_admin_advances_opportunities_opportunity_id_executive_decision_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **opportunity_id** | **str**|  | 
 **approval_request** | [**ApprovalRequest**](ApprovalRequest.md)|  | 

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

# **create_failed_packet_admin_advances_offers_offer_id_failed_recovery_packet_post**
> Dict[str, object] create_failed_packet_admin_advances_offers_offer_id_failed_recovery_packet_post(offer_id, failed_packet_request)

Create Failed Packet

### Example

* Bearer Authentication (HTTPBearer):

```python
import xr7_sdk
from xr7_sdk.models.failed_packet_request import FailedPacketRequest
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
    api_instance = xr7_sdk.AdvanceGovernanceApi(api_client)
    offer_id = 'offer_id_example' # str | 
    failed_packet_request = xr7_sdk.FailedPacketRequest() # FailedPacketRequest | 

    try:
        # Create Failed Packet
        api_response = api_instance.create_failed_packet_admin_advances_offers_offer_id_failed_recovery_packet_post(offer_id, failed_packet_request)
        print("The response of AdvanceGovernanceApi->create_failed_packet_admin_advances_offers_offer_id_failed_recovery_packet_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AdvanceGovernanceApi->create_failed_packet_admin_advances_offers_offer_id_failed_recovery_packet_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **offer_id** | **str**|  | 
 **failed_packet_request** | [**FailedPacketRequest**](FailedPacketRequest.md)|  | 

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

# **executive_queue_admin_advances_queue_executive_get**
> Dict[str, object] executive_queue_admin_advances_queue_executive_get()

Executive Queue

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
    api_instance = xr7_sdk.AdvanceGovernanceApi(api_client)

    try:
        # Executive Queue
        api_response = api_instance.executive_queue_admin_advances_queue_executive_get()
        print("The response of AdvanceGovernanceApi->executive_queue_admin_advances_queue_executive_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AdvanceGovernanceApi->executive_queue_admin_advances_queue_executive_get: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

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

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_artist_offers_artists_artist_id_advance_offers_get**
> Dict[str, object] list_artist_offers_artists_artist_id_advance_offers_get(artist_id)

List Artist Offers

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
    api_instance = xr7_sdk.AdvanceGovernanceApi(api_client)
    artist_id = 'artist_id_example' # str | 

    try:
        # List Artist Offers
        api_response = api_instance.list_artist_offers_artists_artist_id_advance_offers_get(artist_id)
        print("The response of AdvanceGovernanceApi->list_artist_offers_artists_artist_id_advance_offers_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AdvanceGovernanceApi->list_artist_offers_artists_artist_id_advance_offers_get: %s\n" % e)
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

# **publish_offer_admin_advances_opportunities_opportunity_id_publish_offer_post**
> Dict[str, object] publish_offer_admin_advances_opportunities_opportunity_id_publish_offer_post(opportunity_id)

Publish Offer

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
    api_instance = xr7_sdk.AdvanceGovernanceApi(api_client)
    opportunity_id = 'opportunity_id_example' # str | 

    try:
        # Publish Offer
        api_response = api_instance.publish_offer_admin_advances_opportunities_opportunity_id_publish_offer_post(opportunity_id)
        print("The response of AdvanceGovernanceApi->publish_offer_admin_advances_opportunities_opportunity_id_publish_offer_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AdvanceGovernanceApi->publish_offer_admin_advances_opportunities_opportunity_id_publish_offer_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **opportunity_id** | **str**|  | 

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

# **run_nightly_eval_admin_advances_run_nightly_eval_post**
> Dict[str, object] run_nightly_eval_admin_advances_run_nightly_eval_post()

Run Nightly Eval

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
    api_instance = xr7_sdk.AdvanceGovernanceApi(api_client)

    try:
        # Run Nightly Eval
        api_response = api_instance.run_nightly_eval_admin_advances_run_nightly_eval_post()
        print("The response of AdvanceGovernanceApi->run_nightly_eval_admin_advances_run_nightly_eval_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AdvanceGovernanceApi->run_nightly_eval_admin_advances_run_nightly_eval_post: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

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

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

