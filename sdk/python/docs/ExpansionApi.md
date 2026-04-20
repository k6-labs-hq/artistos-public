# xr7_sdk.ExpansionApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**add_team_member_artists_artist_id_team_members_post**](ExpansionApi.md#add_team_member_artists_artist_id_team_members_post) | **POST** /artists/{artist_id}/team/members | Add Team Member
[**anchor_evidence_packet_internal_immutable_log**](ExpansionApi.md#anchor_evidence_packet_internal_immutable_log) | **POST** /claims/{claim_id}/evidence/anchor | Anchor Evidence Packet
[**benchmark_percentiles_artists_artist_id_recovery_benchmark_percentiles_get**](ExpansionApi.md#benchmark_percentiles_artists_artist_id_recovery_benchmark_percentiles_get) | **GET** /artists/{artist_id}/recovery/benchmark-percentiles | Benchmark Percentiles
[**create_oauth_session_artists_artist_id_connect_oauth_session_post**](ExpansionApi.md#create_oauth_session_artists_artist_id_connect_oauth_session_post) | **POST** /artists/{artist_id}/connect/oauth-session | Create Oauth Session
[**dashboard_charts_data_artists_artist_id_dashboard_charts_get**](ExpansionApi.md#dashboard_charts_data_artists_artist_id_dashboard_charts_get) | **GET** /artists/{artist_id}/dashboard/charts | Dashboard Charts Data
[**disconnect_connected_account_artists_artist_id_connect_accounts_account_id_delete**](ExpansionApi.md#disconnect_connected_account_artists_artist_id_connect_accounts_account_id_delete) | **DELETE** /artists/{artist_id}/connect/accounts/{account_id} | Disconnect Connected Account
[**education_guide_detail_education_guides_guide_id_get**](ExpansionApi.md#education_guide_detail_education_guides_guide_id_get) | **GET** /education/guides/{guide_id} | Education Guide Detail
[**education_guides_index_education_guides_get**](ExpansionApi.md#education_guides_index_education_guides_get) | **GET** /education/guides | Education Guides Index
[**estimate_withholding_artists_artist_id_intelligence_withholding_estimate_post**](ExpansionApi.md#estimate_withholding_artists_artist_id_intelligence_withholding_estimate_post) | **POST** /artists/{artist_id}/intelligence/withholding-estimate | Estimate Withholding
[**exchange_oauth_code_artists_artist_id_connect_oauth_session_session_id_exchange_post**](ExpansionApi.md#exchange_oauth_code_artists_artist_id_connect_oauth_session_session_id_exchange_post) | **POST** /artists/{artist_id}/connect/oauth-session/{session_id}/exchange | Exchange Oauth Code
[**export_summary_report_artists_artist_id_reports_summary_get**](ExpansionApi.md#export_summary_report_artists_artist_id_reports_summary_get) | **GET** /artists/{artist_id}/reports/summary | Export Summary Report
[**generate_audit_demand_letter_artists_artist_id_recovery_audit_demand_letter_get**](ExpansionApi.md#generate_audit_demand_letter_artists_artist_id_recovery_audit_demand_letter_get) | **GET** /artists/{artist_id}/recovery/audit-demand-letter | Generate Audit Demand Letter
[**generate_claim_template_artists_artist_id_claims_templates_post**](ExpansionApi.md#generate_claim_template_artists_artist_id_claims_templates_post) | **POST** /artists/{artist_id}/claims/templates | Generate Claim Template
[**get_notification_preferences_artists_artist_id_notifications_preferences_get**](ExpansionApi.md#get_notification_preferences_artists_artist_id_notifications_preferences_get) | **GET** /artists/{artist_id}/notifications/preferences | Get Notification Preferences
[**list_connect_fallbacks_artists_artist_id_connect_fallbacks_get**](ExpansionApi.md#list_connect_fallbacks_artists_artist_id_connect_fallbacks_get) | **GET** /artists/{artist_id}/connect/fallbacks | List Connect Fallbacks
[**list_connected_accounts_artists_artist_id_connect_accounts_get**](ExpansionApi.md#list_connected_accounts_artists_artist_id_connect_accounts_get) | **GET** /artists/{artist_id}/connect/accounts | List Connected Accounts
[**list_team_members_artists_artist_id_team_members_get**](ExpansionApi.md#list_team_members_artists_artist_id_team_members_get) | **GET** /artists/{artist_id}/team/members | List Team Members
[**partnership_targets_partnerships_targets_get**](ExpansionApi.md#partnership_targets_partnerships_targets_get) | **GET** /partnerships/targets | Partnership Targets
[**predict_total_recoverable_artists_artist_id_ml_predict_recoverable_post**](ExpansionApi.md#predict_total_recoverable_artists_artist_id_ml_predict_recoverable_post) | **POST** /artists/{artist_id}/ml/predict-recoverable | Predict Total Recoverable
[**public_recovery_stats_stats_public_recovery_get**](ExpansionApi.md#public_recovery_stats_stats_public_recovery_get) | **GET** /stats/public/recovery | Public Recovery Stats
[**refresh_connected_account_token_artists_artist_id_connect_accounts_account_id_refresh_post**](ExpansionApi.md#refresh_connected_account_token_artists_artist_id_connect_accounts_account_id_refresh_post) | **POST** /artists/{artist_id}/connect/accounts/{account_id}/refresh | Refresh Connected Account Token
[**remove_team_member_artists_artist_id_team_members_member_id_delete**](ExpansionApi.md#remove_team_member_artists_artist_id_team_members_member_id_delete) | **DELETE** /artists/{artist_id}/team/members/{member_id} | Remove Team Member
[**upsert_notification_preferences_artists_artist_id_notifications_preferences_put**](ExpansionApi.md#upsert_notification_preferences_artists_artist_id_notifications_preferences_put) | **PUT** /artists/{artist_id}/notifications/preferences | Upsert Notification Preferences
[**urgent_sol_notification_check_artists_artist_id_notifications_urgent_sol_check_post**](ExpansionApi.md#urgent_sol_notification_check_artists_artist_id_notifications_urgent_sol_check_post) | **POST** /artists/{artist_id}/notifications/urgent-sol-check | Urgent Sol Notification Check
[**white_label_portfolio_b2b_portfolio_org_id_get**](ExpansionApi.md#white_label_portfolio_b2b_portfolio_org_id_get) | **GET** /b2b/portfolio/{org_id} | White Label Portfolio


# **add_team_member_artists_artist_id_team_members_post**
> TeamMemberSchema add_team_member_artists_artist_id_team_members_post(artist_id, team_member_create, x_actor_email=x_actor_email, x_actor_role=x_actor_role)

Add Team Member

### Example


```python
import xr7_sdk
from xr7_sdk.models.team_member_create import TeamMemberCreate
from xr7_sdk.models.team_member_schema import TeamMemberSchema
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
    api_instance = xr7_sdk.ExpansionApi(api_client)
    artist_id = 'artist_id_example' # str |
    team_member_create = xr7_sdk.TeamMemberCreate() # TeamMemberCreate |
    x_actor_email = 'x_actor_email_example' # str |  (optional)
    x_actor_role = 'x_actor_role_example' # str |  (optional)

    try:
        # Add Team Member
        api_response = api_instance.add_team_member_artists_artist_id_team_members_post(artist_id, team_member_create, x_actor_email=x_actor_email, x_actor_role=x_actor_role)
        print("The response of ExpansionApi->add_team_member_artists_artist_id_team_members_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ExpansionApi->add_team_member_artists_artist_id_team_members_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **artist_id** | **str**|  |
 **team_member_create** | [**TeamMemberCreate**](TeamMemberCreate.md)|  |
 **x_actor_email** | **str**|  | [optional]
 **x_actor_role** | **str**|  | [optional]

### Return type

[**TeamMemberSchema**](TeamMemberSchema.md)

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

# **anchor_evidence_packet_internal_immutable_log**
> EvidenceAnchorSchema anchor_evidence_packet_internal_immutable_log(claim_id)

Anchor Evidence Packet

### Example


```python
import xr7_sdk
from xr7_sdk.models.evidence_anchor_schema import EvidenceAnchorSchema
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
    api_instance = xr7_sdk.ExpansionApi(api_client)
    claim_id = 'claim_id_example' # str |

    try:
        # Anchor Evidence Packet
        api_response = api_instance.anchor_evidence_packet_internal_immutable_log(claim_id)
        print("The response of ExpansionApi->anchor_evidence_packet_internal_immutable_log:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ExpansionApi->anchor_evidence_packet_internal_immutable_log: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **claim_id** | **str**|  |

### Return type

[**EvidenceAnchorSchema**](EvidenceAnchorSchema.md)

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

# **benchmark_percentiles_artists_artist_id_recovery_benchmark_percentiles_get**
> object benchmark_percentiles_artists_artist_id_recovery_benchmark_percentiles_get(artist_id, x_actor_email=x_actor_email, x_actor_role=x_actor_role)

Benchmark Percentiles

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
    api_instance = xr7_sdk.ExpansionApi(api_client)
    artist_id = 'artist_id_example' # str |
    x_actor_email = 'x_actor_email_example' # str |  (optional)
    x_actor_role = 'x_actor_role_example' # str |  (optional)

    try:
        # Benchmark Percentiles
        api_response = api_instance.benchmark_percentiles_artists_artist_id_recovery_benchmark_percentiles_get(artist_id, x_actor_email=x_actor_email, x_actor_role=x_actor_role)
        print("The response of ExpansionApi->benchmark_percentiles_artists_artist_id_recovery_benchmark_percentiles_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ExpansionApi->benchmark_percentiles_artists_artist_id_recovery_benchmark_percentiles_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **artist_id** | **str**|  |
 **x_actor_email** | **str**|  | [optional]
 **x_actor_role** | **str**|  | [optional]

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

# **create_oauth_session_artists_artist_id_connect_oauth_session_post**
> object create_oauth_session_artists_artist_id_connect_oauth_session_post(artist_id, o_auth_session_create_request, x_actor_email=x_actor_email, x_actor_role=x_actor_role)

Create Oauth Session

### Example


```python
import xr7_sdk
from xr7_sdk.models.o_auth_session_create_request import OAuthSessionCreateRequest
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
    api_instance = xr7_sdk.ExpansionApi(api_client)
    artist_id = 'artist_id_example' # str |
    o_auth_session_create_request = xr7_sdk.OAuthSessionCreateRequest() # OAuthSessionCreateRequest |
    x_actor_email = 'x_actor_email_example' # str |  (optional)
    x_actor_role = 'x_actor_role_example' # str |  (optional)

    try:
        # Create Oauth Session
        api_response = api_instance.create_oauth_session_artists_artist_id_connect_oauth_session_post(artist_id, o_auth_session_create_request, x_actor_email=x_actor_email, x_actor_role=x_actor_role)
        print("The response of ExpansionApi->create_oauth_session_artists_artist_id_connect_oauth_session_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ExpansionApi->create_oauth_session_artists_artist_id_connect_oauth_session_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **artist_id** | **str**|  |
 **o_auth_session_create_request** | [**OAuthSessionCreateRequest**](OAuthSessionCreateRequest.md)|  |
 **x_actor_email** | **str**|  | [optional]
 **x_actor_role** | **str**|  | [optional]

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

# **dashboard_charts_data_artists_artist_id_dashboard_charts_get**
> object dashboard_charts_data_artists_artist_id_dashboard_charts_get(artist_id, days=days, x_actor_email=x_actor_email, x_actor_role=x_actor_role)

Dashboard Charts Data

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
    api_instance = xr7_sdk.ExpansionApi(api_client)
    artist_id = 'artist_id_example' # str |
    days = 180 # int |  (optional) (default to 180)
    x_actor_email = 'x_actor_email_example' # str |  (optional)
    x_actor_role = 'x_actor_role_example' # str |  (optional)

    try:
        # Dashboard Charts Data
        api_response = api_instance.dashboard_charts_data_artists_artist_id_dashboard_charts_get(artist_id, days=days, x_actor_email=x_actor_email, x_actor_role=x_actor_role)
        print("The response of ExpansionApi->dashboard_charts_data_artists_artist_id_dashboard_charts_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ExpansionApi->dashboard_charts_data_artists_artist_id_dashboard_charts_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **artist_id** | **str**|  |
 **days** | **int**|  | [optional] [default to 180]
 **x_actor_email** | **str**|  | [optional]
 **x_actor_role** | **str**|  | [optional]

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

# **disconnect_connected_account_artists_artist_id_connect_accounts_account_id_delete**
> object disconnect_connected_account_artists_artist_id_connect_accounts_account_id_delete(artist_id, account_id, x_actor_email=x_actor_email, x_actor_role=x_actor_role)

Disconnect Connected Account

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
    api_instance = xr7_sdk.ExpansionApi(api_client)
    artist_id = 'artist_id_example' # str |
    account_id = 'account_id_example' # str |
    x_actor_email = 'x_actor_email_example' # str |  (optional)
    x_actor_role = 'x_actor_role_example' # str |  (optional)

    try:
        # Disconnect Connected Account
        api_response = api_instance.disconnect_connected_account_artists_artist_id_connect_accounts_account_id_delete(artist_id, account_id, x_actor_email=x_actor_email, x_actor_role=x_actor_role)
        print("The response of ExpansionApi->disconnect_connected_account_artists_artist_id_connect_accounts_account_id_delete:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ExpansionApi->disconnect_connected_account_artists_artist_id_connect_accounts_account_id_delete: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **artist_id** | **str**|  |
 **account_id** | **str**|  |
 **x_actor_email** | **str**|  | [optional]
 **x_actor_role** | **str**|  | [optional]

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

# **education_guide_detail_education_guides_guide_id_get**
> object education_guide_detail_education_guides_guide_id_get(guide_id)

Education Guide Detail

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
    api_instance = xr7_sdk.ExpansionApi(api_client)
    guide_id = 'guide_id_example' # str |

    try:
        # Education Guide Detail
        api_response = api_instance.education_guide_detail_education_guides_guide_id_get(guide_id)
        print("The response of ExpansionApi->education_guide_detail_education_guides_guide_id_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ExpansionApi->education_guide_detail_education_guides_guide_id_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **guide_id** | **str**|  |

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

# **education_guides_index_education_guides_get**
> object education_guides_index_education_guides_get()

Education Guides Index

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
    api_instance = xr7_sdk.ExpansionApi(api_client)

    try:
        # Education Guides Index
        api_response = api_instance.education_guides_index_education_guides_get()
        print("The response of ExpansionApi->education_guides_index_education_guides_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ExpansionApi->education_guides_index_education_guides_get: %s\n" % e)
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

# **estimate_withholding_artists_artist_id_intelligence_withholding_estimate_post**
> object estimate_withholding_artists_artist_id_intelligence_withholding_estimate_post(artist_id, currency_tax_estimate_request, x_actor_email=x_actor_email, x_actor_role=x_actor_role)

Estimate Withholding

### Example


```python
import xr7_sdk
from xr7_sdk.models.currency_tax_estimate_request import CurrencyTaxEstimateRequest
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
    api_instance = xr7_sdk.ExpansionApi(api_client)
    artist_id = 'artist_id_example' # str |
    currency_tax_estimate_request = xr7_sdk.CurrencyTaxEstimateRequest() # CurrencyTaxEstimateRequest |
    x_actor_email = 'x_actor_email_example' # str |  (optional)
    x_actor_role = 'x_actor_role_example' # str |  (optional)

    try:
        # Estimate Withholding
        api_response = api_instance.estimate_withholding_artists_artist_id_intelligence_withholding_estimate_post(artist_id, currency_tax_estimate_request, x_actor_email=x_actor_email, x_actor_role=x_actor_role)
        print("The response of ExpansionApi->estimate_withholding_artists_artist_id_intelligence_withholding_estimate_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ExpansionApi->estimate_withholding_artists_artist_id_intelligence_withholding_estimate_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **artist_id** | **str**|  |
 **currency_tax_estimate_request** | [**CurrencyTaxEstimateRequest**](CurrencyTaxEstimateRequest.md)|  |
 **x_actor_email** | **str**|  | [optional]
 **x_actor_role** | **str**|  | [optional]

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

# **exchange_oauth_code_artists_artist_id_connect_oauth_session_session_id_exchange_post**
> object exchange_oauth_code_artists_artist_id_connect_oauth_session_session_id_exchange_post(artist_id, session_id, o_auth_token_exchange_request, x_actor_email=x_actor_email, x_actor_role=x_actor_role)

Exchange Oauth Code

### Example


```python
import xr7_sdk
from xr7_sdk.models.o_auth_token_exchange_request import OAuthTokenExchangeRequest
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
    api_instance = xr7_sdk.ExpansionApi(api_client)
    artist_id = 'artist_id_example' # str |
    session_id = 'session_id_example' # str |
    o_auth_token_exchange_request = xr7_sdk.OAuthTokenExchangeRequest() # OAuthTokenExchangeRequest |
    x_actor_email = 'x_actor_email_example' # str |  (optional)
    x_actor_role = 'x_actor_role_example' # str |  (optional)

    try:
        # Exchange Oauth Code
        api_response = api_instance.exchange_oauth_code_artists_artist_id_connect_oauth_session_session_id_exchange_post(artist_id, session_id, o_auth_token_exchange_request, x_actor_email=x_actor_email, x_actor_role=x_actor_role)
        print("The response of ExpansionApi->exchange_oauth_code_artists_artist_id_connect_oauth_session_session_id_exchange_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ExpansionApi->exchange_oauth_code_artists_artist_id_connect_oauth_session_session_id_exchange_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **artist_id** | **str**|  |
 **session_id** | **str**|  |
 **o_auth_token_exchange_request** | [**OAuthTokenExchangeRequest**](OAuthTokenExchangeRequest.md)|  |
 **x_actor_email** | **str**|  | [optional]
 **x_actor_role** | **str**|  | [optional]

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

# **export_summary_report_artists_artist_id_reports_summary_get**
> object export_summary_report_artists_artist_id_reports_summary_get(artist_id, format=format, x_actor_email=x_actor_email, x_actor_role=x_actor_role)

Export Summary Report

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
    api_instance = xr7_sdk.ExpansionApi(api_client)
    artist_id = 'artist_id_example' # str |
    format = 'json' # str |  (optional) (default to 'json')
    x_actor_email = 'x_actor_email_example' # str |  (optional)
    x_actor_role = 'x_actor_role_example' # str |  (optional)

    try:
        # Export Summary Report
        api_response = api_instance.export_summary_report_artists_artist_id_reports_summary_get(artist_id, format=format, x_actor_email=x_actor_email, x_actor_role=x_actor_role)
        print("The response of ExpansionApi->export_summary_report_artists_artist_id_reports_summary_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ExpansionApi->export_summary_report_artists_artist_id_reports_summary_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **artist_id** | **str**|  |
 **format** | **str**|  | [optional] [default to &#39;json&#39;]
 **x_actor_email** | **str**|  | [optional]
 **x_actor_role** | **str**|  | [optional]

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

# **generate_audit_demand_letter_artists_artist_id_recovery_audit_demand_letter_get**
> object generate_audit_demand_letter_artists_artist_id_recovery_audit_demand_letter_get(artist_id, x_actor_email=x_actor_email, x_actor_role=x_actor_role)

Generate Audit Demand Letter

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
    api_instance = xr7_sdk.ExpansionApi(api_client)
    artist_id = 'artist_id_example' # str |
    x_actor_email = 'x_actor_email_example' # str |  (optional)
    x_actor_role = 'x_actor_role_example' # str |  (optional)

    try:
        # Generate Audit Demand Letter
        api_response = api_instance.generate_audit_demand_letter_artists_artist_id_recovery_audit_demand_letter_get(artist_id, x_actor_email=x_actor_email, x_actor_role=x_actor_role)
        print("The response of ExpansionApi->generate_audit_demand_letter_artists_artist_id_recovery_audit_demand_letter_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ExpansionApi->generate_audit_demand_letter_artists_artist_id_recovery_audit_demand_letter_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **artist_id** | **str**|  |
 **x_actor_email** | **str**|  | [optional]
 **x_actor_role** | **str**|  | [optional]

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

# **generate_claim_template_artists_artist_id_claims_templates_post**
> object generate_claim_template_artists_artist_id_claims_templates_post(artist_id, claim_template_request, x_actor_email=x_actor_email, x_actor_role=x_actor_role)

Generate Claim Template

### Example


```python
import xr7_sdk
from xr7_sdk.models.claim_template_request import ClaimTemplateRequest
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
    api_instance = xr7_sdk.ExpansionApi(api_client)
    artist_id = 'artist_id_example' # str |
    claim_template_request = xr7_sdk.ClaimTemplateRequest() # ClaimTemplateRequest |
    x_actor_email = 'x_actor_email_example' # str |  (optional)
    x_actor_role = 'x_actor_role_example' # str |  (optional)

    try:
        # Generate Claim Template
        api_response = api_instance.generate_claim_template_artists_artist_id_claims_templates_post(artist_id, claim_template_request, x_actor_email=x_actor_email, x_actor_role=x_actor_role)
        print("The response of ExpansionApi->generate_claim_template_artists_artist_id_claims_templates_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ExpansionApi->generate_claim_template_artists_artist_id_claims_templates_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **artist_id** | **str**|  |
 **claim_template_request** | [**ClaimTemplateRequest**](ClaimTemplateRequest.md)|  |
 **x_actor_email** | **str**|  | [optional]
 **x_actor_role** | **str**|  | [optional]

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

# **get_notification_preferences_artists_artist_id_notifications_preferences_get**
> NotificationPreferenceSchema get_notification_preferences_artists_artist_id_notifications_preferences_get(artist_id, x_actor_email=x_actor_email, x_actor_role=x_actor_role)

Get Notification Preferences

### Example


```python
import xr7_sdk
from xr7_sdk.models.notification_preference_schema import NotificationPreferenceSchema
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
    api_instance = xr7_sdk.ExpansionApi(api_client)
    artist_id = 'artist_id_example' # str |
    x_actor_email = 'x_actor_email_example' # str |  (optional)
    x_actor_role = 'x_actor_role_example' # str |  (optional)

    try:
        # Get Notification Preferences
        api_response = api_instance.get_notification_preferences_artists_artist_id_notifications_preferences_get(artist_id, x_actor_email=x_actor_email, x_actor_role=x_actor_role)
        print("The response of ExpansionApi->get_notification_preferences_artists_artist_id_notifications_preferences_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ExpansionApi->get_notification_preferences_artists_artist_id_notifications_preferences_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **artist_id** | **str**|  |
 **x_actor_email** | **str**|  | [optional]
 **x_actor_role** | **str**|  | [optional]

### Return type

[**NotificationPreferenceSchema**](NotificationPreferenceSchema.md)

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

# **list_connect_fallbacks_artists_artist_id_connect_fallbacks_get**
> object list_connect_fallbacks_artists_artist_id_connect_fallbacks_get(artist_id, x_actor_email=x_actor_email, x_actor_role=x_actor_role)

List Connect Fallbacks

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
    api_instance = xr7_sdk.ExpansionApi(api_client)
    artist_id = 'artist_id_example' # str |
    x_actor_email = 'x_actor_email_example' # str |  (optional)
    x_actor_role = 'x_actor_role_example' # str |  (optional)

    try:
        # List Connect Fallbacks
        api_response = api_instance.list_connect_fallbacks_artists_artist_id_connect_fallbacks_get(artist_id, x_actor_email=x_actor_email, x_actor_role=x_actor_role)
        print("The response of ExpansionApi->list_connect_fallbacks_artists_artist_id_connect_fallbacks_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ExpansionApi->list_connect_fallbacks_artists_artist_id_connect_fallbacks_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **artist_id** | **str**|  |
 **x_actor_email** | **str**|  | [optional]
 **x_actor_role** | **str**|  | [optional]

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

# **list_connected_accounts_artists_artist_id_connect_accounts_get**
> object list_connected_accounts_artists_artist_id_connect_accounts_get(artist_id, provider=provider, tenant_id=tenant_id, include_inactive=include_inactive, x_actor_email=x_actor_email, x_actor_role=x_actor_role)

List Connected Accounts

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
    api_instance = xr7_sdk.ExpansionApi(api_client)
    artist_id = 'artist_id_example' # str |
    provider = 'provider_example' # str |  (optional)
    tenant_id = 'tenant_id_example' # str |  (optional)
    include_inactive = False # bool |  (optional) (default to False)
    x_actor_email = 'x_actor_email_example' # str |  (optional)
    x_actor_role = 'x_actor_role_example' # str |  (optional)

    try:
        # List Connected Accounts
        api_response = api_instance.list_connected_accounts_artists_artist_id_connect_accounts_get(artist_id, provider=provider, tenant_id=tenant_id, include_inactive=include_inactive, x_actor_email=x_actor_email, x_actor_role=x_actor_role)
        print("The response of ExpansionApi->list_connected_accounts_artists_artist_id_connect_accounts_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ExpansionApi->list_connected_accounts_artists_artist_id_connect_accounts_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **artist_id** | **str**|  |
 **provider** | **str**|  | [optional]
 **tenant_id** | **str**|  | [optional]
 **include_inactive** | **bool**|  | [optional] [default to False]
 **x_actor_email** | **str**|  | [optional]
 **x_actor_role** | **str**|  | [optional]

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

# **list_team_members_artists_artist_id_team_members_get**
> List[TeamMemberSchema] list_team_members_artists_artist_id_team_members_get(artist_id, x_actor_email=x_actor_email, x_actor_role=x_actor_role)

List Team Members

### Example


```python
import xr7_sdk
from xr7_sdk.models.team_member_schema import TeamMemberSchema
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
    api_instance = xr7_sdk.ExpansionApi(api_client)
    artist_id = 'artist_id_example' # str |
    x_actor_email = 'x_actor_email_example' # str |  (optional)
    x_actor_role = 'x_actor_role_example' # str |  (optional)

    try:
        # List Team Members
        api_response = api_instance.list_team_members_artists_artist_id_team_members_get(artist_id, x_actor_email=x_actor_email, x_actor_role=x_actor_role)
        print("The response of ExpansionApi->list_team_members_artists_artist_id_team_members_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ExpansionApi->list_team_members_artists_artist_id_team_members_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **artist_id** | **str**|  |
 **x_actor_email** | **str**|  | [optional]
 **x_actor_role** | **str**|  | [optional]

### Return type

[**List[TeamMemberSchema]**](TeamMemberSchema.md)

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

# **partnership_targets_partnerships_targets_get**
> object partnership_targets_partnerships_targets_get()

Partnership Targets

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
    api_instance = xr7_sdk.ExpansionApi(api_client)

    try:
        # Partnership Targets
        api_response = api_instance.partnership_targets_partnerships_targets_get()
        print("The response of ExpansionApi->partnership_targets_partnerships_targets_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ExpansionApi->partnership_targets_partnerships_targets_get: %s\n" % e)
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

# **predict_total_recoverable_artists_artist_id_ml_predict_recoverable_post**
> object predict_total_recoverable_artists_artist_id_ml_predict_recoverable_post(artist_id, predict_recoverable_request, x_actor_email=x_actor_email, x_actor_role=x_actor_role)

Predict Total Recoverable

### Example


```python
import xr7_sdk
from xr7_sdk.models.predict_recoverable_request import PredictRecoverableRequest
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
    api_instance = xr7_sdk.ExpansionApi(api_client)
    artist_id = 'artist_id_example' # str |
    predict_recoverable_request = xr7_sdk.PredictRecoverableRequest() # PredictRecoverableRequest |
    x_actor_email = 'x_actor_email_example' # str |  (optional)
    x_actor_role = 'x_actor_role_example' # str |  (optional)

    try:
        # Predict Total Recoverable
        api_response = api_instance.predict_total_recoverable_artists_artist_id_ml_predict_recoverable_post(artist_id, predict_recoverable_request, x_actor_email=x_actor_email, x_actor_role=x_actor_role)
        print("The response of ExpansionApi->predict_total_recoverable_artists_artist_id_ml_predict_recoverable_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ExpansionApi->predict_total_recoverable_artists_artist_id_ml_predict_recoverable_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **artist_id** | **str**|  |
 **predict_recoverable_request** | [**PredictRecoverableRequest**](PredictRecoverableRequest.md)|  |
 **x_actor_email** | **str**|  | [optional]
 **x_actor_role** | **str**|  | [optional]

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

# **public_recovery_stats_stats_public_recovery_get**
> object public_recovery_stats_stats_public_recovery_get()

Public Recovery Stats

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
    api_instance = xr7_sdk.ExpansionApi(api_client)

    try:
        # Public Recovery Stats
        api_response = api_instance.public_recovery_stats_stats_public_recovery_get()
        print("The response of ExpansionApi->public_recovery_stats_stats_public_recovery_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ExpansionApi->public_recovery_stats_stats_public_recovery_get: %s\n" % e)
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

# **refresh_connected_account_token_artists_artist_id_connect_accounts_account_id_refresh_post**
> object refresh_connected_account_token_artists_artist_id_connect_accounts_account_id_refresh_post(artist_id, account_id, o_auth_token_refresh_request, x_actor_email=x_actor_email, x_actor_role=x_actor_role)

Refresh Connected Account Token

### Example


```python
import xr7_sdk
from xr7_sdk.models.o_auth_token_refresh_request import OAuthTokenRefreshRequest
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
    api_instance = xr7_sdk.ExpansionApi(api_client)
    artist_id = 'artist_id_example' # str |
    account_id = 'account_id_example' # str |
    o_auth_token_refresh_request = xr7_sdk.OAuthTokenRefreshRequest() # OAuthTokenRefreshRequest |
    x_actor_email = 'x_actor_email_example' # str |  (optional)
    x_actor_role = 'x_actor_role_example' # str |  (optional)

    try:
        # Refresh Connected Account Token
        api_response = api_instance.refresh_connected_account_token_artists_artist_id_connect_accounts_account_id_refresh_post(artist_id, account_id, o_auth_token_refresh_request, x_actor_email=x_actor_email, x_actor_role=x_actor_role)
        print("The response of ExpansionApi->refresh_connected_account_token_artists_artist_id_connect_accounts_account_id_refresh_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ExpansionApi->refresh_connected_account_token_artists_artist_id_connect_accounts_account_id_refresh_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **artist_id** | **str**|  |
 **account_id** | **str**|  |
 **o_auth_token_refresh_request** | [**OAuthTokenRefreshRequest**](OAuthTokenRefreshRequest.md)|  |
 **x_actor_email** | **str**|  | [optional]
 **x_actor_role** | **str**|  | [optional]

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

# **remove_team_member_artists_artist_id_team_members_member_id_delete**
> object remove_team_member_artists_artist_id_team_members_member_id_delete(artist_id, member_id, x_actor_email=x_actor_email, x_actor_role=x_actor_role)

Remove Team Member

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
    api_instance = xr7_sdk.ExpansionApi(api_client)
    artist_id = 'artist_id_example' # str |
    member_id = 'member_id_example' # str |
    x_actor_email = 'x_actor_email_example' # str |  (optional)
    x_actor_role = 'x_actor_role_example' # str |  (optional)

    try:
        # Remove Team Member
        api_response = api_instance.remove_team_member_artists_artist_id_team_members_member_id_delete(artist_id, member_id, x_actor_email=x_actor_email, x_actor_role=x_actor_role)
        print("The response of ExpansionApi->remove_team_member_artists_artist_id_team_members_member_id_delete:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ExpansionApi->remove_team_member_artists_artist_id_team_members_member_id_delete: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **artist_id** | **str**|  |
 **member_id** | **str**|  |
 **x_actor_email** | **str**|  | [optional]
 **x_actor_role** | **str**|  | [optional]

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

# **upsert_notification_preferences_artists_artist_id_notifications_preferences_put**
> NotificationPreferenceSchema upsert_notification_preferences_artists_artist_id_notifications_preferences_put(artist_id, notification_preference_upsert, x_actor_email=x_actor_email, x_actor_role=x_actor_role)

Upsert Notification Preferences

### Example


```python
import xr7_sdk
from xr7_sdk.models.notification_preference_schema import NotificationPreferenceSchema
from xr7_sdk.models.notification_preference_upsert import NotificationPreferenceUpsert
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
    api_instance = xr7_sdk.ExpansionApi(api_client)
    artist_id = 'artist_id_example' # str |
    notification_preference_upsert = xr7_sdk.NotificationPreferenceUpsert() # NotificationPreferenceUpsert |
    x_actor_email = 'x_actor_email_example' # str |  (optional)
    x_actor_role = 'x_actor_role_example' # str |  (optional)

    try:
        # Upsert Notification Preferences
        api_response = api_instance.upsert_notification_preferences_artists_artist_id_notifications_preferences_put(artist_id, notification_preference_upsert, x_actor_email=x_actor_email, x_actor_role=x_actor_role)
        print("The response of ExpansionApi->upsert_notification_preferences_artists_artist_id_notifications_preferences_put:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ExpansionApi->upsert_notification_preferences_artists_artist_id_notifications_preferences_put: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **artist_id** | **str**|  |
 **notification_preference_upsert** | [**NotificationPreferenceUpsert**](NotificationPreferenceUpsert.md)|  |
 **x_actor_email** | **str**|  | [optional]
 **x_actor_role** | **str**|  | [optional]

### Return type

[**NotificationPreferenceSchema**](NotificationPreferenceSchema.md)

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

# **urgent_sol_notification_check_artists_artist_id_notifications_urgent_sol_check_post**
> object urgent_sol_notification_check_artists_artist_id_notifications_urgent_sol_check_post(artist_id, x_actor_email=x_actor_email, x_actor_role=x_actor_role)

Urgent Sol Notification Check

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
    api_instance = xr7_sdk.ExpansionApi(api_client)
    artist_id = 'artist_id_example' # str |
    x_actor_email = 'x_actor_email_example' # str |  (optional)
    x_actor_role = 'x_actor_role_example' # str |  (optional)

    try:
        # Urgent Sol Notification Check
        api_response = api_instance.urgent_sol_notification_check_artists_artist_id_notifications_urgent_sol_check_post(artist_id, x_actor_email=x_actor_email, x_actor_role=x_actor_role)
        print("The response of ExpansionApi->urgent_sol_notification_check_artists_artist_id_notifications_urgent_sol_check_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ExpansionApi->urgent_sol_notification_check_artists_artist_id_notifications_urgent_sol_check_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **artist_id** | **str**|  |
 **x_actor_email** | **str**|  | [optional]
 **x_actor_role** | **str**|  | [optional]

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

# **white_label_portfolio_b2b_portfolio_org_id_get**
> object white_label_portfolio_b2b_portfolio_org_id_get(org_id)

White Label Portfolio

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
    api_instance = xr7_sdk.ExpansionApi(api_client)
    org_id = 'org_id_example' # str |

    try:
        # White Label Portfolio
        api_response = api_instance.white_label_portfolio_b2b_portfolio_org_id_get(org_id)
        print("The response of ExpansionApi->white_label_portfolio_b2b_portfolio_org_id_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ExpansionApi->white_label_portfolio_b2b_portfolio_org_id_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **org_id** | **str**|  |

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
