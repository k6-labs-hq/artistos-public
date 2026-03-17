# WorkspaceApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**workspaceArtistsWorkspaceArtistsGet**](WorkspaceApi.md#workspaceartistsworkspaceartistsget) | **GET** /workspace/artists | Workspace Artists |
| [**workspaceClaimsWorkspaceClaimsGet**](WorkspaceApi.md#workspaceclaimsworkspaceclaimsget) | **GET** /workspace/claims | Workspace Claims |
| [**workspaceDeadlinesWorkspaceDeadlinesGet**](WorkspaceApi.md#workspacedeadlinesworkspacedeadlinesget) | **GET** /workspace/deadlines | Workspace Deadlines |
| [**workspaceOverviewWorkspaceOverviewGet**](WorkspaceApi.md#workspaceoverviewworkspaceoverviewget) | **GET** /workspace/overview | Workspace Overview |



## workspaceArtistsWorkspaceArtistsGet

> any workspaceArtistsWorkspaceArtistsGet(xWorkspaceKey, xWorkspaceRole)

Workspace Artists

### Example

```ts
import {
  Configuration,
  WorkspaceApi,
} from '@xr7/sdk';
import type { WorkspaceArtistsWorkspaceArtistsGetRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new WorkspaceApi();

  const body = {
    // string (optional)
    xWorkspaceKey: xWorkspaceKey_example,
    // string (optional)
    xWorkspaceRole: xWorkspaceRole_example,
  } satisfies WorkspaceArtistsWorkspaceArtistsGetRequest;

  try {
    const data = await api.workspaceArtistsWorkspaceArtistsGet(body);
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
| **xWorkspaceKey** | `string` |  | [Optional] [Defaults to `&#39;&#39;`] |
| **xWorkspaceRole** | `string` |  | [Optional] [Defaults to `&#39;&#39;`] |

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


## workspaceClaimsWorkspaceClaimsGet

> any workspaceClaimsWorkspaceClaimsGet(xWorkspaceKey, xWorkspaceRole)

Workspace Claims

### Example

```ts
import {
  Configuration,
  WorkspaceApi,
} from '@xr7/sdk';
import type { WorkspaceClaimsWorkspaceClaimsGetRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new WorkspaceApi();

  const body = {
    // string (optional)
    xWorkspaceKey: xWorkspaceKey_example,
    // string (optional)
    xWorkspaceRole: xWorkspaceRole_example,
  } satisfies WorkspaceClaimsWorkspaceClaimsGetRequest;

  try {
    const data = await api.workspaceClaimsWorkspaceClaimsGet(body);
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
| **xWorkspaceKey** | `string` |  | [Optional] [Defaults to `&#39;&#39;`] |
| **xWorkspaceRole** | `string` |  | [Optional] [Defaults to `&#39;&#39;`] |

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


## workspaceDeadlinesWorkspaceDeadlinesGet

> any workspaceDeadlinesWorkspaceDeadlinesGet(xWorkspaceKey, xWorkspaceRole)

Workspace Deadlines

### Example

```ts
import {
  Configuration,
  WorkspaceApi,
} from '@xr7/sdk';
import type { WorkspaceDeadlinesWorkspaceDeadlinesGetRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new WorkspaceApi();

  const body = {
    // string (optional)
    xWorkspaceKey: xWorkspaceKey_example,
    // string (optional)
    xWorkspaceRole: xWorkspaceRole_example,
  } satisfies WorkspaceDeadlinesWorkspaceDeadlinesGetRequest;

  try {
    const data = await api.workspaceDeadlinesWorkspaceDeadlinesGet(body);
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
| **xWorkspaceKey** | `string` |  | [Optional] [Defaults to `&#39;&#39;`] |
| **xWorkspaceRole** | `string` |  | [Optional] [Defaults to `&#39;&#39;`] |

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


## workspaceOverviewWorkspaceOverviewGet

> any workspaceOverviewWorkspaceOverviewGet(xWorkspaceKey, xWorkspaceRole)

Workspace Overview

### Example

```ts
import {
  Configuration,
  WorkspaceApi,
} from '@xr7/sdk';
import type { WorkspaceOverviewWorkspaceOverviewGetRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new WorkspaceApi();

  const body = {
    // string (optional)
    xWorkspaceKey: xWorkspaceKey_example,
    // string (optional)
    xWorkspaceRole: xWorkspaceRole_example,
  } satisfies WorkspaceOverviewWorkspaceOverviewGetRequest;

  try {
    const data = await api.workspaceOverviewWorkspaceOverviewGet(body);
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
| **xWorkspaceKey** | `string` |  | [Optional] [Defaults to `&#39;&#39;`] |
| **xWorkspaceRole** | `string` |  | [Optional] [Defaults to `&#39;&#39;`] |

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

