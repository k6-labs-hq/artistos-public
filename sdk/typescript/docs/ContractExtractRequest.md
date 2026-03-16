
# ContractExtractRequest


## Properties

Name | Type
------------ | -------------
`contractId` | string
`contractText` | string
`effectiveStart` | Date
`effectiveEnd` | Date
`extractedFrom` | string

## Example

```typescript
import type { ContractExtractRequest } from '@xr7/sdk'

// Example values shown below; adjust for your use case
const example = {
  "contractId": null,
  "contractText": null,
  "effectiveStart": null,
  "effectiveEnd": null,
  "extractedFrom": null,
} satisfies ContractExtractRequest

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as ContractExtractRequest
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


