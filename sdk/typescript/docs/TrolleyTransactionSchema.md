
# TrolleyTransactionSchema


## Properties

Name | Type
------------ | -------------
`id` | string
`artistId` | string
`claimId` | string
`type` | [TrolleyTxnType](TrolleyTxnType.md)
`status` | [TrolleyTxnStatus](TrolleyTxnStatus.md)
`grossAmount` | number
`platformFeeAmount` | number
`netAmount` | number
`sourceCurrency` | string
`localAmount` | number
`localCurrency` | string
`exchangeRate` | number
`trolleyPaymentId` | string
`trolleyBatchId` | string
`externalId` | string
`failureReason` | string
`retryCount` | number
`description` | string
`createdAt` | Date
`updatedAt` | Date

## Example

```typescript
import type { TrolleyTransactionSchema } from '@xr7/sdk'

// TODO: Update the object below with actual values
const example = {
  "id": null,
  "artistId": null,
  "claimId": null,
  "type": null,
  "status": null,
  "grossAmount": null,
  "platformFeeAmount": null,
  "netAmount": null,
  "sourceCurrency": null,
  "localAmount": null,
  "localCurrency": null,
  "exchangeRate": null,
  "trolleyPaymentId": null,
  "trolleyBatchId": null,
  "externalId": null,
  "failureReason": null,
  "retryCount": null,
  "description": null,
  "createdAt": null,
  "updatedAt": null,
} satisfies TrolleyTransactionSchema

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as TrolleyTransactionSchema
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


