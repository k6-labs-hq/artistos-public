# xr7_sdk.IntelligenceApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**catalog_valuation_artists_artist_id_ml_catalog_valuation_post**](IntelligenceApi.md#catalog_valuation_artists_artist_id_ml_catalog_valuation_post) | **POST** /artists/{artist_id}/ml/catalog-valuation | Catalog Valuation
[**create_outcome_feedback_artists_artist_id_intelligence_feedback_post**](IntelligenceApi.md#create_outcome_feedback_artists_artist_id_intelligence_feedback_post) | **POST** /artists/{artist_id}/intelligence/feedback | Create Outcome Feedback
[**extract_contract_terms_artists_artist_id_intelligence_contracts_extract_post**](IntelligenceApi.md#extract_contract_terms_artists_artist_id_intelligence_contracts_extract_post) | **POST** /artists/{artist_id}/intelligence/contracts/extract | Extract Contract Terms
[**extract_contract_terms_upload_artists_artist_id_intelligence_contracts_extract_upload_post**](IntelligenceApi.md#extract_contract_terms_upload_artists_artist_id_intelligence_contracts_extract_upload_post) | **POST** /artists/{artist_id}/intelligence/contracts/extract-upload | Extract Contract Terms Upload
[**financing_matches_artists_artist_id_ml_financing_matches_post**](IntelligenceApi.md#financing_matches_artists_artist_id_ml_financing_matches_post) | **POST** /artists/{artist_id}/ml/financing-matches | Financing Matches
[**get_calibration_health_artists_artist_id_intelligence_calibration_get**](IntelligenceApi.md#get_calibration_health_artists_artist_id_intelligence_calibration_get) | **GET** /artists/{artist_id}/intelligence/calibration | Get Calibration Health
[**ingest_royalty_ledger_artists_artist_id_intelligence_ledger_ingest_post**](IntelligenceApi.md#ingest_royalty_ledger_artists_artist_id_intelligence_ledger_ingest_post) | **POST** /artists/{artist_id}/intelligence/ledger/ingest | Ingest Royalty Ledger
[**list_feedback_events_artists_artist_id_intelligence_feedback_events_get**](IntelligenceApi.md#list_feedback_events_artists_artist_id_intelligence_feedback_events_get) | **GET** /artists/{artist_id}/intelligence/feedback/events | List Feedback Events
[**pre_signature_contract_review_artists_artist_id_intelligence_contracts_pre_signature_review_post**](IntelligenceApi.md#pre_signature_contract_review_artists_artist_id_intelligence_contracts_pre_signature_review_post) | **POST** /artists/{artist_id}/intelligence/contracts/pre-signature-review | Pre Signature Contract Review
[**rank_by_expected_utility_artists_artist_id_intelligence_rank_utility_post**](IntelligenceApi.md#rank_by_expected_utility_artists_artist_id_intelligence_rank_utility_post) | **POST** /artists/{artist_id}/intelligence/rank-utility | Rank By Expected Utility
[**registration_auto_fix_artists_artist_id_registration_auto_fix_post**](IntelligenceApi.md#registration_auto_fix_artists_artist_id_registration_auto_fix_post) | **POST** /artists/{artist_id}/registration/auto-fix | Registration Auto Fix
[**registration_status_artists_artist_id_registration_status_get**](IntelligenceApi.md#registration_status_artists_artist_id_registration_status_get) | **GET** /artists/{artist_id}/registration/status | Registration Status
[**run_catalog_audit_on_demand_artists_artist_id_ml_catalog_audit_post**](IntelligenceApi.md#run_catalog_audit_on_demand_artists_artist_id_ml_catalog_audit_post) | **POST** /artists/{artist_id}/ml/catalog-audit | Run Catalog Audit On Demand
[**run_tax_optimizer_artists_artist_id_intelligence_tax_optimizer_post**](IntelligenceApi.md#run_tax_optimizer_artists_artist_id_intelligence_tax_optimizer_post) | **POST** /artists/{artist_id}/intelligence/tax-optimizer | Run Tax Optimizer
[**simulate_expected_payout_artists_artist_id_intelligence_simulate_expected_payout_post**](IntelligenceApi.md#simulate_expected_payout_artists_artist_id_intelligence_simulate_expected_payout_post) | **POST** /artists/{artist_id}/intelligence/simulate-expected-payout | Simulate Expected Payout
[**simulate_optimization_artists_artist_id_ml_simulate_optimization_post**](IntelligenceApi.md#simulate_optimization_artists_artist_id_ml_simulate_optimization_post) | **POST** /artists/{artist_id}/ml/simulate-optimization | Simulate Optimization


# **catalog_valuation_artists_artist_id_ml_catalog_valuation_post**
> object catalog_valuation_artists_artist_id_ml_catalog_valuation_post(artist_id)

Catalog Valuation

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
        # Catalog Valuation
        api_response = api_instance.catalog_valuation_artists_artist_id_ml_catalog_valuation_post(artist_id)
        print("The response of IntelligenceApi->catalog_valuation_artists_artist_id_ml_catalog_valuation_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling IntelligenceApi->catalog_valuation_artists_artist_id_ml_catalog_valuation_post: %s\n" % e)
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

# **financing_matches_artists_artist_id_ml_financing_matches_post**
> object financing_matches_artists_artist_id_ml_financing_matches_post(artist_id)

Financing Matches

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
        # Financing Matches
        api_response = api_instance.financing_matches_artists_artist_id_ml_financing_matches_post(artist_id)
        print("The response of IntelligenceApi->financing_matches_artists_artist_id_ml_financing_matches_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling IntelligenceApi->financing_matches_artists_artist_id_ml_financing_matches_post: %s\n" % e)
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

# **pre_signature_contract_review_artists_artist_id_intelligence_contracts_pre_signature_review_post**
> object pre_signature_contract_review_artists_artist_id_intelligence_contracts_pre_signature_review_post(artist_id, pre_signature_contract_review_request)

Pre Signature Contract Review

### Example


```python
import xr7_sdk
from xr7_sdk.models.pre_signature_contract_review_request import PreSignatureContractReviewRequest
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
    pre_signature_contract_review_request = xr7_sdk.PreSignatureContractReviewRequest() # PreSignatureContractReviewRequest |

    try:
        # Pre Signature Contract Review
        api_response = api_instance.pre_signature_contract_review_artists_artist_id_intelligence_contracts_pre_signature_review_post(artist_id, pre_signature_contract_review_request)
        print("The response of IntelligenceApi->pre_signature_contract_review_artists_artist_id_intelligence_contracts_pre_signature_review_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling IntelligenceApi->pre_signature_contract_review_artists_artist_id_intelligence_contracts_pre_signature_review_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **artist_id** | **str**|  |
 **pre_signature_contract_review_request** | [**PreSignatureContractReviewRequest**](PreSignatureContractReviewRequest.md)|  |

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

# **registration_auto_fix_artists_artist_id_registration_auto_fix_post**
> object registration_auto_fix_artists_artist_id_registration_auto_fix_post(artist_id)

Registration Auto Fix

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
        # Registration Auto Fix
        api_response = api_instance.registration_auto_fix_artists_artist_id_registration_auto_fix_post(artist_id)
        print("The response of IntelligenceApi->registration_auto_fix_artists_artist_id_registration_auto_fix_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling IntelligenceApi->registration_auto_fix_artists_artist_id_registration_auto_fix_post: %s\n" % e)
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

# **registration_status_artists_artist_id_registration_status_get**
> object registration_status_artists_artist_id_registration_status_get(artist_id)

Registration Status

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
        # Registration Status
        api_response = api_instance.registration_status_artists_artist_id_registration_status_get(artist_id)
        print("The response of IntelligenceApi->registration_status_artists_artist_id_registration_status_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling IntelligenceApi->registration_status_artists_artist_id_registration_status_get: %s\n" % e)
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

# **run_catalog_audit_on_demand_artists_artist_id_ml_catalog_audit_post**
> object run_catalog_audit_on_demand_artists_artist_id_ml_catalog_audit_post(artist_id)

Run Catalog Audit On Demand

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
        # Run Catalog Audit On Demand
        api_response = api_instance.run_catalog_audit_on_demand_artists_artist_id_ml_catalog_audit_post(artist_id)
        print("The response of IntelligenceApi->run_catalog_audit_on_demand_artists_artist_id_ml_catalog_audit_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling IntelligenceApi->run_catalog_audit_on_demand_artists_artist_id_ml_catalog_audit_post: %s\n" % e)
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

# **run_tax_optimizer_artists_artist_id_intelligence_tax_optimizer_post**
> object run_tax_optimizer_artists_artist_id_intelligence_tax_optimizer_post(artist_id, tax_optimizer_request)

Run Tax Optimizer

### Example


```python
import xr7_sdk
from xr7_sdk.models.tax_optimizer_request import TaxOptimizerRequest
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
    tax_optimizer_request = xr7_sdk.TaxOptimizerRequest() # TaxOptimizerRequest |

    try:
        # Run Tax Optimizer
        api_response = api_instance.run_tax_optimizer_artists_artist_id_intelligence_tax_optimizer_post(artist_id, tax_optimizer_request)
        print("The response of IntelligenceApi->run_tax_optimizer_artists_artist_id_intelligence_tax_optimizer_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling IntelligenceApi->run_tax_optimizer_artists_artist_id_intelligence_tax_optimizer_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **artist_id** | **str**|  |
 **tax_optimizer_request** | [**TaxOptimizerRequest**](TaxOptimizerRequest.md)|  |

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

# **simulate_optimization_artists_artist_id_ml_simulate_optimization_post**
> object simulate_optimization_artists_artist_id_ml_simulate_optimization_post(artist_id, optimization_simulation_request)

Simulate Optimization

### Example


```python
import xr7_sdk
from xr7_sdk.models.optimization_simulation_request import OptimizationSimulationRequest
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
    optimization_simulation_request = xr7_sdk.OptimizationSimulationRequest() # OptimizationSimulationRequest |

    try:
        # Simulate Optimization
        api_response = api_instance.simulate_optimization_artists_artist_id_ml_simulate_optimization_post(artist_id, optimization_simulation_request)
        print("The response of IntelligenceApi->simulate_optimization_artists_artist_id_ml_simulate_optimization_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling IntelligenceApi->simulate_optimization_artists_artist_id_ml_simulate_optimization_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **artist_id** | **str**|  |
 **optimization_simulation_request** | [**OptimizationSimulationRequest**](OptimizationSimulationRequest.md)|  |

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
