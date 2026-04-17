# BrandingApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**brandingTemplatesBrandingOrgIdTemplatesGet**](BrandingApi.md#brandingtemplatesbrandingorgidtemplatesget) | **GET** /branding/{org_id}/templates | Branding Templates |
| [**createBrandingBrandingOrgIdPost**](BrandingApi.md#createbrandingbrandingorgidpost) | **POST** /branding/{org_id} | Create Branding |
| [**createHelpArticleBrandingOrgIdHelpArticlesPost**](BrandingApi.md#createhelparticlebrandingorgidhelparticlespost) | **POST** /branding/{org_id}/help-articles | Create Help Article |
| [**getBrandingBrandingOrgIdGet**](BrandingApi.md#getbrandingbrandingorgidget) | **GET** /branding/{org_id} | Get Branding |
| [**listHelpArticlesBrandingOrgIdHelpArticlesGet**](BrandingApi.md#listhelparticlesbrandingorgidhelparticlesget) | **GET** /branding/{org_id}/help-articles | List Help Articles |
| [**patchBrandingBrandingOrgIdPatch**](BrandingApi.md#patchbrandingbrandingorgidpatch) | **PATCH** /branding/{org_id} | Patch Branding |
| [**uiShellUiShellGet**](BrandingApi.md#uishelluishellget) | **GET** /ui/shell | Ui Shell |



## brandingTemplatesBrandingOrgIdTemplatesGet

> any brandingTemplatesBrandingOrgIdTemplatesGet(orgId)

Branding Templates

### Example

```ts
import {
  Configuration,
  BrandingApi,
} from '@xr7/sdk';
import type { BrandingTemplatesBrandingOrgIdTemplatesGetRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new BrandingApi();

  const body = {
    // string
    orgId: orgId_example,
  } satisfies BrandingTemplatesBrandingOrgIdTemplatesGetRequest;

  try {
    const data = await api.brandingTemplatesBrandingOrgIdTemplatesGet(body);
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
| **orgId** | `string` |  | [Defaults to `undefined`] |

### Return type

**any**

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## createBrandingBrandingOrgIdPost

> any createBrandingBrandingOrgIdPost(orgId, brandingProfileUpsertRequest)

Create Branding

### Example

```ts
import {
  Configuration,
  BrandingApi,
} from '@xr7/sdk';
import type { CreateBrandingBrandingOrgIdPostRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new BrandingApi();

  const body = {
    // string
    orgId: orgId_example,
    // BrandingProfileUpsertRequest
    brandingProfileUpsertRequest: ...,
  } satisfies CreateBrandingBrandingOrgIdPostRequest;

  try {
    const data = await api.createBrandingBrandingOrgIdPost(body);
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
| **orgId** | `string` |  | [Defaults to `undefined`] |
| **brandingProfileUpsertRequest** | [BrandingProfileUpsertRequest](BrandingProfileUpsertRequest.md) |  | |

### Return type

**any**

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


## createHelpArticleBrandingOrgIdHelpArticlesPost

> any createHelpArticleBrandingOrgIdHelpArticlesPost(orgId, helpArticleCreateRequest)

Create Help Article

### Example

```ts
import {
  Configuration,
  BrandingApi,
} from '@xr7/sdk';
import type { CreateHelpArticleBrandingOrgIdHelpArticlesPostRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new BrandingApi();

  const body = {
    // string
    orgId: orgId_example,
    // HelpArticleCreateRequest
    helpArticleCreateRequest: ...,
  } satisfies CreateHelpArticleBrandingOrgIdHelpArticlesPostRequest;

  try {
    const data = await api.createHelpArticleBrandingOrgIdHelpArticlesPost(body);
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
| **orgId** | `string` |  | [Defaults to `undefined`] |
| **helpArticleCreateRequest** | [HelpArticleCreateRequest](HelpArticleCreateRequest.md) |  | |

### Return type

**any**

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


## getBrandingBrandingOrgIdGet

> any getBrandingBrandingOrgIdGet(orgId)

Get Branding

### Example

```ts
import {
  Configuration,
  BrandingApi,
} from '@xr7/sdk';
import type { GetBrandingBrandingOrgIdGetRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new BrandingApi();

  const body = {
    // string
    orgId: orgId_example,
  } satisfies GetBrandingBrandingOrgIdGetRequest;

  try {
    const data = await api.getBrandingBrandingOrgIdGet(body);
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
| **orgId** | `string` |  | [Defaults to `undefined`] |

### Return type

**any**

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## listHelpArticlesBrandingOrgIdHelpArticlesGet

> any listHelpArticlesBrandingOrgIdHelpArticlesGet(orgId)

List Help Articles

### Example

```ts
import {
  Configuration,
  BrandingApi,
} from '@xr7/sdk';
import type { ListHelpArticlesBrandingOrgIdHelpArticlesGetRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new BrandingApi();

  const body = {
    // string
    orgId: orgId_example,
  } satisfies ListHelpArticlesBrandingOrgIdHelpArticlesGetRequest;

  try {
    const data = await api.listHelpArticlesBrandingOrgIdHelpArticlesGet(body);
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
| **orgId** | `string` |  | [Defaults to `undefined`] |

### Return type

**any**

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## patchBrandingBrandingOrgIdPatch

> any patchBrandingBrandingOrgIdPatch(orgId, brandingProfilePatchRequest)

Patch Branding

### Example

```ts
import {
  Configuration,
  BrandingApi,
} from '@xr7/sdk';
import type { PatchBrandingBrandingOrgIdPatchRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new BrandingApi();

  const body = {
    // string
    orgId: orgId_example,
    // BrandingProfilePatchRequest
    brandingProfilePatchRequest: ...,
  } satisfies PatchBrandingBrandingOrgIdPatchRequest;

  try {
    const data = await api.patchBrandingBrandingOrgIdPatch(body);
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
| **orgId** | `string` |  | [Defaults to `undefined`] |
| **brandingProfilePatchRequest** | [BrandingProfilePatchRequest](BrandingProfilePatchRequest.md) |  | |

### Return type

**any**

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


## uiShellUiShellGet

> string uiShellUiShellGet(orgId)

Ui Shell

### Example

```ts
import {
  Configuration,
  BrandingApi,
} from '@xr7/sdk';
import type { UiShellUiShellGetRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new BrandingApi();

  const body = {
    // string (optional)
    orgId: orgId_example,
  } satisfies UiShellUiShellGetRequest;

  try {
    const data = await api.uiShellUiShellGet(body);
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
| **orgId** | `string` |  | [Optional] [Defaults to `&#39;xr7-default&#39;`] |

### Return type

**string**

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `text/html`, `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)
