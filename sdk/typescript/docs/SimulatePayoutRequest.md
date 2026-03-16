
# SimulatePayoutRequest


## Properties

Name | Type
------------ | -------------
`usageRows` | Array&lt;{ [key: string]: any; }&gt;
`fallbackRate` | number
`defaultWithholdingRate` | number
`defaultFxRate` | number
`payoutCurrency` | string
`receivedAmount` | number
`contractTerms` | { [key: string]: any; }

## Example

```typescript
import type { SimulatePayoutRequest } from '@xr7/sdk'

// Example values shown below; adjust for your use case
const example = {
  "usageRows": null,
  "fallbackRate": null,
  "defaultWithholdingRate": null,
  "defaultFxRate": null,
  "payoutCurrency": null,
  "receivedAmount": null,
  "contractTerms": null,
} satisfies SimulatePayoutRequest

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as SimulatePayoutRequest
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


