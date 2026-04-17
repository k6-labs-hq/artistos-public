# xr7_sdk.BrandingApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**branding_templates_branding_org_id_templates_get**](BrandingApi.md#branding_templates_branding_org_id_templates_get) | **GET** /branding/{org_id}/templates | Branding Templates
[**create_branding_branding_org_id_post**](BrandingApi.md#create_branding_branding_org_id_post) | **POST** /branding/{org_id} | Create Branding
[**create_help_article_branding_org_id_help_articles_post**](BrandingApi.md#create_help_article_branding_org_id_help_articles_post) | **POST** /branding/{org_id}/help-articles | Create Help Article
[**get_branding_branding_org_id_get**](BrandingApi.md#get_branding_branding_org_id_get) | **GET** /branding/{org_id} | Get Branding
[**list_help_articles_branding_org_id_help_articles_get**](BrandingApi.md#list_help_articles_branding_org_id_help_articles_get) | **GET** /branding/{org_id}/help-articles | List Help Articles
[**patch_branding_branding_org_id_patch**](BrandingApi.md#patch_branding_branding_org_id_patch) | **PATCH** /branding/{org_id} | Patch Branding
[**ui_shell_ui_shell_get**](BrandingApi.md#ui_shell_ui_shell_get) | **GET** /ui/shell | Ui Shell


# **branding_templates_branding_org_id_templates_get**
> object branding_templates_branding_org_id_templates_get(org_id)

Branding Templates

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
    api_instance = xr7_sdk.BrandingApi(api_client)
    org_id = 'org_id_example' # str |

    try:
        # Branding Templates
        api_response = api_instance.branding_templates_branding_org_id_templates_get(org_id)
        print("The response of BrandingApi->branding_templates_branding_org_id_templates_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling BrandingApi->branding_templates_branding_org_id_templates_get: %s\n" % e)
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

# **create_branding_branding_org_id_post**
> object create_branding_branding_org_id_post(org_id, branding_profile_upsert_request)

Create Branding

### Example


```python
import xr7_sdk
from xr7_sdk.models.branding_profile_upsert_request import BrandingProfileUpsertRequest
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
    api_instance = xr7_sdk.BrandingApi(api_client)
    org_id = 'org_id_example' # str |
    branding_profile_upsert_request = xr7_sdk.BrandingProfileUpsertRequest() # BrandingProfileUpsertRequest |

    try:
        # Create Branding
        api_response = api_instance.create_branding_branding_org_id_post(org_id, branding_profile_upsert_request)
        print("The response of BrandingApi->create_branding_branding_org_id_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling BrandingApi->create_branding_branding_org_id_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **org_id** | **str**|  |
 **branding_profile_upsert_request** | [**BrandingProfileUpsertRequest**](BrandingProfileUpsertRequest.md)|  |

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

# **create_help_article_branding_org_id_help_articles_post**
> object create_help_article_branding_org_id_help_articles_post(org_id, help_article_create_request)

Create Help Article

### Example


```python
import xr7_sdk
from xr7_sdk.models.help_article_create_request import HelpArticleCreateRequest
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
    api_instance = xr7_sdk.BrandingApi(api_client)
    org_id = 'org_id_example' # str |
    help_article_create_request = xr7_sdk.HelpArticleCreateRequest() # HelpArticleCreateRequest |

    try:
        # Create Help Article
        api_response = api_instance.create_help_article_branding_org_id_help_articles_post(org_id, help_article_create_request)
        print("The response of BrandingApi->create_help_article_branding_org_id_help_articles_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling BrandingApi->create_help_article_branding_org_id_help_articles_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **org_id** | **str**|  |
 **help_article_create_request** | [**HelpArticleCreateRequest**](HelpArticleCreateRequest.md)|  |

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

# **get_branding_branding_org_id_get**
> object get_branding_branding_org_id_get(org_id)

Get Branding

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
    api_instance = xr7_sdk.BrandingApi(api_client)
    org_id = 'org_id_example' # str |

    try:
        # Get Branding
        api_response = api_instance.get_branding_branding_org_id_get(org_id)
        print("The response of BrandingApi->get_branding_branding_org_id_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling BrandingApi->get_branding_branding_org_id_get: %s\n" % e)
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

# **list_help_articles_branding_org_id_help_articles_get**
> object list_help_articles_branding_org_id_help_articles_get(org_id)

List Help Articles

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
    api_instance = xr7_sdk.BrandingApi(api_client)
    org_id = 'org_id_example' # str |

    try:
        # List Help Articles
        api_response = api_instance.list_help_articles_branding_org_id_help_articles_get(org_id)
        print("The response of BrandingApi->list_help_articles_branding_org_id_help_articles_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling BrandingApi->list_help_articles_branding_org_id_help_articles_get: %s\n" % e)
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

# **patch_branding_branding_org_id_patch**
> object patch_branding_branding_org_id_patch(org_id, branding_profile_patch_request)

Patch Branding

### Example


```python
import xr7_sdk
from xr7_sdk.models.branding_profile_patch_request import BrandingProfilePatchRequest
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
    api_instance = xr7_sdk.BrandingApi(api_client)
    org_id = 'org_id_example' # str |
    branding_profile_patch_request = xr7_sdk.BrandingProfilePatchRequest() # BrandingProfilePatchRequest |

    try:
        # Patch Branding
        api_response = api_instance.patch_branding_branding_org_id_patch(org_id, branding_profile_patch_request)
        print("The response of BrandingApi->patch_branding_branding_org_id_patch:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling BrandingApi->patch_branding_branding_org_id_patch: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **org_id** | **str**|  |
 **branding_profile_patch_request** | [**BrandingProfilePatchRequest**](BrandingProfilePatchRequest.md)|  |

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

# **ui_shell_ui_shell_get**
> str ui_shell_ui_shell_get(org_id=org_id)

Ui Shell

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
    api_instance = xr7_sdk.BrandingApi(api_client)
    org_id = 'xr7-default' # str |  (optional) (default to 'xr7-default')

    try:
        # Ui Shell
        api_response = api_instance.ui_shell_ui_shell_get(org_id=org_id)
        print("The response of BrandingApi->ui_shell_ui_shell_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling BrandingApi->ui_shell_ui_shell_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **org_id** | **str**|  | [optional] [default to &#39;xr7-default&#39;]

### Return type

**str**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: text/html, application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)
