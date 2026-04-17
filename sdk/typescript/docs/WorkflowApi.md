# WorkflowApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**runFullAutonomousWorkflowArtistsArtistIdWorkflowRunFullAutonomousPost**](WorkflowApi.md#runfullautonomousworkflowartistsartistidworkflowrunfullautonomouspost) | **POST** /artists/{artist_id}/workflow/run-full-autonomous | Run Full Autonomous Workflow |
| [**workflowRunStatusArtistsArtistIdWorkflowRunsRunIdGet**](WorkflowApi.md#workflowrunstatusartistsartistidworkflowrunsrunidget) | **GET** /artists/{artist_id}/workflow/runs/{run_id} | Workflow Run Status |



## runFullAutonomousWorkflowArtistsArtistIdWorkflowRunFullAutonomousPost

> WorkflowRunResponse runFullAutonomousWorkflowArtistsArtistIdWorkflowRunFullAutonomousPost(artistId)

Run Full Autonomous Workflow

### Example

```ts
import {
  Configuration,
  WorkflowApi,
} from '@xr7/sdk';
import type { RunFullAutonomousWorkflowArtistsArtistIdWorkflowRunFullAutonomousPostRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new WorkflowApi();

  const body = {
    // string
    artistId: artistId_example,
  } satisfies RunFullAutonomousWorkflowArtistsArtistIdWorkflowRunFullAutonomousPostRequest;

  try {
    const data = await api.runFullAutonomousWorkflowArtistsArtistIdWorkflowRunFullAutonomousPost(body);
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
| **artistId** | `string` |  | [Defaults to `undefined`] |

### Return type

[**WorkflowRunResponse**](WorkflowRunResponse.md)

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


## workflowRunStatusArtistsArtistIdWorkflowRunsRunIdGet

> any workflowRunStatusArtistsArtistIdWorkflowRunsRunIdGet(artistId, runId)

Workflow Run Status

### Example

```ts
import {
  Configuration,
  WorkflowApi,
} from '@xr7/sdk';
import type { WorkflowRunStatusArtistsArtistIdWorkflowRunsRunIdGetRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new WorkflowApi();

  const body = {
    // string
    artistId: artistId_example,
    // string
    runId: runId_example,
  } satisfies WorkflowRunStatusArtistsArtistIdWorkflowRunsRunIdGetRequest;

  try {
    const data = await api.workflowRunStatusArtistsArtistIdWorkflowRunsRunIdGet(body);
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
| **artistId** | `string` |  | [Defaults to `undefined`] |
| **runId** | `string` |  | [Defaults to `undefined`] |

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
