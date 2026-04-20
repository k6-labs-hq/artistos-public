
# UtilityRankRequest


## Properties

Name | Type
------------ | -------------
`items` | Array&lt;{ [key: string]: any; }&gt;
`analystHourlyCost` | number

## Example

```typescript
import type { UtilityRankRequest } from '@xr7/sdk'

// TODO: Update the object below with actual values
const example = {
  "items": null,
  "analystHourlyCost": null,
} satisfies UtilityRankRequest

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as UtilityRankRequest
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)
