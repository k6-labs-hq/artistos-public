
# CeleroTransactionSchema


## Properties

Name | Type
------------ | -------------
`id` | string
`artistId` | string
`claimId` | string
`type` | [CeleroTxnType](CeleroTxnType.md)
`amount` | number
`currency` | string
`status` | [CeleroTxnStatus](CeleroTxnStatus.md)
`celeroTransactionId` | string
`celeroCustomerVaultId` | string
`celeroAuthCode` | string
`celeroResponseCode` | string
`celeroResponseText` | string
`orderId` | string
`description` | string
`createdAt` | Date
`updatedAt` | Date

## Example

```typescript
import type { CeleroTransactionSchema } from '@xr7/sdk'

// TODO: Update the object below with actual values
const example = {
  "id": null,
  "artistId": null,
  "claimId": null,
  "type": null,
  "amount": null,
  "currency": null,
  "status": null,
  "celeroTransactionId": null,
  "celeroCustomerVaultId": null,
  "celeroAuthCode": null,
  "celeroResponseCode": null,
  "celeroResponseText": null,
  "orderId": null,
  "description": null,
  "createdAt": null,
  "updatedAt": null,
} satisfies CeleroTransactionSchema

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as CeleroTransactionSchema
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


