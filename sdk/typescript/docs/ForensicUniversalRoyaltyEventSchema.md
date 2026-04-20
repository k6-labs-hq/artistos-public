
# ForensicUniversalRoyaltyEventSchema


## Properties

Name | Type
------------ | -------------
`eventId` | string
`workId` | string
`isrc` | string
`iswc` | string
`title` | string
`artistName` | string
`writerName` | string
`publisherName` | string
`distributor` | string
`platform` | string
`usageType` | string
`usageCount` | number
`payoutAmount` | number
`payoutCurrency` | string
`statementPeriodStart` | Date
`statementPeriodEnd` | Date
`sourceFileId` | string
`confidenceScore` | number
`metadataFlags` | string
`ingestionTimestamp` | Date

## Example

```typescript
import type { ForensicUniversalRoyaltyEventSchema } from '@xr7/sdk'

// TODO: Update the object below with actual values
const example = {
  "eventId": null,
  "workId": null,
  "isrc": null,
  "iswc": null,
  "title": null,
  "artistName": null,
  "writerName": null,
  "publisherName": null,
  "distributor": null,
  "platform": null,
  "usageType": null,
  "usageCount": null,
  "payoutAmount": null,
  "payoutCurrency": null,
  "statementPeriodStart": null,
  "statementPeriodEnd": null,
  "sourceFileId": null,
  "confidenceScore": null,
  "metadataFlags": null,
  "ingestionTimestamp": null,
} satisfies ForensicUniversalRoyaltyEventSchema

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as ForensicUniversalRoyaltyEventSchema
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)
