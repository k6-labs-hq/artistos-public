
# DecideReviewItemRequest


## Properties

Name | Type
------------ | -------------
`decision` | [ReviewDecisionType](ReviewDecisionType.md)
`notes` | string

## Example

```typescript
import type { DecideReviewItemRequest } from '@xr7/sdk'

// Example values shown below; adjust for your use case
const example = {
  "decision": null,
  "notes": null,
} satisfies DecideReviewItemRequest

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as DecideReviewItemRequest
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


