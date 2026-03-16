
# MLFeedbackEventSchema


## Properties

Name | Type
------------ | -------------
`id` | string
`artistId` | string
`feedbackType` | [MLFeedbackType](MLFeedbackType.md)
`sourceType` | string
`sourceId` | string
`anomalyId` | string
`claimId` | string
`subtype` | string
`category` | string
`artistProfileSegment` | string
`modelVersion` | string
`modelPrediction` | number
`humanDecision` | string
`outcome` | string
`estimatedAmount` | number
`actualAmount` | number
`payload` | { [key: string]: any; }
`createdAt` | Date

## Example

```typescript
import type { MLFeedbackEventSchema } from '@xr7/sdk'

// Example values shown below; adjust for your use case
const example = {
  "id": null,
  "artistId": null,
  "feedbackType": null,
  "sourceType": null,
  "sourceId": null,
  "anomalyId": null,
  "claimId": null,
  "subtype": null,
  "category": null,
  "artistProfileSegment": null,
  "modelVersion": null,
  "modelPrediction": null,
  "humanDecision": null,
  "outcome": null,
  "estimatedAmount": null,
  "actualAmount": null,
  "payload": null,
  "createdAt": null,
} satisfies MLFeedbackEventSchema

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as MLFeedbackEventSchema
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


