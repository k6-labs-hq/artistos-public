# Xr7ForensicsApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**getGapReportArtistsArtistIdXr7ReconciliationGapsGet**](Xr7ForensicsApi.md#getgapreportartistsartistidxr7reconciliationgapsget) | **GET** /artists/{artist_id}/xr7/reconciliation/gaps | Get Gap Report |
| [**queueApiIngestionArtistsArtistIdXr7QueueApiIngestionPost**](Xr7ForensicsApi.md#queueapiingestionartistsartistidxr7queueapiingestionpost) | **POST** /artists/{artist_id}/xr7/queue/api-ingestion | Queue Api Ingestion |
| [**queueBlackBoxArtistsArtistIdXr7QueueBlackBoxDetectionPost**](Xr7ForensicsApi.md#queueblackboxartistsartistidxr7queueblackboxdetectionpost) | **POST** /artists/{artist_id}/xr7/queue/black-box-detection | Queue Black Box |
| [**queueFileIngestionArtistsArtistIdXr7QueueFileIngestionPost**](Xr7ForensicsApi.md#queuefileingestionartistsartistidxr7queuefileingestionpost) | **POST** /artists/{artist_id}/xr7/queue/file-ingestion | Queue File Ingestion |
| [**queueFingerprintingArtistsArtistIdXr7QueueFingerprintingPost**](Xr7ForensicsApi.md#queuefingerprintingartistsartistidxr7queuefingerprintingpost) | **POST** /artists/{artist_id}/xr7/queue/fingerprinting | Queue Fingerprinting |
| [**queueReconciliationArtistsArtistIdXr7QueueReconciliationPost**](Xr7ForensicsApi.md#queuereconciliationartistsartistidxr7queuereconciliationpost) | **POST** /artists/{artist_id}/xr7/queue/reconciliation | Queue Reconciliation |
| [**runApiIngestionArtistsArtistIdXr7PipelinesApiIngestionPost**](Xr7ForensicsApi.md#runapiingestionartistsartistidxr7pipelinesapiingestionpost) | **POST** /artists/{artist_id}/xr7/pipelines/api-ingestion | Run Api Ingestion |
| [**runBlackBoxArtistsArtistIdXr7PipelinesBlackBoxDetectionPost**](Xr7ForensicsApi.md#runblackboxartistsartistidxr7pipelinesblackboxdetectionpost) | **POST** /artists/{artist_id}/xr7/pipelines/black-box-detection | Run Black Box |
| [**runFileIngestionArtistsArtistIdXr7PipelinesFileIngestionPost**](Xr7ForensicsApi.md#runfileingestionartistsartistidxr7pipelinesfileingestionpost) | **POST** /artists/{artist_id}/xr7/pipelines/file-ingestion | Run File Ingestion |
| [**runFingerprintingArtistsArtistIdXr7PipelinesFingerprintingPost**](Xr7ForensicsApi.md#runfingerprintingartistsartistidxr7pipelinesfingerprintingpost) | **POST** /artists/{artist_id}/xr7/pipelines/fingerprinting | Run Fingerprinting |
| [**runReconciliationArtistsArtistIdXr7PipelinesReconciliationPost**](Xr7ForensicsApi.md#runreconciliationartistsartistidxr7pipelinesreconciliationpost) | **POST** /artists/{artist_id}/xr7/pipelines/reconciliation | Run Reconciliation |
| [**upsertXr7CredentialsArtistsArtistIdXr7CredentialsPost**](Xr7ForensicsApi.md#upsertxr7credentialsartistsartistidxr7credentialspost) | **POST** /artists/{artist_id}/xr7/credentials | Upsert Xr7 Credentials |



## getGapReportArtistsArtistIdXr7ReconciliationGapsGet

> any getGapReportArtistsArtistIdXr7ReconciliationGapsGet(artistId, tenantId)

Get Gap Report

### Example

```ts
import {
  Configuration,
  Xr7ForensicsApi,
} from '@xr7/sdk';
import type { GetGapReportArtistsArtistIdXr7ReconciliationGapsGetRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new Xr7ForensicsApi();

  const body = {
    // string
    artistId: artistId_example,
    // string (optional)
    tenantId: tenantId_example,
  } satisfies GetGapReportArtistsArtistIdXr7ReconciliationGapsGetRequest;

  try {
    const data = await api.getGapReportArtistsArtistIdXr7ReconciliationGapsGet(body);
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


## queueApiIngestionArtistsArtistIdXr7QueueApiIngestionPost

> any queueApiIngestionArtistsArtistIdXr7QueueApiIngestionPost(artistId, aPIIngestionRequest)

Queue Api Ingestion

### Example

```ts
import {
  Configuration,
  Xr7ForensicsApi,
} from '@xr7/sdk';
import type { QueueApiIngestionArtistsArtistIdXr7QueueApiIngestionPostRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new Xr7ForensicsApi();

  const body = {
    // string
    artistId: artistId_example,
    // APIIngestionRequest
    aPIIngestionRequest: ...,
  } satisfies QueueApiIngestionArtistsArtistIdXr7QueueApiIngestionPostRequest;

  try {
    const data = await api.queueApiIngestionArtistsArtistIdXr7QueueApiIngestionPost(body);
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
| **aPIIngestionRequest** | [APIIngestionRequest](APIIngestionRequest.md) |  | |

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


## queueBlackBoxArtistsArtistIdXr7QueueBlackBoxDetectionPost

> any queueBlackBoxArtistsArtistIdXr7QueueBlackBoxDetectionPost(artistId, blackBoxRequest)

Queue Black Box

### Example

```ts
import {
  Configuration,
  Xr7ForensicsApi,
} from '@xr7/sdk';
import type { QueueBlackBoxArtistsArtistIdXr7QueueBlackBoxDetectionPostRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new Xr7ForensicsApi();

  const body = {
    // string
    artistId: artistId_example,
    // BlackBoxRequest
    blackBoxRequest: ...,
  } satisfies QueueBlackBoxArtistsArtistIdXr7QueueBlackBoxDetectionPostRequest;

  try {
    const data = await api.queueBlackBoxArtistsArtistIdXr7QueueBlackBoxDetectionPost(body);
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
| **blackBoxRequest** | [BlackBoxRequest](BlackBoxRequest.md) |  | |

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


## queueFileIngestionArtistsArtistIdXr7QueueFileIngestionPost

> any queueFileIngestionArtistsArtistIdXr7QueueFileIngestionPost(artistId, sourceSystem, file, tenantId, queueBackend)

Queue File Ingestion

### Example

```ts
import {
  Configuration,
  Xr7ForensicsApi,
} from '@xr7/sdk';
import type { QueueFileIngestionArtistsArtistIdXr7QueueFileIngestionPostRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new Xr7ForensicsApi();

  const body = {
    // string
    artistId: artistId_example,
    // string
    sourceSystem: sourceSystem_example,
    // string
    file: file_example,
    // string (optional)
    tenantId: tenantId_example,
    // string (optional)
    queueBackend: queueBackend_example,
  } satisfies QueueFileIngestionArtistsArtistIdXr7QueueFileIngestionPostRequest;

  try {
    const data = await api.queueFileIngestionArtistsArtistIdXr7QueueFileIngestionPost(body);
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
| **sourceSystem** | `string` |  | [Defaults to `undefined`] |
| **file** | `string` |  | [Defaults to `undefined`] |
| **tenantId** | `string` |  | [Optional] [Defaults to `&#39;default&#39;`] |
| **queueBackend** | `string` |  | [Optional] [Defaults to `&#39;celery&#39;`] |

### Return type

**any**

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: `multipart/form-data`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## queueFingerprintingArtistsArtistIdXr7QueueFingerprintingPost

> any queueFingerprintingArtistsArtistIdXr7QueueFingerprintingPost(artistId, fingerprintingRequest)

Queue Fingerprinting

### Example

```ts
import {
  Configuration,
  Xr7ForensicsApi,
} from '@xr7/sdk';
import type { QueueFingerprintingArtistsArtistIdXr7QueueFingerprintingPostRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new Xr7ForensicsApi();

  const body = {
    // string
    artistId: artistId_example,
    // FingerprintingRequest
    fingerprintingRequest: ...,
  } satisfies QueueFingerprintingArtistsArtistIdXr7QueueFingerprintingPostRequest;

  try {
    const data = await api.queueFingerprintingArtistsArtistIdXr7QueueFingerprintingPost(body);
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
| **fingerprintingRequest** | [FingerprintingRequest](FingerprintingRequest.md) |  | |

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


## queueReconciliationArtistsArtistIdXr7QueueReconciliationPost

> any queueReconciliationArtistsArtistIdXr7QueueReconciliationPost(artistId, reconciliationRequest)

Queue Reconciliation

### Example

```ts
import {
  Configuration,
  Xr7ForensicsApi,
} from '@xr7/sdk';
import type { QueueReconciliationArtistsArtistIdXr7QueueReconciliationPostRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new Xr7ForensicsApi();

  const body = {
    // string
    artistId: artistId_example,
    // ReconciliationRequest
    reconciliationRequest: ...,
  } satisfies QueueReconciliationArtistsArtistIdXr7QueueReconciliationPostRequest;

  try {
    const data = await api.queueReconciliationArtistsArtistIdXr7QueueReconciliationPost(body);
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
| **reconciliationRequest** | [ReconciliationRequest](ReconciliationRequest.md) |  | |

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


## runApiIngestionArtistsArtistIdXr7PipelinesApiIngestionPost

> any runApiIngestionArtistsArtistIdXr7PipelinesApiIngestionPost(artistId, aPIIngestionRequest)

Run Api Ingestion

### Example

```ts
import {
  Configuration,
  Xr7ForensicsApi,
} from '@xr7/sdk';
import type { RunApiIngestionArtistsArtistIdXr7PipelinesApiIngestionPostRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new Xr7ForensicsApi();

  const body = {
    // string
    artistId: artistId_example,
    // APIIngestionRequest
    aPIIngestionRequest: ...,
  } satisfies RunApiIngestionArtistsArtistIdXr7PipelinesApiIngestionPostRequest;

  try {
    const data = await api.runApiIngestionArtistsArtistIdXr7PipelinesApiIngestionPost(body);
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
| **aPIIngestionRequest** | [APIIngestionRequest](APIIngestionRequest.md) |  | |

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


## runBlackBoxArtistsArtistIdXr7PipelinesBlackBoxDetectionPost

> any runBlackBoxArtistsArtistIdXr7PipelinesBlackBoxDetectionPost(artistId, blackBoxRequest)

Run Black Box

### Example

```ts
import {
  Configuration,
  Xr7ForensicsApi,
} from '@xr7/sdk';
import type { RunBlackBoxArtistsArtistIdXr7PipelinesBlackBoxDetectionPostRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new Xr7ForensicsApi();

  const body = {
    // string
    artistId: artistId_example,
    // BlackBoxRequest
    blackBoxRequest: ...,
  } satisfies RunBlackBoxArtistsArtistIdXr7PipelinesBlackBoxDetectionPostRequest;

  try {
    const data = await api.runBlackBoxArtistsArtistIdXr7PipelinesBlackBoxDetectionPost(body);
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
| **blackBoxRequest** | [BlackBoxRequest](BlackBoxRequest.md) |  | |

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


## runFileIngestionArtistsArtistIdXr7PipelinesFileIngestionPost

> any runFileIngestionArtistsArtistIdXr7PipelinesFileIngestionPost(artistId, sourceSystem, file, tenantId)

Run File Ingestion

### Example

```ts
import {
  Configuration,
  Xr7ForensicsApi,
} from '@xr7/sdk';
import type { RunFileIngestionArtistsArtistIdXr7PipelinesFileIngestionPostRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new Xr7ForensicsApi();

  const body = {
    // string
    artistId: artistId_example,
    // string
    sourceSystem: sourceSystem_example,
    // string
    file: file_example,
    // string (optional)
    tenantId: tenantId_example,
  } satisfies RunFileIngestionArtistsArtistIdXr7PipelinesFileIngestionPostRequest;

  try {
    const data = await api.runFileIngestionArtistsArtistIdXr7PipelinesFileIngestionPost(body);
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
| **sourceSystem** | `string` |  | [Defaults to `undefined`] |
| **file** | `string` |  | [Defaults to `undefined`] |
| **tenantId** | `string` |  | [Optional] [Defaults to `&#39;default&#39;`] |

### Return type

**any**

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: `multipart/form-data`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## runFingerprintingArtistsArtistIdXr7PipelinesFingerprintingPost

> any runFingerprintingArtistsArtistIdXr7PipelinesFingerprintingPost(artistId, fingerprintingRequest)

Run Fingerprinting

### Example

```ts
import {
  Configuration,
  Xr7ForensicsApi,
} from '@xr7/sdk';
import type { RunFingerprintingArtistsArtistIdXr7PipelinesFingerprintingPostRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new Xr7ForensicsApi();

  const body = {
    // string
    artistId: artistId_example,
    // FingerprintingRequest
    fingerprintingRequest: ...,
  } satisfies RunFingerprintingArtistsArtistIdXr7PipelinesFingerprintingPostRequest;

  try {
    const data = await api.runFingerprintingArtistsArtistIdXr7PipelinesFingerprintingPost(body);
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
| **fingerprintingRequest** | [FingerprintingRequest](FingerprintingRequest.md) |  | |

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


## runReconciliationArtistsArtistIdXr7PipelinesReconciliationPost

> any runReconciliationArtistsArtistIdXr7PipelinesReconciliationPost(artistId, reconciliationRequest)

Run Reconciliation

### Example

```ts
import {
  Configuration,
  Xr7ForensicsApi,
} from '@xr7/sdk';
import type { RunReconciliationArtistsArtistIdXr7PipelinesReconciliationPostRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new Xr7ForensicsApi();

  const body = {
    // string
    artistId: artistId_example,
    // ReconciliationRequest
    reconciliationRequest: ...,
  } satisfies RunReconciliationArtistsArtistIdXr7PipelinesReconciliationPostRequest;

  try {
    const data = await api.runReconciliationArtistsArtistIdXr7PipelinesReconciliationPost(body);
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
| **reconciliationRequest** | [ReconciliationRequest](ReconciliationRequest.md) |  | |

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


## upsertXr7CredentialsArtistsArtistIdXr7CredentialsPost

> any upsertXr7CredentialsArtistsArtistIdXr7CredentialsPost(artistId, xR7ConnectorCredentialUpsert)

Upsert Xr7 Credentials

### Example

```ts
import {
  Configuration,
  Xr7ForensicsApi,
} from '@xr7/sdk';
import type { UpsertXr7CredentialsArtistsArtistIdXr7CredentialsPostRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new Xr7ForensicsApi();

  const body = {
    // string
    artistId: artistId_example,
    // XR7ConnectorCredentialUpsert
    xR7ConnectorCredentialUpsert: ...,
  } satisfies UpsertXr7CredentialsArtistsArtistIdXr7CredentialsPostRequest;

  try {
    const data = await api.upsertXr7CredentialsArtistsArtistIdXr7CredentialsPost(body);
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
| **xR7ConnectorCredentialUpsert** | [XR7ConnectorCredentialUpsert](XR7ConnectorCredentialUpsert.md) |  | |

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

