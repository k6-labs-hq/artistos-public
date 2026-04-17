# IngestionApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**connectRegionalGlobalArtistsArtistIdConnectRegionalGlobalPost**](IngestionApi.md#connectregionalglobalartistsartistidconnectregionalglobalpost) | **POST** /artists/{artist_id}/connect/regional-global | Connect Regional Global |
| [**connectSoundexchangeMlcArtistsArtistIdConnectSoundexchangeMlcPost**](IngestionApi.md#connectsoundexchangemlcartistsartistidconnectsoundexchangemlcpost) | **POST** /artists/{artist_id}/connect/soundexchange-mlc | Connect Soundexchange Mlc |
| [**getStatementArtistsArtistIdStatementsStatementIdGet**](IngestionApi.md#getstatementartistsartistidstatementsstatementidget) | **GET** /artists/{artist_id}/statements/{statement_id} | Get Statement |
| [**listStatementsArtistsArtistIdStatementsGet**](IngestionApi.md#liststatementsartistsartistidstatementsget) | **GET** /artists/{artist_id}/statements | List Statements |
| [**regionalGlobalStatusArtistsArtistIdConnectRegionalGlobalStatusGet**](IngestionApi.md#regionalglobalstatusartistsartistidconnectregionalglobalstatusget) | **GET** /artists/{artist_id}/connect/regional-global/status | Regional Global Status |
| [**soundexchangeMlcStatusArtistsArtistIdConnectSoundexchangeMlcStatusGet**](IngestionApi.md#soundexchangemlcstatusartistsartistidconnectsoundexchangemlcstatusget) | **GET** /artists/{artist_id}/connect/soundexchange-mlc/status | Soundexchange Mlc Status |
| [**supportedFormatsIngestionSupportedFormatsGet**](IngestionApi.md#supportedformatsingestionsupportedformatsget) | **GET** /ingestion/supported-formats | Supported Formats |
| [**uploadStatementArtistsArtistIdStatementsUploadPost**](IngestionApi.md#uploadstatementartistsartistidstatementsuploadpost) | **POST** /artists/{artist_id}/statements/upload | Upload Statement |
| [**uploadStatementBatchArtistsArtistIdStatementsUploadBatchPost**](IngestionApi.md#uploadstatementbatchartistsartistidstatementsuploadbatchpost) | **POST** /artists/{artist_id}/statements/upload-batch | Upload Statement Batch |



## connectRegionalGlobalArtistsArtistIdConnectRegionalGlobalPost

> any connectRegionalGlobalArtistsArtistIdConnectRegionalGlobalPost(artistId, genre, territory)

Connect Regional Global

### Example

```ts
import {
  Configuration,
  IngestionApi,
} from '@xr7/sdk';
import type { ConnectRegionalGlobalArtistsArtistIdConnectRegionalGlobalPostRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new IngestionApi();

  const body = {
    // string
    artistId: artistId_example,
    // string (optional)
    genre: genre_example,
    // string (optional)
    territory: territory_example,
  } satisfies ConnectRegionalGlobalArtistsArtistIdConnectRegionalGlobalPostRequest;

  try {
    const data = await api.connectRegionalGlobalArtistsArtistIdConnectRegionalGlobalPost(body);
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
| **genre** | `string` |  | [Optional] [Defaults to `&#39;latin&#39;`] |
| **territory** | `string` |  | [Optional] [Defaults to `&#39;LATAM&#39;`] |

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


## connectSoundexchangeMlcArtistsArtistIdConnectSoundexchangeMlcPost

> any connectSoundexchangeMlcArtistsArtistIdConnectSoundexchangeMlcPost(artistId, yearsBack)

Connect Soundexchange Mlc

### Example

```ts
import {
  Configuration,
  IngestionApi,
} from '@xr7/sdk';
import type { ConnectSoundexchangeMlcArtistsArtistIdConnectSoundexchangeMlcPostRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new IngestionApi();

  const body = {
    // string
    artistId: artistId_example,
    // number (optional)
    yearsBack: 56,
  } satisfies ConnectSoundexchangeMlcArtistsArtistIdConnectSoundexchangeMlcPostRequest;

  try {
    const data = await api.connectSoundexchangeMlcArtistsArtistIdConnectSoundexchangeMlcPost(body);
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
| **yearsBack** | `number` |  | [Optional] [Defaults to `10`] |

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


## getStatementArtistsArtistIdStatementsStatementIdGet

> StatementSchema getStatementArtistsArtistIdStatementsStatementIdGet(artistId, statementId)

Get Statement

Return details of a single statement upload.

### Example

```ts
import {
  Configuration,
  IngestionApi,
} from '@xr7/sdk';
import type { GetStatementArtistsArtistIdStatementsStatementIdGetRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new IngestionApi();

  const body = {
    // string
    artistId: artistId_example,
    // string
    statementId: statementId_example,
  } satisfies GetStatementArtistsArtistIdStatementsStatementIdGetRequest;

  try {
    const data = await api.getStatementArtistsArtistIdStatementsStatementIdGet(body);
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
| **statementId** | `string` |  | [Defaults to `undefined`] |

### Return type

[**StatementSchema**](StatementSchema.md)

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


## listStatementsArtistsArtistIdStatementsGet

> Array&lt;StatementSchema&gt; listStatementsArtistsArtistIdStatementsGet(artistId)

List Statements

Return all statement uploads for an artist, newest first.

### Example

```ts
import {
  Configuration,
  IngestionApi,
} from '@xr7/sdk';
import type { ListStatementsArtistsArtistIdStatementsGetRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new IngestionApi();

  const body = {
    // string
    artistId: artistId_example,
  } satisfies ListStatementsArtistsArtistIdStatementsGetRequest;

  try {
    const data = await api.listStatementsArtistsArtistIdStatementsGet(body);
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

[**Array&lt;StatementSchema&gt;**](StatementSchema.md)

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


## regionalGlobalStatusArtistsArtistIdConnectRegionalGlobalStatusGet

> any regionalGlobalStatusArtistsArtistIdConnectRegionalGlobalStatusGet(artistId)

Regional Global Status

### Example

```ts
import {
  Configuration,
  IngestionApi,
} from '@xr7/sdk';
import type { RegionalGlobalStatusArtistsArtistIdConnectRegionalGlobalStatusGetRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new IngestionApi();

  const body = {
    // string
    artistId: artistId_example,
  } satisfies RegionalGlobalStatusArtistsArtistIdConnectRegionalGlobalStatusGetRequest;

  try {
    const data = await api.regionalGlobalStatusArtistsArtistIdConnectRegionalGlobalStatusGet(body);
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


## soundexchangeMlcStatusArtistsArtistIdConnectSoundexchangeMlcStatusGet

> any soundexchangeMlcStatusArtistsArtistIdConnectSoundexchangeMlcStatusGet(artistId)

Soundexchange Mlc Status

### Example

```ts
import {
  Configuration,
  IngestionApi,
} from '@xr7/sdk';
import type { SoundexchangeMlcStatusArtistsArtistIdConnectSoundexchangeMlcStatusGetRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new IngestionApi();

  const body = {
    // string
    artistId: artistId_example,
  } satisfies SoundexchangeMlcStatusArtistsArtistIdConnectSoundexchangeMlcStatusGetRequest;

  try {
    const data = await api.soundexchangeMlcStatusArtistsArtistIdConnectSoundexchangeMlcStatusGet(body);
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


## supportedFormatsIngestionSupportedFormatsGet

> { [key: string]: any; } supportedFormatsIngestionSupportedFormatsGet()

Supported Formats

Return the complete list of explicitly supported royalty statement formats, grouped by type (distributor, PRO, DSP, generic).  For each format the response includes: - &#x60;&#x60;name&#x60;&#x60; — human-readable distributor/PRO name - &#x60;&#x60;type&#x60;&#x60; — &#x60;&#x60;\&quot;distributor\&quot;&#x60;&#x60; | &#x60;&#x60;\&quot;pro\&quot;&#x60;&#x60; | &#x60;&#x60;\&quot;dsp\&quot;&#x60;&#x60; | &#x60;&#x60;\&quot;generic\&quot;&#x60;&#x60; - &#x60;&#x60;key_columns&#x60;&#x60; — representative column headers from that format\&#39;s CSV - &#x60;&#x60;description&#x60;&#x60; — how to obtain the file and what it covers  Any file that does not match an explicit format is handled by the &#x60;&#x60;\&quot;generic\&quot;&#x60;&#x60; fallback, which recognises any file with recognisable date, source, quantity, and amount columns.  This covers distributors such as Songtradr, Vydia, AWAL, Symphonic, INgrooves, Believe, Kobalt, and others.

### Example

```ts
import {
  Configuration,
  IngestionApi,
} from '@xr7/sdk';
import type { SupportedFormatsIngestionSupportedFormatsGetRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new IngestionApi();

  try {
    const data = await api.supportedFormatsIngestionSupportedFormatsGet();
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


## uploadStatementArtistsArtistIdStatementsUploadPost

> StatementSchema uploadStatementArtistsArtistIdStatementsUploadPost(artistId, file)

Upload Statement

Upload a royalty statement file and ingest it into the database.  Supported formats are automatically detected from the column headers:     **DistroKid**, **TuneCore**, **CD Baby**, **ASCAP**, **BMI**,     **Spotify for Artists**, **SoundCloud**, and a **generic** fallback for any statement with recognisable date / amount / quantity columns.  After ingestion, anomaly detection is run automatically so that any under-payment issues are immediately flagged.  Returns a :class:&#x60;~XR7.models.statement.Statement&#x60; record summarising what was parsed and saved.  **Requires prior acceptance of the Artist Recovery Services Agreement.** Call &#x60;&#x60;GET /terms&#x60;&#x60; to read the agreement and &#x60;&#x60;POST /artists/{artist_id}/terms/accept&#x60;&#x60; to accept it.  This endpoint returns HTTP 403 until the artist has agreed to the terms.

### Example

```ts
import {
  Configuration,
  IngestionApi,
} from '@xr7/sdk';
import type { UploadStatementArtistsArtistIdStatementsUploadPostRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new IngestionApi();

  const body = {
    // string
    artistId: artistId_example,
    // string
    file: file_example,
  } satisfies UploadStatementArtistsArtistIdStatementsUploadPostRequest;

  try {
    const data = await api.uploadStatementArtistsArtistIdStatementsUploadPost(body);
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

[**StatementSchema**](StatementSchema.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: `multipart/form-data`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **201** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## uploadStatementBatchArtistsArtistIdStatementsUploadBatchPost

> any uploadStatementBatchArtistsArtistIdStatementsUploadBatchPost(artistId, files)

Upload Statement Batch

Upload and process a batch of statement files (CSV/ZIP/PDF) with malware scanning and parallel parsing.

### Example

```ts
import {
  Configuration,
  IngestionApi,
} from '@xr7/sdk';
import type { UploadStatementBatchArtistsArtistIdStatementsUploadBatchPostRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new IngestionApi();

  const body = {
    // string
    artistId: artistId_example,
    // Array<string>
    files: ...,
  } satisfies UploadStatementBatchArtistsArtistIdStatementsUploadBatchPostRequest;

  try {
    const data = await api.uploadStatementBatchArtistsArtistIdStatementsUploadBatchPost(body);
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
