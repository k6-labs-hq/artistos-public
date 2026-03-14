# xr7_sdk.IntelligenceApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_outcome_feedback_artists_artist_id_intelligence_feedback_post**](IntelligenceApi.md#create_outcome_feedback_artists_artist_id_intelligence_feedback_post) | **POST** /artists/{artist_id}/intelligence/feedback | Create Outcome Feedback
[**extract_contract_terms_artists_artist_id_intelligence_contracts_extract_post**](IntelligenceApi.md#extract_contract_terms_artists_artist_id_intelligence_contracts_extract_post) | **POST** /artists/{artist_id}/intelligence/contracts/extract | Extract Contract Terms
[**extract_contract_terms_upload_artists_artist_id_intelligence_contracts_extract_upload_post**](IntelligenceApi.md#extract_contract_terms_upload_artists_artist_id_intelligence_contracts_extract_upload_post) | **POST** /artists/{artist_id}/intelligence/contracts/extract-upload | Extract Contract Terms Upload
[**get_calibration_health_artists_artist_id_intelligence_calibration_get**](IntelligenceApi.md#get_calibration_health_artists_artist_id_intelligence_calibration_get) | **GET** /artists/{artist_id}/intelligence/calibration | Get Calibration Health
[**ingest_royalty_ledger_artists_artist_id_intelligence_ledger_ingest_post**](IntelligenceApi.md#ingest_royalty_ledger_artists_artist_id_intelligence_ledger_ingest_post) | **POST** /artists/{artist_id}/intelligence/ledger/ingest | Ingest Royalty Ledger
[**list_feedback_events_artists_artist_id_intelligence_feedback_events_get**](IntelligenceApi.md#list_feedback_events_artists_artist_id_intelligence_feedback_events_get) | **GET** /artists/{artist_id}/intelligence/feedback/events | List Feedback Events
[**rank_by_expected_utility_artists_artist_id_intelligence_rank_utility_post**](IntelligenceApi.md#rank_by_expected_utility_artists_artist_id_intelligence_rank_utility_post) | **POST** /artists/{artist_id}/intelligence/rank-utility | Rank By Expected Utility
[**simulate_expected_payout_artists_artist_id_intelligence_simulate_expected_payout_post**](IntelligenceApi.md#simulate_expected_payout_artists_artist_id_intelligence_simulate_expected_payout_post) | **POST** /artists/{artist_id}/intelligence/simulate-expected-payout | Simulate Expected Payout


# **create_outcome_feedback_artists_artist_id_intelligence_feedback_post**
> RecoveryOutcomeFeedbackSchema create_outcome_feedback_artists_artist_id_intelligence_feedback_post(artist_id, structured_feedback_request)

Create Outcome Feedback

### Example


```python
import xr7_sdk
from xr7_sdk.models.recovery_outcome_feedback_schema import RecoveryOutcomeFeedbackSchema
from xr7_sdk.models.structured_feedback_request import StructuredFeedbackRequest
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
    api_instance = xr7_sdk.IntelligenceApi(api_client)
    artist_id = 'artist_id_example' # str | 
    structured_feedback_request = xr7_sdk.StructuredFeedbackRequest() # StructuredFeedbackRequest | 

    try:
        # Create Outcome Feedback
        api_response = api_instance.create_outcome_feedback_artists_artist_id_intelligence_feedback_post(artist_id, structured_feedback_request)
        print("The response of IntelligenceApi->create_outcome_feedback_artists_artist_id_intelligence_feedback_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling IntelligenceApi->create_outcome_feedback_artists_artist_id_intelligence_feedback_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **artist_id** | **str**|  | 
 **structured_feedback_request** | [**StructuredFeedbackRequest**](StructuredFeedbackRequest.md)|  | 

### Return type

[**RecoveryOutcomeFeedbackSchema**](RecoveryOutcomeFeedbackSchema.md)

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

# **extract_contract_terms_artists_artist_id_intelligence_contracts_extract_post**
> object extract_contract_terms_artists_artist_id_intelligence_contracts_extract_post(artist_id, contract_extract_request)

Extract Contract Terms

### Example


```python
import xr7_sdk
from xr7_sdk.models.contract_extract_request import ContractExtractRequest
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
    api_instance = xr7_sdk.IntelligenceApi(api_client)
    artist_id = 'artist_id_example' # str | 
    contract_extract_request = xr7_sdk.ContractExtractRequest() # ContractExtractRequest | 

    try:
        # Extract Contract Terms
        api_response = api_instance.extract_contract_terms_artists_artist_id_intelligence_contracts_extract_post(artist_id, contract_extract_request)
        print("The response of IntelligenceApi->extract_contract_terms_artists_artist_id_intelligence_contracts_extract_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling IntelligenceApi->extract_contract_terms_artists_artist_id_intelligence_contracts_extract_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **artist_id** | **str**|  | 
 **contract_extract_request** | [**ContractExtractRequest**](ContractExtractRequest.md)|  | 

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

# **extract_contract_terms_upload_artists_artist_id_intelligence_contracts_extract_upload_post**
> object extract_contract_terms_upload_artists_artist_id_intelligence_contracts_extract_upload_post(artist_id, file, contract_id=contract_id, effective_start=effective_start, effective_end=effective_end, extracted_from=extracted_from)

Extract Contract Terms Upload

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
    api_instance = xr7_sdk.IntelligenceApi(api_client)
    artist_id = 'artist_id_example' # str | 
    file = 'file_example' # str | 
    contract_id = 'contract_id_example' # str |  (optional)
    effective_start = 'effective_start_example' # str |  (optional)
    effective_end = 'effective_end_example' # str |  (optional)
    extracted_from = 'extracted_from_example' # str |  (optional)

    try:
        # Extract Contract Terms Upload
        api_response = api_instance.extract_contract_terms_upload_artists_artist_id_intelligence_contracts_extract_upload_post(artist_id, file, contract_id=contract_id, effective_start=effective_start, effective_end=effective_end, extracted_from=extracted_from)
        print("The response of IntelligenceApi->extract_contract_terms_upload_artists_artist_id_intelligence_contracts_extract_upload_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling IntelligenceApi->extract_contract_terms_upload_artists_artist_id_intelligence_contracts_extract_upload_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **artist_id** | **str**|  | 
 **file** | **str**|  | 
 **contract_id** | **str**|  | [optional] 
 **effective_start** | **str**|  | [optional] 
 **effective_end** | **str**|  | [optional] 
 **extracted_from** | **str**|  | [optional] 

### Return type

**object**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: multipart/form-data
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_calibration_health_artists_artist_id_intelligence_calibration_get**
> object get_calibration_health_artists_artist_id_intelligence_calibration_get(artist_id)

Get Calibration Health

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
    api_instance = xr7_sdk.IntelligenceApi(api_client)
    artist_id = 'artist_id_example' # str | 

    try:
        # Get Calibration Health
        api_response = api_instance.get_calibration_health_artists_artist_id_intelligence_calibration_get(artist_id)
        print("The response of IntelligenceApi->get_calibration_health_artists_artist_id_intelligence_calibration_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling IntelligenceApi->get_calibration_health_artists_artist_id_intelligence_calibration_get: %s\n" % e)
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

# **ingest_royalty_ledger_artists_artist_id_intelligence_ledger_ingest_post**
> object ingest_royalty_ledger_artists_artist_id_intelligence_ledger_ingest_post(artist_id, ledger_ingest_request)

Ingest Royalty Ledger

### Example


```python
import xr7_sdk
from xr7_sdk.models.ledger_ingest_request import LedgerIngestRequest
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
    api_instance = xr7_sdk.IntelligenceApi(api_client)
    artist_id = 'artist_id_example' # str | 
    ledger_ingest_request = xr7_sdk.LedgerIngestRequest() # LedgerIngestRequest | 

    try:
        # Ingest Royalty Ledger
        api_response = api_instance.ingest_royalty_ledger_artists_artist_id_intelligence_ledger_ingest_post(artist_id, ledger_ingest_request)
        print("The response of IntelligenceApi->ingest_royalty_ledger_artists_artist_id_intelligence_ledger_ingest_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling IntelligenceApi->ingest_royalty_ledger_artists_artist_id_intelligence_ledger_ingest_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **artist_id** | **str**|  | 
 **ledger_ingest_request** | [**LedgerIngestRequest**](LedgerIngestRequest.md)|  | 

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

# **list_feedback_events_artists_artist_id_intelligence_feedback_events_get**
> List[MLFeedbackEventSchema] list_feedback_events_artists_artist_id_intelligence_feedback_events_get(artist_id)

List Feedback Events

### Example


```python
import xr7_sdk
from xr7_sdk.models.ml_feedback_event_schema import MLFeedbackEventSchema
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
    api_instance = xr7_sdk.IntelligenceApi(api_client)
    artist_id = 'artist_id_example' # str | 

    try:
        # List Feedback Events
        api_response = api_instance.list_feedback_events_artists_artist_id_intelligence_feedback_events_get(artist_id)
        print("The response of IntelligenceApi->list_feedback_events_artists_artist_id_intelligence_feedback_events_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling IntelligenceApi->list_feedback_events_artists_artist_id_intelligence_feedback_events_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **artist_id** | **str**|  | 

### Return type

[**List[MLFeedbackEventSchema]**](MLFeedbackEventSchema.md)

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

# **rank_by_expected_utility_artists_artist_id_intelligence_rank_utility_post**
> object rank_by_expected_utility_artists_artist_id_intelligence_rank_utility_post(artist_id, utility_rank_request)

Rank By Expected Utility

### Example


```python
import xr7_sdk
from xr7_sdk.models.utility_rank_request import UtilityRankRequest
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
    api_instance = xr7_sdk.IntelligenceApi(api_client)
    artist_id = 'artist_id_example' # str | 
    utility_rank_request = xr7_sdk.UtilityRankRequest() # UtilityRankRequest | 

    try:
        # Rank By Expected Utility
        api_response = api_instance.rank_by_expected_utility_artists_artist_id_intelligence_rank_utility_post(artist_id, utility_rank_request)
        print("The response of IntelligenceApi->rank_by_expected_utility_artists_artist_id_intelligence_rank_utility_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling IntelligenceApi->rank_by_expected_utility_artists_artist_id_intelligence_rank_utility_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **artist_id** | **str**|  | 
 **utility_rank_request** | [**UtilityRankRequest**](UtilityRankRequest.md)|  | 

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

# **simulate_expected_payout_artists_artist_id_intelligence_simulate_expected_payout_post**
> object simulate_expected_payout_artists_artist_id_intelligence_simulate_expected_payout_post(artist_id, simulate_payout_request)

Simulate Expected Payout

### Example


```python
import xr7_sdk
from xr7_sdk.models.simulate_payout_request import SimulatePayoutRequest
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
    api_instance = xr7_sdk.IntelligenceApi(api_client)
    artist_id = 'artist_id_example' # str | 
    simulate_payout_request = xr7_sdk.SimulatePayoutRequest() # SimulatePayoutRequest | 

    try:
        # Simulate Expected Payout
        api_response = api_instance.simulate_expected_payout_artists_artist_id_intelligence_simulate_expected_payout_post(artist_id, simulate_payout_request)
        print("The response of IntelligenceApi->simulate_expected_payout_artists_artist_id_intelligence_simulate_expected_payout_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling IntelligenceApi->simulate_expected_payout_artists_artist_id_intelligence_simulate_expected_payout_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **artist_id** | **str**|  | 
 **simulate_payout_request** | [**SimulatePayoutRequest**](SimulatePayoutRequest.md)|  | 

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

