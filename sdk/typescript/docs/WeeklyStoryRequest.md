
# WeeklyStoryRequest


## Properties

Name | Type
------------ | -------------
`totalRecovered` | number
`totalRecoverable` | number
`newAnomalies` | number
`claimsProgressed` | number
`deposits` | Array&lt;{ [key: string]: any; }&gt;
`currency` | string

## Example

```typescript
import type { WeeklyStoryRequest } from '@xr7/sdk'

// TODO: Update the object below with actual values
const example = {
  "totalRecovered": null,
  "totalRecoverable": null,
  "newAnomalies": null,
  "claimsProgressed": null,
  "deposits": null,
  "currency": null,
} satisfies WeeklyStoryRequest

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as WeeklyStoryRequest
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


