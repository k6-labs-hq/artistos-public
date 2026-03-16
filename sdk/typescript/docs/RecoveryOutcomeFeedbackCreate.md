
# RecoveryOutcomeFeedbackCreate


## Properties

Name | Type
------------ | -------------
`anomalyId` | string
`claimId` | string
`outcome` | [FeedbackOutcome](FeedbackOutcome.md)
`recoveredAmount` | number
`reasonCode` | string
`analystNote` | string

## Example

```typescript
import type { RecoveryOutcomeFeedbackCreate } from '@xr7/sdk'

// Example values shown below; adjust for your use case
const example = {
  "anomalyId": null,
  "claimId": null,
  "outcome": null,
  "recoveredAmount": null,
  "reasonCode": null,
  "analystNote": null,
} satisfies RecoveryOutcomeFeedbackCreate

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as RecoveryOutcomeFeedbackCreate
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


