
# EstimateRequest


## Properties

Name | Type
------------ | -------------
`estimateToken` | string
`careerStage` | string
`genre` | string
`yearsActive` | number
`territory` | string

## Example

```typescript
import type { EstimateRequest } from '@xr7/sdk'

// TODO: Update the object below with actual values
const example = {
  "estimateToken": null,
  "careerStage": null,
  "genre": null,
  "yearsActive": null,
  "territory": null,
} satisfies EstimateRequest

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as EstimateRequest
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)
