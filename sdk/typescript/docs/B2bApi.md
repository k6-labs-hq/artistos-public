# B2bApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**b2bDashboardB2bOrgOrgIdDashboardGet**](B2bApi.md#b2bdashboardb2borgorgiddashboardget) | **GET** /b2b/org/{org_id}/dashboard | B2B Dashboard |
| [**bulkOnboardB2bOrgOrgIdArtistsBulkOnboardPost**](B2bApi.md#bulkonboardb2borgorgidartistsbulkonboardpost) | **POST** /b2b/org/{org_id}/artists/bulk-onboard | Bulk Onboard |
| [**managementAnomaliesDrilldownManagementOrgIdAnomaliesGet**](B2bApi.md#managementanomaliesdrilldownmanagementorgidanomaliesget) | **GET** /management/{org_id}/anomalies | Management Anomalies Drilldown |
| [**managementArtistDrilldownManagementOrgIdArtistsArtistIdGet**](B2bApi.md#managementartistdrilldownmanagementorgidartistsartistidget) | **GET** /management/{org_id}/artists/{artist_id} | Management Artist Drilldown |
| [**managementCatalogDrilldownManagementOrgIdCatalogGet**](B2bApi.md#managementcatalogdrilldownmanagementorgidcatalogget) | **GET** /management/{org_id}/catalog | Management Catalog Drilldown |
| [**managementClaimsDrilldownManagementOrgIdClaimsGet**](B2bApi.md#managementclaimsdrilldownmanagementorgidclaimsget) | **GET** /management/{org_id}/claims | Management Claims Drilldown |
| [**managementDashboardManagementOrgIdDashboardGet**](B2bApi.md#managementdashboardmanagementorgiddashboardget) | **GET** /management/{org_id}/dashboard | Management Dashboard |
| [**managementDashboardV2ManagementOrgIdDashboardV2Get**](B2bApi.md#managementdashboardv2managementorgiddashboardv2get) | **GET** /management/{org_id}/dashboard/v2 | Management Dashboard V2 |
| [**managementForecastManagementOrgIdForecastGet**](B2bApi.md#managementforecastmanagementorgidforecastget) | **GET** /management/{org_id}/forecast | Management Forecast |
| [**orgPortfolioOrgOrgIdPortfolioGet**](B2bApi.md#orgportfolioorgorgidportfolioget) | **GET** /org/{org_id}/portfolio | Org Portfolio |
| [**xr7OperatorDashboardXr7OperatorDashboardGet**](B2bApi.md#xr7operatordashboardxr7operatordashboardget) | **GET** /xr7/operator/dashboard | Xr7 Operator Dashboard |



## b2bDashboardB2bOrgOrgIdDashboardGet

> any b2bDashboardB2bOrgOrgIdDashboardGet(orgId, xOrgKey, xOrgRole, xOrgActor)

B2B Dashboard

### Example

```ts
import {
  Configuration,
  B2bApi,
} from '@xr7/sdk';
import type { B2bDashboardB2bOrgOrgIdDashboardGetRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new B2bApi();

  const body = {
    // string
    orgId: orgId_example,
    // string (optional)
    xOrgKey: xOrgKey_example,
    // string (optional)
    xOrgRole: xOrgRole_example,
    // string (optional)
    xOrgActor: xOrgActor_example,
  } satisfies B2bDashboardB2bOrgOrgIdDashboardGetRequest;

  try {
    const data = await api.b2bDashboardB2bOrgOrgIdDashboardGet(body);
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
| **orgId** | `string` |  | [Defaults to `undefined`] |
| **xOrgKey** | `string` |  | [Optional] [Defaults to `&#39;&#39;`] |
| **xOrgRole** | `string` |  | [Optional] [Defaults to `&#39;&#39;`] |
| **xOrgActor** | `string` |  | [Optional] [Defaults to `&#39;&#39;`] |

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


## bulkOnboardB2bOrgOrgIdArtistsBulkOnboardPost

> any bulkOnboardB2bOrgOrgIdArtistsBulkOnboardPost(orgId, bulkOnboardRequest, xOrgKey, xOrgRole, xOrgActor)

Bulk Onboard

### Example

```ts
import {
  Configuration,
  B2bApi,
} from '@xr7/sdk';
import type { BulkOnboardB2bOrgOrgIdArtistsBulkOnboardPostRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new B2bApi();

  const body = {
    // string
    orgId: orgId_example,
    // BulkOnboardRequest
    bulkOnboardRequest: ...,
    // string (optional)
    xOrgKey: xOrgKey_example,
    // string (optional)
    xOrgRole: xOrgRole_example,
    // string (optional)
    xOrgActor: xOrgActor_example,
  } satisfies BulkOnboardB2bOrgOrgIdArtistsBulkOnboardPostRequest;

  try {
    const data = await api.bulkOnboardB2bOrgOrgIdArtistsBulkOnboardPost(body);
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
| **orgId** | `string` |  | [Defaults to `undefined`] |
| **bulkOnboardRequest** | [BulkOnboardRequest](BulkOnboardRequest.md) |  | |
| **xOrgKey** | `string` |  | [Optional] [Defaults to `&#39;&#39;`] |
| **xOrgRole** | `string` |  | [Optional] [Defaults to `&#39;&#39;`] |
| **xOrgActor** | `string` |  | [Optional] [Defaults to `&#39;&#39;`] |

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


## managementAnomaliesDrilldownManagementOrgIdAnomaliesGet

> any managementAnomaliesDrilldownManagementOrgIdAnomaliesGet(orgId, severity, status, category, limit, xOrgKey, xOrgRole, xOrgActor)

Management Anomalies Drilldown

### Example

```ts
import {
  Configuration,
  B2bApi,
} from '@xr7/sdk';
import type { ManagementAnomaliesDrilldownManagementOrgIdAnomaliesGetRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new B2bApi();

  const body = {
    // string
    orgId: orgId_example,
    // string (optional)
    severity: severity_example,
    // string (optional)
    status: status_example,
    // string (optional)
    category: category_example,
    // number (optional)
    limit: 56,
    // string (optional)
    xOrgKey: xOrgKey_example,
    // string (optional)
    xOrgRole: xOrgRole_example,
    // string (optional)
    xOrgActor: xOrgActor_example,
  } satisfies ManagementAnomaliesDrilldownManagementOrgIdAnomaliesGetRequest;

  try {
    const data = await api.managementAnomaliesDrilldownManagementOrgIdAnomaliesGet(body);
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
| **orgId** | `string` |  | [Defaults to `undefined`] |
| **severity** | `string` |  | [Optional] [Defaults to `undefined`] |
| **status** | `string` |  | [Optional] [Defaults to `undefined`] |
| **category** | `string` |  | [Optional] [Defaults to `undefined`] |
| **limit** | `number` |  | [Optional] [Defaults to `100`] |
| **xOrgKey** | `string` |  | [Optional] [Defaults to `&#39;&#39;`] |
| **xOrgRole** | `string` |  | [Optional] [Defaults to `&#39;&#39;`] |
| **xOrgActor** | `string` |  | [Optional] [Defaults to `&#39;&#39;`] |

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


## managementArtistDrilldownManagementOrgIdArtistsArtistIdGet

> any managementArtistDrilldownManagementOrgIdArtistsArtistIdGet(orgId, artistId, xOrgKey, xOrgRole, xOrgActor)

Management Artist Drilldown

### Example

```ts
import {
  Configuration,
  B2bApi,
} from '@xr7/sdk';
import type { ManagementArtistDrilldownManagementOrgIdArtistsArtistIdGetRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new B2bApi();

  const body = {
    // string
    orgId: orgId_example,
    // string
    artistId: artistId_example,
    // string (optional)
    xOrgKey: xOrgKey_example,
    // string (optional)
    xOrgRole: xOrgRole_example,
    // string (optional)
    xOrgActor: xOrgActor_example,
  } satisfies ManagementArtistDrilldownManagementOrgIdArtistsArtistIdGetRequest;

  try {
    const data = await api.managementArtistDrilldownManagementOrgIdArtistsArtistIdGet(body);
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
| **orgId** | `string` |  | [Defaults to `undefined`] |
| **artistId** | `string` |  | [Defaults to `undefined`] |
| **xOrgKey** | `string` |  | [Optional] [Defaults to `&#39;&#39;`] |
| **xOrgRole** | `string` |  | [Optional] [Defaults to `&#39;&#39;`] |
| **xOrgActor** | `string` |  | [Optional] [Defaults to `&#39;&#39;`] |

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


## managementCatalogDrilldownManagementOrgIdCatalogGet

> any managementCatalogDrilldownManagementOrgIdCatalogGet(orgId, xOrgKey, xOrgRole, xOrgActor)

Management Catalog Drilldown

### Example

```ts
import {
  Configuration,
  B2bApi,
} from '@xr7/sdk';
import type { ManagementCatalogDrilldownManagementOrgIdCatalogGetRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new B2bApi();

  const body = {
    // string
    orgId: orgId_example,
    // string (optional)
    xOrgKey: xOrgKey_example,
    // string (optional)
    xOrgRole: xOrgRole_example,
    // string (optional)
    xOrgActor: xOrgActor_example,
  } satisfies ManagementCatalogDrilldownManagementOrgIdCatalogGetRequest;

  try {
    const data = await api.managementCatalogDrilldownManagementOrgIdCatalogGet(body);
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
| **orgId** | `string` |  | [Defaults to `undefined`] |
| **xOrgKey** | `string` |  | [Optional] [Defaults to `&#39;&#39;`] |
| **xOrgRole** | `string` |  | [Optional] [Defaults to `&#39;&#39;`] |
| **xOrgActor** | `string` |  | [Optional] [Defaults to `&#39;&#39;`] |

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


## managementClaimsDrilldownManagementOrgIdClaimsGet

> any managementClaimsDrilldownManagementOrgIdClaimsGet(orgId, status, solWindowDays, limit, xOrgKey, xOrgRole, xOrgActor)

Management Claims Drilldown

### Example

```ts
import {
  Configuration,
  B2bApi,
} from '@xr7/sdk';
import type { ManagementClaimsDrilldownManagementOrgIdClaimsGetRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new B2bApi();

  const body = {
    // string
    orgId: orgId_example,
    // string (optional)
    status: status_example,
    // number (optional)
    solWindowDays: 56,
    // number (optional)
    limit: 56,
    // string (optional)
    xOrgKey: xOrgKey_example,
    // string (optional)
    xOrgRole: xOrgRole_example,
    // string (optional)
    xOrgActor: xOrgActor_example,
  } satisfies ManagementClaimsDrilldownManagementOrgIdClaimsGetRequest;

  try {
    const data = await api.managementClaimsDrilldownManagementOrgIdClaimsGet(body);
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
| **orgId** | `string` |  | [Defaults to `undefined`] |
| **status** | `string` |  | [Optional] [Defaults to `undefined`] |
| **solWindowDays** | `number` |  | [Optional] [Defaults to `30`] |
| **limit** | `number` |  | [Optional] [Defaults to `100`] |
| **xOrgKey** | `string` |  | [Optional] [Defaults to `&#39;&#39;`] |
| **xOrgRole** | `string` |  | [Optional] [Defaults to `&#39;&#39;`] |
| **xOrgActor** | `string` |  | [Optional] [Defaults to `&#39;&#39;`] |

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


## managementDashboardManagementOrgIdDashboardGet

> any managementDashboardManagementOrgIdDashboardGet(orgId, xOrgKey, xOrgRole, xOrgActor)

Management Dashboard

### Example

```ts
import {
  Configuration,
  B2bApi,
} from '@xr7/sdk';
import type { ManagementDashboardManagementOrgIdDashboardGetRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new B2bApi();

  const body = {
    // string
    orgId: orgId_example,
    // string (optional)
    xOrgKey: xOrgKey_example,
    // string (optional)
    xOrgRole: xOrgRole_example,
    // string (optional)
    xOrgActor: xOrgActor_example,
  } satisfies ManagementDashboardManagementOrgIdDashboardGetRequest;

  try {
    const data = await api.managementDashboardManagementOrgIdDashboardGet(body);
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
| **orgId** | `string` |  | [Defaults to `undefined`] |
| **xOrgKey** | `string` |  | [Optional] [Defaults to `&#39;&#39;`] |
| **xOrgRole** | `string` |  | [Optional] [Defaults to `&#39;&#39;`] |
| **xOrgActor** | `string` |  | [Optional] [Defaults to `&#39;&#39;`] |

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


## managementDashboardV2ManagementOrgIdDashboardV2Get

> any managementDashboardV2ManagementOrgIdDashboardV2Get(orgId, xOrgKey, xOrgRole, xOrgActor)

Management Dashboard V2

### Example

```ts
import {
  Configuration,
  B2bApi,
} from '@xr7/sdk';
import type { ManagementDashboardV2ManagementOrgIdDashboardV2GetRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new B2bApi();

  const body = {
    // string
    orgId: orgId_example,
    // string (optional)
    xOrgKey: xOrgKey_example,
    // string (optional)
    xOrgRole: xOrgRole_example,
    // string (optional)
    xOrgActor: xOrgActor_example,
  } satisfies ManagementDashboardV2ManagementOrgIdDashboardV2GetRequest;

  try {
    const data = await api.managementDashboardV2ManagementOrgIdDashboardV2Get(body);
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
| **orgId** | `string` |  | [Defaults to `undefined`] |
| **xOrgKey** | `string` |  | [Optional] [Defaults to `&#39;&#39;`] |
| **xOrgRole** | `string` |  | [Optional] [Defaults to `&#39;&#39;`] |
| **xOrgActor** | `string` |  | [Optional] [Defaults to `&#39;&#39;`] |

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


## managementForecastManagementOrgIdForecastGet

> any managementForecastManagementOrgIdForecastGet(orgId, xOrgKey, xOrgRole, xOrgActor)

Management Forecast

### Example

```ts
import {
  Configuration,
  B2bApi,
} from '@xr7/sdk';
import type { ManagementForecastManagementOrgIdForecastGetRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new B2bApi();

  const body = {
    // string
    orgId: orgId_example,
    // string (optional)
    xOrgKey: xOrgKey_example,
    // string (optional)
    xOrgRole: xOrgRole_example,
    // string (optional)
    xOrgActor: xOrgActor_example,
  } satisfies ManagementForecastManagementOrgIdForecastGetRequest;

  try {
    const data = await api.managementForecastManagementOrgIdForecastGet(body);
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
| **orgId** | `string` |  | [Defaults to `undefined`] |
| **xOrgKey** | `string` |  | [Optional] [Defaults to `&#39;&#39;`] |
| **xOrgRole** | `string` |  | [Optional] [Defaults to `&#39;&#39;`] |
| **xOrgActor** | `string` |  | [Optional] [Defaults to `&#39;&#39;`] |

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


## orgPortfolioOrgOrgIdPortfolioGet

> any orgPortfolioOrgOrgIdPortfolioGet(orgId, xOrgKey, xOrgRole, xOrgActor)

Org Portfolio

### Example

```ts
import {
  Configuration,
  B2bApi,
} from '@xr7/sdk';
import type { OrgPortfolioOrgOrgIdPortfolioGetRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new B2bApi();

  const body = {
    // string
    orgId: orgId_example,
    // string (optional)
    xOrgKey: xOrgKey_example,
    // string (optional)
    xOrgRole: xOrgRole_example,
    // string (optional)
    xOrgActor: xOrgActor_example,
  } satisfies OrgPortfolioOrgOrgIdPortfolioGetRequest;

  try {
    const data = await api.orgPortfolioOrgOrgIdPortfolioGet(body);
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
| **orgId** | `string` |  | [Defaults to `undefined`] |
| **xOrgKey** | `string` |  | [Optional] [Defaults to `&#39;&#39;`] |
| **xOrgRole** | `string` |  | [Optional] [Defaults to `&#39;&#39;`] |
| **xOrgActor** | `string` |  | [Optional] [Defaults to `&#39;&#39;`] |

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


## xr7OperatorDashboardXr7OperatorDashboardGet

> any xr7OperatorDashboardXr7OperatorDashboardGet(orgId, xOrgKey, xOrgRole, xOrgActor)

Xr7 Operator Dashboard

### Example

```ts
import {
  Configuration,
  B2bApi,
} from '@xr7/sdk';
import type { Xr7OperatorDashboardXr7OperatorDashboardGetRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new B2bApi();

  const body = {
    // string (optional)
    orgId: orgId_example,
    // string (optional)
    xOrgKey: xOrgKey_example,
    // string (optional)
    xOrgRole: xOrgRole_example,
    // string (optional)
    xOrgActor: xOrgActor_example,
  } satisfies Xr7OperatorDashboardXr7OperatorDashboardGetRequest;

  try {
    const data = await api.xr7OperatorDashboardXr7OperatorDashboardGet(body);
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
| **orgId** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xOrgKey** | `string` |  | [Optional] [Defaults to `&#39;&#39;`] |
| **xOrgRole** | `string` |  | [Optional] [Defaults to `&#39;&#39;`] |
| **xOrgActor** | `string` |  | [Optional] [Defaults to `&#39;&#39;`] |

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

