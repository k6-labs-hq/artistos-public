
# XR7ApiRoutersXr7ValuationForecastRequest


## Properties

Name | Type
------------ | -------------
`tenantId` | string
`horizonDays` | number
`scenarioOverrides` | { [key: string]: any; }

## Example

```typescript
import type { XR7ApiRoutersXr7ValuationForecastRequest } from '@xr7/sdk'

// TODO: Update the object below with actual values
const example = {
  "tenantId": null,
  "horizonDays": null,
  "scenarioOverrides": null,
} satisfies XR7ApiRoutersXr7ValuationForecastRequest

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as XR7ApiRoutersXr7ValuationForecastRequest
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


