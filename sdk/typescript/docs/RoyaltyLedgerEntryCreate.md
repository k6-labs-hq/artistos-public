
# RoyaltyLedgerEntryCreate


## Properties

Name | Type
------------ | -------------
`source` | string
`recordType` | [LedgerRecordType](LedgerRecordType.md)
`sourceFile` | string
`sourceRow` | number
`contractVersion` | string
`workId` | string
`eventType` | string
`periodStart` | Date
`periodEnd` | Date
`quantity` | number
`rate` | number
`expectedAmount` | number
`receivedAmount` | number
`currency` | string
`fxRateUsed` | number
`territory` | string

## Example

```typescript
import type { RoyaltyLedgerEntryCreate } from '@xr7/sdk'

// TODO: Update the object below with actual values
const example = {
  "source": null,
  "recordType": null,
  "sourceFile": null,
  "sourceRow": null,
  "contractVersion": null,
  "workId": null,
  "eventType": null,
  "periodStart": null,
  "periodEnd": null,
  "quantity": null,
  "rate": null,
  "expectedAmount": null,
  "receivedAmount": null,
  "currency": null,
  "fxRateUsed": null,
  "territory": null,
} satisfies RoyaltyLedgerEntryCreate

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as RoyaltyLedgerEntryCreate
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


