
# WidgetLeadSchema


## Properties

Name | Type
------------ | -------------
`id` | string
`artistName` | string
`email` | string
`careerStage` | string
`genre` | string
`yearsActive` | number
`territory` | string
`estimateConservative` | number
`estimateLikely` | number
`estimateOptimistic` | number
`currency` | string
`resultsEmailed` | boolean
`claimed` | boolean
`claimSubmittedAt` | Date
`createdAt` | Date

## Example

```typescript
import type { WidgetLeadSchema } from '@xr7/sdk'

// Example values shown below; adjust for your use case
const example = {
  "id": null,
  "artistName": null,
  "email": null,
  "careerStage": null,
  "genre": null,
  "yearsActive": null,
  "territory": null,
  "estimateConservative": null,
  "estimateLikely": null,
  "estimateOptimistic": null,
  "currency": null,
  "resultsEmailed": null,
  "claimed": null,
  "claimSubmittedAt": null,
  "createdAt": null,
} satisfies WidgetLeadSchema

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as WidgetLeadSchema
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


