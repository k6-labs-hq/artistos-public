# TermsApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**acceptTermsArtistsArtistIdTermsAcceptPost**](TermsApi.md#accepttermsartistsartistidtermsacceptpost) | **POST** /artists/{artist_id}/terms/accept | Accept Terms |
| [**getTermsTermsGet**](TermsApi.md#gettermstermsget) | **GET** /terms | Get Terms |
| [**termsStatusArtistsArtistIdTermsStatusGet**](TermsApi.md#termsstatusartistsartistidtermsstatusget) | **GET** /artists/{artist_id}/terms/status | Terms Status |



## acceptTermsArtistsArtistIdTermsAcceptPost

> TermsAcceptanceSchema acceptTermsArtistsArtistIdTermsAcceptPost(artistId, termsAcceptRequest)

Accept Terms

Record the artist\&#39;s acceptance of the current Artist Recovery Services Agreement.  This endpoint: 1. Verifies the artist exists. 2. Verifies the version the artist was shown matches the live version    (stale-page protection). 3. Verifies the &#x60;&#x60;agreed&#x60;&#x60; flag is &#x60;&#x60;true&#x60;&#x60; — a bare form POST cannot    accidentally create an acceptance record. 4. Persists an immutable TermsAcceptance row with server-set timestamp,    IP address, and User-Agent string.  Submitting again after the artist has already accepted the current version is idempotent — the existing acceptance record is returned without creating a duplicate.

### Example

```ts
import {
  Configuration,
  TermsApi,
} from '@xr7/sdk';
import type { AcceptTermsArtistsArtistIdTermsAcceptPostRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new TermsApi();

  const body = {
    // string
    artistId: artistId_example,
    // TermsAcceptRequest
    termsAcceptRequest: ...,
  } satisfies AcceptTermsArtistsArtistIdTermsAcceptPostRequest;

  try {
    const data = await api.acceptTermsArtistsArtistIdTermsAcceptPost(body);
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
| **termsAcceptRequest** | [TermsAcceptRequest](TermsAcceptRequest.md) |  | |

### Return type

[**TermsAcceptanceSchema**](TermsAcceptanceSchema.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **201** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## getTermsTermsGet

> { [key: string]: any; } getTermsTermsGet()

Get Terms

Return the current Artist Recovery Services Agreement text, version identifier, and SHA-256 hash.  The client should render the full &#x60;&#x60;text&#x60;&#x60; field for the artist to read before presenting the acceptance checkbox.  The &#x60;&#x60;version&#x60;&#x60; and &#x60;&#x60;sha256&#x60;&#x60; values must be echoed back verbatim in POST /artists/{id}/terms/accept.

### Example

```ts
import {
  Configuration,
  TermsApi,
} from '@xr7/sdk';
import type { GetTermsTermsGetRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new TermsApi();

  try {
    const data = await api.getTermsTermsGet();
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

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## termsStatusArtistsArtistIdTermsStatusGet

> { [key: string]: any; } termsStatusArtistsArtistIdTermsStatusGet(artistId)

Terms Status

Return whether the artist has accepted the current version of the Artist Recovery Services Agreement.  &#x60;&#x60;accepted&#x60;&#x60; is &#x60;&#x60;True&#x60;&#x60; only if there is an acceptance record for the *current* live version.  If the terms were updated since the artist last agreed, &#x60;&#x60;accepted&#x60;&#x60; will be &#x60;&#x60;False&#x60;&#x60; and &#x60;&#x60;pending_version&#x60;&#x60; will indicate the version the artist needs to accept.

### Example

```ts
import {
  Configuration,
  TermsApi,
} from '@xr7/sdk';
import type { TermsStatusArtistsArtistIdTermsStatusGetRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new TermsApi();

  const body = {
    // string
    artistId: artistId_example,
  } satisfies TermsStatusArtistsArtistIdTermsStatusGetRequest;

  try {
    const data = await api.termsStatusArtistsArtistIdTermsStatusGet(body);
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
