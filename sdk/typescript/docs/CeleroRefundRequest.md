
# CeleroRefundRequest

Refund a previous charge, optionally for a partial amount.

## Properties

Name | Type
------------ | -------------
`amount` | number

## Example

```typescript
import type { CeleroRefundRequest } from '@xr7/sdk'

// Example values shown below; adjust for your use case
const example = {
  "amount": null,
} satisfies CeleroRefundRequest

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as CeleroRefundRequest
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


