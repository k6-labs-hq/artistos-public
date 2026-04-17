# ReferralsApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**getReferralsArtistsArtistIdReferralsGet**](ReferralsApi.md#getreferralsartistsartistidreferralsget) | **GET** /artists/{artist_id}/referrals | Get Referrals |
| [**registerReferralArtistsArtistIdReferralsPost**](ReferralsApi.md#registerreferralartistsartistidreferralspost) | **POST** /artists/{artist_id}/referrals | Register Referral |



## getReferralsArtistsArtistIdReferralsGet

> { [key: string]: any; } getReferralsArtistsArtistIdReferralsGet(artistId)

Get Referrals

Return the referral tree and lifetime earnings for this artist.

### Example

```ts
import {
  Configuration,
  ReferralsApi,
} from '@xr7/sdk';
import type { GetReferralsArtistsArtistIdReferralsGetRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const config = new Configuration({
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new ReferralsApi(config);

  const body = {
    // string
    artistId: artistId_example,
  } satisfies GetReferralsArtistsArtistIdReferralsGetRequest;

  try {
    const data = await api.getReferralsArtistsArtistIdReferralsGet(body);
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


## registerReferralArtistsArtistIdReferralsPost

> { [key: string]: any; } registerReferralArtistsArtistIdReferralsPost(artistId, referralRequest)

Register Referral

Register a new artist referral link.  The referrer earns a percentage of the referred artist\&#39;s net recoveries.

### Example

```ts
import {
  Configuration,
  ReferralsApi,
} from '@xr7/sdk';
import type { RegisterReferralArtistsArtistIdReferralsPostRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const config = new Configuration({
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new ReferralsApi(config);

  const body = {
    // string
    artistId: artistId_example,
    // ReferralRequest
    referralRequest: ...,
  } satisfies RegisterReferralArtistsArtistIdReferralsPostRequest;

  try {
    const data = await api.registerReferralArtistsArtistIdReferralsPost(body);
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
| **referralRequest** | [ReferralRequest](ReferralRequest.md) |  | |

### Return type

**{ [key: string]: any; }**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)
