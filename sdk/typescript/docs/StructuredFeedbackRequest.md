
# StructuredFeedbackRequest


## Properties

Name | Type
------------ | -------------
`anomalyId` | string
`claimId` | string
`outcome` | string
`recoveredAmount` | number
`reasonCode` | string
`analystNote` | string
`feedbackType` | [MLFeedbackType](MLFeedbackType.md)
`sourceType` | string
`sourceId` | string
`subtype` | string
`category` | string
`artistProfileSegment` | string
`modelVersion` | string
`modelPrediction` | number
`humanDecision` | string
`estimatedAmount` | number
`actualAmount` | number
`payload` | { [key: string]: any; }

## Example

```typescript
import type { StructuredFeedbackRequest } from '@xr7/sdk'

// TODO: Update the object below with actual values
const example = {
  "anomalyId": null,
  "claimId": null,
  "outcome": null,
  "recoveredAmount": null,
  "reasonCode": null,
  "analystNote": null,
  "feedbackType": null,
  "sourceType": null,
  "sourceId": null,
  "subtype": null,
  "category": null,
  "artistProfileSegment": null,
  "modelVersion": null,
  "modelPrediction": null,
  "humanDecision": null,
  "estimatedAmount": null,
  "actualAmount": null,
  "payload": null,
} satisfies StructuredFeedbackRequest

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as StructuredFeedbackRequest
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


