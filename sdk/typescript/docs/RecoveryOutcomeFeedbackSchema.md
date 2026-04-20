
# RecoveryOutcomeFeedbackSchema


## Properties

Name | Type
------------ | -------------
`id` | string
`artistId` | string
`anomalyId` | string
`claimId` | string
`outcome` | [FeedbackOutcome](FeedbackOutcome.md)
`recoveredAmount` | number
`reasonCode` | string
`analystNote` | string
`createdAt` | Date

## Example

```typescript
import type { RecoveryOutcomeFeedbackSchema } from '@xr7/sdk'

// TODO: Update the object below with actual values
const example = {
  "id": null,
  "artistId": null,
  "anomalyId": null,
  "claimId": null,
  "outcome": null,
  "recoveredAmount": null,
  "reasonCode": null,
  "analystNote": null,
  "createdAt": null,
} satisfies RecoveryOutcomeFeedbackSchema

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as RecoveryOutcomeFeedbackSchema
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)
