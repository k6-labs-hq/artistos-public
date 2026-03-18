# GovernanceApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**eraseArtistDataArtistsArtistIdPrivacyErasePost**](GovernanceApi.md#eraseartistdataartistsartistidprivacyerasepost) | **POST** /artists/{artist_id}/privacy/erase | Erase Artist Data |
| [**exportArtistDataArtistsArtistIdPrivacyExportPost**](GovernanceApi.md#exportartistdataartistsartistidprivacyexportpost) | **POST** /artists/{artist_id}/privacy/export | Export Artist Data |
| [**listAdminAuditEventsAdminAuditEventsGet**](GovernanceApi.md#listadminauditeventsadminauditeventsget) | **GET** /admin/audit/events | List Admin Audit Events |



## eraseArtistDataArtistsArtistIdPrivacyErasePost

> { [key: string]: any; } eraseArtistDataArtistsArtistIdPrivacyErasePost(artistId)

Erase Artist Data

### Example

```ts
import {
  Configuration,
  GovernanceApi,
} from '@xr7/sdk';
import type { EraseArtistDataArtistsArtistIdPrivacyErasePostRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const config = new Configuration({ 
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new GovernanceApi(config);

  const body = {
    // string
    artistId: artistId_example,
  } satisfies EraseArtistDataArtistsArtistIdPrivacyErasePostRequest;

  try {
    const data = await api.eraseArtistDataArtistsArtistIdPrivacyErasePost(body);
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
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## exportArtistDataArtistsArtistIdPrivacyExportPost

> { [key: string]: any; } exportArtistDataArtistsArtistIdPrivacyExportPost(artistId)

Export Artist Data

### Example

```ts
import {
  Configuration,
  GovernanceApi,
} from '@xr7/sdk';
import type { ExportArtistDataArtistsArtistIdPrivacyExportPostRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const config = new Configuration({ 
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new GovernanceApi(config);

  const body = {
    // string
    artistId: artistId_example,
  } satisfies ExportArtistDataArtistsArtistIdPrivacyExportPostRequest;

  try {
    const data = await api.exportArtistDataArtistsArtistIdPrivacyExportPost(body);
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
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## listAdminAuditEventsAdminAuditEventsGet

> { [key: string]: any; } listAdminAuditEventsAdminAuditEventsGet(limit)

List Admin Audit Events

### Example

```ts
import {
  Configuration,
  GovernanceApi,
} from '@xr7/sdk';
import type { ListAdminAuditEventsAdminAuditEventsGetRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const config = new Configuration({ 
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new GovernanceApi(config);

  const body = {
    // number (optional)
    limit: 56,
  } satisfies ListAdminAuditEventsAdminAuditEventsGetRequest;

  try {
    const data = await api.listAdminAuditEventsAdminAuditEventsGet(body);
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
| **limit** | `number` |  | [Optional] [Defaults to `100`] |

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
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

