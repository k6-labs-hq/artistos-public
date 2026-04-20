# TeamApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**networkInviteArtistsArtistIdNetworkInvitePost**](TeamApi.md#networkinviteartistsartistidnetworkinvitepost) | **POST** /artists/{artist_id}/network/invite | Network Invite |



## networkInviteArtistsArtistIdNetworkInvitePost

> any networkInviteArtistsArtistIdNetworkInvitePost(artistId, inviteRequest)

Network Invite

### Example

```ts
import {
  Configuration,
  TeamApi,
} from '@xr7/sdk';
import type { NetworkInviteArtistsArtistIdNetworkInvitePostRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new TeamApi();

  const body = {
    // string
    artistId: artistId_example,
    // InviteRequest
    inviteRequest: ...,
  } satisfies NetworkInviteArtistsArtistIdNetworkInvitePostRequest;

  try {
    const data = await api.networkInviteArtistsArtistIdNetworkInvitePost(body);
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
| **inviteRequest** | [InviteRequest](InviteRequest.md) |  | |

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
