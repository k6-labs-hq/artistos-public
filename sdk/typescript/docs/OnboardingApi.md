# OnboardingApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**applySplitRepairsArtistsArtistIdSplitsRepairPost**](OnboardingApi.md#applysplitrepairsartistsartistidsplitsrepairpost) | **POST** /artists/{artist_id}/splits/repair | Apply Split Repairs |
| [**buildCatalogWorkGraphArtistsArtistIdCatalogGraphBuildPost**](OnboardingApi.md#buildcatalogworkgraphartistsartistidcataloggraphbuildpost) | **POST** /artists/{artist_id}/catalog/graph/build | Build Catalog Work Graph |
| [**catalogMetadataHealthArtistsArtistIdCatalogMetadataHealthGet**](OnboardingApi.md#catalogmetadatahealthartistsartistidcatalogmetadatahealthget) | **GET** /artists/{artist_id}/catalog/metadata-health | Catalog Metadata Health |
| [**catalogRepairsArtistsArtistIdCatalogRepairsGet**](OnboardingApi.md#catalogrepairsartistsartistidcatalogrepairsget) | **GET** /artists/{artist_id}/catalog/repairs | Catalog Repairs |
| [**confirmCatalogItemArtistsArtistIdCatalogConfirmPost**](OnboardingApi.md#confirmcatalogitemartistsartistidcatalogconfirmpost) | **POST** /artists/{artist_id}/catalog/confirm | Confirm Catalog Item |
| [**createSyncJobArtistsArtistIdSyncJobsPost**](OnboardingApi.md#createsyncjobartistsartistidsyncjobspost) | **POST** /artists/{artist_id}/sync/jobs | Create Sync Job |
| [**generateAuditEvidencePacketClaimsClaimIdEvidenceGenerateAuditPost**](OnboardingApi.md#generateauditevidencepacketclaimsclaimidevidencegenerateauditpost) | **POST** /claims/{claim_id}/evidence/generate-audit | Generate Audit Evidence Packet |
| [**getPermissionsDashboardUiPermissionsUiGet**](OnboardingApi.md#getpermissionsdashboarduipermissionsuiget) | **GET** /permissions/ui | Get Permissions Dashboard Ui |
| [**getSyncJobArtistsArtistIdSyncJobsJobIdGet**](OnboardingApi.md#getsyncjobartistsartistidsyncjobsjobidget) | **GET** /artists/{artist_id}/sync/jobs/{job_id} | Get Sync Job |
| [**inferCatalogArtistsArtistIdCatalogInferPost**](OnboardingApi.md#infercatalogartistsartistidcataloginferpost) | **POST** /artists/{artist_id}/catalog/infer | Infer Catalog |
| [**listCatalogConfirmationsArtistsArtistIdCatalogConfirmGet**](OnboardingApi.md#listcatalogconfirmationsartistsartistidcatalogconfirmget) | **GET** /artists/{artist_id}/catalog/confirm | List Catalog Confirmations |
| [**listImmutableLedgerEntriesArtistsArtistIdLedgerImmutableGet**](OnboardingApi.md#listimmutableledgerentriesartistsartistidledgerimmutableget) | **GET** /artists/{artist_id}/ledger/immutable | List Immutable Ledger Entries |
| [**listParserPluginsArtistsArtistIdParsersPluginsGet**](OnboardingApi.md#listparserpluginsartistsartistidparserspluginsget) | **GET** /artists/{artist_id}/parsers/plugins | List Parser Plugins |
| [**listSyncJobsArtistsArtistIdSyncJobsGet**](OnboardingApi.md#listsyncjobsartistsartistidsyncjobsget) | **GET** /artists/{artist_id}/sync/jobs | List Sync Jobs |
| [**missingDataStatusArtistsArtistIdIngestionMissingDataGet**](OnboardingApi.md#missingdatastatusartistsartistidingestionmissingdataget) | **GET** /artists/{artist_id}/ingestion/missing-data | Missing Data Status |
| [**onboardingStatusArtistsArtistIdOnboardingStatusGet**](OnboardingApi.md#onboardingstatusartistsartistidonboardingstatusget) | **GET** /artists/{artist_id}/onboarding/status | Onboarding Status |
| [**parseStatementWithEngineArtistsArtistIdParsersParserTypePost**](OnboardingApi.md#parsestatementwithengineartistsartistidparsersparsertypepost) | **POST** /artists/{artist_id}/parsers/{parser_type} | Parse Statement With Engine |
| [**permissionsDashboardArtistsArtistIdConnectPermissionsDashboardGet**](OnboardingApi.md#permissionsdashboardartistsartistidconnectpermissionsdashboardget) | **GET** /artists/{artist_id}/connect/permissions-dashboard | Permissions Dashboard |
| [**previewFullWorkflowArtistsArtistIdWorkflowPreviewGet**](OnboardingApi.md#previewfullworkflowartistsartistidworkflowpreviewget) | **GET** /artists/{artist_id}/workflow/preview | Preview Full Workflow |
| [**requeueDueSyncJobsArtistsArtistIdSyncJobsRequeueDuePost**](OnboardingApi.md#requeueduesyncjobsartistsartistidsyncjobsrequeueduepost) | **POST** /artists/{artist_id}/sync/jobs/requeue-due | Requeue Due Sync Jobs |
| [**runDataFetcherArtistsArtistIdFetchersIntegrationPost**](OnboardingApi.md#rundatafetcherartistsartistidfetchersintegrationpost) | **POST** /artists/{artist_id}/fetchers/{integration} | Run Data Fetcher |
| [**runFullWorkflowArtistsArtistIdWorkflowRunPost**](OnboardingApi.md#runfullworkflowartistsartistidworkflowrunpost) | **POST** /artists/{artist_id}/workflow/run | Run Full Workflow |
| [**runRecoveryAutomationArtistsArtistIdRecoveryAutomatePost**](OnboardingApi.md#runrecoveryautomationartistsartistidrecoveryautomatepost) | **POST** /artists/{artist_id}/recovery/automate | Run Recovery Automation |
| [**runSyncJobNowArtistsArtistIdSyncJobsJobIdRunPost**](OnboardingApi.md#runsyncjobnowartistsartistidsyncjobsjobidrunpost) | **POST** /artists/{artist_id}/sync/jobs/{job_id}/run | Run Sync Job Now |
| [**uploadAnyStatementArtistsArtistIdIngestionUploadAnyPost**](OnboardingApi.md#uploadanystatementartistsartistidingestionuploadanypost) | **POST** /artists/{artist_id}/ingestion/upload-any | Upload Any Statement |
| [**upsertParserPluginArtistsArtistIdParsersPluginsPut**](OnboardingApi.md#upsertparserpluginartistsartistidparserspluginsput) | **PUT** /artists/{artist_id}/parsers/plugins | Upsert Parser Plugin |
| [**varianceScanArtistsArtistIdVarianceScanPost**](OnboardingApi.md#variancescanartistsartistidvariancescanpost) | **POST** /artists/{artist_id}/variance/scan | Variance Scan |



## applySplitRepairsArtistsArtistIdSplitsRepairPost

> any applySplitRepairsArtistsArtistIdSplitsRepairPost(artistId, splitRepairRequest)

Apply Split Repairs

### Example

```ts
import {
  Configuration,
  OnboardingApi,
} from '@xr7/sdk';
import type { ApplySplitRepairsArtistsArtistIdSplitsRepairPostRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new OnboardingApi();

  const body = {
    // string
    artistId: artistId_example,
    // SplitRepairRequest
    splitRepairRequest: ...,
  } satisfies ApplySplitRepairsArtistsArtistIdSplitsRepairPostRequest;

  try {
    const data = await api.applySplitRepairsArtistsArtistIdSplitsRepairPost(body);
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
| **splitRepairRequest** | [SplitRepairRequest](SplitRepairRequest.md) |  | |

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


## buildCatalogWorkGraphArtistsArtistIdCatalogGraphBuildPost

> any buildCatalogWorkGraphArtistsArtistIdCatalogGraphBuildPost(artistId)

Build Catalog Work Graph

### Example

```ts
import {
  Configuration,
  OnboardingApi,
} from '@xr7/sdk';
import type { BuildCatalogWorkGraphArtistsArtistIdCatalogGraphBuildPostRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new OnboardingApi();

  const body = {
    // string
    artistId: artistId_example,
  } satisfies BuildCatalogWorkGraphArtistsArtistIdCatalogGraphBuildPostRequest;

  try {
    const data = await api.buildCatalogWorkGraphArtistsArtistIdCatalogGraphBuildPost(body);
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


## catalogMetadataHealthArtistsArtistIdCatalogMetadataHealthGet

> any catalogMetadataHealthArtistsArtistIdCatalogMetadataHealthGet(artistId)

Catalog Metadata Health

### Example

```ts
import {
  Configuration,
  OnboardingApi,
} from '@xr7/sdk';
import type { CatalogMetadataHealthArtistsArtistIdCatalogMetadataHealthGetRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new OnboardingApi();

  const body = {
    // string
    artistId: artistId_example,
  } satisfies CatalogMetadataHealthArtistsArtistIdCatalogMetadataHealthGetRequest;

  try {
    const data = await api.catalogMetadataHealthArtistsArtistIdCatalogMetadataHealthGet(body);
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


## catalogRepairsArtistsArtistIdCatalogRepairsGet

> any catalogRepairsArtistsArtistIdCatalogRepairsGet(artistId)

Catalog Repairs

### Example

```ts
import {
  Configuration,
  OnboardingApi,
} from '@xr7/sdk';
import type { CatalogRepairsArtistsArtistIdCatalogRepairsGetRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new OnboardingApi();

  const body = {
    // string
    artistId: artistId_example,
  } satisfies CatalogRepairsArtistsArtistIdCatalogRepairsGetRequest;

  try {
    const data = await api.catalogRepairsArtistsArtistIdCatalogRepairsGet(body);
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


## confirmCatalogItemArtistsArtistIdCatalogConfirmPost

> CatalogConfirmationSchema confirmCatalogItemArtistsArtistIdCatalogConfirmPost(artistId, xR7ApiRoutersOnboardingCatalogConfirmRequest)

Confirm Catalog Item

### Example

```ts
import {
  Configuration,
  OnboardingApi,
} from '@xr7/sdk';
import type { ConfirmCatalogItemArtistsArtistIdCatalogConfirmPostRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new OnboardingApi();

  const body = {
    // string
    artistId: artistId_example,
    // XR7ApiRoutersOnboardingCatalogConfirmRequest
    xR7ApiRoutersOnboardingCatalogConfirmRequest: ...,
  } satisfies ConfirmCatalogItemArtistsArtistIdCatalogConfirmPostRequest;

  try {
    const data = await api.confirmCatalogItemArtistsArtistIdCatalogConfirmPost(body);
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
| **xR7ApiRoutersOnboardingCatalogConfirmRequest** | [XR7ApiRoutersOnboardingCatalogConfirmRequest](XR7ApiRoutersOnboardingCatalogConfirmRequest.md) |  | |

### Return type

[**CatalogConfirmationSchema**](CatalogConfirmationSchema.md)

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


## createSyncJobArtistsArtistIdSyncJobsPost

> SyncJobSchema createSyncJobArtistsArtistIdSyncJobsPost(artistId, syncJobCreateRequest)

Create Sync Job

### Example

```ts
import {
  Configuration,
  OnboardingApi,
} from '@xr7/sdk';
import type { CreateSyncJobArtistsArtistIdSyncJobsPostRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new OnboardingApi();

  const body = {
    // string
    artistId: artistId_example,
    // SyncJobCreateRequest
    syncJobCreateRequest: ...,
  } satisfies CreateSyncJobArtistsArtistIdSyncJobsPostRequest;

  try {
    const data = await api.createSyncJobArtistsArtistIdSyncJobsPost(body);
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
| **syncJobCreateRequest** | [SyncJobCreateRequest](SyncJobCreateRequest.md) |  | |

### Return type

[**SyncJobSchema**](SyncJobSchema.md)

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


## generateAuditEvidencePacketClaimsClaimIdEvidenceGenerateAuditPost

> any generateAuditEvidencePacketClaimsClaimIdEvidenceGenerateAuditPost(claimId)

Generate Audit Evidence Packet

### Example

```ts
import {
  Configuration,
  OnboardingApi,
} from '@xr7/sdk';
import type { GenerateAuditEvidencePacketClaimsClaimIdEvidenceGenerateAuditPostRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new OnboardingApi();

  const body = {
    // string
    claimId: claimId_example,
  } satisfies GenerateAuditEvidencePacketClaimsClaimIdEvidenceGenerateAuditPostRequest;

  try {
    const data = await api.generateAuditEvidencePacketClaimsClaimIdEvidenceGenerateAuditPost(body);
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


## getPermissionsDashboardUiPermissionsUiGet

> any getPermissionsDashboardUiPermissionsUiGet()

Get Permissions Dashboard Ui

### Example

```ts
import {
  Configuration,
  OnboardingApi,
} from '@xr7/sdk';
import type { GetPermissionsDashboardUiPermissionsUiGetRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new OnboardingApi();

  try {
    const data = await api.getPermissionsDashboardUiPermissionsUiGet();
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

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## getSyncJobArtistsArtistIdSyncJobsJobIdGet

> SyncJobSchema getSyncJobArtistsArtistIdSyncJobsJobIdGet(artistId, jobId)

Get Sync Job

### Example

```ts
import {
  Configuration,
  OnboardingApi,
} from '@xr7/sdk';
import type { GetSyncJobArtistsArtistIdSyncJobsJobIdGetRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new OnboardingApi();

  const body = {
    // string
    artistId: artistId_example,
    // string
    jobId: jobId_example,
  } satisfies GetSyncJobArtistsArtistIdSyncJobsJobIdGetRequest;

  try {
    const data = await api.getSyncJobArtistsArtistIdSyncJobsJobIdGet(body);
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
| **jobId** | `string` |  | [Defaults to `undefined`] |

### Return type

[**SyncJobSchema**](SyncJobSchema.md)

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


## inferCatalogArtistsArtistIdCatalogInferPost

> any inferCatalogArtistsArtistIdCatalogInferPost(artistId)

Infer Catalog

### Example

```ts
import {
  Configuration,
  OnboardingApi,
} from '@xr7/sdk';
import type { InferCatalogArtistsArtistIdCatalogInferPostRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new OnboardingApi();

  const body = {
    // string
    artistId: artistId_example,
  } satisfies InferCatalogArtistsArtistIdCatalogInferPostRequest;

  try {
    const data = await api.inferCatalogArtistsArtistIdCatalogInferPost(body);
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


## listCatalogConfirmationsArtistsArtistIdCatalogConfirmGet

> Array&lt;CatalogConfirmationSchema&gt; listCatalogConfirmationsArtistsArtistIdCatalogConfirmGet(artistId)

List Catalog Confirmations

### Example

```ts
import {
  Configuration,
  OnboardingApi,
} from '@xr7/sdk';
import type { ListCatalogConfirmationsArtistsArtistIdCatalogConfirmGetRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new OnboardingApi();

  const body = {
    // string
    artistId: artistId_example,
  } satisfies ListCatalogConfirmationsArtistsArtistIdCatalogConfirmGetRequest;

  try {
    const data = await api.listCatalogConfirmationsArtistsArtistIdCatalogConfirmGet(body);
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

[**Array&lt;CatalogConfirmationSchema&gt;**](CatalogConfirmationSchema.md)

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


## listImmutableLedgerEntriesArtistsArtistIdLedgerImmutableGet

> Array&lt;ImmutableLedgerEntrySchema&gt; listImmutableLedgerEntriesArtistsArtistIdLedgerImmutableGet(artistId)

List Immutable Ledger Entries

### Example

```ts
import {
  Configuration,
  OnboardingApi,
} from '@xr7/sdk';
import type { ListImmutableLedgerEntriesArtistsArtistIdLedgerImmutableGetRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new OnboardingApi();

  const body = {
    // string
    artistId: artistId_example,
  } satisfies ListImmutableLedgerEntriesArtistsArtistIdLedgerImmutableGetRequest;

  try {
    const data = await api.listImmutableLedgerEntriesArtistsArtistIdLedgerImmutableGet(body);
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

[**Array&lt;ImmutableLedgerEntrySchema&gt;**](ImmutableLedgerEntrySchema.md)

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


## listParserPluginsArtistsArtistIdParsersPluginsGet

> Array&lt;ParserPluginSchema&gt; listParserPluginsArtistsArtistIdParsersPluginsGet(artistId)

List Parser Plugins

### Example

```ts
import {
  Configuration,
  OnboardingApi,
} from '@xr7/sdk';
import type { ListParserPluginsArtistsArtistIdParsersPluginsGetRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new OnboardingApi();

  const body = {
    // string
    artistId: artistId_example,
  } satisfies ListParserPluginsArtistsArtistIdParsersPluginsGetRequest;

  try {
    const data = await api.listParserPluginsArtistsArtistIdParsersPluginsGet(body);
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

[**Array&lt;ParserPluginSchema&gt;**](ParserPluginSchema.md)

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


## listSyncJobsArtistsArtistIdSyncJobsGet

> Array&lt;SyncJobSchema&gt; listSyncJobsArtistsArtistIdSyncJobsGet(artistId)

List Sync Jobs

### Example

```ts
import {
  Configuration,
  OnboardingApi,
} from '@xr7/sdk';
import type { ListSyncJobsArtistsArtistIdSyncJobsGetRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new OnboardingApi();

  const body = {
    // string
    artistId: artistId_example,
  } satisfies ListSyncJobsArtistsArtistIdSyncJobsGetRequest;

  try {
    const data = await api.listSyncJobsArtistsArtistIdSyncJobsGet(body);
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

[**Array&lt;SyncJobSchema&gt;**](SyncJobSchema.md)

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


## missingDataStatusArtistsArtistIdIngestionMissingDataGet

> any missingDataStatusArtistsArtistIdIngestionMissingDataGet(artistId)

Missing Data Status

### Example

```ts
import {
  Configuration,
  OnboardingApi,
} from '@xr7/sdk';
import type { MissingDataStatusArtistsArtistIdIngestionMissingDataGetRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new OnboardingApi();

  const body = {
    // string
    artistId: artistId_example,
  } satisfies MissingDataStatusArtistsArtistIdIngestionMissingDataGetRequest;

  try {
    const data = await api.missingDataStatusArtistsArtistIdIngestionMissingDataGet(body);
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


## onboardingStatusArtistsArtistIdOnboardingStatusGet

> any onboardingStatusArtistsArtistIdOnboardingStatusGet(artistId)

Onboarding Status

### Example

```ts
import {
  Configuration,
  OnboardingApi,
} from '@xr7/sdk';
import type { OnboardingStatusArtistsArtistIdOnboardingStatusGetRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new OnboardingApi();

  const body = {
    // string
    artistId: artistId_example,
  } satisfies OnboardingStatusArtistsArtistIdOnboardingStatusGetRequest;

  try {
    const data = await api.onboardingStatusArtistsArtistIdOnboardingStatusGet(body);
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


## parseStatementWithEngineArtistsArtistIdParsersParserTypePost

> any parseStatementWithEngineArtistsArtistIdParsersParserTypePost(artistId, parserType, file)

Parse Statement With Engine

### Example

```ts
import {
  Configuration,
  OnboardingApi,
} from '@xr7/sdk';
import type { ParseStatementWithEngineArtistsArtistIdParsersParserTypePostRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new OnboardingApi();

  const body = {
    // string
    artistId: artistId_example,
    // string
    parserType: parserType_example,
    // string
    file: file_example,
  } satisfies ParseStatementWithEngineArtistsArtistIdParsersParserTypePostRequest;

  try {
    const data = await api.parseStatementWithEngineArtistsArtistIdParsersParserTypePost(body);
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
| **parserType** | `string` |  | [Defaults to `undefined`] |
| **file** | `string` |  | [Defaults to `undefined`] |

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


## permissionsDashboardArtistsArtistIdConnectPermissionsDashboardGet

> any permissionsDashboardArtistsArtistIdConnectPermissionsDashboardGet(artistId)

Permissions Dashboard

### Example

```ts
import {
  Configuration,
  OnboardingApi,
} from '@xr7/sdk';
import type { PermissionsDashboardArtistsArtistIdConnectPermissionsDashboardGetRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new OnboardingApi();

  const body = {
    // string
    artistId: artistId_example,
  } satisfies PermissionsDashboardArtistsArtistIdConnectPermissionsDashboardGetRequest;

  try {
    const data = await api.permissionsDashboardArtistsArtistIdConnectPermissionsDashboardGet(body);
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


## previewFullWorkflowArtistsArtistIdWorkflowPreviewGet

> any previewFullWorkflowArtistsArtistIdWorkflowPreviewGet(artistId)

Preview Full Workflow

### Example

```ts
import {
  Configuration,
  OnboardingApi,
} from '@xr7/sdk';
import type { PreviewFullWorkflowArtistsArtistIdWorkflowPreviewGetRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new OnboardingApi();

  const body = {
    // string
    artistId: artistId_example,
  } satisfies PreviewFullWorkflowArtistsArtistIdWorkflowPreviewGetRequest;

  try {
    const data = await api.previewFullWorkflowArtistsArtistIdWorkflowPreviewGet(body);
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


## requeueDueSyncJobsArtistsArtistIdSyncJobsRequeueDuePost

> any requeueDueSyncJobsArtistsArtistIdSyncJobsRequeueDuePost(artistId)

Requeue Due Sync Jobs

### Example

```ts
import {
  Configuration,
  OnboardingApi,
} from '@xr7/sdk';
import type { RequeueDueSyncJobsArtistsArtistIdSyncJobsRequeueDuePostRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new OnboardingApi();

  const body = {
    // string
    artistId: artistId_example,
  } satisfies RequeueDueSyncJobsArtistsArtistIdSyncJobsRequeueDuePostRequest;

  try {
    const data = await api.requeueDueSyncJobsArtistsArtistIdSyncJobsRequeueDuePost(body);
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


## runDataFetcherArtistsArtistIdFetchersIntegrationPost

> any runDataFetcherArtistsArtistIdFetchersIntegrationPost(artistId, integration)

Run Data Fetcher

### Example

```ts
import {
  Configuration,
  OnboardingApi,
} from '@xr7/sdk';
import type { RunDataFetcherArtistsArtistIdFetchersIntegrationPostRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new OnboardingApi();

  const body = {
    // string
    artistId: artistId_example,
    // string
    integration: integration_example,
  } satisfies RunDataFetcherArtistsArtistIdFetchersIntegrationPostRequest;

  try {
    const data = await api.runDataFetcherArtistsArtistIdFetchersIntegrationPost(body);
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
| **integration** | `string` |  | [Defaults to `undefined`] |

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


## runFullWorkflowArtistsArtistIdWorkflowRunPost

> any runFullWorkflowArtistsArtistIdWorkflowRunPost(artistId, workflowRunRequest)

Run Full Workflow

### Example

```ts
import {
  Configuration,
  OnboardingApi,
} from '@xr7/sdk';
import type { RunFullWorkflowArtistsArtistIdWorkflowRunPostRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new OnboardingApi();

  const body = {
    // string
    artistId: artistId_example,
    // WorkflowRunRequest
    workflowRunRequest: ...,
  } satisfies RunFullWorkflowArtistsArtistIdWorkflowRunPostRequest;

  try {
    const data = await api.runFullWorkflowArtistsArtistIdWorkflowRunPost(body);
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
| **workflowRunRequest** | [WorkflowRunRequest](WorkflowRunRequest.md) |  | |

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


## runRecoveryAutomationArtistsArtistIdRecoveryAutomatePost

> any runRecoveryAutomationArtistsArtistIdRecoveryAutomatePost(artistId)

Run Recovery Automation

### Example

```ts
import {
  Configuration,
  OnboardingApi,
} from '@xr7/sdk';
import type { RunRecoveryAutomationArtistsArtistIdRecoveryAutomatePostRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new OnboardingApi();

  const body = {
    // string
    artistId: artistId_example,
  } satisfies RunRecoveryAutomationArtistsArtistIdRecoveryAutomatePostRequest;

  try {
    const data = await api.runRecoveryAutomationArtistsArtistIdRecoveryAutomatePost(body);
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


## runSyncJobNowArtistsArtistIdSyncJobsJobIdRunPost

> SyncJobSchema runSyncJobNowArtistsArtistIdSyncJobsJobIdRunPost(artistId, jobId, asyncRun)

Run Sync Job Now

### Example

```ts
import {
  Configuration,
  OnboardingApi,
} from '@xr7/sdk';
import type { RunSyncJobNowArtistsArtistIdSyncJobsJobIdRunPostRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new OnboardingApi();

  const body = {
    // string
    artistId: artistId_example,
    // string
    jobId: jobId_example,
    // boolean (optional)
    asyncRun: true,
  } satisfies RunSyncJobNowArtistsArtistIdSyncJobsJobIdRunPostRequest;

  try {
    const data = await api.runSyncJobNowArtistsArtistIdSyncJobsJobIdRunPost(body);
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
| **jobId** | `string` |  | [Defaults to `undefined`] |
| **asyncRun** | `boolean` |  | [Optional] [Defaults to `false`] |

### Return type

[**SyncJobSchema**](SyncJobSchema.md)

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


## uploadAnyStatementArtistsArtistIdIngestionUploadAnyPost

> any uploadAnyStatementArtistsArtistIdIngestionUploadAnyPost(artistId, files, strictValidation)

Upload Any Statement

### Example

```ts
import {
  Configuration,
  OnboardingApi,
} from '@xr7/sdk';
import type { UploadAnyStatementArtistsArtistIdIngestionUploadAnyPostRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new OnboardingApi();

  const body = {
    // string
    artistId: artistId_example,
    // Array<string>
    files: ...,
    // boolean (optional)
    strictValidation: true,
  } satisfies UploadAnyStatementArtistsArtistIdIngestionUploadAnyPostRequest;

  try {
    const data = await api.uploadAnyStatementArtistsArtistIdIngestionUploadAnyPost(body);
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
| **files** | `Array<string>` |  | |
| **strictValidation** | `boolean` |  | [Optional] [Defaults to `true`] |

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


## upsertParserPluginArtistsArtistIdParsersPluginsPut

> ParserPluginSchema upsertParserPluginArtistsArtistIdParsersPluginsPut(artistId, parserPluginUpsertRequest)

Upsert Parser Plugin

### Example

```ts
import {
  Configuration,
  OnboardingApi,
} from '@xr7/sdk';
import type { UpsertParserPluginArtistsArtistIdParsersPluginsPutRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new OnboardingApi();

  const body = {
    // string
    artistId: artistId_example,
    // ParserPluginUpsertRequest
    parserPluginUpsertRequest: ...,
  } satisfies UpsertParserPluginArtistsArtistIdParsersPluginsPutRequest;

  try {
    const data = await api.upsertParserPluginArtistsArtistIdParsersPluginsPut(body);
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
| **parserPluginUpsertRequest** | [ParserPluginUpsertRequest](ParserPluginUpsertRequest.md) |  | |

### Return type

[**ParserPluginSchema**](ParserPluginSchema.md)

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


## varianceScanArtistsArtistIdVarianceScanPost

> any varianceScanArtistsArtistIdVarianceScanPost(artistId, varianceScanRequest)

Variance Scan

### Example

```ts
import {
  Configuration,
  OnboardingApi,
} from '@xr7/sdk';
import type { VarianceScanArtistsArtistIdVarianceScanPostRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new OnboardingApi();

  const body = {
    // string
    artistId: artistId_example,
    // VarianceScanRequest
    varianceScanRequest: ...,
  } satisfies VarianceScanArtistsArtistIdVarianceScanPostRequest;

  try {
    const data = await api.varianceScanArtistsArtistIdVarianceScanPost(body);
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
| **varianceScanRequest** | [VarianceScanRequest](VarianceScanRequest.md) |  | |

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

