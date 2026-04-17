# TransparencyApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**explainAnomalyArtistsArtistIdAnomaliesAnomalyIdExplainGet**](TransparencyApi.md#explainanomalyartistsartistidanomaliesanomalyidexplainget) | **GET** /artists/{artist_id}/anomalies/{anomaly_id}/explain | Explain Anomaly |
| [**fullLedgerArtistsArtistIdLedgerFullGet**](TransparencyApi.md#fullledgerartistsartistidledgerfullget) | **GET** /artists/{artist_id}/ledger/full | Full Ledger |



## explainAnomalyArtistsArtistIdAnomaliesAnomalyIdExplainGet

> any explainAnomalyArtistsArtistIdAnomaliesAnomalyIdExplainGet(artistId, anomalyId)

Explain Anomaly

### Example

```ts
import {
  Configuration,
  TransparencyApi,
} from '@xr7/sdk';
import type { ExplainAnomalyArtistsArtistIdAnomaliesAnomalyIdExplainGetRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new TransparencyApi();

  const body = {
    // string
    artistId: artistId_example,
    // string
    anomalyId: anomalyId_example,
  } satisfies ExplainAnomalyArtistsArtistIdAnomaliesAnomalyIdExplainGetRequest;

  try {
    const data = await api.explainAnomalyArtistsArtistIdAnomaliesAnomalyIdExplainGet(body);
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
| **anomalyId** | `string` |  | [Defaults to `undefined`] |

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


## fullLedgerArtistsArtistIdLedgerFullGet

> any fullLedgerArtistsArtistIdLedgerFullGet(artistId, includeRawStatements)

Full Ledger

### Example

```ts
import {
  Configuration,
  TransparencyApi,
} from '@xr7/sdk';
import type { FullLedgerArtistsArtistIdLedgerFullGetRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new TransparencyApi();

  const body = {
    // string
    artistId: artistId_example,
    // boolean (optional)
    includeRawStatements: true,
  } satisfies FullLedgerArtistsArtistIdLedgerFullGetRequest;

  try {
    const data = await api.fullLedgerArtistsArtistIdLedgerFullGet(body);
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
| **includeRawStatements** | `boolean` |  | [Optional] [Defaults to `true`] |

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
