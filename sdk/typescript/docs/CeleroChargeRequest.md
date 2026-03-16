
# CeleroChargeRequest

Charge the artist\'s Celero vault for a specific claim\'s contingency fee.

## Properties

Name | Type
------------ | -------------
`claimId` | string
`ipAddress` | string

## Example

```typescript
import type { CeleroChargeRequest } from '@xr7/sdk'

// Example values shown below; adjust for your use case
const example = {
  "claimId": null,
  "ipAddress": null,
} satisfies CeleroChargeRequest

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as CeleroChargeRequest
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


