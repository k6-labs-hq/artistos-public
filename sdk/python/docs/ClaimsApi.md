# xr7_sdk.ClaimsApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**activate_negotiator_agent_claims_claim_id_activate_agent_post**](ClaimsApi.md#activate_negotiator_agent_claims_claim_id_activate_agent_post) | **POST** /claims/{claim_id}/activate-agent | Activate Negotiator Agent
[**advance_claim_claims_claim_id_advance_post**](ClaimsApi.md#advance_claim_claims_claim_id_advance_post) | **POST** /claims/{claim_id}/advance | Advance Claim
[**claim_automation_plan_claims_claim_id_automation_plan_get**](ClaimsApi.md#claim_automation_plan_claims_claim_id_automation_plan_get) | **GET** /claims/{claim_id}/automation-plan | Claim Automation Plan
[**claim_evidence_optimized_claims_claim_id_evidence_optimized_get**](ClaimsApi.md#claim_evidence_optimized_claims_claim_id_evidence_optimized_get) | **GET** /claims/{claim_id}/evidence/optimized | Claim Evidence Optimized
[**claim_evidence_strength_claims_claim_id_evidence_strength_get**](ClaimsApi.md#claim_evidence_strength_claims_claim_id_evidence_strength_get) | **GET** /claims/{claim_id}/evidence/strength | Claim Evidence Strength
[**claim_forecast_claims_claim_id_forecast_get**](ClaimsApi.md#claim_forecast_claims_claim_id_forecast_get) | **GET** /claims/{claim_id}/forecast | Claim Forecast
[**claim_negotiation_intel_claims_claim_id_negotiation_intel_get**](ClaimsApi.md#claim_negotiation_intel_claims_claim_id_negotiation_intel_get) | **GET** /claims/{claim_id}/negotiation-intel | Claim Negotiation Intel
[**claim_playbook_claims_claim_id_playbook_get**](ClaimsApi.md#claim_playbook_claims_claim_id_playbook_get) | **GET** /claims/{claim_id}/playbook | Claim Playbook
[**claim_sla_prediction_claims_claim_id_sla_prediction_get**](ClaimsApi.md#claim_sla_prediction_claims_claim_id_sla_prediction_get) | **GET** /claims/{claim_id}/sla-prediction | Claim Sla Prediction
[**claim_strength_explainer_claims_claim_id_strength_explainer_get**](ClaimsApi.md#claim_strength_explainer_claims_claim_id_strength_explainer_get) | **GET** /claims/{claim_id}/strength-explainer | Claim Strength Explainer
[**create_claim_for_artist_artists_artist_id_claims_post**](ClaimsApi.md#create_claim_for_artist_artists_artist_id_claims_post) | **POST** /artists/{artist_id}/claims | Create Claim For Artist
[**escalate_legal_claims_claim_id_escalate_legal_post**](ClaimsApi.md#escalate_legal_claims_claim_id_escalate_legal_post) | **POST** /claims/{claim_id}/escalate-legal | Escalate Legal
[**export_evidence_packet_claims_claim_id_evidence_export_get**](ClaimsApi.md#export_evidence_packet_claims_claim_id_evidence_export_get) | **GET** /claims/{claim_id}/evidence/export | Export Evidence Packet
[**export_evidence_packet_expert_mode_claims_claim_id_evidence_export_post**](ClaimsApi.md#export_evidence_packet_expert_mode_claims_claim_id_evidence_export_post) | **POST** /claims/{claim_id}/evidence/export | Export Evidence Packet Expert Mode
[**generate_attorney_evidence_file_api_claims_claim_id_attorney_evidence_post**](ClaimsApi.md#generate_attorney_evidence_file_api_claims_claim_id_attorney_evidence_post) | **POST** /api/claims/{claim_id}/attorney-evidence | Generate Attorney Evidence File
[**generate_attorney_evidence_file_claims_claim_id_attorney_evidence_post**](ClaimsApi.md#generate_attorney_evidence_file_claims_claim_id_attorney_evidence_post) | **POST** /claims/{claim_id}/attorney-evidence | Generate Attorney Evidence File
[**generate_evidence_claims_claim_id_evidence_post**](ClaimsApi.md#generate_evidence_claims_claim_id_evidence_post) | **POST** /claims/{claim_id}/evidence | Generate Evidence
[**get_claim_claims_claim_id_get**](ClaimsApi.md#get_claim_claims_claim_id_get) | **GET** /claims/{claim_id} | Get Claim
[**get_evidence_claims_claim_id_evidence_get**](ClaimsApi.md#get_evidence_claims_claim_id_evidence_get) | **GET** /claims/{claim_id}/evidence | Get Evidence
[**list_claims_artists_artist_id_claims_get**](ClaimsApi.md#list_claims_artists_artist_id_claims_get) | **GET** /artists/{artist_id}/claims | List Claims
[**reconcile_claim_claims_claim_id_reconcile_post**](ClaimsApi.md#reconcile_claim_claims_claim_id_reconcile_post) | **POST** /claims/{claim_id}/reconcile | Reconcile Claim
[**verify_evidence_packet_claims_claim_id_evidence_verify_get**](ClaimsApi.md#verify_evidence_packet_claims_claim_id_evidence_verify_get) | **GET** /claims/{claim_id}/evidence/verify | Verify Evidence Packet


# **activate_negotiator_agent_claims_claim_id_activate_agent_post**
> object activate_negotiator_agent_claims_claim_id_activate_agent_post(claim_id)

Activate Negotiator Agent

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
        # Activate Negotiator Agent
        api_response = api_instance.activate_negotiator_agent_claims_claim_id_activate_agent_post(claim_id)
        print("The response of ClaimsApi->activate_negotiator_agent_claims_claim_id_activate_agent_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ClaimsApi->activate_negotiator_agent_claims_claim_id_activate_agent_post: %s\n" % e)
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

# **claim_automation_plan_claims_claim_id_automation_plan_get**
> object claim_automation_plan_claims_claim_id_automation_plan_get(claim_id)

Claim Automation Plan

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
        # Claim Automation Plan
        api_response = api_instance.claim_automation_plan_claims_claim_id_automation_plan_get(claim_id)
        print("The response of ClaimsApi->claim_automation_plan_claims_claim_id_automation_plan_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ClaimsApi->claim_automation_plan_claims_claim_id_automation_plan_get: %s\n" % e)
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

# **claim_evidence_optimized_claims_claim_id_evidence_optimized_get**
> object claim_evidence_optimized_claims_claim_id_evidence_optimized_get(claim_id)

Claim Evidence Optimized

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
        # Claim Evidence Optimized
        api_response = api_instance.claim_evidence_optimized_claims_claim_id_evidence_optimized_get(claim_id)
        print("The response of ClaimsApi->claim_evidence_optimized_claims_claim_id_evidence_optimized_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ClaimsApi->claim_evidence_optimized_claims_claim_id_evidence_optimized_get: %s\n" % e)
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

# **claim_evidence_strength_claims_claim_id_evidence_strength_get**
> object claim_evidence_strength_claims_claim_id_evidence_strength_get(claim_id)

Claim Evidence Strength

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
        # Claim Evidence Strength
        api_response = api_instance.claim_evidence_strength_claims_claim_id_evidence_strength_get(claim_id)
        print("The response of ClaimsApi->claim_evidence_strength_claims_claim_id_evidence_strength_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ClaimsApi->claim_evidence_strength_claims_claim_id_evidence_strength_get: %s\n" % e)
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

# **claim_forecast_claims_claim_id_forecast_get**
> object claim_forecast_claims_claim_id_forecast_get(claim_id)

Claim Forecast

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
        # Claim Forecast
        api_response = api_instance.claim_forecast_claims_claim_id_forecast_get(claim_id)
        print("The response of ClaimsApi->claim_forecast_claims_claim_id_forecast_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ClaimsApi->claim_forecast_claims_claim_id_forecast_get: %s\n" % e)
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

# **claim_negotiation_intel_claims_claim_id_negotiation_intel_get**
> object claim_negotiation_intel_claims_claim_id_negotiation_intel_get(claim_id)

Claim Negotiation Intel

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
        # Claim Negotiation Intel
        api_response = api_instance.claim_negotiation_intel_claims_claim_id_negotiation_intel_get(claim_id)
        print("The response of ClaimsApi->claim_negotiation_intel_claims_claim_id_negotiation_intel_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ClaimsApi->claim_negotiation_intel_claims_claim_id_negotiation_intel_get: %s\n" % e)
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

# **claim_playbook_claims_claim_id_playbook_get**
> object claim_playbook_claims_claim_id_playbook_get(claim_id)

Claim Playbook

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
        # Claim Playbook
        api_response = api_instance.claim_playbook_claims_claim_id_playbook_get(claim_id)
        print("The response of ClaimsApi->claim_playbook_claims_claim_id_playbook_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ClaimsApi->claim_playbook_claims_claim_id_playbook_get: %s\n" % e)
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

# **claim_sla_prediction_claims_claim_id_sla_prediction_get**
> object claim_sla_prediction_claims_claim_id_sla_prediction_get(claim_id)

Claim Sla Prediction

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
        # Claim Sla Prediction
        api_response = api_instance.claim_sla_prediction_claims_claim_id_sla_prediction_get(claim_id)
        print("The response of ClaimsApi->claim_sla_prediction_claims_claim_id_sla_prediction_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ClaimsApi->claim_sla_prediction_claims_claim_id_sla_prediction_get: %s\n" % e)
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

# **claim_strength_explainer_claims_claim_id_strength_explainer_get**
> object claim_strength_explainer_claims_claim_id_strength_explainer_get(claim_id)

Claim Strength Explainer

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
        # Claim Strength Explainer
        api_response = api_instance.claim_strength_explainer_claims_claim_id_strength_explainer_get(claim_id)
        print("The response of ClaimsApi->claim_strength_explainer_claims_claim_id_strength_explainer_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ClaimsApi->claim_strength_explainer_claims_claim_id_strength_explainer_get: %s\n" % e)
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

# **create_claim_for_artist_artists_artist_id_claims_post**
> ClaimSchema create_claim_for_artist_artists_artist_id_claims_post(artist_id, claim_create_request)

Create Claim For Artist

### Example

* Bearer Authentication (HTTPBearer):

```python
import xr7_sdk
from xr7_sdk.models.claim_create_request import ClaimCreateRequest
from xr7_sdk.models.claim_schema import ClaimSchema
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
    api_instance = xr7_sdk.ClaimsApi(api_client)
    artist_id = 'artist_id_example' # str |
    claim_create_request = xr7_sdk.ClaimCreateRequest() # ClaimCreateRequest |

    try:
        # Create Claim For Artist
        api_response = api_instance.create_claim_for_artist_artists_artist_id_claims_post(artist_id, claim_create_request)
        print("The response of ClaimsApi->create_claim_for_artist_artists_artist_id_claims_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ClaimsApi->create_claim_for_artist_artists_artist_id_claims_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **artist_id** | **str**|  |
 **claim_create_request** | [**ClaimCreateRequest**](ClaimCreateRequest.md)|  |

### Return type

[**ClaimSchema**](ClaimSchema.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **escalate_legal_claims_claim_id_escalate_legal_post**
> object escalate_legal_claims_claim_id_escalate_legal_post(claim_id)

Escalate Legal

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
        # Escalate Legal
        api_response = api_instance.escalate_legal_claims_claim_id_escalate_legal_post(claim_id)
        print("The response of ClaimsApi->escalate_legal_claims_claim_id_escalate_legal_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ClaimsApi->escalate_legal_claims_claim_id_escalate_legal_post: %s\n" % e)
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

# **export_evidence_packet_expert_mode_claims_claim_id_evidence_export_post**
> object export_evidence_packet_expert_mode_claims_claim_id_evidence_export_post(claim_id, mode=mode)

Export Evidence Packet Expert Mode

Export evidence with optional expert witness mode for arbitration/litigation workflows.

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
    mode = 'standard' # str |  (optional) (default to 'standard')

    try:
        # Export Evidence Packet Expert Mode
        api_response = api_instance.export_evidence_packet_expert_mode_claims_claim_id_evidence_export_post(claim_id, mode=mode)
        print("The response of ClaimsApi->export_evidence_packet_expert_mode_claims_claim_id_evidence_export_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ClaimsApi->export_evidence_packet_expert_mode_claims_claim_id_evidence_export_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **claim_id** | **str**|  |
 **mode** | **str**|  | [optional] [default to &#39;standard&#39;]

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

# **generate_attorney_evidence_file_api_claims_claim_id_attorney_evidence_post**
> object generate_attorney_evidence_file_api_claims_claim_id_attorney_evidence_post(claim_id, attorney_evidence_request)

Generate Attorney Evidence File

### Example


```python
import xr7_sdk
from xr7_sdk.models.attorney_evidence_request import AttorneyEvidenceRequest
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
    attorney_evidence_request = xr7_sdk.AttorneyEvidenceRequest() # AttorneyEvidenceRequest |

    try:
        # Generate Attorney Evidence File
        api_response = api_instance.generate_attorney_evidence_file_api_claims_claim_id_attorney_evidence_post(claim_id, attorney_evidence_request)
        print("The response of ClaimsApi->generate_attorney_evidence_file_api_claims_claim_id_attorney_evidence_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ClaimsApi->generate_attorney_evidence_file_api_claims_claim_id_attorney_evidence_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **claim_id** | **str**|  |
 **attorney_evidence_request** | [**AttorneyEvidenceRequest**](AttorneyEvidenceRequest.md)|  |

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

# **generate_attorney_evidence_file_claims_claim_id_attorney_evidence_post**
> object generate_attorney_evidence_file_claims_claim_id_attorney_evidence_post(claim_id, attorney_evidence_request)

Generate Attorney Evidence File

### Example


```python
import xr7_sdk
from xr7_sdk.models.attorney_evidence_request import AttorneyEvidenceRequest
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
    attorney_evidence_request = xr7_sdk.AttorneyEvidenceRequest() # AttorneyEvidenceRequest |

    try:
        # Generate Attorney Evidence File
        api_response = api_instance.generate_attorney_evidence_file_claims_claim_id_attorney_evidence_post(claim_id, attorney_evidence_request)
        print("The response of ClaimsApi->generate_attorney_evidence_file_claims_claim_id_attorney_evidence_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ClaimsApi->generate_attorney_evidence_file_claims_claim_id_attorney_evidence_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **claim_id** | **str**|  |
 **attorney_evidence_request** | [**AttorneyEvidenceRequest**](AttorneyEvidenceRequest.md)|  |

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

# **get_evidence_claims_claim_id_evidence_get**
> object get_evidence_claims_claim_id_evidence_get(claim_id)

Get Evidence

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
    api_instance = xr7_sdk.ClaimsApi(api_client)
    claim_id = 'claim_id_example' # str |

    try:
        # Get Evidence
        api_response = api_instance.get_evidence_claims_claim_id_evidence_get(claim_id)
        print("The response of ClaimsApi->get_evidence_claims_claim_id_evidence_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ClaimsApi->get_evidence_claims_claim_id_evidence_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **claim_id** | **str**|  |

### Return type

**object**

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

# **list_claims_artists_artist_id_claims_get**
> object list_claims_artists_artist_id_claims_get(artist_id)

List Claims

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
