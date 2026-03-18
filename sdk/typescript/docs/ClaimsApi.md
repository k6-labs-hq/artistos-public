# ClaimsApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**activateNegotiatorAgentClaimsClaimIdActivateAgentPost**](ClaimsApi.md#activatenegotiatoragentclaimsclaimidactivateagentpost) | **POST** /claims/{claim_id}/activate-agent | Activate Negotiator Agent |
| [**advanceClaimClaimsClaimIdAdvancePost**](ClaimsApi.md#advanceclaimclaimsclaimidadvancepost) | **POST** /claims/{claim_id}/advance | Advance Claim |
| [**claimAutomationPlanClaimsClaimIdAutomationPlanGet**](ClaimsApi.md#claimautomationplanclaimsclaimidautomationplanget) | **GET** /claims/{claim_id}/automation-plan | Claim Automation Plan |
| [**claimEvidenceOptimizedClaimsClaimIdEvidenceOptimizedGet**](ClaimsApi.md#claimevidenceoptimizedclaimsclaimidevidenceoptimizedget) | **GET** /claims/{claim_id}/evidence/optimized | Claim Evidence Optimized |
| [**claimEvidenceStrengthClaimsClaimIdEvidenceStrengthGet**](ClaimsApi.md#claimevidencestrengthclaimsclaimidevidencestrengthget) | **GET** /claims/{claim_id}/evidence/strength | Claim Evidence Strength |
| [**claimForecastClaimsClaimIdForecastGet**](ClaimsApi.md#claimforecastclaimsclaimidforecastget) | **GET** /claims/{claim_id}/forecast | Claim Forecast |
| [**claimNegotiationIntelClaimsClaimIdNegotiationIntelGet**](ClaimsApi.md#claimnegotiationintelclaimsclaimidnegotiationintelget) | **GET** /claims/{claim_id}/negotiation-intel | Claim Negotiation Intel |
| [**claimPlaybookClaimsClaimIdPlaybookGet**](ClaimsApi.md#claimplaybookclaimsclaimidplaybookget) | **GET** /claims/{claim_id}/playbook | Claim Playbook |
| [**claimSlaPredictionClaimsClaimIdSlaPredictionGet**](ClaimsApi.md#claimslapredictionclaimsclaimidslapredictionget) | **GET** /claims/{claim_id}/sla-prediction | Claim Sla Prediction |
| [**claimStrengthExplainerClaimsClaimIdStrengthExplainerGet**](ClaimsApi.md#claimstrengthexplainerclaimsclaimidstrengthexplainerget) | **GET** /claims/{claim_id}/strength-explainer | Claim Strength Explainer |
| [**createClaimForArtistArtistsArtistIdClaimsPost**](ClaimsApi.md#createclaimforartistartistsartistidclaimspost) | **POST** /artists/{artist_id}/claims | Create Claim For Artist |
| [**escalateLegalClaimsClaimIdEscalateLegalPost**](ClaimsApi.md#escalatelegalclaimsclaimidescalatelegalpost) | **POST** /claims/{claim_id}/escalate-legal | Escalate Legal |
| [**exportEvidencePacketClaimsClaimIdEvidenceExportGet**](ClaimsApi.md#exportevidencepacketclaimsclaimidevidenceexportget) | **GET** /claims/{claim_id}/evidence/export | Export Evidence Packet |
| [**exportEvidencePacketExpertModeClaimsClaimIdEvidenceExportPost**](ClaimsApi.md#exportevidencepacketexpertmodeclaimsclaimidevidenceexportpost) | **POST** /claims/{claim_id}/evidence/export | Export Evidence Packet Expert Mode |
| [**generateAttorneyEvidenceFileApiClaimsClaimIdAttorneyEvidencePost**](ClaimsApi.md#generateattorneyevidencefileapiclaimsclaimidattorneyevidencepost) | **POST** /api/claims/{claim_id}/attorney-evidence | Generate Attorney Evidence File |
| [**generateAttorneyEvidenceFileClaimsClaimIdAttorneyEvidencePost**](ClaimsApi.md#generateattorneyevidencefileclaimsclaimidattorneyevidencepost) | **POST** /claims/{claim_id}/attorney-evidence | Generate Attorney Evidence File |
| [**generateEvidenceClaimsClaimIdEvidencePost**](ClaimsApi.md#generateevidenceclaimsclaimidevidencepost) | **POST** /claims/{claim_id}/evidence | Generate Evidence |
| [**getClaimClaimsClaimIdGet**](ClaimsApi.md#getclaimclaimsclaimidget) | **GET** /claims/{claim_id} | Get Claim |
| [**getEvidenceClaimsClaimIdEvidenceGet**](ClaimsApi.md#getevidenceclaimsclaimidevidenceget) | **GET** /claims/{claim_id}/evidence | Get Evidence |
| [**listClaimsArtistsArtistIdClaimsGet**](ClaimsApi.md#listclaimsartistsartistidclaimsget) | **GET** /artists/{artist_id}/claims | List Claims |
| [**reconcileClaimClaimsClaimIdReconcilePost**](ClaimsApi.md#reconcileclaimclaimsclaimidreconcilepost) | **POST** /claims/{claim_id}/reconcile | Reconcile Claim |
| [**verifyEvidencePacketClaimsClaimIdEvidenceVerifyGet**](ClaimsApi.md#verifyevidencepacketclaimsclaimidevidenceverifyget) | **GET** /claims/{claim_id}/evidence/verify | Verify Evidence Packet |



## activateNegotiatorAgentClaimsClaimIdActivateAgentPost

> any activateNegotiatorAgentClaimsClaimIdActivateAgentPost(claimId)

Activate Negotiator Agent

### Example

```ts
import {
  Configuration,
  ClaimsApi,
} from '@xr7/sdk';
import type { ActivateNegotiatorAgentClaimsClaimIdActivateAgentPostRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new ClaimsApi();

  const body = {
    // string
    claimId: claimId_example,
  } satisfies ActivateNegotiatorAgentClaimsClaimIdActivateAgentPostRequest;

  try {
    const data = await api.activateNegotiatorAgentClaimsClaimIdActivateAgentPost(body);
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
| **claimId** | `string` |  | [Defaults to `undefined`] |

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


## advanceClaimClaimsClaimIdAdvancePost

> ClaimSchema advanceClaimClaimsClaimIdAdvancePost(claimId)

Advance Claim

### Example

```ts
import {
  Configuration,
  ClaimsApi,
} from '@xr7/sdk';
import type { AdvanceClaimClaimsClaimIdAdvancePostRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new ClaimsApi();

  const body = {
    // string
    claimId: claimId_example,
  } satisfies AdvanceClaimClaimsClaimIdAdvancePostRequest;

  try {
    const data = await api.advanceClaimClaimsClaimIdAdvancePost(body);
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
| **claimId** | `string` |  | [Defaults to `undefined`] |

### Return type

[**ClaimSchema**](ClaimSchema.md)

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


## claimAutomationPlanClaimsClaimIdAutomationPlanGet

> any claimAutomationPlanClaimsClaimIdAutomationPlanGet(claimId)

Claim Automation Plan

### Example

```ts
import {
  Configuration,
  ClaimsApi,
} from '@xr7/sdk';
import type { ClaimAutomationPlanClaimsClaimIdAutomationPlanGetRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new ClaimsApi();

  const body = {
    // string
    claimId: claimId_example,
  } satisfies ClaimAutomationPlanClaimsClaimIdAutomationPlanGetRequest;

  try {
    const data = await api.claimAutomationPlanClaimsClaimIdAutomationPlanGet(body);
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
| **claimId** | `string` |  | [Defaults to `undefined`] |

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


## claimEvidenceOptimizedClaimsClaimIdEvidenceOptimizedGet

> any claimEvidenceOptimizedClaimsClaimIdEvidenceOptimizedGet(claimId)

Claim Evidence Optimized

### Example

```ts
import {
  Configuration,
  ClaimsApi,
} from '@xr7/sdk';
import type { ClaimEvidenceOptimizedClaimsClaimIdEvidenceOptimizedGetRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new ClaimsApi();

  const body = {
    // string
    claimId: claimId_example,
  } satisfies ClaimEvidenceOptimizedClaimsClaimIdEvidenceOptimizedGetRequest;

  try {
    const data = await api.claimEvidenceOptimizedClaimsClaimIdEvidenceOptimizedGet(body);
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
| **claimId** | `string` |  | [Defaults to `undefined`] |

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


## claimEvidenceStrengthClaimsClaimIdEvidenceStrengthGet

> any claimEvidenceStrengthClaimsClaimIdEvidenceStrengthGet(claimId)

Claim Evidence Strength

### Example

```ts
import {
  Configuration,
  ClaimsApi,
} from '@xr7/sdk';
import type { ClaimEvidenceStrengthClaimsClaimIdEvidenceStrengthGetRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new ClaimsApi();

  const body = {
    // string
    claimId: claimId_example,
  } satisfies ClaimEvidenceStrengthClaimsClaimIdEvidenceStrengthGetRequest;

  try {
    const data = await api.claimEvidenceStrengthClaimsClaimIdEvidenceStrengthGet(body);
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
| **claimId** | `string` |  | [Defaults to `undefined`] |

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


## claimForecastClaimsClaimIdForecastGet

> any claimForecastClaimsClaimIdForecastGet(claimId)

Claim Forecast

### Example

```ts
import {
  Configuration,
  ClaimsApi,
} from '@xr7/sdk';
import type { ClaimForecastClaimsClaimIdForecastGetRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new ClaimsApi();

  const body = {
    // string
    claimId: claimId_example,
  } satisfies ClaimForecastClaimsClaimIdForecastGetRequest;

  try {
    const data = await api.claimForecastClaimsClaimIdForecastGet(body);
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
| **claimId** | `string` |  | [Defaults to `undefined`] |

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


## claimNegotiationIntelClaimsClaimIdNegotiationIntelGet

> any claimNegotiationIntelClaimsClaimIdNegotiationIntelGet(claimId)

Claim Negotiation Intel

### Example

```ts
import {
  Configuration,
  ClaimsApi,
} from '@xr7/sdk';
import type { ClaimNegotiationIntelClaimsClaimIdNegotiationIntelGetRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new ClaimsApi();

  const body = {
    // string
    claimId: claimId_example,
  } satisfies ClaimNegotiationIntelClaimsClaimIdNegotiationIntelGetRequest;

  try {
    const data = await api.claimNegotiationIntelClaimsClaimIdNegotiationIntelGet(body);
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
| **claimId** | `string` |  | [Defaults to `undefined`] |

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


## claimPlaybookClaimsClaimIdPlaybookGet

> any claimPlaybookClaimsClaimIdPlaybookGet(claimId)

Claim Playbook

### Example

```ts
import {
  Configuration,
  ClaimsApi,
} from '@xr7/sdk';
import type { ClaimPlaybookClaimsClaimIdPlaybookGetRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new ClaimsApi();

  const body = {
    // string
    claimId: claimId_example,
  } satisfies ClaimPlaybookClaimsClaimIdPlaybookGetRequest;

  try {
    const data = await api.claimPlaybookClaimsClaimIdPlaybookGet(body);
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
| **claimId** | `string` |  | [Defaults to `undefined`] |

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


## claimSlaPredictionClaimsClaimIdSlaPredictionGet

> any claimSlaPredictionClaimsClaimIdSlaPredictionGet(claimId)

Claim Sla Prediction

### Example

```ts
import {
  Configuration,
  ClaimsApi,
} from '@xr7/sdk';
import type { ClaimSlaPredictionClaimsClaimIdSlaPredictionGetRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new ClaimsApi();

  const body = {
    // string
    claimId: claimId_example,
  } satisfies ClaimSlaPredictionClaimsClaimIdSlaPredictionGetRequest;

  try {
    const data = await api.claimSlaPredictionClaimsClaimIdSlaPredictionGet(body);
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
| **claimId** | `string` |  | [Defaults to `undefined`] |

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


## claimStrengthExplainerClaimsClaimIdStrengthExplainerGet

> any claimStrengthExplainerClaimsClaimIdStrengthExplainerGet(claimId)

Claim Strength Explainer

### Example

```ts
import {
  Configuration,
  ClaimsApi,
} from '@xr7/sdk';
import type { ClaimStrengthExplainerClaimsClaimIdStrengthExplainerGetRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new ClaimsApi();

  const body = {
    // string
    claimId: claimId_example,
  } satisfies ClaimStrengthExplainerClaimsClaimIdStrengthExplainerGetRequest;

  try {
    const data = await api.claimStrengthExplainerClaimsClaimIdStrengthExplainerGet(body);
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
| **claimId** | `string` |  | [Defaults to `undefined`] |

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


## createClaimForArtistArtistsArtistIdClaimsPost

> ClaimSchema createClaimForArtistArtistsArtistIdClaimsPost(artistId, claimCreateRequest, authorization)

Create Claim For Artist

### Example

```ts
import {
  Configuration,
  ClaimsApi,
} from '@xr7/sdk';
import type { CreateClaimForArtistArtistsArtistIdClaimsPostRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new ClaimsApi();

  const body = {
    // string
    artistId: artistId_example,
    // ClaimCreateRequest
    claimCreateRequest: ...,
    // string (optional)
    authorization: authorization_example,
  } satisfies CreateClaimForArtistArtistsArtistIdClaimsPostRequest;

  try {
    const data = await api.createClaimForArtistArtistsArtistIdClaimsPost(body);
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
| **claimCreateRequest** | [ClaimCreateRequest](ClaimCreateRequest.md) |  | |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

[**ClaimSchema**](ClaimSchema.md)

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


## escalateLegalClaimsClaimIdEscalateLegalPost

> any escalateLegalClaimsClaimIdEscalateLegalPost(claimId)

Escalate Legal

### Example

```ts
import {
  Configuration,
  ClaimsApi,
} from '@xr7/sdk';
import type { EscalateLegalClaimsClaimIdEscalateLegalPostRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new ClaimsApi();

  const body = {
    // string
    claimId: claimId_example,
  } satisfies EscalateLegalClaimsClaimIdEscalateLegalPostRequest;

  try {
    const data = await api.escalateLegalClaimsClaimIdEscalateLegalPost(body);
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
| **claimId** | `string` |  | [Defaults to `undefined`] |

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


## exportEvidencePacketClaimsClaimIdEvidenceExportGet

> any exportEvidencePacketClaimsClaimIdEvidenceExportGet(claimId, format, refresh)

Export Evidence Packet

### Example

```ts
import {
  Configuration,
  ClaimsApi,
} from '@xr7/sdk';
import type { ExportEvidencePacketClaimsClaimIdEvidenceExportGetRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new ClaimsApi();

  const body = {
    // string
    claimId: claimId_example,
    // string (optional)
    format: format_example,
    // boolean (optional)
    refresh: true,
  } satisfies ExportEvidencePacketClaimsClaimIdEvidenceExportGetRequest;

  try {
    const data = await api.exportEvidencePacketClaimsClaimIdEvidenceExportGet(body);
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
| **claimId** | `string` |  | [Defaults to `undefined`] |
| **format** | `string` |  | [Optional] [Defaults to `&#39;zip&#39;`] |
| **refresh** | `boolean` |  | [Optional] [Defaults to `false`] |

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


## exportEvidencePacketExpertModeClaimsClaimIdEvidenceExportPost

> any exportEvidencePacketExpertModeClaimsClaimIdEvidenceExportPost(claimId, mode)

Export Evidence Packet Expert Mode

Export evidence with optional expert witness mode for arbitration/litigation workflows.

### Example

```ts
import {
  Configuration,
  ClaimsApi,
} from '@xr7/sdk';
import type { ExportEvidencePacketExpertModeClaimsClaimIdEvidenceExportPostRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new ClaimsApi();

  const body = {
    // string
    claimId: claimId_example,
    // string (optional)
    mode: mode_example,
  } satisfies ExportEvidencePacketExpertModeClaimsClaimIdEvidenceExportPostRequest;

  try {
    const data = await api.exportEvidencePacketExpertModeClaimsClaimIdEvidenceExportPost(body);
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
| **claimId** | `string` |  | [Defaults to `undefined`] |
| **mode** | `string` |  | [Optional] [Defaults to `&#39;standard&#39;`] |

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


## generateAttorneyEvidenceFileApiClaimsClaimIdAttorneyEvidencePost

> any generateAttorneyEvidenceFileApiClaimsClaimIdAttorneyEvidencePost(claimId, attorneyEvidenceRequest)

Generate Attorney Evidence File

### Example

```ts
import {
  Configuration,
  ClaimsApi,
} from '@xr7/sdk';
import type { GenerateAttorneyEvidenceFileApiClaimsClaimIdAttorneyEvidencePostRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new ClaimsApi();

  const body = {
    // string
    claimId: claimId_example,
    // AttorneyEvidenceRequest
    attorneyEvidenceRequest: ...,
  } satisfies GenerateAttorneyEvidenceFileApiClaimsClaimIdAttorneyEvidencePostRequest;

  try {
    const data = await api.generateAttorneyEvidenceFileApiClaimsClaimIdAttorneyEvidencePost(body);
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
| **claimId** | `string` |  | [Defaults to `undefined`] |
| **attorneyEvidenceRequest** | [AttorneyEvidenceRequest](AttorneyEvidenceRequest.md) |  | |

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


## generateAttorneyEvidenceFileClaimsClaimIdAttorneyEvidencePost

> any generateAttorneyEvidenceFileClaimsClaimIdAttorneyEvidencePost(claimId, attorneyEvidenceRequest)

Generate Attorney Evidence File

### Example

```ts
import {
  Configuration,
  ClaimsApi,
} from '@xr7/sdk';
import type { GenerateAttorneyEvidenceFileClaimsClaimIdAttorneyEvidencePostRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new ClaimsApi();

  const body = {
    // string
    claimId: claimId_example,
    // AttorneyEvidenceRequest
    attorneyEvidenceRequest: ...,
  } satisfies GenerateAttorneyEvidenceFileClaimsClaimIdAttorneyEvidencePostRequest;

  try {
    const data = await api.generateAttorneyEvidenceFileClaimsClaimIdAttorneyEvidencePost(body);
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
| **claimId** | `string` |  | [Defaults to `undefined`] |
| **attorneyEvidenceRequest** | [AttorneyEvidenceRequest](AttorneyEvidenceRequest.md) |  | |

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


## generateEvidenceClaimsClaimIdEvidencePost

> any generateEvidenceClaimsClaimIdEvidencePost(claimId)

Generate Evidence

### Example

```ts
import {
  Configuration,
  ClaimsApi,
} from '@xr7/sdk';
import type { GenerateEvidenceClaimsClaimIdEvidencePostRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new ClaimsApi();

  const body = {
    // string
    claimId: claimId_example,
  } satisfies GenerateEvidenceClaimsClaimIdEvidencePostRequest;

  try {
    const data = await api.generateEvidenceClaimsClaimIdEvidencePost(body);
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
| **claimId** | `string` |  | [Defaults to `undefined`] |

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


## getClaimClaimsClaimIdGet

> ClaimSchema getClaimClaimsClaimIdGet(claimId)

Get Claim

### Example

```ts
import {
  Configuration,
  ClaimsApi,
} from '@xr7/sdk';
import type { GetClaimClaimsClaimIdGetRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new ClaimsApi();

  const body = {
    // string
    claimId: claimId_example,
  } satisfies GetClaimClaimsClaimIdGetRequest;

  try {
    const data = await api.getClaimClaimsClaimIdGet(body);
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
| **claimId** | `string` |  | [Defaults to `undefined`] |

### Return type

[**ClaimSchema**](ClaimSchema.md)

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


## getEvidenceClaimsClaimIdEvidenceGet

> any getEvidenceClaimsClaimIdEvidenceGet(claimId, authorization)

Get Evidence

### Example

```ts
import {
  Configuration,
  ClaimsApi,
} from '@xr7/sdk';
import type { GetEvidenceClaimsClaimIdEvidenceGetRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new ClaimsApi();

  const body = {
    // string
    claimId: claimId_example,
    // string (optional)
    authorization: authorization_example,
  } satisfies GetEvidenceClaimsClaimIdEvidenceGetRequest;

  try {
    const data = await api.getEvidenceClaimsClaimIdEvidenceGet(body);
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
| **claimId** | `string` |  | [Defaults to `undefined`] |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |

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


## listClaimsArtistsArtistIdClaimsGet

> any listClaimsArtistsArtistIdClaimsGet(artistId)

List Claims

### Example

```ts
import {
  Configuration,
  ClaimsApi,
} from '@xr7/sdk';
import type { ListClaimsArtistsArtistIdClaimsGetRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new ClaimsApi();

  const body = {
    // string
    artistId: artistId_example,
  } satisfies ListClaimsArtistsArtistIdClaimsGetRequest;

  try {
    const data = await api.listClaimsArtistsArtistIdClaimsGet(body);
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


## reconcileClaimClaimsClaimIdReconcilePost

> ClaimSchema reconcileClaimClaimsClaimIdReconcilePost(claimId, reconcileRequest)

Reconcile Claim

### Example

```ts
import {
  Configuration,
  ClaimsApi,
} from '@xr7/sdk';
import type { ReconcileClaimClaimsClaimIdReconcilePostRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new ClaimsApi();

  const body = {
    // string
    claimId: claimId_example,
    // ReconcileRequest
    reconcileRequest: ...,
  } satisfies ReconcileClaimClaimsClaimIdReconcilePostRequest;

  try {
    const data = await api.reconcileClaimClaimsClaimIdReconcilePost(body);
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
| **claimId** | `string` |  | [Defaults to `undefined`] |
| **reconcileRequest** | [ReconcileRequest](ReconcileRequest.md) |  | |

### Return type

[**ClaimSchema**](ClaimSchema.md)

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


## verifyEvidencePacketClaimsClaimIdEvidenceVerifyGet

> any verifyEvidencePacketClaimsClaimIdEvidenceVerifyGet(claimId, expectedPriorPacketHash)

Verify Evidence Packet

### Example

```ts
import {
  Configuration,
  ClaimsApi,
} from '@xr7/sdk';
import type { VerifyEvidencePacketClaimsClaimIdEvidenceVerifyGetRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new ClaimsApi();

  const body = {
    // string
    claimId: claimId_example,
    // string (optional)
    expectedPriorPacketHash: expectedPriorPacketHash_example,
  } satisfies VerifyEvidencePacketClaimsClaimIdEvidenceVerifyGetRequest;

  try {
    const data = await api.verifyEvidencePacketClaimsClaimIdEvidenceVerifyGet(body);
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
| **claimId** | `string` |  | [Defaults to `undefined`] |
| **expectedPriorPacketHash** | `string` |  | [Optional] [Defaults to `undefined`] |

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

