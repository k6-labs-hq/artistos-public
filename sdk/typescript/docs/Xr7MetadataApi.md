# Xr7MetadataApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**applyRepairsArtistsArtistIdXr7MetadataRepairApplyPost**](Xr7MetadataApi.md#applyrepairsartistsartistidxr7metadatarepairapplypost) | **POST** /artists/{artist_id}/xr7/metadata/repair/apply | Apply Repairs |
| [**suggestRepairsArtistsArtistIdXr7MetadataRepairSuggestPost**](Xr7MetadataApi.md#suggestrepairsartistsartistidxr7metadatarepairsuggestpost) | **POST** /artists/{artist_id}/xr7/metadata/repair/suggest | Suggest Repairs |



## applyRepairsArtistsArtistIdXr7MetadataRepairApplyPost

> any applyRepairsArtistsArtistIdXr7MetadataRepairApplyPost(artistId, metadataRepairApplyRequest)

Apply Repairs

### Example

```ts
import {
  Configuration,
  Xr7MetadataApi,
} from '@xr7/sdk';
import type { ApplyRepairsArtistsArtistIdXr7MetadataRepairApplyPostRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new Xr7MetadataApi();

  const body = {
    // string
    artistId: artistId_example,
    // MetadataRepairApplyRequest
    metadataRepairApplyRequest: ...,
  } satisfies ApplyRepairsArtistsArtistIdXr7MetadataRepairApplyPostRequest;

  try {
    const data = await api.applyRepairsArtistsArtistIdXr7MetadataRepairApplyPost(body);
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
| **metadataRepairApplyRequest** | [MetadataRepairApplyRequest](MetadataRepairApplyRequest.md) |  | |

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


## suggestRepairsArtistsArtistIdXr7MetadataRepairSuggestPost

> any suggestRepairsArtistsArtistIdXr7MetadataRepairSuggestPost(artistId, metadataRepairSuggestRequest)

Suggest Repairs

### Example

```ts
import {
  Configuration,
  Xr7MetadataApi,
} from '@xr7/sdk';
import type { SuggestRepairsArtistsArtistIdXr7MetadataRepairSuggestPostRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new Xr7MetadataApi();

  const body = {
    // string
    artistId: artistId_example,
    // MetadataRepairSuggestRequest
    metadataRepairSuggestRequest: ...,
  } satisfies SuggestRepairsArtistsArtistIdXr7MetadataRepairSuggestPostRequest;

  try {
    const data = await api.suggestRepairsArtistsArtistIdXr7MetadataRepairSuggestPost(body);
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
| **metadataRepairSuggestRequest** | [MetadataRepairSuggestRequest](MetadataRepairSuggestRequest.md) |  | |

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

