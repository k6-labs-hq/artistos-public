
# BlackBoxRequest


## Properties

Name | Type
------------ | -------------
`tenantId` | string
`minConfidence` | number
`queueBackend` | string

## Example

```typescript
import type { BlackBoxRequest } from '@xr7/sdk'

// TODO: Update the object below with actual values
const example = {
  "tenantId": null,
  "minConfidence": null,
  "queueBackend": null,
} satisfies BlackBoxRequest

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as BlackBoxRequest
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)
