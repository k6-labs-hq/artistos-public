# AuthApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**adminLoginAuthLoginAdminPost**](AuthApi.md#adminloginauthloginadminpost) | **POST** /auth/login/admin | Admin Login |
| [**artistLoginAuthLoginArtistPost**](AuthApi.md#artistloginauthloginartistpost) | **POST** /auth/login/artist | Artist Login |
| [**authMeAuthMeGet**](AuthApi.md#authmeauthmeget) | **GET** /auth/me | Auth Me |



## adminLoginAuthLoginAdminPost

> TokenResponse adminLoginAuthLoginAdminPost(adminLoginRequest)

Admin Login

### Example

```ts
import {
  Configuration,
  AuthApi,
} from '@xr7/sdk';
import type { AdminLoginAuthLoginAdminPostRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new AuthApi();

  const body = {
    // AdminLoginRequest
    adminLoginRequest: ...,
  } satisfies AdminLoginAuthLoginAdminPostRequest;

  try {
    const data = await api.adminLoginAuthLoginAdminPost(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **adminLoginRequest** | [AdminLoginRequest](AdminLoginRequest.md) |  | |

### Return type

[**TokenResponse**](TokenResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## artistLoginAuthLoginArtistPost

> TokenResponse artistLoginAuthLoginArtistPost(artistLoginRequest)

Artist Login

### Example

```ts
import {
  Configuration,
  AuthApi,
} from '@xr7/sdk';
import type { ArtistLoginAuthLoginArtistPostRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new AuthApi();

  const body = {
    // ArtistLoginRequest
    artistLoginRequest: ...,
  } satisfies ArtistLoginAuthLoginArtistPostRequest;

  try {
    const data = await api.artistLoginAuthLoginArtistPost(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **artistLoginRequest** | [ArtistLoginRequest](ArtistLoginRequest.md) |  | |

### Return type

[**TokenResponse**](TokenResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## authMeAuthMeGet

> { [key: string]: any; } authMeAuthMeGet()

Auth Me

### Example

```ts
import {
  Configuration,
  AuthApi,
} from '@xr7/sdk';
import type { AuthMeAuthMeGetRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const config = new Configuration({
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new AuthApi(config);

  try {
    const data = await api.authMeAuthMeGet();
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters

This endpoint does not need any parameter.

### Return type

**{ [key: string]: any; }**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)
