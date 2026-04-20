
# MetadataRepairApplyRequest


## Properties

Name | Type
------------ | -------------
`tenantId` | string
`suggestionIds` | Array&lt;string&gt;
`dryRun` | boolean

## Example

```typescript
import type { MetadataRepairApplyRequest } from '@xr7/sdk'

// TODO: Update the object below with actual values
const example = {
  "tenantId": null,
  "suggestionIds": null,
  "dryRun": null,
} satisfies MetadataRepairApplyRequest

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as MetadataRepairApplyRequest
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)
