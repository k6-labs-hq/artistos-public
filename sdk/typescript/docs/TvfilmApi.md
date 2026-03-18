# TvfilmApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**runTvfilmAgentsTvfilmArtistsArtistIdAgentsRunPost**](TvfilmApi.md#runtvfilmagentstvfilmartistsartistidagentsrunpost) | **POST** /tvfilm/artists/{artist_id}/agents/run | Run Tvfilm Agents |
| [**tvfilmAnomalyRuleCatalogTvfilmCatalogsAnomalyRulesGet**](TvfilmApi.md#tvfilmanomalyrulecatalogtvfilmcatalogsanomalyrulesget) | **GET** /tvfilm/catalogs/anomaly-rules | Tvfilm Anomaly Rule Catalog |
| [**tvfilmBulkDraftClaimsTvfilmArtistsArtistIdClaimsBulkDraftPost**](TvfilmApi.md#tvfilmbulkdraftclaimstvfilmartistsartistidclaimsbulkdraftpost) | **POST** /tvfilm/artists/{artist_id}/claims/bulk-draft | Tvfilm Bulk Draft Claims |
| [**tvfilmBulkExportClaimsTvfilmArtistsArtistIdClaimsBulkExportPost**](TvfilmApi.md#tvfilmbulkexportclaimstvfilmartistsartistidclaimsbulkexportpost) | **POST** /tvfilm/artists/{artist_id}/claims/bulk-export | Tvfilm Bulk Export Claims |
| [**tvfilmCalculationAuditTvfilmArtistsArtistIdCalculationAuditGet**](TvfilmApi.md#tvfilmcalculationaudittvfilmartistsartistidcalculationauditget) | **GET** /tvfilm/artists/{artist_id}/calculation-audit | Tvfilm Calculation Audit |
| [**tvfilmDashboardTvfilmArtistsArtistIdDashboardGet**](TvfilmApi.md#tvfilmdashboardtvfilmartistsartistiddashboardget) | **GET** /tvfilm/artists/{artist_id}/dashboard | Tvfilm Dashboard |
| [**tvfilmDraftClaimsTvfilmArtistsArtistIdClaimsDraftPost**](TvfilmApi.md#tvfilmdraftclaimstvfilmartistsartistidclaimsdraftpost) | **POST** /tvfilm/artists/{artist_id}/claims/draft | Tvfilm Draft Claims |
| [**tvfilmEnterprisePortfolioAnalyzeTvfilmEnterprisePortfolioAnalyzePost**](TvfilmApi.md#tvfilmenterpriseportfolioanalyzetvfilmenterpriseportfolioanalyzepost) | **POST** /tvfilm/enterprise/portfolio/analyze | Tvfilm Enterprise Portfolio Analyze |
| [**tvfilmEnterprisePortfolioJobTvfilmEnterprisePortfolioJobIdGet**](TvfilmApi.md#tvfilmenterpriseportfoliojobtvfilmenterpriseportfoliojobidget) | **GET** /tvfilm/enterprise/portfolio/{job_id} | Tvfilm Enterprise Portfolio Job |
| [**tvfilmEvidenceTemplatesTvfilmCatalogsEvidenceTemplatesGet**](TvfilmApi.md#tvfilmevidencetemplatestvfilmcatalogsevidencetemplatesget) | **GET** /tvfilm/catalogs/evidence-templates | Tvfilm Evidence Templates |
| [**tvfilmExportEvidencePacketTvfilmClaimsClaimIdEvidenceExportGet**](TvfilmApi.md#tvfilmexportevidencepackettvfilmclaimsclaimidevidenceexportget) | **GET** /tvfilm/claims/{claim_id}/evidence/export | Tvfilm Export Evidence Packet |
| [**tvfilmForecastTvfilmArtistsArtistIdForecastPost**](TvfilmApi.md#tvfilmforecasttvfilmartistsartistidforecastpost) | **POST** /tvfilm/artists/{artist_id}/forecast | Tvfilm Forecast |
| [**tvfilmIngestionCommitTvfilmArtistsArtistIdIngestionCommitPost**](TvfilmApi.md#tvfilmingestioncommittvfilmartistsartistidingestioncommitpost) | **POST** /tvfilm/artists/{artist_id}/ingestion/commit | Tvfilm Ingestion Commit |
| [**tvfilmIngestionFormatsTvfilmIngestionFormatsGet**](TvfilmApi.md#tvfilmingestionformatstvfilmingestionformatsget) | **GET** /tvfilm/ingestion/formats | Tvfilm Ingestion Formats |
| [**tvfilmIngestionPreviewTvfilmIngestionPreviewPost**](TvfilmApi.md#tvfilmingestionpreviewtvfilmingestionpreviewpost) | **POST** /tvfilm/ingestion/preview | Tvfilm Ingestion Preview |
| [**tvfilmRoleOptionsTvfilmRolesOptionsGet**](TvfilmApi.md#tvfilmroleoptionstvfilmrolesoptionsget) | **GET** /tvfilm/roles/options | Tvfilm Role Options |
| [**tvfilmScanAnomaliesTvfilmArtistsArtistIdAnomaliesScanPost**](TvfilmApi.md#tvfilmscananomaliestvfilmartistsartistidanomaliesscanpost) | **POST** /tvfilm/artists/{artist_id}/anomalies/scan | Tvfilm Scan Anomalies |
| [**tvfilmTrustExplainTvfilmTrustExplainPost**](TvfilmApi.md#tvfilmtrustexplaintvfilmtrustexplainpost) | **POST** /tvfilm/trust/explain | Tvfilm Trust Explain |



## runTvfilmAgentsTvfilmArtistsArtistIdAgentsRunPost

> any runTvfilmAgentsTvfilmArtistsArtistIdAgentsRunPost(artistId)

Run Tvfilm Agents

### Example

```ts
import {
  Configuration,
  TvfilmApi,
} from '@xr7/sdk';
import type { RunTvfilmAgentsTvfilmArtistsArtistIdAgentsRunPostRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new TvfilmApi();

  const body = {
    // string
    artistId: artistId_example,
  } satisfies RunTvfilmAgentsTvfilmArtistsArtistIdAgentsRunPostRequest;

  try {
    const data = await api.runTvfilmAgentsTvfilmArtistsArtistIdAgentsRunPost(body);
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


## tvfilmAnomalyRuleCatalogTvfilmCatalogsAnomalyRulesGet

> any tvfilmAnomalyRuleCatalogTvfilmCatalogsAnomalyRulesGet()

Tvfilm Anomaly Rule Catalog

### Example

```ts
import {
  Configuration,
  TvfilmApi,
} from '@xr7/sdk';
import type { TvfilmAnomalyRuleCatalogTvfilmCatalogsAnomalyRulesGetRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new TvfilmApi();

  try {
    const data = await api.tvfilmAnomalyRuleCatalogTvfilmCatalogsAnomalyRulesGet();
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


## tvfilmBulkDraftClaimsTvfilmArtistsArtistIdClaimsBulkDraftPost

> any tvfilmBulkDraftClaimsTvfilmArtistsArtistIdClaimsBulkDraftPost(artistId, tVFilmBulkClaimDraftRequest)

Tvfilm Bulk Draft Claims

### Example

```ts
import {
  Configuration,
  TvfilmApi,
} from '@xr7/sdk';
import type { TvfilmBulkDraftClaimsTvfilmArtistsArtistIdClaimsBulkDraftPostRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new TvfilmApi();

  const body = {
    // string
    artistId: artistId_example,
    // TVFilmBulkClaimDraftRequest
    tVFilmBulkClaimDraftRequest: ...,
  } satisfies TvfilmBulkDraftClaimsTvfilmArtistsArtistIdClaimsBulkDraftPostRequest;

  try {
    const data = await api.tvfilmBulkDraftClaimsTvfilmArtistsArtistIdClaimsBulkDraftPost(body);
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
| **tVFilmBulkClaimDraftRequest** | [TVFilmBulkClaimDraftRequest](TVFilmBulkClaimDraftRequest.md) |  | |

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


## tvfilmBulkExportClaimsTvfilmArtistsArtistIdClaimsBulkExportPost

> any tvfilmBulkExportClaimsTvfilmArtistsArtistIdClaimsBulkExportPost(artistId, tVFilmBulkExportRequest)

Tvfilm Bulk Export Claims

### Example

```ts
import {
  Configuration,
  TvfilmApi,
} from '@xr7/sdk';
import type { TvfilmBulkExportClaimsTvfilmArtistsArtistIdClaimsBulkExportPostRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new TvfilmApi();

  const body = {
    // string
    artistId: artistId_example,
    // TVFilmBulkExportRequest
    tVFilmBulkExportRequest: ...,
  } satisfies TvfilmBulkExportClaimsTvfilmArtistsArtistIdClaimsBulkExportPostRequest;

  try {
    const data = await api.tvfilmBulkExportClaimsTvfilmArtistsArtistIdClaimsBulkExportPost(body);
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
| **tVFilmBulkExportRequest** | [TVFilmBulkExportRequest](TVFilmBulkExportRequest.md) |  | |

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


## tvfilmCalculationAuditTvfilmArtistsArtistIdCalculationAuditGet

> any tvfilmCalculationAuditTvfilmArtistsArtistIdCalculationAuditGet(artistId)

Tvfilm Calculation Audit

### Example

```ts
import {
  Configuration,
  TvfilmApi,
} from '@xr7/sdk';
import type { TvfilmCalculationAuditTvfilmArtistsArtistIdCalculationAuditGetRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new TvfilmApi();

  const body = {
    // string
    artistId: artistId_example,
  } satisfies TvfilmCalculationAuditTvfilmArtistsArtistIdCalculationAuditGetRequest;

  try {
    const data = await api.tvfilmCalculationAuditTvfilmArtistsArtistIdCalculationAuditGet(body);
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


## tvfilmDashboardTvfilmArtistsArtistIdDashboardGet

> any tvfilmDashboardTvfilmArtistsArtistIdDashboardGet(artistId)

Tvfilm Dashboard

### Example

```ts
import {
  Configuration,
  TvfilmApi,
} from '@xr7/sdk';
import type { TvfilmDashboardTvfilmArtistsArtistIdDashboardGetRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new TvfilmApi();

  const body = {
    // string
    artistId: artistId_example,
  } satisfies TvfilmDashboardTvfilmArtistsArtistIdDashboardGetRequest;

  try {
    const data = await api.tvfilmDashboardTvfilmArtistsArtistIdDashboardGet(body);
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


## tvfilmDraftClaimsTvfilmArtistsArtistIdClaimsDraftPost

> any tvfilmDraftClaimsTvfilmArtistsArtistIdClaimsDraftPost(artistId, tVFilmClaimDraftRequest)

Tvfilm Draft Claims

### Example

```ts
import {
  Configuration,
  TvfilmApi,
} from '@xr7/sdk';
import type { TvfilmDraftClaimsTvfilmArtistsArtistIdClaimsDraftPostRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new TvfilmApi();

  const body = {
    // string
    artistId: artistId_example,
    // TVFilmClaimDraftRequest
    tVFilmClaimDraftRequest: ...,
  } satisfies TvfilmDraftClaimsTvfilmArtistsArtistIdClaimsDraftPostRequest;

  try {
    const data = await api.tvfilmDraftClaimsTvfilmArtistsArtistIdClaimsDraftPost(body);
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
| **tVFilmClaimDraftRequest** | [TVFilmClaimDraftRequest](TVFilmClaimDraftRequest.md) |  | |

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


## tvfilmEnterprisePortfolioAnalyzeTvfilmEnterprisePortfolioAnalyzePost

> any tvfilmEnterprisePortfolioAnalyzeTvfilmEnterprisePortfolioAnalyzePost(tVFilmPortfolioAnalysisRequest)

Tvfilm Enterprise Portfolio Analyze

### Example

```ts
import {
  Configuration,
  TvfilmApi,
} from '@xr7/sdk';
import type { TvfilmEnterprisePortfolioAnalyzeTvfilmEnterprisePortfolioAnalyzePostRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new TvfilmApi();

  const body = {
    // TVFilmPortfolioAnalysisRequest
    tVFilmPortfolioAnalysisRequest: ...,
  } satisfies TvfilmEnterprisePortfolioAnalyzeTvfilmEnterprisePortfolioAnalyzePostRequest;

  try {
    const data = await api.tvfilmEnterprisePortfolioAnalyzeTvfilmEnterprisePortfolioAnalyzePost(body);
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
| **tVFilmPortfolioAnalysisRequest** | [TVFilmPortfolioAnalysisRequest](TVFilmPortfolioAnalysisRequest.md) |  | |

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


## tvfilmEnterprisePortfolioJobTvfilmEnterprisePortfolioJobIdGet

> any tvfilmEnterprisePortfolioJobTvfilmEnterprisePortfolioJobIdGet(jobId)

Tvfilm Enterprise Portfolio Job

### Example

```ts
import {
  Configuration,
  TvfilmApi,
} from '@xr7/sdk';
import type { TvfilmEnterprisePortfolioJobTvfilmEnterprisePortfolioJobIdGetRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new TvfilmApi();

  const body = {
    // string
    jobId: jobId_example,
  } satisfies TvfilmEnterprisePortfolioJobTvfilmEnterprisePortfolioJobIdGetRequest;

  try {
    const data = await api.tvfilmEnterprisePortfolioJobTvfilmEnterprisePortfolioJobIdGet(body);
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
| **jobId** | `string` |  | [Defaults to `undefined`] |

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


## tvfilmEvidenceTemplatesTvfilmCatalogsEvidenceTemplatesGet

> any tvfilmEvidenceTemplatesTvfilmCatalogsEvidenceTemplatesGet()

Tvfilm Evidence Templates

### Example

```ts
import {
  Configuration,
  TvfilmApi,
} from '@xr7/sdk';
import type { TvfilmEvidenceTemplatesTvfilmCatalogsEvidenceTemplatesGetRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new TvfilmApi();

  try {
    const data = await api.tvfilmEvidenceTemplatesTvfilmCatalogsEvidenceTemplatesGet();
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


## tvfilmExportEvidencePacketTvfilmClaimsClaimIdEvidenceExportGet

> any tvfilmExportEvidencePacketTvfilmClaimsClaimIdEvidenceExportGet(claimId, format)

Tvfilm Export Evidence Packet

### Example

```ts
import {
  Configuration,
  TvfilmApi,
} from '@xr7/sdk';
import type { TvfilmExportEvidencePacketTvfilmClaimsClaimIdEvidenceExportGetRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new TvfilmApi();

  const body = {
    // string
    claimId: claimId_example,
    // string (optional)
    format: format_example,
  } satisfies TvfilmExportEvidencePacketTvfilmClaimsClaimIdEvidenceExportGetRequest;

  try {
    const data = await api.tvfilmExportEvidencePacketTvfilmClaimsClaimIdEvidenceExportGet(body);
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


## tvfilmForecastTvfilmArtistsArtistIdForecastPost

> any tvfilmForecastTvfilmArtistsArtistIdForecastPost(artistId, tVFilmForecastRequest)

Tvfilm Forecast

### Example

```ts
import {
  Configuration,
  TvfilmApi,
} from '@xr7/sdk';
import type { TvfilmForecastTvfilmArtistsArtistIdForecastPostRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new TvfilmApi();

  const body = {
    // string
    artistId: artistId_example,
    // TVFilmForecastRequest
    tVFilmForecastRequest: ...,
  } satisfies TvfilmForecastTvfilmArtistsArtistIdForecastPostRequest;

  try {
    const data = await api.tvfilmForecastTvfilmArtistsArtistIdForecastPost(body);
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
| **tVFilmForecastRequest** | [TVFilmForecastRequest](TVFilmForecastRequest.md) |  | |

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


## tvfilmIngestionCommitTvfilmArtistsArtistIdIngestionCommitPost

> any tvfilmIngestionCommitTvfilmArtistsArtistIdIngestionCommitPost(artistId, file)

Tvfilm Ingestion Commit

### Example

```ts
import {
  Configuration,
  TvfilmApi,
} from '@xr7/sdk';
import type { TvfilmIngestionCommitTvfilmArtistsArtistIdIngestionCommitPostRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new TvfilmApi();

  const body = {
    // string
    artistId: artistId_example,
    // string
    file: file_example,
  } satisfies TvfilmIngestionCommitTvfilmArtistsArtistIdIngestionCommitPostRequest;

  try {
    const data = await api.tvfilmIngestionCommitTvfilmArtistsArtistIdIngestionCommitPost(body);
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


## tvfilmIngestionFormatsTvfilmIngestionFormatsGet

> any tvfilmIngestionFormatsTvfilmIngestionFormatsGet()

Tvfilm Ingestion Formats

### Example

```ts
import {
  Configuration,
  TvfilmApi,
} from '@xr7/sdk';
import type { TvfilmIngestionFormatsTvfilmIngestionFormatsGetRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new TvfilmApi();

  try {
    const data = await api.tvfilmIngestionFormatsTvfilmIngestionFormatsGet();
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


## tvfilmIngestionPreviewTvfilmIngestionPreviewPost

> any tvfilmIngestionPreviewTvfilmIngestionPreviewPost(file)

Tvfilm Ingestion Preview

### Example

```ts
import {
  Configuration,
  TvfilmApi,
} from '@xr7/sdk';
import type { TvfilmIngestionPreviewTvfilmIngestionPreviewPostRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new TvfilmApi();

  const body = {
    // string
    file: file_example,
  } satisfies TvfilmIngestionPreviewTvfilmIngestionPreviewPostRequest;

  try {
    const data = await api.tvfilmIngestionPreviewTvfilmIngestionPreviewPost(body);
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


## tvfilmRoleOptionsTvfilmRolesOptionsGet

> any tvfilmRoleOptionsTvfilmRolesOptionsGet()

Tvfilm Role Options

### Example

```ts
import {
  Configuration,
  TvfilmApi,
} from '@xr7/sdk';
import type { TvfilmRoleOptionsTvfilmRolesOptionsGetRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new TvfilmApi();

  try {
    const data = await api.tvfilmRoleOptionsTvfilmRolesOptionsGet();
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


## tvfilmScanAnomaliesTvfilmArtistsArtistIdAnomaliesScanPost

> any tvfilmScanAnomaliesTvfilmArtistsArtistIdAnomaliesScanPost(artistId)

Tvfilm Scan Anomalies

### Example

```ts
import {
  Configuration,
  TvfilmApi,
} from '@xr7/sdk';
import type { TvfilmScanAnomaliesTvfilmArtistsArtistIdAnomaliesScanPostRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new TvfilmApi();

  const body = {
    // string
    artistId: artistId_example,
  } satisfies TvfilmScanAnomaliesTvfilmArtistsArtistIdAnomaliesScanPostRequest;

  try {
    const data = await api.tvfilmScanAnomaliesTvfilmArtistsArtistIdAnomaliesScanPost(body);
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


## tvfilmTrustExplainTvfilmTrustExplainPost

> any tvfilmTrustExplainTvfilmTrustExplainPost(tVFilmTrustExplainRequest)

Tvfilm Trust Explain

### Example

```ts
import {
  Configuration,
  TvfilmApi,
} from '@xr7/sdk';
import type { TvfilmTrustExplainTvfilmTrustExplainPostRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new TvfilmApi();

  const body = {
    // TVFilmTrustExplainRequest
    tVFilmTrustExplainRequest: ...,
  } satisfies TvfilmTrustExplainTvfilmTrustExplainPostRequest;

  try {
    const data = await api.tvfilmTrustExplainTvfilmTrustExplainPost(body);
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
| **tVFilmTrustExplainRequest** | [TVFilmTrustExplainRequest](TVFilmTrustExplainRequest.md) |  | |

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

