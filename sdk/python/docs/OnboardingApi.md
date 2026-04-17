# xr7_sdk.OnboardingApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**apply_split_repairs_artists_artist_id_splits_repair_post**](OnboardingApi.md#apply_split_repairs_artists_artist_id_splits_repair_post) | **POST** /artists/{artist_id}/splits/repair | Apply Split Repairs
[**build_catalog_work_graph_artists_artist_id_catalog_graph_build_post**](OnboardingApi.md#build_catalog_work_graph_artists_artist_id_catalog_graph_build_post) | **POST** /artists/{artist_id}/catalog/graph/build | Build Catalog Work Graph
[**catalog_metadata_health_artists_artist_id_catalog_metadata_health_get**](OnboardingApi.md#catalog_metadata_health_artists_artist_id_catalog_metadata_health_get) | **GET** /artists/{artist_id}/catalog/metadata-health | Catalog Metadata Health
[**catalog_repairs_artists_artist_id_catalog_repairs_get**](OnboardingApi.md#catalog_repairs_artists_artist_id_catalog_repairs_get) | **GET** /artists/{artist_id}/catalog/repairs | Catalog Repairs
[**confirm_catalog_item_artists_artist_id_catalog_confirm_post**](OnboardingApi.md#confirm_catalog_item_artists_artist_id_catalog_confirm_post) | **POST** /artists/{artist_id}/catalog/confirm | Confirm Catalog Item
[**create_sync_job_artists_artist_id_sync_jobs_post**](OnboardingApi.md#create_sync_job_artists_artist_id_sync_jobs_post) | **POST** /artists/{artist_id}/sync/jobs | Create Sync Job
[**generate_audit_evidence_packet_claims_claim_id_evidence_generate_audit_post**](OnboardingApi.md#generate_audit_evidence_packet_claims_claim_id_evidence_generate_audit_post) | **POST** /claims/{claim_id}/evidence/generate-audit | Generate Audit Evidence Packet
[**get_permissions_dashboard_ui_permissions_ui_get**](OnboardingApi.md#get_permissions_dashboard_ui_permissions_ui_get) | **GET** /permissions/ui | Get Permissions Dashboard Ui
[**get_sync_job_artists_artist_id_sync_jobs_job_id_get**](OnboardingApi.md#get_sync_job_artists_artist_id_sync_jobs_job_id_get) | **GET** /artists/{artist_id}/sync/jobs/{job_id} | Get Sync Job
[**infer_catalog_artists_artist_id_catalog_infer_post**](OnboardingApi.md#infer_catalog_artists_artist_id_catalog_infer_post) | **POST** /artists/{artist_id}/catalog/infer | Infer Catalog
[**list_catalog_confirmations_artists_artist_id_catalog_confirm_get**](OnboardingApi.md#list_catalog_confirmations_artists_artist_id_catalog_confirm_get) | **GET** /artists/{artist_id}/catalog/confirm | List Catalog Confirmations
[**list_immutable_ledger_entries_artists_artist_id_ledger_immutable_get**](OnboardingApi.md#list_immutable_ledger_entries_artists_artist_id_ledger_immutable_get) | **GET** /artists/{artist_id}/ledger/immutable | List Immutable Ledger Entries
[**list_parser_plugins_artists_artist_id_parsers_plugins_get**](OnboardingApi.md#list_parser_plugins_artists_artist_id_parsers_plugins_get) | **GET** /artists/{artist_id}/parsers/plugins | List Parser Plugins
[**list_sync_jobs_artists_artist_id_sync_jobs_get**](OnboardingApi.md#list_sync_jobs_artists_artist_id_sync_jobs_get) | **GET** /artists/{artist_id}/sync/jobs | List Sync Jobs
[**missing_data_status_artists_artist_id_ingestion_missing_data_get**](OnboardingApi.md#missing_data_status_artists_artist_id_ingestion_missing_data_get) | **GET** /artists/{artist_id}/ingestion/missing-data | Missing Data Status
[**onboarding_auto_artists_artist_id_onboarding_auto_post**](OnboardingApi.md#onboarding_auto_artists_artist_id_onboarding_auto_post) | **POST** /artists/{artist_id}/onboarding/auto | Onboarding Auto
[**onboarding_status_artists_artist_id_onboarding_status_get**](OnboardingApi.md#onboarding_status_artists_artist_id_onboarding_status_get) | **GET** /artists/{artist_id}/onboarding/status | Onboarding Status
[**parse_statement_with_engine_artists_artist_id_parsers_parser_type_post**](OnboardingApi.md#parse_statement_with_engine_artists_artist_id_parsers_parser_type_post) | **POST** /artists/{artist_id}/parsers/{parser_type} | Parse Statement With Engine
[**permissions_dashboard_artists_artist_id_connect_permissions_dashboard_get**](OnboardingApi.md#permissions_dashboard_artists_artist_id_connect_permissions_dashboard_get) | **GET** /artists/{artist_id}/connect/permissions-dashboard | Permissions Dashboard
[**preview_full_workflow_artists_artist_id_workflow_preview_get**](OnboardingApi.md#preview_full_workflow_artists_artist_id_workflow_preview_get) | **GET** /artists/{artist_id}/workflow/preview | Preview Full Workflow
[**requeue_due_sync_jobs_artists_artist_id_sync_jobs_requeue_due_post**](OnboardingApi.md#requeue_due_sync_jobs_artists_artist_id_sync_jobs_requeue_due_post) | **POST** /artists/{artist_id}/sync/jobs/requeue-due | Requeue Due Sync Jobs
[**run_data_fetcher_artists_artist_id_fetchers_integration_post**](OnboardingApi.md#run_data_fetcher_artists_artist_id_fetchers_integration_post) | **POST** /artists/{artist_id}/fetchers/{integration} | Run Data Fetcher
[**run_full_workflow_artists_artist_id_workflow_run_post**](OnboardingApi.md#run_full_workflow_artists_artist_id_workflow_run_post) | **POST** /artists/{artist_id}/workflow/run | Run Full Workflow
[**run_recovery_automation_artists_artist_id_recovery_automate_post**](OnboardingApi.md#run_recovery_automation_artists_artist_id_recovery_automate_post) | **POST** /artists/{artist_id}/recovery/automate | Run Recovery Automation
[**run_sync_job_now_artists_artist_id_sync_jobs_job_id_run_post**](OnboardingApi.md#run_sync_job_now_artists_artist_id_sync_jobs_job_id_run_post) | **POST** /artists/{artist_id}/sync/jobs/{job_id}/run | Run Sync Job Now
[**upload_any_statement_artists_artist_id_ingestion_upload_any_post**](OnboardingApi.md#upload_any_statement_artists_artist_id_ingestion_upload_any_post) | **POST** /artists/{artist_id}/ingestion/upload-any | Upload Any Statement
[**upsert_parser_plugin_artists_artist_id_parsers_plugins_put**](OnboardingApi.md#upsert_parser_plugin_artists_artist_id_parsers_plugins_put) | **PUT** /artists/{artist_id}/parsers/plugins | Upsert Parser Plugin
[**variance_scan_artists_artist_id_variance_scan_post**](OnboardingApi.md#variance_scan_artists_artist_id_variance_scan_post) | **POST** /artists/{artist_id}/variance/scan | Variance Scan


# **apply_split_repairs_artists_artist_id_splits_repair_post**
> object apply_split_repairs_artists_artist_id_splits_repair_post(artist_id, split_repair_request)

Apply Split Repairs

### Example


```python
import xr7_sdk
from xr7_sdk.models.split_repair_request import SplitRepairRequest
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
    api_instance = xr7_sdk.OnboardingApi(api_client)
    artist_id = 'artist_id_example' # str |
    split_repair_request = xr7_sdk.SplitRepairRequest() # SplitRepairRequest |

    try:
        # Apply Split Repairs
        api_response = api_instance.apply_split_repairs_artists_artist_id_splits_repair_post(artist_id, split_repair_request)
        print("The response of OnboardingApi->apply_split_repairs_artists_artist_id_splits_repair_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling OnboardingApi->apply_split_repairs_artists_artist_id_splits_repair_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **artist_id** | **str**|  |
 **split_repair_request** | [**SplitRepairRequest**](SplitRepairRequest.md)|  |

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

# **build_catalog_work_graph_artists_artist_id_catalog_graph_build_post**
> object build_catalog_work_graph_artists_artist_id_catalog_graph_build_post(artist_id)

Build Catalog Work Graph

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
    api_instance = xr7_sdk.OnboardingApi(api_client)
    artist_id = 'artist_id_example' # str |

    try:
        # Build Catalog Work Graph
        api_response = api_instance.build_catalog_work_graph_artists_artist_id_catalog_graph_build_post(artist_id)
        print("The response of OnboardingApi->build_catalog_work_graph_artists_artist_id_catalog_graph_build_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling OnboardingApi->build_catalog_work_graph_artists_artist_id_catalog_graph_build_post: %s\n" % e)
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

# **catalog_metadata_health_artists_artist_id_catalog_metadata_health_get**
> object catalog_metadata_health_artists_artist_id_catalog_metadata_health_get(artist_id)

Catalog Metadata Health

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
    api_instance = xr7_sdk.OnboardingApi(api_client)
    artist_id = 'artist_id_example' # str |

    try:
        # Catalog Metadata Health
        api_response = api_instance.catalog_metadata_health_artists_artist_id_catalog_metadata_health_get(artist_id)
        print("The response of OnboardingApi->catalog_metadata_health_artists_artist_id_catalog_metadata_health_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling OnboardingApi->catalog_metadata_health_artists_artist_id_catalog_metadata_health_get: %s\n" % e)
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

# **catalog_repairs_artists_artist_id_catalog_repairs_get**
> object catalog_repairs_artists_artist_id_catalog_repairs_get(artist_id)

Catalog Repairs

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
    api_instance = xr7_sdk.OnboardingApi(api_client)
    artist_id = 'artist_id_example' # str |

    try:
        # Catalog Repairs
        api_response = api_instance.catalog_repairs_artists_artist_id_catalog_repairs_get(artist_id)
        print("The response of OnboardingApi->catalog_repairs_artists_artist_id_catalog_repairs_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling OnboardingApi->catalog_repairs_artists_artist_id_catalog_repairs_get: %s\n" % e)
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

# **confirm_catalog_item_artists_artist_id_catalog_confirm_post**
> CatalogConfirmationSchema confirm_catalog_item_artists_artist_id_catalog_confirm_post(artist_id, xr7_api_routers_onboarding_catalog_confirm_request)

Confirm Catalog Item

### Example


```python
import xr7_sdk
from xr7_sdk.models.catalog_confirmation_schema import CatalogConfirmationSchema
from xr7_sdk.models.xr7_api_routers_onboarding_catalog_confirm_request import XR7ApiRoutersOnboardingCatalogConfirmRequest
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
    api_instance = xr7_sdk.OnboardingApi(api_client)
    artist_id = 'artist_id_example' # str |
    xr7_api_routers_onboarding_catalog_confirm_request = xr7_sdk.XR7ApiRoutersOnboardingCatalogConfirmRequest() # XR7ApiRoutersOnboardingCatalogConfirmRequest |

    try:
        # Confirm Catalog Item
        api_response = api_instance.confirm_catalog_item_artists_artist_id_catalog_confirm_post(artist_id, xr7_api_routers_onboarding_catalog_confirm_request)
        print("The response of OnboardingApi->confirm_catalog_item_artists_artist_id_catalog_confirm_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling OnboardingApi->confirm_catalog_item_artists_artist_id_catalog_confirm_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **artist_id** | **str**|  |
 **xr7_api_routers_onboarding_catalog_confirm_request** | [**XR7ApiRoutersOnboardingCatalogConfirmRequest**](XR7ApiRoutersOnboardingCatalogConfirmRequest.md)|  |

### Return type

[**CatalogConfirmationSchema**](CatalogConfirmationSchema.md)

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

# **create_sync_job_artists_artist_id_sync_jobs_post**
> SyncJobSchema create_sync_job_artists_artist_id_sync_jobs_post(artist_id, sync_job_create_request)

Create Sync Job

### Example


```python
import xr7_sdk
from xr7_sdk.models.sync_job_create_request import SyncJobCreateRequest
from xr7_sdk.models.sync_job_schema import SyncJobSchema
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
    api_instance = xr7_sdk.OnboardingApi(api_client)
    artist_id = 'artist_id_example' # str |
    sync_job_create_request = xr7_sdk.SyncJobCreateRequest() # SyncJobCreateRequest |

    try:
        # Create Sync Job
        api_response = api_instance.create_sync_job_artists_artist_id_sync_jobs_post(artist_id, sync_job_create_request)
        print("The response of OnboardingApi->create_sync_job_artists_artist_id_sync_jobs_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling OnboardingApi->create_sync_job_artists_artist_id_sync_jobs_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **artist_id** | **str**|  |
 **sync_job_create_request** | [**SyncJobCreateRequest**](SyncJobCreateRequest.md)|  |

### Return type

[**SyncJobSchema**](SyncJobSchema.md)

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

# **generate_audit_evidence_packet_claims_claim_id_evidence_generate_audit_post**
> object generate_audit_evidence_packet_claims_claim_id_evidence_generate_audit_post(claim_id)

Generate Audit Evidence Packet

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
    api_instance = xr7_sdk.OnboardingApi(api_client)
    claim_id = 'claim_id_example' # str |

    try:
        # Generate Audit Evidence Packet
        api_response = api_instance.generate_audit_evidence_packet_claims_claim_id_evidence_generate_audit_post(claim_id)
        print("The response of OnboardingApi->generate_audit_evidence_packet_claims_claim_id_evidence_generate_audit_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling OnboardingApi->generate_audit_evidence_packet_claims_claim_id_evidence_generate_audit_post: %s\n" % e)
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

# **get_permissions_dashboard_ui_permissions_ui_get**
> object get_permissions_dashboard_ui_permissions_ui_get()

Get Permissions Dashboard Ui

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
    api_instance = xr7_sdk.OnboardingApi(api_client)

    try:
        # Get Permissions Dashboard Ui
        api_response = api_instance.get_permissions_dashboard_ui_permissions_ui_get()
        print("The response of OnboardingApi->get_permissions_dashboard_ui_permissions_ui_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling OnboardingApi->get_permissions_dashboard_ui_permissions_ui_get: %s\n" % e)
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

# **get_sync_job_artists_artist_id_sync_jobs_job_id_get**
> SyncJobSchema get_sync_job_artists_artist_id_sync_jobs_job_id_get(artist_id, job_id)

Get Sync Job

### Example


```python
import xr7_sdk
from xr7_sdk.models.sync_job_schema import SyncJobSchema
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
    api_instance = xr7_sdk.OnboardingApi(api_client)
    artist_id = 'artist_id_example' # str |
    job_id = 'job_id_example' # str |

    try:
        # Get Sync Job
        api_response = api_instance.get_sync_job_artists_artist_id_sync_jobs_job_id_get(artist_id, job_id)
        print("The response of OnboardingApi->get_sync_job_artists_artist_id_sync_jobs_job_id_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling OnboardingApi->get_sync_job_artists_artist_id_sync_jobs_job_id_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **artist_id** | **str**|  |
 **job_id** | **str**|  |

### Return type

[**SyncJobSchema**](SyncJobSchema.md)

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

# **infer_catalog_artists_artist_id_catalog_infer_post**
> object infer_catalog_artists_artist_id_catalog_infer_post(artist_id)

Infer Catalog

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
    api_instance = xr7_sdk.OnboardingApi(api_client)
    artist_id = 'artist_id_example' # str |

    try:
        # Infer Catalog
        api_response = api_instance.infer_catalog_artists_artist_id_catalog_infer_post(artist_id)
        print("The response of OnboardingApi->infer_catalog_artists_artist_id_catalog_infer_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling OnboardingApi->infer_catalog_artists_artist_id_catalog_infer_post: %s\n" % e)
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

# **list_catalog_confirmations_artists_artist_id_catalog_confirm_get**
> List[CatalogConfirmationSchema] list_catalog_confirmations_artists_artist_id_catalog_confirm_get(artist_id)

List Catalog Confirmations

### Example


```python
import xr7_sdk
from xr7_sdk.models.catalog_confirmation_schema import CatalogConfirmationSchema
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
    api_instance = xr7_sdk.OnboardingApi(api_client)
    artist_id = 'artist_id_example' # str |

    try:
        # List Catalog Confirmations
        api_response = api_instance.list_catalog_confirmations_artists_artist_id_catalog_confirm_get(artist_id)
        print("The response of OnboardingApi->list_catalog_confirmations_artists_artist_id_catalog_confirm_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling OnboardingApi->list_catalog_confirmations_artists_artist_id_catalog_confirm_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **artist_id** | **str**|  |

### Return type

[**List[CatalogConfirmationSchema]**](CatalogConfirmationSchema.md)

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

# **list_immutable_ledger_entries_artists_artist_id_ledger_immutable_get**
> List[ImmutableLedgerEntrySchema] list_immutable_ledger_entries_artists_artist_id_ledger_immutable_get(artist_id)

List Immutable Ledger Entries

### Example


```python
import xr7_sdk
from xr7_sdk.models.immutable_ledger_entry_schema import ImmutableLedgerEntrySchema
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
    api_instance = xr7_sdk.OnboardingApi(api_client)
    artist_id = 'artist_id_example' # str |

    try:
        # List Immutable Ledger Entries
        api_response = api_instance.list_immutable_ledger_entries_artists_artist_id_ledger_immutable_get(artist_id)
        print("The response of OnboardingApi->list_immutable_ledger_entries_artists_artist_id_ledger_immutable_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling OnboardingApi->list_immutable_ledger_entries_artists_artist_id_ledger_immutable_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **artist_id** | **str**|  |

### Return type

[**List[ImmutableLedgerEntrySchema]**](ImmutableLedgerEntrySchema.md)

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

# **list_parser_plugins_artists_artist_id_parsers_plugins_get**
> List[ParserPluginSchema] list_parser_plugins_artists_artist_id_parsers_plugins_get(artist_id)

List Parser Plugins

### Example


```python
import xr7_sdk
from xr7_sdk.models.parser_plugin_schema import ParserPluginSchema
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
    api_instance = xr7_sdk.OnboardingApi(api_client)
    artist_id = 'artist_id_example' # str |

    try:
        # List Parser Plugins
        api_response = api_instance.list_parser_plugins_artists_artist_id_parsers_plugins_get(artist_id)
        print("The response of OnboardingApi->list_parser_plugins_artists_artist_id_parsers_plugins_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling OnboardingApi->list_parser_plugins_artists_artist_id_parsers_plugins_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **artist_id** | **str**|  |

### Return type

[**List[ParserPluginSchema]**](ParserPluginSchema.md)

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

# **list_sync_jobs_artists_artist_id_sync_jobs_get**
> List[SyncJobSchema] list_sync_jobs_artists_artist_id_sync_jobs_get(artist_id)

List Sync Jobs

### Example


```python
import xr7_sdk
from xr7_sdk.models.sync_job_schema import SyncJobSchema
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
    api_instance = xr7_sdk.OnboardingApi(api_client)
    artist_id = 'artist_id_example' # str |

    try:
        # List Sync Jobs
        api_response = api_instance.list_sync_jobs_artists_artist_id_sync_jobs_get(artist_id)
        print("The response of OnboardingApi->list_sync_jobs_artists_artist_id_sync_jobs_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling OnboardingApi->list_sync_jobs_artists_artist_id_sync_jobs_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **artist_id** | **str**|  |

### Return type

[**List[SyncJobSchema]**](SyncJobSchema.md)

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

# **missing_data_status_artists_artist_id_ingestion_missing_data_get**
> object missing_data_status_artists_artist_id_ingestion_missing_data_get(artist_id)

Missing Data Status

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
    api_instance = xr7_sdk.OnboardingApi(api_client)
    artist_id = 'artist_id_example' # str |

    try:
        # Missing Data Status
        api_response = api_instance.missing_data_status_artists_artist_id_ingestion_missing_data_get(artist_id)
        print("The response of OnboardingApi->missing_data_status_artists_artist_id_ingestion_missing_data_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling OnboardingApi->missing_data_status_artists_artist_id_ingestion_missing_data_get: %s\n" % e)
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

# **onboarding_auto_artists_artist_id_onboarding_auto_post**
> object onboarding_auto_artists_artist_id_onboarding_auto_post(artist_id, onboarding_auto_request)

Onboarding Auto

Run one-call onboarding bootstrap for baseline activation.

This endpoint marks the artist as onboarded (if still NEW), executes due
sync jobs when requested, and returns an updated onboarding summary.

### Example


```python
import xr7_sdk
from xr7_sdk.models.onboarding_auto_request import OnboardingAutoRequest
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
    api_instance = xr7_sdk.OnboardingApi(api_client)
    artist_id = 'artist_id_example' # str |
    onboarding_auto_request = xr7_sdk.OnboardingAutoRequest() # OnboardingAutoRequest |

    try:
        # Onboarding Auto
        api_response = api_instance.onboarding_auto_artists_artist_id_onboarding_auto_post(artist_id, onboarding_auto_request)
        print("The response of OnboardingApi->onboarding_auto_artists_artist_id_onboarding_auto_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling OnboardingApi->onboarding_auto_artists_artist_id_onboarding_auto_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **artist_id** | **str**|  |
 **onboarding_auto_request** | [**OnboardingAutoRequest**](OnboardingAutoRequest.md)|  |

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

# **onboarding_status_artists_artist_id_onboarding_status_get**
> object onboarding_status_artists_artist_id_onboarding_status_get(artist_id)

Onboarding Status

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
    api_instance = xr7_sdk.OnboardingApi(api_client)
    artist_id = 'artist_id_example' # str |

    try:
        # Onboarding Status
        api_response = api_instance.onboarding_status_artists_artist_id_onboarding_status_get(artist_id)
        print("The response of OnboardingApi->onboarding_status_artists_artist_id_onboarding_status_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling OnboardingApi->onboarding_status_artists_artist_id_onboarding_status_get: %s\n" % e)
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

# **parse_statement_with_engine_artists_artist_id_parsers_parser_type_post**
> object parse_statement_with_engine_artists_artist_id_parsers_parser_type_post(artist_id, parser_type, file)

Parse Statement With Engine

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
    api_instance = xr7_sdk.OnboardingApi(api_client)
    artist_id = 'artist_id_example' # str |
    parser_type = 'parser_type_example' # str |
    file = 'file_example' # str |

    try:
        # Parse Statement With Engine
        api_response = api_instance.parse_statement_with_engine_artists_artist_id_parsers_parser_type_post(artist_id, parser_type, file)
        print("The response of OnboardingApi->parse_statement_with_engine_artists_artist_id_parsers_parser_type_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling OnboardingApi->parse_statement_with_engine_artists_artist_id_parsers_parser_type_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **artist_id** | **str**|  |
 **parser_type** | **str**|  |
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

# **permissions_dashboard_artists_artist_id_connect_permissions_dashboard_get**
> object permissions_dashboard_artists_artist_id_connect_permissions_dashboard_get(artist_id)

Permissions Dashboard

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
    api_instance = xr7_sdk.OnboardingApi(api_client)
    artist_id = 'artist_id_example' # str |

    try:
        # Permissions Dashboard
        api_response = api_instance.permissions_dashboard_artists_artist_id_connect_permissions_dashboard_get(artist_id)
        print("The response of OnboardingApi->permissions_dashboard_artists_artist_id_connect_permissions_dashboard_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling OnboardingApi->permissions_dashboard_artists_artist_id_connect_permissions_dashboard_get: %s\n" % e)
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

# **preview_full_workflow_artists_artist_id_workflow_preview_get**
> object preview_full_workflow_artists_artist_id_workflow_preview_get(artist_id)

Preview Full Workflow

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
    api_instance = xr7_sdk.OnboardingApi(api_client)
    artist_id = 'artist_id_example' # str |

    try:
        # Preview Full Workflow
        api_response = api_instance.preview_full_workflow_artists_artist_id_workflow_preview_get(artist_id)
        print("The response of OnboardingApi->preview_full_workflow_artists_artist_id_workflow_preview_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling OnboardingApi->preview_full_workflow_artists_artist_id_workflow_preview_get: %s\n" % e)
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

# **requeue_due_sync_jobs_artists_artist_id_sync_jobs_requeue_due_post**
> object requeue_due_sync_jobs_artists_artist_id_sync_jobs_requeue_due_post(artist_id)

Requeue Due Sync Jobs

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
    api_instance = xr7_sdk.OnboardingApi(api_client)
    artist_id = 'artist_id_example' # str |

    try:
        # Requeue Due Sync Jobs
        api_response = api_instance.requeue_due_sync_jobs_artists_artist_id_sync_jobs_requeue_due_post(artist_id)
        print("The response of OnboardingApi->requeue_due_sync_jobs_artists_artist_id_sync_jobs_requeue_due_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling OnboardingApi->requeue_due_sync_jobs_artists_artist_id_sync_jobs_requeue_due_post: %s\n" % e)
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

# **run_data_fetcher_artists_artist_id_fetchers_integration_post**
> object run_data_fetcher_artists_artist_id_fetchers_integration_post(artist_id, integration)

Run Data Fetcher

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
    api_instance = xr7_sdk.OnboardingApi(api_client)
    artist_id = 'artist_id_example' # str |
    integration = 'integration_example' # str |

    try:
        # Run Data Fetcher
        api_response = api_instance.run_data_fetcher_artists_artist_id_fetchers_integration_post(artist_id, integration)
        print("The response of OnboardingApi->run_data_fetcher_artists_artist_id_fetchers_integration_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling OnboardingApi->run_data_fetcher_artists_artist_id_fetchers_integration_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **artist_id** | **str**|  |
 **integration** | **str**|  |

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

# **run_full_workflow_artists_artist_id_workflow_run_post**
> object run_full_workflow_artists_artist_id_workflow_run_post(artist_id, workflow_run_request)

Run Full Workflow

### Example


```python
import xr7_sdk
from xr7_sdk.models.workflow_run_request import WorkflowRunRequest
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
    api_instance = xr7_sdk.OnboardingApi(api_client)
    artist_id = 'artist_id_example' # str |
    workflow_run_request = xr7_sdk.WorkflowRunRequest() # WorkflowRunRequest |

    try:
        # Run Full Workflow
        api_response = api_instance.run_full_workflow_artists_artist_id_workflow_run_post(artist_id, workflow_run_request)
        print("The response of OnboardingApi->run_full_workflow_artists_artist_id_workflow_run_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling OnboardingApi->run_full_workflow_artists_artist_id_workflow_run_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **artist_id** | **str**|  |
 **workflow_run_request** | [**WorkflowRunRequest**](WorkflowRunRequest.md)|  |

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

# **run_recovery_automation_artists_artist_id_recovery_automate_post**
> object run_recovery_automation_artists_artist_id_recovery_automate_post(artist_id)

Run Recovery Automation

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
    api_instance = xr7_sdk.OnboardingApi(api_client)
    artist_id = 'artist_id_example' # str |

    try:
        # Run Recovery Automation
        api_response = api_instance.run_recovery_automation_artists_artist_id_recovery_automate_post(artist_id)
        print("The response of OnboardingApi->run_recovery_automation_artists_artist_id_recovery_automate_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling OnboardingApi->run_recovery_automation_artists_artist_id_recovery_automate_post: %s\n" % e)
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

# **run_sync_job_now_artists_artist_id_sync_jobs_job_id_run_post**
> SyncJobSchema run_sync_job_now_artists_artist_id_sync_jobs_job_id_run_post(artist_id, job_id, async_run=async_run)

Run Sync Job Now

### Example


```python
import xr7_sdk
from xr7_sdk.models.sync_job_schema import SyncJobSchema
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
    api_instance = xr7_sdk.OnboardingApi(api_client)
    artist_id = 'artist_id_example' # str |
    job_id = 'job_id_example' # str |
    async_run = False # bool |  (optional) (default to False)

    try:
        # Run Sync Job Now
        api_response = api_instance.run_sync_job_now_artists_artist_id_sync_jobs_job_id_run_post(artist_id, job_id, async_run=async_run)
        print("The response of OnboardingApi->run_sync_job_now_artists_artist_id_sync_jobs_job_id_run_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling OnboardingApi->run_sync_job_now_artists_artist_id_sync_jobs_job_id_run_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **artist_id** | **str**|  |
 **job_id** | **str**|  |
 **async_run** | **bool**|  | [optional] [default to False]

### Return type

[**SyncJobSchema**](SyncJobSchema.md)

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

# **upload_any_statement_artists_artist_id_ingestion_upload_any_post**
> object upload_any_statement_artists_artist_id_ingestion_upload_any_post(artist_id, files, strict_validation=strict_validation)

Upload Any Statement

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
    api_instance = xr7_sdk.OnboardingApi(api_client)
    artist_id = 'artist_id_example' # str |
    files = ['files_example'] # List[str] |
    strict_validation = True # bool |  (optional) (default to True)

    try:
        # Upload Any Statement
        api_response = api_instance.upload_any_statement_artists_artist_id_ingestion_upload_any_post(artist_id, files, strict_validation=strict_validation)
        print("The response of OnboardingApi->upload_any_statement_artists_artist_id_ingestion_upload_any_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling OnboardingApi->upload_any_statement_artists_artist_id_ingestion_upload_any_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **artist_id** | **str**|  |
 **files** | [**List[str]**](str.md)|  |
 **strict_validation** | **bool**|  | [optional] [default to True]

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

# **upsert_parser_plugin_artists_artist_id_parsers_plugins_put**
> ParserPluginSchema upsert_parser_plugin_artists_artist_id_parsers_plugins_put(artist_id, parser_plugin_upsert_request)

Upsert Parser Plugin

### Example


```python
import xr7_sdk
from xr7_sdk.models.parser_plugin_schema import ParserPluginSchema
from xr7_sdk.models.parser_plugin_upsert_request import ParserPluginUpsertRequest
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
    api_instance = xr7_sdk.OnboardingApi(api_client)
    artist_id = 'artist_id_example' # str |
    parser_plugin_upsert_request = xr7_sdk.ParserPluginUpsertRequest() # ParserPluginUpsertRequest |

    try:
        # Upsert Parser Plugin
        api_response = api_instance.upsert_parser_plugin_artists_artist_id_parsers_plugins_put(artist_id, parser_plugin_upsert_request)
        print("The response of OnboardingApi->upsert_parser_plugin_artists_artist_id_parsers_plugins_put:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling OnboardingApi->upsert_parser_plugin_artists_artist_id_parsers_plugins_put: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **artist_id** | **str**|  |
 **parser_plugin_upsert_request** | [**ParserPluginUpsertRequest**](ParserPluginUpsertRequest.md)|  |

### Return type

[**ParserPluginSchema**](ParserPluginSchema.md)

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

# **variance_scan_artists_artist_id_variance_scan_post**
> object variance_scan_artists_artist_id_variance_scan_post(artist_id, variance_scan_request)

Variance Scan

### Example


```python
import xr7_sdk
from xr7_sdk.models.variance_scan_request import VarianceScanRequest
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
    api_instance = xr7_sdk.OnboardingApi(api_client)
    artist_id = 'artist_id_example' # str |
    variance_scan_request = xr7_sdk.VarianceScanRequest() # VarianceScanRequest |

    try:
        # Variance Scan
        api_response = api_instance.variance_scan_artists_artist_id_variance_scan_post(artist_id, variance_scan_request)
        print("The response of OnboardingApi->variance_scan_artists_artist_id_variance_scan_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling OnboardingApi->variance_scan_artists_artist_id_variance_scan_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **artist_id** | **str**|  |
 **variance_scan_request** | [**VarianceScanRequest**](VarianceScanRequest.md)|  |

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
