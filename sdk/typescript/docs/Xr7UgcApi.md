# Xr7UgcApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**ingestSignalsArtistsArtistIdXr7UgcSignalsIngestPost**](Xr7UgcApi.md#ingestsignalsartistsartistidxr7ugcsignalsingestpost) | **POST** /artists/{artist_id}/xr7/ugc/signals/ingest | Ingest Signals |
| [**ugcOpportunitiesArtistsArtistIdXr7UgcOpportunitiesGet**](Xr7UgcApi.md#ugcopportunitiesartistsartistidxr7ugcopportunitiesget) | **GET** /artists/{artist_id}/xr7/ugc/opportunities | Ugc Opportunities |



## ingestSignalsArtistsArtistIdXr7UgcSignalsIngestPost

> any ingestSignalsArtistsArtistIdXr7UgcSignalsIngestPost(artistId, uGCSignalIngestRequest)

Ingest Signals

### Example

```ts
import {
  Configuration,
  Xr7UgcApi,
} from '@xr7/sdk';
import type { IngestSignalsArtistsArtistIdXr7UgcSignalsIngestPostRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new Xr7UgcApi();

  const body = {
    // string
    artistId: artistId_example,
    // UGCSignalIngestRequest
    uGCSignalIngestRequest: ...,
  } satisfies IngestSignalsArtistsArtistIdXr7UgcSignalsIngestPostRequest;

  try {
    const data = await api.ingestSignalsArtistsArtistIdXr7UgcSignalsIngestPost(body);
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
| **uGCSignalIngestRequest** | [UGCSignalIngestRequest](UGCSignalIngestRequest.md) |  | |

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


## ugcOpportunitiesArtistsArtistIdXr7UgcOpportunitiesGet

> any ugcOpportunitiesArtistsArtistIdXr7UgcOpportunitiesGet(artistId, tenantId, minConfidence, minEstimatedValue, status)

Ugc Opportunities

### Example

```ts
import {
  Configuration,
  Xr7UgcApi,
} from '@xr7/sdk';
import type { UgcOpportunitiesArtistsArtistIdXr7UgcOpportunitiesGetRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new Xr7UgcApi();

  const body = {
    // string
    artistId: artistId_example,
    // string (optional)
    tenantId: tenantId_example,
    // number (optional)
    minConfidence: 8.14,
    // number (optional)
    minEstimatedValue: 8.14,
    // string (optional)
    status: status_example,
  } satisfies UgcOpportunitiesArtistsArtistIdXr7UgcOpportunitiesGetRequest;

  try {
    const data = await api.ugcOpportunitiesArtistsArtistIdXr7UgcOpportunitiesGet(body);
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
| **tenantId** | `string` |  | [Optional] [Defaults to `&#39;default&#39;`] |
| **minConfidence** | `number` |  | [Optional] [Defaults to `0.65`] |
| **minEstimatedValue** | `number` |  | [Optional] [Defaults to `0.0`] |
| **status** | `string` |  | [Optional] [Defaults to `undefined`] |

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
