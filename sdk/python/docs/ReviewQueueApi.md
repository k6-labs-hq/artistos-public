# xr7_sdk.ReviewQueueApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**assign_review_item_review_queue_items_item_id_assign_post**](ReviewQueueApi.md#assign_review_item_review_queue_items_item_id_assign_post) | **POST** /review-queue/items/{item_id}/assign | Assign Review Item
[**check_threshold_review_queue_threshold_check_post**](ReviewQueueApi.md#check_threshold_review_queue_threshold_check_post) | **POST** /review-queue/threshold-check | Check Threshold
[**create_review_item_review_queue_items_post**](ReviewQueueApi.md#create_review_item_review_queue_items_post) | **POST** /review-queue/items | Create Review Item
[**decide_review_item_review_queue_items_item_id_decision_post**](ReviewQueueApi.md#decide_review_item_review_queue_items_item_id_decision_post) | **POST** /review-queue/items/{item_id}/decision | Decide Review Item
[**list_decisions_review_queue_decisions_get**](ReviewQueueApi.md#list_decisions_review_queue_decisions_get) | **GET** /review-queue/decisions | List Decisions
[**list_review_items_review_queue_items_get**](ReviewQueueApi.md#list_review_items_review_queue_items_get) | **GET** /review-queue/items | List Review Items
[**review_queue_metrics_review_queue_metrics_get**](ReviewQueueApi.md#review_queue_metrics_review_queue_metrics_get) | **GET** /review-queue/metrics | Review Queue Metrics


# **assign_review_item_review_queue_items_item_id_assign_post**
> ReviewAssignmentSchema assign_review_item_review_queue_items_item_id_assign_post(item_id, assign_review_item_request, x_analyst_key=x_analyst_key, x_analyst_email=x_analyst_email)

Assign Review Item

### Example


```python
import xr7_sdk
from xr7_sdk.models.assign_review_item_request import AssignReviewItemRequest
from xr7_sdk.models.review_assignment_schema import ReviewAssignmentSchema
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
    api_instance = xr7_sdk.ReviewQueueApi(api_client)
    item_id = 'item_id_example' # str |
    assign_review_item_request = xr7_sdk.AssignReviewItemRequest() # AssignReviewItemRequest |
    x_analyst_key = '' # str |  (optional) (default to '')
    x_analyst_email = '' # str |  (optional) (default to '')

    try:
        # Assign Review Item
        api_response = api_instance.assign_review_item_review_queue_items_item_id_assign_post(item_id, assign_review_item_request, x_analyst_key=x_analyst_key, x_analyst_email=x_analyst_email)
        print("The response of ReviewQueueApi->assign_review_item_review_queue_items_item_id_assign_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ReviewQueueApi->assign_review_item_review_queue_items_item_id_assign_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **item_id** | **str**|  |
 **assign_review_item_request** | [**AssignReviewItemRequest**](AssignReviewItemRequest.md)|  |
 **x_analyst_key** | **str**|  | [optional] [default to &#39;&#39;]
 **x_analyst_email** | **str**|  | [optional] [default to &#39;&#39;]

### Return type

[**ReviewAssignmentSchema**](ReviewAssignmentSchema.md)

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

# **check_threshold_review_queue_threshold_check_post**
> object check_threshold_review_queue_threshold_check_post(x_analyst_key=x_analyst_key, x_analyst_email=x_analyst_email)

Check Threshold

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
    api_instance = xr7_sdk.ReviewQueueApi(api_client)
    x_analyst_key = '' # str |  (optional) (default to '')
    x_analyst_email = '' # str |  (optional) (default to '')

    try:
        # Check Threshold
        api_response = api_instance.check_threshold_review_queue_threshold_check_post(x_analyst_key=x_analyst_key, x_analyst_email=x_analyst_email)
        print("The response of ReviewQueueApi->check_threshold_review_queue_threshold_check_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ReviewQueueApi->check_threshold_review_queue_threshold_check_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **x_analyst_key** | **str**|  | [optional] [default to &#39;&#39;]
 **x_analyst_email** | **str**|  | [optional] [default to &#39;&#39;]

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

# **create_review_item_review_queue_items_post**
> ReviewItemSchema create_review_item_review_queue_items_post(create_review_item_request, x_analyst_key=x_analyst_key, x_analyst_email=x_analyst_email)

Create Review Item

### Example


```python
import xr7_sdk
from xr7_sdk.models.create_review_item_request import CreateReviewItemRequest
from xr7_sdk.models.review_item_schema import ReviewItemSchema
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
    api_instance = xr7_sdk.ReviewQueueApi(api_client)
    create_review_item_request = xr7_sdk.CreateReviewItemRequest() # CreateReviewItemRequest |
    x_analyst_key = '' # str |  (optional) (default to '')
    x_analyst_email = '' # str |  (optional) (default to '')

    try:
        # Create Review Item
        api_response = api_instance.create_review_item_review_queue_items_post(create_review_item_request, x_analyst_key=x_analyst_key, x_analyst_email=x_analyst_email)
        print("The response of ReviewQueueApi->create_review_item_review_queue_items_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ReviewQueueApi->create_review_item_review_queue_items_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **create_review_item_request** | [**CreateReviewItemRequest**](CreateReviewItemRequest.md)|  |
 **x_analyst_key** | **str**|  | [optional] [default to &#39;&#39;]
 **x_analyst_email** | **str**|  | [optional] [default to &#39;&#39;]

### Return type

[**ReviewItemSchema**](ReviewItemSchema.md)

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

# **decide_review_item_review_queue_items_item_id_decision_post**
> ReviewDecisionSchema decide_review_item_review_queue_items_item_id_decision_post(item_id, decide_review_item_request, x_analyst_key=x_analyst_key, x_analyst_email=x_analyst_email)

Decide Review Item

### Example


```python
import xr7_sdk
from xr7_sdk.models.decide_review_item_request import DecideReviewItemRequest
from xr7_sdk.models.review_decision_schema import ReviewDecisionSchema
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
    api_instance = xr7_sdk.ReviewQueueApi(api_client)
    item_id = 'item_id_example' # str |
    decide_review_item_request = xr7_sdk.DecideReviewItemRequest() # DecideReviewItemRequest |
    x_analyst_key = '' # str |  (optional) (default to '')
    x_analyst_email = '' # str |  (optional) (default to '')

    try:
        # Decide Review Item
        api_response = api_instance.decide_review_item_review_queue_items_item_id_decision_post(item_id, decide_review_item_request, x_analyst_key=x_analyst_key, x_analyst_email=x_analyst_email)
        print("The response of ReviewQueueApi->decide_review_item_review_queue_items_item_id_decision_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ReviewQueueApi->decide_review_item_review_queue_items_item_id_decision_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **item_id** | **str**|  |
 **decide_review_item_request** | [**DecideReviewItemRequest**](DecideReviewItemRequest.md)|  |
 **x_analyst_key** | **str**|  | [optional] [default to &#39;&#39;]
 **x_analyst_email** | **str**|  | [optional] [default to &#39;&#39;]

### Return type

[**ReviewDecisionSchema**](ReviewDecisionSchema.md)

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

# **list_decisions_review_queue_decisions_get**
> List[ReviewDecisionSchema] list_decisions_review_queue_decisions_get(item_id=item_id, limit=limit, offset=offset, x_analyst_key=x_analyst_key, x_analyst_email=x_analyst_email)

List Decisions

### Example


```python
import xr7_sdk
from xr7_sdk.models.review_decision_schema import ReviewDecisionSchema
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
    api_instance = xr7_sdk.ReviewQueueApi(api_client)
    item_id = 'item_id_example' # str |  (optional)
    limit = 100 # int |  (optional) (default to 100)
    offset = 0 # int |  (optional) (default to 0)
    x_analyst_key = '' # str |  (optional) (default to '')
    x_analyst_email = '' # str |  (optional) (default to '')

    try:
        # List Decisions
        api_response = api_instance.list_decisions_review_queue_decisions_get(item_id=item_id, limit=limit, offset=offset, x_analyst_key=x_analyst_key, x_analyst_email=x_analyst_email)
        print("The response of ReviewQueueApi->list_decisions_review_queue_decisions_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ReviewQueueApi->list_decisions_review_queue_decisions_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **item_id** | **str**|  | [optional]
 **limit** | **int**|  | [optional] [default to 100]
 **offset** | **int**|  | [optional] [default to 0]
 **x_analyst_key** | **str**|  | [optional] [default to &#39;&#39;]
 **x_analyst_email** | **str**|  | [optional] [default to &#39;&#39;]

### Return type

[**List[ReviewDecisionSchema]**](ReviewDecisionSchema.md)

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

# **list_review_items_review_queue_items_get**
> List[ReviewItemSchema] list_review_items_review_queue_items_get(status=status, artist_id=artist_id, assigned_analyst_email=assigned_analyst_email, limit=limit, offset=offset, x_analyst_key=x_analyst_key, x_analyst_email=x_analyst_email)

List Review Items

### Example


```python
import xr7_sdk
from xr7_sdk.models.review_item_schema import ReviewItemSchema
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
    api_instance = xr7_sdk.ReviewQueueApi(api_client)
    status = 'status_example' # str |  (optional)
    artist_id = 'artist_id_example' # str |  (optional)
    assigned_analyst_email = 'assigned_analyst_email_example' # str |  (optional)
    limit = 100 # int |  (optional) (default to 100)
    offset = 0 # int |  (optional) (default to 0)
    x_analyst_key = '' # str |  (optional) (default to '')
    x_analyst_email = '' # str |  (optional) (default to '')

    try:
        # List Review Items
        api_response = api_instance.list_review_items_review_queue_items_get(status=status, artist_id=artist_id, assigned_analyst_email=assigned_analyst_email, limit=limit, offset=offset, x_analyst_key=x_analyst_key, x_analyst_email=x_analyst_email)
        print("The response of ReviewQueueApi->list_review_items_review_queue_items_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ReviewQueueApi->list_review_items_review_queue_items_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **status** | **str**|  | [optional]
 **artist_id** | **str**|  | [optional]
 **assigned_analyst_email** | **str**|  | [optional]
 **limit** | **int**|  | [optional] [default to 100]
 **offset** | **int**|  | [optional] [default to 0]
 **x_analyst_key** | **str**|  | [optional] [default to &#39;&#39;]
 **x_analyst_email** | **str**|  | [optional] [default to &#39;&#39;]

### Return type

[**List[ReviewItemSchema]**](ReviewItemSchema.md)

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

# **review_queue_metrics_review_queue_metrics_get**
> object review_queue_metrics_review_queue_metrics_get(x_analyst_key=x_analyst_key, x_analyst_email=x_analyst_email)

Review Queue Metrics

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
    api_instance = xr7_sdk.ReviewQueueApi(api_client)
    x_analyst_key = '' # str |  (optional) (default to '')
    x_analyst_email = '' # str |  (optional) (default to '')

    try:
        # Review Queue Metrics
        api_response = api_instance.review_queue_metrics_review_queue_metrics_get(x_analyst_key=x_analyst_key, x_analyst_email=x_analyst_email)
        print("The response of ReviewQueueApi->review_queue_metrics_review_queue_metrics_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ReviewQueueApi->review_queue_metrics_review_queue_metrics_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **x_analyst_key** | **str**|  | [optional] [default to &#39;&#39;]
 **x_analyst_email** | **str**|  | [optional] [default to &#39;&#39;]

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
