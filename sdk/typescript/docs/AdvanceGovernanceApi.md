# AdvanceGovernanceApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**acceptArtistOfferArtistsArtistIdAdvanceOffersOfferIdAcceptPost**](AdvanceGovernanceApi.md#acceptartistofferartistsartistidadvanceoffersofferidacceptpost) | **POST** /artists/{artist_id}/advance/offers/{offer_id}/accept | Accept Artist Offer |
| [**analystQueueAdminAdvancesQueueAnalystGet**](AdvanceGovernanceApi.md#analystqueueadminadvancesqueueanalystget) | **GET** /admin/advances/queue/analyst | Analyst Queue |
| [**approveAnalystAdminAdvancesOpportunitiesOpportunityIdAnalystDecisionPost**](AdvanceGovernanceApi.md#approveanalystadminadvancesopportunitiesopportunityidanalystdecisionpost) | **POST** /admin/advances/opportunities/{opportunity_id}/analyst-decision | Approve Analyst |
| [**approveExecutiveAdminAdvancesOpportunitiesOpportunityIdExecutiveDecisionPost**](AdvanceGovernanceApi.md#approveexecutiveadminadvancesopportunitiesopportunityidexecutivedecisionpost) | **POST** /admin/advances/opportunities/{opportunity_id}/executive-decision | Approve Executive |
| [**completePacketAdminAdvancesPacketsPacketIdCompletePost**](AdvanceGovernanceApi.md#completepacketadminadvancespacketspacketidcompletepost) | **POST** /admin/advances/packets/{packet_id}/complete | Complete Packet |
| [**createFailedPacketAdminAdvancesOffersOfferIdFailedRecoveryPacketPost**](AdvanceGovernanceApi.md#createfailedpacketadminadvancesoffersofferidfailedrecoverypacketpost) | **POST** /admin/advances/offers/{offer_id}/failed-recovery-packet | Create Failed Packet |
| [**executiveQueueAdminAdvancesQueueExecutiveGet**](AdvanceGovernanceApi.md#executivequeueadminadvancesqueueexecutiveget) | **GET** /admin/advances/queue/executive | Executive Queue |
| [**listArtistOffersArtistsArtistIdAdvanceOffersGet**](AdvanceGovernanceApi.md#listartistoffersartistsartistidadvanceoffersget) | **GET** /artists/{artist_id}/advance/offers | List Artist Offers |
| [**publishOfferAdminAdvancesOpportunitiesOpportunityIdPublishOfferPost**](AdvanceGovernanceApi.md#publishofferadminadvancesopportunitiesopportunityidpublishofferpost) | **POST** /admin/advances/opportunities/{opportunity_id}/publish-offer | Publish Offer |
| [**runNightlyEvalAdminAdvancesRunNightlyEvalPost**](AdvanceGovernanceApi.md#runnightlyevaladminadvancesrunnightlyevalpost) | **POST** /admin/advances/run-nightly-eval | Run Nightly Eval |
| [**signFailedPacketAdminAdvancesPacketsPacketIdSignPost**](AdvanceGovernanceApi.md#signfailedpacketadminadvancespacketspacketidsignpost) | **POST** /admin/advances/packets/{packet_id}/sign | Sign Failed Packet |



## acceptArtistOfferArtistsArtistIdAdvanceOffersOfferIdAcceptPost

> { [key: string]: any; } acceptArtistOfferArtistsArtistIdAdvanceOffersOfferIdAcceptPost(artistId, offerId)

Accept Artist Offer

### Example

```ts
import {
  Configuration,
  AdvanceGovernanceApi,
} from '@xr7/sdk';
import type { AcceptArtistOfferArtistsArtistIdAdvanceOffersOfferIdAcceptPostRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const config = new Configuration({ 
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new AdvanceGovernanceApi(config);

  const body = {
    // string
    artistId: artistId_example,
    // string
    offerId: offerId_example,
  } satisfies AcceptArtistOfferArtistsArtistIdAdvanceOffersOfferIdAcceptPostRequest;

  try {
    const data = await api.acceptArtistOfferArtistsArtistIdAdvanceOffersOfferIdAcceptPost(body);
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
| **offerId** | `string` |  | [Defaults to `undefined`] |

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


## analystQueueAdminAdvancesQueueAnalystGet

> { [key: string]: any; } analystQueueAdminAdvancesQueueAnalystGet()

Analyst Queue

### Example

```ts
import {
  Configuration,
  AdvanceGovernanceApi,
} from '@xr7/sdk';
import type { AnalystQueueAdminAdvancesQueueAnalystGetRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const config = new Configuration({ 
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new AdvanceGovernanceApi(config);

  try {
    const data = await api.analystQueueAdminAdvancesQueueAnalystGet();
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

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## approveAnalystAdminAdvancesOpportunitiesOpportunityIdAnalystDecisionPost

> { [key: string]: any; } approveAnalystAdminAdvancesOpportunitiesOpportunityIdAnalystDecisionPost(opportunityId, approvalRequest)

Approve Analyst

### Example

```ts
import {
  Configuration,
  AdvanceGovernanceApi,
} from '@xr7/sdk';
import type { ApproveAnalystAdminAdvancesOpportunitiesOpportunityIdAnalystDecisionPostRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const config = new Configuration({ 
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new AdvanceGovernanceApi(config);

  const body = {
    // string
    opportunityId: opportunityId_example,
    // ApprovalRequest
    approvalRequest: ...,
  } satisfies ApproveAnalystAdminAdvancesOpportunitiesOpportunityIdAnalystDecisionPostRequest;

  try {
    const data = await api.approveAnalystAdminAdvancesOpportunitiesOpportunityIdAnalystDecisionPost(body);
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
| **opportunityId** | `string` |  | [Defaults to `undefined`] |
| **approvalRequest** | [ApprovalRequest](ApprovalRequest.md) |  | |

### Return type

**{ [key: string]: any; }**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## approveExecutiveAdminAdvancesOpportunitiesOpportunityIdExecutiveDecisionPost

> { [key: string]: any; } approveExecutiveAdminAdvancesOpportunitiesOpportunityIdExecutiveDecisionPost(opportunityId, approvalRequest)

Approve Executive

### Example

```ts
import {
  Configuration,
  AdvanceGovernanceApi,
} from '@xr7/sdk';
import type { ApproveExecutiveAdminAdvancesOpportunitiesOpportunityIdExecutiveDecisionPostRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const config = new Configuration({ 
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new AdvanceGovernanceApi(config);

  const body = {
    // string
    opportunityId: opportunityId_example,
    // ApprovalRequest
    approvalRequest: ...,
  } satisfies ApproveExecutiveAdminAdvancesOpportunitiesOpportunityIdExecutiveDecisionPostRequest;

  try {
    const data = await api.approveExecutiveAdminAdvancesOpportunitiesOpportunityIdExecutiveDecisionPost(body);
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
| **opportunityId** | `string` |  | [Defaults to `undefined`] |
| **approvalRequest** | [ApprovalRequest](ApprovalRequest.md) |  | |

### Return type

**{ [key: string]: any; }**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## completePacketAdminAdvancesPacketsPacketIdCompletePost

> { [key: string]: any; } completePacketAdminAdvancesPacketsPacketIdCompletePost(packetId)

Complete Packet

### Example

```ts
import {
  Configuration,
  AdvanceGovernanceApi,
} from '@xr7/sdk';
import type { CompletePacketAdminAdvancesPacketsPacketIdCompletePostRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const config = new Configuration({ 
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new AdvanceGovernanceApi(config);

  const body = {
    // string
    packetId: packetId_example,
  } satisfies CompletePacketAdminAdvancesPacketsPacketIdCompletePostRequest;

  try {
    const data = await api.completePacketAdminAdvancesPacketsPacketIdCompletePost(body);
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
| **packetId** | `string` |  | [Defaults to `undefined`] |

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


## createFailedPacketAdminAdvancesOffersOfferIdFailedRecoveryPacketPost

> { [key: string]: any; } createFailedPacketAdminAdvancesOffersOfferIdFailedRecoveryPacketPost(offerId, failedPacketRequest)

Create Failed Packet

### Example

```ts
import {
  Configuration,
  AdvanceGovernanceApi,
} from '@xr7/sdk';
import type { CreateFailedPacketAdminAdvancesOffersOfferIdFailedRecoveryPacketPostRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const config = new Configuration({ 
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new AdvanceGovernanceApi(config);

  const body = {
    // string
    offerId: offerId_example,
    // FailedPacketRequest
    failedPacketRequest: ...,
  } satisfies CreateFailedPacketAdminAdvancesOffersOfferIdFailedRecoveryPacketPostRequest;

  try {
    const data = await api.createFailedPacketAdminAdvancesOffersOfferIdFailedRecoveryPacketPost(body);
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
| **offerId** | `string` |  | [Defaults to `undefined`] |
| **failedPacketRequest** | [FailedPacketRequest](FailedPacketRequest.md) |  | |

### Return type

**{ [key: string]: any; }**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## executiveQueueAdminAdvancesQueueExecutiveGet

> { [key: string]: any; } executiveQueueAdminAdvancesQueueExecutiveGet()

Executive Queue

### Example

```ts
import {
  Configuration,
  AdvanceGovernanceApi,
} from '@xr7/sdk';
import type { ExecutiveQueueAdminAdvancesQueueExecutiveGetRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const config = new Configuration({ 
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new AdvanceGovernanceApi(config);

  try {
    const data = await api.executiveQueueAdminAdvancesQueueExecutiveGet();
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

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## listArtistOffersArtistsArtistIdAdvanceOffersGet

> { [key: string]: any; } listArtistOffersArtistsArtistIdAdvanceOffersGet(artistId)

List Artist Offers

### Example

```ts
import {
  Configuration,
  AdvanceGovernanceApi,
} from '@xr7/sdk';
import type { ListArtistOffersArtistsArtistIdAdvanceOffersGetRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const config = new Configuration({ 
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new AdvanceGovernanceApi(config);

  const body = {
    // string
    artistId: artistId_example,
  } satisfies ListArtistOffersArtistsArtistIdAdvanceOffersGetRequest;

  try {
    const data = await api.listArtistOffersArtistsArtistIdAdvanceOffersGet(body);
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


## publishOfferAdminAdvancesOpportunitiesOpportunityIdPublishOfferPost

> { [key: string]: any; } publishOfferAdminAdvancesOpportunitiesOpportunityIdPublishOfferPost(opportunityId)

Publish Offer

### Example

```ts
import {
  Configuration,
  AdvanceGovernanceApi,
} from '@xr7/sdk';
import type { PublishOfferAdminAdvancesOpportunitiesOpportunityIdPublishOfferPostRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const config = new Configuration({ 
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new AdvanceGovernanceApi(config);

  const body = {
    // string
    opportunityId: opportunityId_example,
  } satisfies PublishOfferAdminAdvancesOpportunitiesOpportunityIdPublishOfferPostRequest;

  try {
    const data = await api.publishOfferAdminAdvancesOpportunitiesOpportunityIdPublishOfferPost(body);
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
| **opportunityId** | `string` |  | [Defaults to `undefined`] |

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


## runNightlyEvalAdminAdvancesRunNightlyEvalPost

> { [key: string]: any; } runNightlyEvalAdminAdvancesRunNightlyEvalPost()

Run Nightly Eval

### Example

```ts
import {
  Configuration,
  AdvanceGovernanceApi,
} from '@xr7/sdk';
import type { RunNightlyEvalAdminAdvancesRunNightlyEvalPostRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const config = new Configuration({ 
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new AdvanceGovernanceApi(config);

  try {
    const data = await api.runNightlyEvalAdminAdvancesRunNightlyEvalPost();
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

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## signFailedPacketAdminAdvancesPacketsPacketIdSignPost

> { [key: string]: any; } signFailedPacketAdminAdvancesPacketsPacketIdSignPost(packetId, packetSignRequest)

Sign Failed Packet

### Example

```ts
import {
  Configuration,
  AdvanceGovernanceApi,
} from '@xr7/sdk';
import type { SignFailedPacketAdminAdvancesPacketsPacketIdSignPostRequest } from '@xr7/sdk';

async function example() {
  console.log("🚀 Testing @xr7/sdk SDK...");
  const config = new Configuration({ 
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new AdvanceGovernanceApi(config);

  const body = {
    // string
    packetId: packetId_example,
    // PacketSignRequest
    packetSignRequest: ...,
  } satisfies SignFailedPacketAdminAdvancesPacketsPacketIdSignPostRequest;

  try {
    const data = await api.signFailedPacketAdminAdvancesPacketsPacketIdSignPost(body);
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
| **packetId** | `string` |  | [Defaults to `undefined`] |
| **packetSignRequest** | [PacketSignRequest](PacketSignRequest.md) |  | |

### Return type

**{ [key: string]: any; }**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

