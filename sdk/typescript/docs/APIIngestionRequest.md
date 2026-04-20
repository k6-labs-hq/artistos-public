
# APIIngestionRequest


## Properties

Name | Type
------------ | -------------
`tenantId` | string
`providers` | Array&lt;string&gt;
`since` | Date
`until` | Date
`queueBackend` | string

## Example

```typescript
import type { APIIngestionRequest } from '@xr7/sdk'

// TODO: Update the object below with actual values
const example = {
  "tenantId": null,
  "providers": null,
  "since": null,
  "until": null,
  "queueBackend": null,
} satisfies APIIngestionRequest

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as APIIngestionRequest
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)
