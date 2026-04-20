# WidgetApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**claimWidgetClaimPost**](WidgetApi.md#claimwidgetclaimpost) | **POST** /widget/claim | Claim |
| [**estimateWidgetEstimatePost**](WidgetApi.md#estimatewidgetestimatepost) | **POST** /widget/estimate | Estimate |
| [**listLeadsWidgetLeadsGet**](WidgetApi.md#listleadswidgetleadsget) | **GET** /widget/leads | List Leads |
| [**registerWidgetRegisterPost**](WidgetApi.md#registerwidgetregisterpost) | **POST** /widget/register | Register |
| [**verifyWidgetVerifyPost**](WidgetApi.md#verifywidgetverifypost) | **POST** /widget/verify | Verify |



## claimWidgetClaimPost

> any claimWidgetClaimPost(claimRequest)

Claim

Mark a lead as \&quot;claimed\&quot; when the artist clicks the recovery CTA.  The &#x60;&#x60;lead_id&#x60;&#x60; returned by &#x60;&#x60;POST /widget/estimate&#x60;&#x60; is required. Idempotent — calling this multiple times on the same lead is safe.

### Example

```ts
import {
  Configuration,
  WidgetApi,
} from '@xr7/sdk';
import type { ClaimWidgetClaimPostRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new WidgetApi();

  const body = {
    // ClaimRequest
    claimRequest: ...,
  } satisfies ClaimWidgetClaimPostRequest;

  try {
    const data = await api.claimWidgetClaimPost(body);
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
| **claimRequest** | [ClaimRequest](ClaimRequest.md) |  | |

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


## estimateWidgetEstimatePost

> any estimateWidgetEstimatePost(estimateRequest)

Estimate

Step 3 of the MFA flow.  Presents the estimate token obtained from &#x60;&#x60;POST /widget/verify&#x60;&#x60; along with optional career profile information.  Saves a lead record to the database, emails the estimate results to the artist, and returns the full royalty owed estimate.

### Example

```ts
import {
  Configuration,
  WidgetApi,
} from '@xr7/sdk';
import type { EstimateWidgetEstimatePostRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new WidgetApi();

  const body = {
    // EstimateRequest
    estimateRequest: ...,
  } satisfies EstimateWidgetEstimatePostRequest;

  try {
    const data = await api.estimateWidgetEstimatePost(body);
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
| **estimateRequest** | [EstimateRequest](EstimateRequest.md) |  | |

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


## listLeadsWidgetLeadsGet

> Array&lt;WidgetLeadSchema&gt; listLeadsWidgetLeadsGet(xAdminKey)

List Leads

Return all widget leads in reverse-chronological order.  Requires the &#x60;&#x60;X-Admin-Key&#x60;&#x60; request header to equal the &#x60;&#x60;WIDGET_ADMIN_KEY&#x60;&#x60; environment variable.

### Example

```ts
import {
  Configuration,
  WidgetApi,
} from '@xr7/sdk';
import type { ListLeadsWidgetLeadsGetRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new WidgetApi();

  const body = {
    // string (optional)
    xAdminKey: xAdminKey_example,
  } satisfies ListLeadsWidgetLeadsGetRequest;

  try {
    const data = await api.listLeadsWidgetLeadsGet(body);
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
| **xAdminKey** | `string` |  | [Optional] [Defaults to `&#39;&#39;`] |

### Return type

[**Array&lt;WidgetLeadSchema&gt;**](WidgetLeadSchema.md)

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


## registerWidgetRegisterPost

> RegisterResponse registerWidgetRegisterPost(registerRequest)

Register

Step 1 of the MFA flow.  Validates the artist\&#39;s identity details, creates a verification session, and dispatches a 6-digit OTP to both the provided phone number and email address.  In **development** environments (&#x60;&#x60;XR7_ENV&#x60;&#x60; ≠ &#x60;&#x60;production&#x60;&#x60;), the OTPs are also returned in the response body under &#x60;&#x60;dev_phone_otp&#x60;&#x60; and &#x60;&#x60;dev_email_otp&#x60;&#x60; so that local testing requires no external credentials. These fields are **absent** in production.

### Example

```ts
import {
  Configuration,
  WidgetApi,
} from '@xr7/sdk';
import type { RegisterWidgetRegisterPostRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new WidgetApi();

  const body = {
    // RegisterRequest
    registerRequest: ...,
  } satisfies RegisterWidgetRegisterPostRequest;

  try {
    const data = await api.registerWidgetRegisterPost(body);
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
| **registerRequest** | [RegisterRequest](RegisterRequest.md) |  | |

### Return type

[**RegisterResponse**](RegisterResponse.md)

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


## verifyWidgetVerifyPost

> VerifyResponse verifyWidgetVerifyPost(verifyRequest)

Verify

Step 2 of the MFA flow.  Both the phone OTP and email OTP must be correct.  On success, a short-lived estimate token is returned.  This token must be presented to &#x60;&#x60;POST /widget/estimate&#x60;&#x60; to retrieve the royalty estimate.

### Example

```ts
import {
  Configuration,
  WidgetApi,
} from '@xr7/sdk';
import type { VerifyWidgetVerifyPostRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new WidgetApi();

  const body = {
    // VerifyRequest
    verifyRequest: ...,
  } satisfies VerifyWidgetVerifyPostRequest;

  try {
    const data = await api.verifyWidgetVerifyPost(body);
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
| **verifyRequest** | [VerifyRequest](VerifyRequest.md) |  | |

### Return type

[**VerifyResponse**](VerifyResponse.md)

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
