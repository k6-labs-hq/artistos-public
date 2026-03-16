
# CurrencyTaxEstimateRequest


## Properties

Name | Type
------------ | -------------
`grossAmount` | number
`sourceCurrency` | string
`payoutCurrency` | string
`fxRate` | number
`withholdingRate` | number

## Example

```typescript
import type { CurrencyTaxEstimateRequest } from '@xr7/sdk'

// Example values shown below; adjust for your use case
const example = {
  "grossAmount": null,
  "sourceCurrency": null,
  "payoutCurrency": null,
  "fxRate": null,
  "withholdingRate": null,
} satisfies CurrencyTaxEstimateRequest

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as CurrencyTaxEstimateRequest
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


