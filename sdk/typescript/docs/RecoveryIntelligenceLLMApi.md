# RecoveryIntelligenceLLMApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**llmDemandLetterArtistsArtistIdLlmDemandLetterPost**](RecoveryIntelligenceLLMApi.md#llmdemandletterartistsartistidllmdemandletterpost) | **POST** /artists/{artist_id}/llm/demand-letter | Llm Demand Letter |
| [**llmNegotiationScriptArtistsArtistIdLlmNegotiationScriptPost**](RecoveryIntelligenceLLMApi.md#llmnegotiationscriptartistsartistidllmnegotiationscriptpost) | **POST** /artists/{artist_id}/llm/negotiation-script | Llm Negotiation Script |
| [**llmPersonalizedAdviceArtistsArtistIdLlmAdvicePost**](RecoveryIntelligenceLLMApi.md#llmpersonalizedadviceartistsartistidllmadvicepost) | **POST** /artists/{artist_id}/llm/advice | Llm Personalized Advice |



## llmDemandLetterArtistsArtistIdLlmDemandLetterPost

> DemandLetterResponse llmDemandLetterArtistsArtistIdLlmDemandLetterPost(artistId, demandLetterRequest, xActorEmail, xActorRole)

Llm Demand Letter

### Example

```ts
import {
  Configuration,
  RecoveryIntelligenceLLMApi,
} from '@xr7/sdk';
import type { LlmDemandLetterArtistsArtistIdLlmDemandLetterPostRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new RecoveryIntelligenceLLMApi();

  const body = {
    // string
    artistId: artistId_example,
    // DemandLetterRequest
    demandLetterRequest: ...,
    // string (optional)
    xActorEmail: xActorEmail_example,
    // string (optional)
    xActorRole: xActorRole_example,
  } satisfies LlmDemandLetterArtistsArtistIdLlmDemandLetterPostRequest;

  try {
    const data = await api.llmDemandLetterArtistsArtistIdLlmDemandLetterPost(body);
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
| **demandLetterRequest** | [DemandLetterRequest](DemandLetterRequest.md) |  | |
| **xActorEmail** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xActorRole** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

[**DemandLetterResponse**](DemandLetterResponse.md)

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


## llmNegotiationScriptArtistsArtistIdLlmNegotiationScriptPost

> NegotiationScriptResponse llmNegotiationScriptArtistsArtistIdLlmNegotiationScriptPost(artistId, negotiationScriptRequest, xActorEmail, xActorRole)

Llm Negotiation Script

### Example

```ts
import {
  Configuration,
  RecoveryIntelligenceLLMApi,
} from '@xr7/sdk';
import type { LlmNegotiationScriptArtistsArtistIdLlmNegotiationScriptPostRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new RecoveryIntelligenceLLMApi();

  const body = {
    // string
    artistId: artistId_example,
    // NegotiationScriptRequest
    negotiationScriptRequest: ...,
    // string (optional)
    xActorEmail: xActorEmail_example,
    // string (optional)
    xActorRole: xActorRole_example,
  } satisfies LlmNegotiationScriptArtistsArtistIdLlmNegotiationScriptPostRequest;

  try {
    const data = await api.llmNegotiationScriptArtistsArtistIdLlmNegotiationScriptPost(body);
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
| **negotiationScriptRequest** | [NegotiationScriptRequest](NegotiationScriptRequest.md) |  | |
| **xActorEmail** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xActorRole** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

[**NegotiationScriptResponse**](NegotiationScriptResponse.md)

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


## llmPersonalizedAdviceArtistsArtistIdLlmAdvicePost

> AdviceResponse llmPersonalizedAdviceArtistsArtistIdLlmAdvicePost(artistId, adviceRequest, xActorEmail, xActorRole)

Llm Personalized Advice

### Example

```ts
import {
  Configuration,
  RecoveryIntelligenceLLMApi,
} from '@xr7/sdk';
import type { LlmPersonalizedAdviceArtistsArtistIdLlmAdvicePostRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new RecoveryIntelligenceLLMApi();

  const body = {
    // string
    artistId: artistId_example,
    // AdviceRequest
    adviceRequest: ...,
    // string (optional)
    xActorEmail: xActorEmail_example,
    // string (optional)
    xActorRole: xActorRole_example,
  } satisfies LlmPersonalizedAdviceArtistsArtistIdLlmAdvicePostRequest;

  try {
    const data = await api.llmPersonalizedAdviceArtistsArtistIdLlmAdvicePost(body);
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
| **adviceRequest** | [AdviceRequest](AdviceRequest.md) |  | |
| **xActorEmail** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xActorRole** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

[**AdviceResponse**](AdviceResponse.md)

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

