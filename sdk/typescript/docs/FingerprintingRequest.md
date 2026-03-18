
# FingerprintingRequest


## Properties

Name | Type
------------ | -------------
`tenantId` | string
`platform` | string
`detections` | Array&lt;{ [key: string]: any; }&gt;
`queueBackend` | string

## Example

```typescript
import type { FingerprintingRequest } from '@xr7/sdk'

// TODO: Update the object below with actual values
const example = {
  "tenantId": null,
  "platform": null,
  "detections": null,
  "queueBackend": null,
} satisfies FingerprintingRequest

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as FingerprintingRequest
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


