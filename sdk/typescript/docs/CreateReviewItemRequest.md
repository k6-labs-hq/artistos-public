
# CreateReviewItemRequest


## Properties

Name | Type
------------ | -------------
`artistId` | string
`sourceType` | [ReviewSourceType](ReviewSourceType.md)
`sourceId` | string
`reason` | string
`priorityScore` | number
`payload` | { [key: string]: any; }

## Example

```typescript
import type { CreateReviewItemRequest } from '@xr7/sdk'

// Example values shown below; adjust for your use case
const example = {
  "artistId": null,
  "sourceType": null,
  "sourceId": null,
  "reason": null,
  "priorityScore": null,
  "payload": null,
} satisfies CreateReviewItemRequest

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as CreateReviewItemRequest
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


