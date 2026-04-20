
# IdentityDecisionRequest


## Properties

Name | Type
------------ | -------------
`decision` | [IdentityDecisionStatus](IdentityDecisionStatus.md)
`actor` | string
`reason` | string

## Example

```typescript
import type { IdentityDecisionRequest } from '@xr7/sdk'

// TODO: Update the object below with actual values
const example = {
  "decision": null,
  "actor": null,
  "reason": null,
} satisfies IdentityDecisionRequest

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as IdentityDecisionRequest
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)
