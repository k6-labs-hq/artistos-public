
# SplitRepairRequest


## Properties

Name | Type
------------ | -------------
`rightsRows` | Array&lt;{ [key: string]: any; }&gt;
`payoutRows` | Array&lt;{ [key: string]: any; }&gt;
`applyThreshold` | number

## Example

```typescript
import type { SplitRepairRequest } from '@xr7/sdk'

// TODO: Update the object below with actual values
const example = {
  "rightsRows": null,
  "payoutRows": null,
  "applyThreshold": null,
} satisfies SplitRepairRequest

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as SplitRepairRequest
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


