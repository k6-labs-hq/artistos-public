# TrustApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**getTrustTraceArtistsArtistIdTrustTraceGet**](TrustApi.md#gettrusttraceartistsartistidtrusttraceget) | **GET** /artists/{artist_id}/trust/trace | Get Trust Trace |



## getTrustTraceArtistsArtistIdTrustTraceGet

> { [key: string]: any; } getTrustTraceArtistsArtistIdTrustTraceGet(artistId)

Get Trust Trace

Return the real-time pipeline trace feed for this artist.  Each entry contains stage, sub_stage, confidence (0-1), eta_seconds, and a plain-English explanation of what XR7 is doing right now.

### Example

```ts
import {
  Configuration,
  TrustApi,
} from '@xr7/sdk';
import type { GetTrustTraceArtistsArtistIdTrustTraceGetRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const config = new Configuration({ 
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new TrustApi(config);

  const body = {
    // string
    artistId: artistId_example,
  } satisfies GetTrustTraceArtistsArtistIdTrustTraceGetRequest;

  try {
    const data = await api.getTrustTraceArtistsArtistIdTrustTraceGet(body);
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

