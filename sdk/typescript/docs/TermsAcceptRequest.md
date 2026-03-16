
# TermsAcceptRequest

Body for POST /artists/{artist_id}/terms/accept.  ``terms_version`` must match the version the server returns from GET /terms.  This prevents a client that cached an old version of the T&C from accidentally accepting stale terms.

## Properties

Name | Type
------------ | -------------
`termsVersion` | string
`agreed` | boolean

## Example

```typescript
import type { TermsAcceptRequest } from '@xr7/sdk'

// Example values shown below; adjust for your use case
const example = {
  "termsVersion": null,
  "agreed": null,
} satisfies TermsAcceptRequest

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as TermsAcceptRequest
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


