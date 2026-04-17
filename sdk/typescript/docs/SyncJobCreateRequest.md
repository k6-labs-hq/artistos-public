
# SyncJobCreateRequest


## Properties

Name | Type
------------ | -------------
`integration` | string
`maxAttempts` | number
`payload` | { [key: string]: any; }
`runAsync` | boolean
`queueBackend` | string

## Example

```typescript
import type { SyncJobCreateRequest } from '@xr7/sdk'

// TODO: Update the object below with actual values
const example = {
  "integration": null,
  "maxAttempts": null,
  "payload": null,
  "runAsync": null,
  "queueBackend": null,
} satisfies SyncJobCreateRequest

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as SyncJobCreateRequest
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)
