# xr7_sdk.TvfilmApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**run_tvfilm_agents_tvfilm_artists_artist_id_agents_run_post**](TvfilmApi.md#run_tvfilm_agents_tvfilm_artists_artist_id_agents_run_post) | **POST** /tvfilm/artists/{artist_id}/agents/run | Run Tvfilm Agents
[**tvfilm_anomaly_rule_catalog_tvfilm_catalogs_anomaly_rules_get**](TvfilmApi.md#tvfilm_anomaly_rule_catalog_tvfilm_catalogs_anomaly_rules_get) | **GET** /tvfilm/catalogs/anomaly-rules | Tvfilm Anomaly Rule Catalog
[**tvfilm_bulk_draft_claims_tvfilm_artists_artist_id_claims_bulk_draft_post**](TvfilmApi.md#tvfilm_bulk_draft_claims_tvfilm_artists_artist_id_claims_bulk_draft_post) | **POST** /tvfilm/artists/{artist_id}/claims/bulk-draft | Tvfilm Bulk Draft Claims
[**tvfilm_bulk_export_claims_tvfilm_artists_artist_id_claims_bulk_export_post**](TvfilmApi.md#tvfilm_bulk_export_claims_tvfilm_artists_artist_id_claims_bulk_export_post) | **POST** /tvfilm/artists/{artist_id}/claims/bulk-export | Tvfilm Bulk Export Claims
[**tvfilm_calculation_audit_tvfilm_artists_artist_id_calculation_audit_get**](TvfilmApi.md#tvfilm_calculation_audit_tvfilm_artists_artist_id_calculation_audit_get) | **GET** /tvfilm/artists/{artist_id}/calculation-audit | Tvfilm Calculation Audit
[**tvfilm_dashboard_tvfilm_artists_artist_id_dashboard_get**](TvfilmApi.md#tvfilm_dashboard_tvfilm_artists_artist_id_dashboard_get) | **GET** /tvfilm/artists/{artist_id}/dashboard | Tvfilm Dashboard
[**tvfilm_draft_claims_tvfilm_artists_artist_id_claims_draft_post**](TvfilmApi.md#tvfilm_draft_claims_tvfilm_artists_artist_id_claims_draft_post) | **POST** /tvfilm/artists/{artist_id}/claims/draft | Tvfilm Draft Claims
[**tvfilm_enterprise_portfolio_analyze_tvfilm_enterprise_portfolio_analyze_post**](TvfilmApi.md#tvfilm_enterprise_portfolio_analyze_tvfilm_enterprise_portfolio_analyze_post) | **POST** /tvfilm/enterprise/portfolio/analyze | Tvfilm Enterprise Portfolio Analyze
[**tvfilm_enterprise_portfolio_job_tvfilm_enterprise_portfolio_job_id_get**](TvfilmApi.md#tvfilm_enterprise_portfolio_job_tvfilm_enterprise_portfolio_job_id_get) | **GET** /tvfilm/enterprise/portfolio/{job_id} | Tvfilm Enterprise Portfolio Job
[**tvfilm_evidence_templates_tvfilm_catalogs_evidence_templates_get**](TvfilmApi.md#tvfilm_evidence_templates_tvfilm_catalogs_evidence_templates_get) | **GET** /tvfilm/catalogs/evidence-templates | Tvfilm Evidence Templates
[**tvfilm_export_evidence_packet_tvfilm_claims_claim_id_evidence_export_get**](TvfilmApi.md#tvfilm_export_evidence_packet_tvfilm_claims_claim_id_evidence_export_get) | **GET** /tvfilm/claims/{claim_id}/evidence/export | Tvfilm Export Evidence Packet
[**tvfilm_forecast_tvfilm_artists_artist_id_forecast_post**](TvfilmApi.md#tvfilm_forecast_tvfilm_artists_artist_id_forecast_post) | **POST** /tvfilm/artists/{artist_id}/forecast | Tvfilm Forecast
[**tvfilm_ingestion_commit_tvfilm_artists_artist_id_ingestion_commit_post**](TvfilmApi.md#tvfilm_ingestion_commit_tvfilm_artists_artist_id_ingestion_commit_post) | **POST** /tvfilm/artists/{artist_id}/ingestion/commit | Tvfilm Ingestion Commit
[**tvfilm_ingestion_formats_tvfilm_ingestion_formats_get**](TvfilmApi.md#tvfilm_ingestion_formats_tvfilm_ingestion_formats_get) | **GET** /tvfilm/ingestion/formats | Tvfilm Ingestion Formats
[**tvfilm_ingestion_preview_tvfilm_ingestion_preview_post**](TvfilmApi.md#tvfilm_ingestion_preview_tvfilm_ingestion_preview_post) | **POST** /tvfilm/ingestion/preview | Tvfilm Ingestion Preview
[**tvfilm_role_options_tvfilm_roles_options_get**](TvfilmApi.md#tvfilm_role_options_tvfilm_roles_options_get) | **GET** /tvfilm/roles/options | Tvfilm Role Options
[**tvfilm_scan_anomalies_tvfilm_artists_artist_id_anomalies_scan_post**](TvfilmApi.md#tvfilm_scan_anomalies_tvfilm_artists_artist_id_anomalies_scan_post) | **POST** /tvfilm/artists/{artist_id}/anomalies/scan | Tvfilm Scan Anomalies
[**tvfilm_trust_explain_tvfilm_trust_explain_post**](TvfilmApi.md#tvfilm_trust_explain_tvfilm_trust_explain_post) | **POST** /tvfilm/trust/explain | Tvfilm Trust Explain


# **run_tvfilm_agents_tvfilm_artists_artist_id_agents_run_post**
> object run_tvfilm_agents_tvfilm_artists_artist_id_agents_run_post(artist_id)

Run Tvfilm Agents

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
    api_instance = xr7_sdk.TvfilmApi(api_client)
    artist_id = 'artist_id_example' # str | 

    try:
        # Run Tvfilm Agents
        api_response = api_instance.run_tvfilm_agents_tvfilm_artists_artist_id_agents_run_post(artist_id)
        print("The response of TvfilmApi->run_tvfilm_agents_tvfilm_artists_artist_id_agents_run_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TvfilmApi->run_tvfilm_agents_tvfilm_artists_artist_id_agents_run_post: %s\n" % e)
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

# **tvfilm_anomaly_rule_catalog_tvfilm_catalogs_anomaly_rules_get**
> object tvfilm_anomaly_rule_catalog_tvfilm_catalogs_anomaly_rules_get()

Tvfilm Anomaly Rule Catalog

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
    api_instance = xr7_sdk.TvfilmApi(api_client)

    try:
        # Tvfilm Anomaly Rule Catalog
        api_response = api_instance.tvfilm_anomaly_rule_catalog_tvfilm_catalogs_anomaly_rules_get()
        print("The response of TvfilmApi->tvfilm_anomaly_rule_catalog_tvfilm_catalogs_anomaly_rules_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TvfilmApi->tvfilm_anomaly_rule_catalog_tvfilm_catalogs_anomaly_rules_get: %s\n" % e)
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

# **tvfilm_bulk_draft_claims_tvfilm_artists_artist_id_claims_bulk_draft_post**
> object tvfilm_bulk_draft_claims_tvfilm_artists_artist_id_claims_bulk_draft_post(artist_id, tv_film_bulk_claim_draft_request)

Tvfilm Bulk Draft Claims

### Example


```python
import xr7_sdk
from xr7_sdk.models.tv_film_bulk_claim_draft_request import TVFilmBulkClaimDraftRequest
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
    api_instance = xr7_sdk.TvfilmApi(api_client)
    artist_id = 'artist_id_example' # str | 
    tv_film_bulk_claim_draft_request = xr7_sdk.TVFilmBulkClaimDraftRequest() # TVFilmBulkClaimDraftRequest | 

    try:
        # Tvfilm Bulk Draft Claims
        api_response = api_instance.tvfilm_bulk_draft_claims_tvfilm_artists_artist_id_claims_bulk_draft_post(artist_id, tv_film_bulk_claim_draft_request)
        print("The response of TvfilmApi->tvfilm_bulk_draft_claims_tvfilm_artists_artist_id_claims_bulk_draft_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TvfilmApi->tvfilm_bulk_draft_claims_tvfilm_artists_artist_id_claims_bulk_draft_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **artist_id** | **str**|  | 
 **tv_film_bulk_claim_draft_request** | [**TVFilmBulkClaimDraftRequest**](TVFilmBulkClaimDraftRequest.md)|  | 

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

# **tvfilm_bulk_export_claims_tvfilm_artists_artist_id_claims_bulk_export_post**
> object tvfilm_bulk_export_claims_tvfilm_artists_artist_id_claims_bulk_export_post(artist_id, tv_film_bulk_export_request)

Tvfilm Bulk Export Claims

### Example


```python
import xr7_sdk
from xr7_sdk.models.tv_film_bulk_export_request import TVFilmBulkExportRequest
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
    api_instance = xr7_sdk.TvfilmApi(api_client)
    artist_id = 'artist_id_example' # str | 
    tv_film_bulk_export_request = xr7_sdk.TVFilmBulkExportRequest() # TVFilmBulkExportRequest | 

    try:
        # Tvfilm Bulk Export Claims
        api_response = api_instance.tvfilm_bulk_export_claims_tvfilm_artists_artist_id_claims_bulk_export_post(artist_id, tv_film_bulk_export_request)
        print("The response of TvfilmApi->tvfilm_bulk_export_claims_tvfilm_artists_artist_id_claims_bulk_export_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TvfilmApi->tvfilm_bulk_export_claims_tvfilm_artists_artist_id_claims_bulk_export_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **artist_id** | **str**|  | 
 **tv_film_bulk_export_request** | [**TVFilmBulkExportRequest**](TVFilmBulkExportRequest.md)|  | 

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

# **tvfilm_calculation_audit_tvfilm_artists_artist_id_calculation_audit_get**
> object tvfilm_calculation_audit_tvfilm_artists_artist_id_calculation_audit_get(artist_id)

Tvfilm Calculation Audit

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
    api_instance = xr7_sdk.TvfilmApi(api_client)
    artist_id = 'artist_id_example' # str | 

    try:
        # Tvfilm Calculation Audit
        api_response = api_instance.tvfilm_calculation_audit_tvfilm_artists_artist_id_calculation_audit_get(artist_id)
        print("The response of TvfilmApi->tvfilm_calculation_audit_tvfilm_artists_artist_id_calculation_audit_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TvfilmApi->tvfilm_calculation_audit_tvfilm_artists_artist_id_calculation_audit_get: %s\n" % e)
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

# **tvfilm_dashboard_tvfilm_artists_artist_id_dashboard_get**
> object tvfilm_dashboard_tvfilm_artists_artist_id_dashboard_get(artist_id)

Tvfilm Dashboard

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
    api_instance = xr7_sdk.TvfilmApi(api_client)
    artist_id = 'artist_id_example' # str | 

    try:
        # Tvfilm Dashboard
        api_response = api_instance.tvfilm_dashboard_tvfilm_artists_artist_id_dashboard_get(artist_id)
        print("The response of TvfilmApi->tvfilm_dashboard_tvfilm_artists_artist_id_dashboard_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TvfilmApi->tvfilm_dashboard_tvfilm_artists_artist_id_dashboard_get: %s\n" % e)
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

# **tvfilm_draft_claims_tvfilm_artists_artist_id_claims_draft_post**
> object tvfilm_draft_claims_tvfilm_artists_artist_id_claims_draft_post(artist_id, tv_film_claim_draft_request)

Tvfilm Draft Claims

### Example


```python
import xr7_sdk
from xr7_sdk.models.tv_film_claim_draft_request import TVFilmClaimDraftRequest
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
    api_instance = xr7_sdk.TvfilmApi(api_client)
    artist_id = 'artist_id_example' # str | 
    tv_film_claim_draft_request = xr7_sdk.TVFilmClaimDraftRequest() # TVFilmClaimDraftRequest | 

    try:
        # Tvfilm Draft Claims
        api_response = api_instance.tvfilm_draft_claims_tvfilm_artists_artist_id_claims_draft_post(artist_id, tv_film_claim_draft_request)
        print("The response of TvfilmApi->tvfilm_draft_claims_tvfilm_artists_artist_id_claims_draft_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TvfilmApi->tvfilm_draft_claims_tvfilm_artists_artist_id_claims_draft_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **artist_id** | **str**|  | 
 **tv_film_claim_draft_request** | [**TVFilmClaimDraftRequest**](TVFilmClaimDraftRequest.md)|  | 

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

# **tvfilm_enterprise_portfolio_analyze_tvfilm_enterprise_portfolio_analyze_post**
> object tvfilm_enterprise_portfolio_analyze_tvfilm_enterprise_portfolio_analyze_post(tv_film_portfolio_analysis_request)

Tvfilm Enterprise Portfolio Analyze

### Example


```python
import xr7_sdk
from xr7_sdk.models.tv_film_portfolio_analysis_request import TVFilmPortfolioAnalysisRequest
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
    api_instance = xr7_sdk.TvfilmApi(api_client)
    tv_film_portfolio_analysis_request = xr7_sdk.TVFilmPortfolioAnalysisRequest() # TVFilmPortfolioAnalysisRequest | 

    try:
        # Tvfilm Enterprise Portfolio Analyze
        api_response = api_instance.tvfilm_enterprise_portfolio_analyze_tvfilm_enterprise_portfolio_analyze_post(tv_film_portfolio_analysis_request)
        print("The response of TvfilmApi->tvfilm_enterprise_portfolio_analyze_tvfilm_enterprise_portfolio_analyze_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TvfilmApi->tvfilm_enterprise_portfolio_analyze_tvfilm_enterprise_portfolio_analyze_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **tv_film_portfolio_analysis_request** | [**TVFilmPortfolioAnalysisRequest**](TVFilmPortfolioAnalysisRequest.md)|  | 

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

# **tvfilm_enterprise_portfolio_job_tvfilm_enterprise_portfolio_job_id_get**
> object tvfilm_enterprise_portfolio_job_tvfilm_enterprise_portfolio_job_id_get(job_id)

Tvfilm Enterprise Portfolio Job

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
    api_instance = xr7_sdk.TvfilmApi(api_client)
    job_id = 'job_id_example' # str | 

    try:
        # Tvfilm Enterprise Portfolio Job
        api_response = api_instance.tvfilm_enterprise_portfolio_job_tvfilm_enterprise_portfolio_job_id_get(job_id)
        print("The response of TvfilmApi->tvfilm_enterprise_portfolio_job_tvfilm_enterprise_portfolio_job_id_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TvfilmApi->tvfilm_enterprise_portfolio_job_tvfilm_enterprise_portfolio_job_id_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **job_id** | **str**|  | 

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

# **tvfilm_evidence_templates_tvfilm_catalogs_evidence_templates_get**
> object tvfilm_evidence_templates_tvfilm_catalogs_evidence_templates_get()

Tvfilm Evidence Templates

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
    api_instance = xr7_sdk.TvfilmApi(api_client)

    try:
        # Tvfilm Evidence Templates
        api_response = api_instance.tvfilm_evidence_templates_tvfilm_catalogs_evidence_templates_get()
        print("The response of TvfilmApi->tvfilm_evidence_templates_tvfilm_catalogs_evidence_templates_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TvfilmApi->tvfilm_evidence_templates_tvfilm_catalogs_evidence_templates_get: %s\n" % e)
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

# **tvfilm_export_evidence_packet_tvfilm_claims_claim_id_evidence_export_get**
> object tvfilm_export_evidence_packet_tvfilm_claims_claim_id_evidence_export_get(claim_id, format=format)

Tvfilm Export Evidence Packet

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
    api_instance = xr7_sdk.TvfilmApi(api_client)
    claim_id = 'claim_id_example' # str | 
    format = 'zip' # str |  (optional) (default to 'zip')

    try:
        # Tvfilm Export Evidence Packet
        api_response = api_instance.tvfilm_export_evidence_packet_tvfilm_claims_claim_id_evidence_export_get(claim_id, format=format)
        print("The response of TvfilmApi->tvfilm_export_evidence_packet_tvfilm_claims_claim_id_evidence_export_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TvfilmApi->tvfilm_export_evidence_packet_tvfilm_claims_claim_id_evidence_export_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **claim_id** | **str**|  | 
 **format** | **str**|  | [optional] [default to &#39;zip&#39;]

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

# **tvfilm_forecast_tvfilm_artists_artist_id_forecast_post**
> object tvfilm_forecast_tvfilm_artists_artist_id_forecast_post(artist_id, tv_film_forecast_request)

Tvfilm Forecast

### Example


```python
import xr7_sdk
from xr7_sdk.models.tv_film_forecast_request import TVFilmForecastRequest
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
    api_instance = xr7_sdk.TvfilmApi(api_client)
    artist_id = 'artist_id_example' # str | 
    tv_film_forecast_request = xr7_sdk.TVFilmForecastRequest() # TVFilmForecastRequest | 

    try:
        # Tvfilm Forecast
        api_response = api_instance.tvfilm_forecast_tvfilm_artists_artist_id_forecast_post(artist_id, tv_film_forecast_request)
        print("The response of TvfilmApi->tvfilm_forecast_tvfilm_artists_artist_id_forecast_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TvfilmApi->tvfilm_forecast_tvfilm_artists_artist_id_forecast_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **artist_id** | **str**|  | 
 **tv_film_forecast_request** | [**TVFilmForecastRequest**](TVFilmForecastRequest.md)|  | 

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

# **tvfilm_ingestion_commit_tvfilm_artists_artist_id_ingestion_commit_post**
> object tvfilm_ingestion_commit_tvfilm_artists_artist_id_ingestion_commit_post(artist_id, file)

Tvfilm Ingestion Commit

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
    api_instance = xr7_sdk.TvfilmApi(api_client)
    artist_id = 'artist_id_example' # str | 
    file = 'file_example' # str | 

    try:
        # Tvfilm Ingestion Commit
        api_response = api_instance.tvfilm_ingestion_commit_tvfilm_artists_artist_id_ingestion_commit_post(artist_id, file)
        print("The response of TvfilmApi->tvfilm_ingestion_commit_tvfilm_artists_artist_id_ingestion_commit_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TvfilmApi->tvfilm_ingestion_commit_tvfilm_artists_artist_id_ingestion_commit_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **artist_id** | **str**|  | 
 **file** | **str**|  | 

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

# **tvfilm_ingestion_formats_tvfilm_ingestion_formats_get**
> object tvfilm_ingestion_formats_tvfilm_ingestion_formats_get()

Tvfilm Ingestion Formats

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
    api_instance = xr7_sdk.TvfilmApi(api_client)

    try:
        # Tvfilm Ingestion Formats
        api_response = api_instance.tvfilm_ingestion_formats_tvfilm_ingestion_formats_get()
        print("The response of TvfilmApi->tvfilm_ingestion_formats_tvfilm_ingestion_formats_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TvfilmApi->tvfilm_ingestion_formats_tvfilm_ingestion_formats_get: %s\n" % e)
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

# **tvfilm_ingestion_preview_tvfilm_ingestion_preview_post**
> object tvfilm_ingestion_preview_tvfilm_ingestion_preview_post(file)

Tvfilm Ingestion Preview

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
    api_instance = xr7_sdk.TvfilmApi(api_client)
    file = 'file_example' # str | 

    try:
        # Tvfilm Ingestion Preview
        api_response = api_instance.tvfilm_ingestion_preview_tvfilm_ingestion_preview_post(file)
        print("The response of TvfilmApi->tvfilm_ingestion_preview_tvfilm_ingestion_preview_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TvfilmApi->tvfilm_ingestion_preview_tvfilm_ingestion_preview_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **file** | **str**|  | 

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

# **tvfilm_role_options_tvfilm_roles_options_get**
> object tvfilm_role_options_tvfilm_roles_options_get()

Tvfilm Role Options

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
    api_instance = xr7_sdk.TvfilmApi(api_client)

    try:
        # Tvfilm Role Options
        api_response = api_instance.tvfilm_role_options_tvfilm_roles_options_get()
        print("The response of TvfilmApi->tvfilm_role_options_tvfilm_roles_options_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TvfilmApi->tvfilm_role_options_tvfilm_roles_options_get: %s\n" % e)
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

# **tvfilm_scan_anomalies_tvfilm_artists_artist_id_anomalies_scan_post**
> object tvfilm_scan_anomalies_tvfilm_artists_artist_id_anomalies_scan_post(artist_id)

Tvfilm Scan Anomalies

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
    api_instance = xr7_sdk.TvfilmApi(api_client)
    artist_id = 'artist_id_example' # str | 

    try:
        # Tvfilm Scan Anomalies
        api_response = api_instance.tvfilm_scan_anomalies_tvfilm_artists_artist_id_anomalies_scan_post(artist_id)
        print("The response of TvfilmApi->tvfilm_scan_anomalies_tvfilm_artists_artist_id_anomalies_scan_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TvfilmApi->tvfilm_scan_anomalies_tvfilm_artists_artist_id_anomalies_scan_post: %s\n" % e)
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

# **tvfilm_trust_explain_tvfilm_trust_explain_post**
> object tvfilm_trust_explain_tvfilm_trust_explain_post(tv_film_trust_explain_request)

Tvfilm Trust Explain

### Example


```python
import xr7_sdk
from xr7_sdk.models.tv_film_trust_explain_request import TVFilmTrustExplainRequest
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
    api_instance = xr7_sdk.TvfilmApi(api_client)
    tv_film_trust_explain_request = xr7_sdk.TVFilmTrustExplainRequest() # TVFilmTrustExplainRequest | 

    try:
        # Tvfilm Trust Explain
        api_response = api_instance.tvfilm_trust_explain_tvfilm_trust_explain_post(tv_film_trust_explain_request)
        print("The response of TvfilmApi->tvfilm_trust_explain_tvfilm_trust_explain_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TvfilmApi->tvfilm_trust_explain_tvfilm_trust_explain_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **tv_film_trust_explain_request** | [**TVFilmTrustExplainRequest**](TVFilmTrustExplainRequest.md)|  | 

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

