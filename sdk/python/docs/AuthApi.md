# xr7_sdk.AuthApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**admin_login_auth_login_admin_post**](AuthApi.md#admin_login_auth_login_admin_post) | **POST** /auth/login/admin | Admin Login
[**artist_login_auth_login_artist_post**](AuthApi.md#artist_login_auth_login_artist_post) | **POST** /auth/login/artist | Artist Login
[**auth_me_auth_me_get**](AuthApi.md#auth_me_auth_me_get) | **GET** /auth/me | Auth Me


# **admin_login_auth_login_admin_post**
> TokenResponse admin_login_auth_login_admin_post(admin_login_request)

Admin Login

### Example


```python
import xr7_sdk
from xr7_sdk.models.admin_login_request import AdminLoginRequest
from xr7_sdk.models.token_response import TokenResponse
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
    api_instance = xr7_sdk.AuthApi(api_client)
    admin_login_request = xr7_sdk.AdminLoginRequest() # AdminLoginRequest |

    try:
        # Admin Login
        api_response = api_instance.admin_login_auth_login_admin_post(admin_login_request)
        print("The response of AuthApi->admin_login_auth_login_admin_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AuthApi->admin_login_auth_login_admin_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **admin_login_request** | [**AdminLoginRequest**](AdminLoginRequest.md)|  |

### Return type

[**TokenResponse**](TokenResponse.md)

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

# **artist_login_auth_login_artist_post**
> TokenResponse artist_login_auth_login_artist_post(artist_login_request)

Artist Login

### Example


```python
import xr7_sdk
from xr7_sdk.models.artist_login_request import ArtistLoginRequest
from xr7_sdk.models.token_response import TokenResponse
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
    api_instance = xr7_sdk.AuthApi(api_client)
    artist_login_request = xr7_sdk.ArtistLoginRequest() # ArtistLoginRequest |

    try:
        # Artist Login
        api_response = api_instance.artist_login_auth_login_artist_post(artist_login_request)
        print("The response of AuthApi->artist_login_auth_login_artist_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AuthApi->artist_login_auth_login_artist_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **artist_login_request** | [**ArtistLoginRequest**](ArtistLoginRequest.md)|  |

### Return type

[**TokenResponse**](TokenResponse.md)

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

# **auth_me_auth_me_get**
> Dict[str, object] auth_me_auth_me_get()

Auth Me

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
    api_instance = xr7_sdk.AuthApi(api_client)

    try:
        # Auth Me
        api_response = api_instance.auth_me_auth_me_get()
        print("The response of AuthApi->auth_me_auth_me_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AuthApi->auth_me_auth_me_get: %s\n" % e)
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
