# xr7_sdk.RecoveryIntelligenceLLMApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**llm_demand_letter_artists_artist_id_llm_demand_letter_post**](RecoveryIntelligenceLLMApi.md#llm_demand_letter_artists_artist_id_llm_demand_letter_post) | **POST** /artists/{artist_id}/llm/demand-letter | Llm Demand Letter
[**llm_negotiation_script_artists_artist_id_llm_negotiation_script_post**](RecoveryIntelligenceLLMApi.md#llm_negotiation_script_artists_artist_id_llm_negotiation_script_post) | **POST** /artists/{artist_id}/llm/negotiation-script | Llm Negotiation Script
[**llm_personalized_advice_artists_artist_id_llm_advice_post**](RecoveryIntelligenceLLMApi.md#llm_personalized_advice_artists_artist_id_llm_advice_post) | **POST** /artists/{artist_id}/llm/advice | Llm Personalized Advice


# **llm_demand_letter_artists_artist_id_llm_demand_letter_post**
> DemandLetterResponse llm_demand_letter_artists_artist_id_llm_demand_letter_post(artist_id, demand_letter_request, x_actor_email=x_actor_email, x_actor_role=x_actor_role)

Llm Demand Letter

### Example


```python
import xr7_sdk
from xr7_sdk.models.demand_letter_request import DemandLetterRequest
from xr7_sdk.models.demand_letter_response import DemandLetterResponse
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
    api_instance = xr7_sdk.RecoveryIntelligenceLLMApi(api_client)
    artist_id = 'artist_id_example' # str |
    demand_letter_request = xr7_sdk.DemandLetterRequest() # DemandLetterRequest |
    x_actor_email = 'x_actor_email_example' # str |  (optional)
    x_actor_role = 'x_actor_role_example' # str |  (optional)

    try:
        # Llm Demand Letter
        api_response = api_instance.llm_demand_letter_artists_artist_id_llm_demand_letter_post(artist_id, demand_letter_request, x_actor_email=x_actor_email, x_actor_role=x_actor_role)
        print("The response of RecoveryIntelligenceLLMApi->llm_demand_letter_artists_artist_id_llm_demand_letter_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling RecoveryIntelligenceLLMApi->llm_demand_letter_artists_artist_id_llm_demand_letter_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **artist_id** | **str**|  |
 **demand_letter_request** | [**DemandLetterRequest**](DemandLetterRequest.md)|  |
 **x_actor_email** | **str**|  | [optional]
 **x_actor_role** | **str**|  | [optional]

### Return type

[**DemandLetterResponse**](DemandLetterResponse.md)

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

# **llm_negotiation_script_artists_artist_id_llm_negotiation_script_post**
> NegotiationScriptResponse llm_negotiation_script_artists_artist_id_llm_negotiation_script_post(artist_id, negotiation_script_request, x_actor_email=x_actor_email, x_actor_role=x_actor_role)

Llm Negotiation Script

### Example


```python
import xr7_sdk
from xr7_sdk.models.negotiation_script_request import NegotiationScriptRequest
from xr7_sdk.models.negotiation_script_response import NegotiationScriptResponse
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
    api_instance = xr7_sdk.RecoveryIntelligenceLLMApi(api_client)
    artist_id = 'artist_id_example' # str |
    negotiation_script_request = xr7_sdk.NegotiationScriptRequest() # NegotiationScriptRequest |
    x_actor_email = 'x_actor_email_example' # str |  (optional)
    x_actor_role = 'x_actor_role_example' # str |  (optional)

    try:
        # Llm Negotiation Script
        api_response = api_instance.llm_negotiation_script_artists_artist_id_llm_negotiation_script_post(artist_id, negotiation_script_request, x_actor_email=x_actor_email, x_actor_role=x_actor_role)
        print("The response of RecoveryIntelligenceLLMApi->llm_negotiation_script_artists_artist_id_llm_negotiation_script_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling RecoveryIntelligenceLLMApi->llm_negotiation_script_artists_artist_id_llm_negotiation_script_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **artist_id** | **str**|  |
 **negotiation_script_request** | [**NegotiationScriptRequest**](NegotiationScriptRequest.md)|  |
 **x_actor_email** | **str**|  | [optional]
 **x_actor_role** | **str**|  | [optional]

### Return type

[**NegotiationScriptResponse**](NegotiationScriptResponse.md)

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

# **llm_personalized_advice_artists_artist_id_llm_advice_post**
> AdviceResponse llm_personalized_advice_artists_artist_id_llm_advice_post(artist_id, advice_request, x_actor_email=x_actor_email, x_actor_role=x_actor_role)

Llm Personalized Advice

### Example


```python
import xr7_sdk
from xr7_sdk.models.advice_request import AdviceRequest
from xr7_sdk.models.advice_response import AdviceResponse
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
    api_instance = xr7_sdk.RecoveryIntelligenceLLMApi(api_client)
    artist_id = 'artist_id_example' # str |
    advice_request = xr7_sdk.AdviceRequest() # AdviceRequest |
    x_actor_email = 'x_actor_email_example' # str |  (optional)
    x_actor_role = 'x_actor_role_example' # str |  (optional)

    try:
        # Llm Personalized Advice
        api_response = api_instance.llm_personalized_advice_artists_artist_id_llm_advice_post(artist_id, advice_request, x_actor_email=x_actor_email, x_actor_role=x_actor_role)
        print("The response of RecoveryIntelligenceLLMApi->llm_personalized_advice_artists_artist_id_llm_advice_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling RecoveryIntelligenceLLMApi->llm_personalized_advice_artists_artist_id_llm_advice_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **artist_id** | **str**|  |
 **advice_request** | [**AdviceRequest**](AdviceRequest.md)|  |
 **x_actor_email** | **str**|  | [optional]
 **x_actor_role** | **str**|  | [optional]

### Return type

[**AdviceResponse**](AdviceResponse.md)

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
