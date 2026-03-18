# MlSuiteApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**mlCalibrationDashboardArtistsArtistIdMlCalibrationDashboardGet**](MlSuiteApi.md#mlcalibrationdashboardartistsartistidmlcalibrationdashboardget) | **GET** /artists/{artist_id}/ml/calibration-dashboard | Ml Calibration Dashboard |
| [**mlExplainArtistsArtistIdMlExplainGet**](MlSuiteApi.md#mlexplainartistsartistidmlexplainget) | **GET** /artists/{artist_id}/ml/explain | Ml Explain |



## mlCalibrationDashboardArtistsArtistIdMlCalibrationDashboardGet

> { [key: string]: any; } mlCalibrationDashboardArtistsArtistIdMlCalibrationDashboardGet(artistId)

Ml Calibration Dashboard

### Example

```ts
import {
  Configuration,
  MlSuiteApi,
} from '@xr7/sdk';
import type { MlCalibrationDashboardArtistsArtistIdMlCalibrationDashboardGetRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const config = new Configuration({ 
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new MlSuiteApi(config);

  const body = {
    // string
    artistId: artistId_example,
  } satisfies MlCalibrationDashboardArtistsArtistIdMlCalibrationDashboardGetRequest;

  try {
    const data = await api.mlCalibrationDashboardArtistsArtistIdMlCalibrationDashboardGet(body);
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

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## mlExplainArtistsArtistIdMlExplainGet

> { [key: string]: any; } mlExplainArtistsArtistIdMlExplainGet(artistId)

Ml Explain

### Example

```ts
import {
  Configuration,
  MlSuiteApi,
} from '@xr7/sdk';
import type { MlExplainArtistsArtistIdMlExplainGetRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const config = new Configuration({ 
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new MlSuiteApi(config);

  const body = {
    // string
    artistId: artistId_example,
  } satisfies MlExplainArtistsArtistIdMlExplainGetRequest;

  try {
    const data = await api.mlExplainArtistsArtistIdMlExplainGet(body);
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

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

