
# TVFilmForecastRequest


## Properties

Name | Type
------------ | -------------
`anomalyIds` | Array&lt;string&gt;
`confidenceOverride` | number

## Example

```typescript
import type { TVFilmForecastRequest } from '@xr7/sdk'

// TODO: Update the object below with actual values
const example = {
  "anomalyIds": null,
  "confidenceOverride": null,
} satisfies TVFilmForecastRequest

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as TVFilmForecastRequest
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)
