
# AdvanceOfferRequest


## Properties

Name | Type
------------ | -------------
`predictedLowForecast` | number
`currency` | string
`advanceFeePct` | number

## Example

```typescript
import type { AdvanceOfferRequest } from '@xr7/sdk'

// TODO: Update the object below with actual values
const example = {
  "predictedLowForecast": null,
  "currency": null,
  "advanceFeePct": null,
} satisfies AdvanceOfferRequest

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as AdvanceOfferRequest
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


