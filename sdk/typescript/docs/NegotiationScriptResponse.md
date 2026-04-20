
# NegotiationScriptResponse


## Properties

Name | Type
------------ | -------------
`artistId` | string
`claimId` | string
`script` | { [key: string]: any; }

## Example

```typescript
import type { NegotiationScriptResponse } from '@xr7/sdk'

// TODO: Update the object below with actual values
const example = {
  "artistId": null,
  "claimId": null,
  "script": null,
} satisfies NegotiationScriptResponse

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as NegotiationScriptResponse
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)
