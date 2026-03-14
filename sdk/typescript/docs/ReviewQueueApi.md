# ReviewQueueApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**assignReviewItemReviewQueueItemsItemIdAssignPost**](ReviewQueueApi.md#assignreviewitemreviewqueueitemsitemidassignpost) | **POST** /review-queue/items/{item_id}/assign | Assign Review Item |
| [**checkThresholdReviewQueueThresholdCheckPost**](ReviewQueueApi.md#checkthresholdreviewqueuethresholdcheckpost) | **POST** /review-queue/threshold-check | Check Threshold |
| [**createReviewItemReviewQueueItemsPost**](ReviewQueueApi.md#createreviewitemreviewqueueitemspost) | **POST** /review-queue/items | Create Review Item |
| [**decideReviewItemReviewQueueItemsItemIdDecisionPost**](ReviewQueueApi.md#decidereviewitemreviewqueueitemsitemiddecisionpost) | **POST** /review-queue/items/{item_id}/decision | Decide Review Item |
| [**listDecisionsReviewQueueDecisionsGet**](ReviewQueueApi.md#listdecisionsreviewqueuedecisionsget) | **GET** /review-queue/decisions | List Decisions |
| [**listReviewItemsReviewQueueItemsGet**](ReviewQueueApi.md#listreviewitemsreviewqueueitemsget) | **GET** /review-queue/items | List Review Items |
| [**reviewQueueMetricsReviewQueueMetricsGet**](ReviewQueueApi.md#reviewqueuemetricsreviewqueuemetricsget) | **GET** /review-queue/metrics | Review Queue Metrics |



## assignReviewItemReviewQueueItemsItemIdAssignPost

> ReviewAssignmentSchema assignReviewItemReviewQueueItemsItemIdAssignPost(itemId, assignReviewItemRequest, xAnalystKey, xAnalystEmail)

Assign Review Item

### Example

```ts
import {
  Configuration,
  ReviewQueueApi,
} from '@xr7/sdk';
import type { AssignReviewItemReviewQueueItemsItemIdAssignPostRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new ReviewQueueApi();

  const body = {
    // string
    itemId: itemId_example,
    // AssignReviewItemRequest
    assignReviewItemRequest: ...,
    // string (optional)
    xAnalystKey: xAnalystKey_example,
    // string (optional)
    xAnalystEmail: xAnalystEmail_example,
  } satisfies AssignReviewItemReviewQueueItemsItemIdAssignPostRequest;

  try {
    const data = await api.assignReviewItemReviewQueueItemsItemIdAssignPost(body);
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
| **itemId** | `string` |  | [Defaults to `undefined`] |
| **assignReviewItemRequest** | [AssignReviewItemRequest](AssignReviewItemRequest.md) |  | |
| **xAnalystKey** | `string` |  | [Optional] [Defaults to `&#39;&#39;`] |
| **xAnalystEmail** | `string` |  | [Optional] [Defaults to `&#39;&#39;`] |

### Return type

[**ReviewAssignmentSchema**](ReviewAssignmentSchema.md)

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


## checkThresholdReviewQueueThresholdCheckPost

> any checkThresholdReviewQueueThresholdCheckPost(xAnalystKey, xAnalystEmail)

Check Threshold

### Example

```ts
import {
  Configuration,
  ReviewQueueApi,
} from '@xr7/sdk';
import type { CheckThresholdReviewQueueThresholdCheckPostRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new ReviewQueueApi();

  const body = {
    // string (optional)
    xAnalystKey: xAnalystKey_example,
    // string (optional)
    xAnalystEmail: xAnalystEmail_example,
  } satisfies CheckThresholdReviewQueueThresholdCheckPostRequest;

  try {
    const data = await api.checkThresholdReviewQueueThresholdCheckPost(body);
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
| **xAnalystKey** | `string` |  | [Optional] [Defaults to `&#39;&#39;`] |
| **xAnalystEmail** | `string` |  | [Optional] [Defaults to `&#39;&#39;`] |

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


## createReviewItemReviewQueueItemsPost

> ReviewItemSchema createReviewItemReviewQueueItemsPost(createReviewItemRequest, xAnalystKey, xAnalystEmail)

Create Review Item

### Example

```ts
import {
  Configuration,
  ReviewQueueApi,
} from '@xr7/sdk';
import type { CreateReviewItemReviewQueueItemsPostRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new ReviewQueueApi();

  const body = {
    // CreateReviewItemRequest
    createReviewItemRequest: ...,
    // string (optional)
    xAnalystKey: xAnalystKey_example,
    // string (optional)
    xAnalystEmail: xAnalystEmail_example,
  } satisfies CreateReviewItemReviewQueueItemsPostRequest;

  try {
    const data = await api.createReviewItemReviewQueueItemsPost(body);
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
| **createReviewItemRequest** | [CreateReviewItemRequest](CreateReviewItemRequest.md) |  | |
| **xAnalystKey** | `string` |  | [Optional] [Defaults to `&#39;&#39;`] |
| **xAnalystEmail** | `string` |  | [Optional] [Defaults to `&#39;&#39;`] |

### Return type

[**ReviewItemSchema**](ReviewItemSchema.md)

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


## decideReviewItemReviewQueueItemsItemIdDecisionPost

> ReviewDecisionSchema decideReviewItemReviewQueueItemsItemIdDecisionPost(itemId, decideReviewItemRequest, xAnalystKey, xAnalystEmail)

Decide Review Item

### Example

```ts
import {
  Configuration,
  ReviewQueueApi,
} from '@xr7/sdk';
import type { DecideReviewItemReviewQueueItemsItemIdDecisionPostRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new ReviewQueueApi();

  const body = {
    // string
    itemId: itemId_example,
    // DecideReviewItemRequest
    decideReviewItemRequest: ...,
    // string (optional)
    xAnalystKey: xAnalystKey_example,
    // string (optional)
    xAnalystEmail: xAnalystEmail_example,
  } satisfies DecideReviewItemReviewQueueItemsItemIdDecisionPostRequest;

  try {
    const data = await api.decideReviewItemReviewQueueItemsItemIdDecisionPost(body);
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
| **itemId** | `string` |  | [Defaults to `undefined`] |
| **decideReviewItemRequest** | [DecideReviewItemRequest](DecideReviewItemRequest.md) |  | |
| **xAnalystKey** | `string` |  | [Optional] [Defaults to `&#39;&#39;`] |
| **xAnalystEmail** | `string` |  | [Optional] [Defaults to `&#39;&#39;`] |

### Return type

[**ReviewDecisionSchema**](ReviewDecisionSchema.md)

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


## listDecisionsReviewQueueDecisionsGet

> Array&lt;ReviewDecisionSchema&gt; listDecisionsReviewQueueDecisionsGet(itemId, limit, offset, xAnalystKey, xAnalystEmail)

List Decisions

### Example

```ts
import {
  Configuration,
  ReviewQueueApi,
} from '@xr7/sdk';
import type { ListDecisionsReviewQueueDecisionsGetRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new ReviewQueueApi();

  const body = {
    // string (optional)
    itemId: itemId_example,
    // number (optional)
    limit: 56,
    // number (optional)
    offset: 56,
    // string (optional)
    xAnalystKey: xAnalystKey_example,
    // string (optional)
    xAnalystEmail: xAnalystEmail_example,
  } satisfies ListDecisionsReviewQueueDecisionsGetRequest;

  try {
    const data = await api.listDecisionsReviewQueueDecisionsGet(body);
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
| **itemId** | `string` |  | [Optional] [Defaults to `undefined`] |
| **limit** | `number` |  | [Optional] [Defaults to `100`] |
| **offset** | `number` |  | [Optional] [Defaults to `0`] |
| **xAnalystKey** | `string` |  | [Optional] [Defaults to `&#39;&#39;`] |
| **xAnalystEmail** | `string` |  | [Optional] [Defaults to `&#39;&#39;`] |

### Return type

[**Array&lt;ReviewDecisionSchema&gt;**](ReviewDecisionSchema.md)

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


## listReviewItemsReviewQueueItemsGet

> Array&lt;ReviewItemSchema&gt; listReviewItemsReviewQueueItemsGet(status, artistId, assignedAnalystEmail, limit, offset, xAnalystKey, xAnalystEmail)

List Review Items

### Example

```ts
import {
  Configuration,
  ReviewQueueApi,
} from '@xr7/sdk';
import type { ListReviewItemsReviewQueueItemsGetRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new ReviewQueueApi();

  const body = {
    // string (optional)
    status: status_example,
    // string (optional)
    artistId: artistId_example,
    // string (optional)
    assignedAnalystEmail: assignedAnalystEmail_example,
    // number (optional)
    limit: 56,
    // number (optional)
    offset: 56,
    // string (optional)
    xAnalystKey: xAnalystKey_example,
    // string (optional)
    xAnalystEmail: xAnalystEmail_example,
  } satisfies ListReviewItemsReviewQueueItemsGetRequest;

  try {
    const data = await api.listReviewItemsReviewQueueItemsGet(body);
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
| **status** | `string` |  | [Optional] [Defaults to `undefined`] |
| **artistId** | `string` |  | [Optional] [Defaults to `undefined`] |
| **assignedAnalystEmail** | `string` |  | [Optional] [Defaults to `undefined`] |
| **limit** | `number` |  | [Optional] [Defaults to `100`] |
| **offset** | `number` |  | [Optional] [Defaults to `0`] |
| **xAnalystKey** | `string` |  | [Optional] [Defaults to `&#39;&#39;`] |
| **xAnalystEmail** | `string` |  | [Optional] [Defaults to `&#39;&#39;`] |

### Return type

[**Array&lt;ReviewItemSchema&gt;**](ReviewItemSchema.md)

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


## reviewQueueMetricsReviewQueueMetricsGet

> any reviewQueueMetricsReviewQueueMetricsGet(xAnalystKey, xAnalystEmail)

Review Queue Metrics

### Example

```ts
import {
  Configuration,
  ReviewQueueApi,
} from '@xr7/sdk';
import type { ReviewQueueMetricsReviewQueueMetricsGetRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const api = new ReviewQueueApi();

  const body = {
    // string (optional)
    xAnalystKey: xAnalystKey_example,
    // string (optional)
    xAnalystEmail: xAnalystEmail_example,
  } satisfies ReviewQueueMetricsReviewQueueMetricsGetRequest;

  try {
    const data = await api.reviewQueueMetricsReviewQueueMetricsGet(body);
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
| **xAnalystKey** | `string` |  | [Optional] [Defaults to `&#39;&#39;`] |
| **xAnalystEmail** | `string` |  | [Optional] [Defaults to `&#39;&#39;`] |

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

