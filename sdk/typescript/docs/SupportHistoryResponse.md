
# SupportHistoryResponse


## Properties

Name | Type
------------ | -------------
`total` | number
`page` | number
`pageSize` | number
`nextCursor` | string
`items` | [Array&lt;SupportMessageView&gt;](SupportMessageView.md)

## Example

```typescript
import type { SupportHistoryResponse } from '@xr7/sdk'

// TODO: Update the object below with actual values
const example = {
  "total": null,
  "page": null,
  "pageSize": null,
  "nextCursor": null,
  "items": null,
} satisfies SupportHistoryResponse

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as SupportHistoryResponse
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)
