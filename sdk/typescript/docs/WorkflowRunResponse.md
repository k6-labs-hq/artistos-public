
# WorkflowRunResponse


## Properties

Name | Type
------------ | -------------
`artistId` | string
`runId` | string
`status` | string
`statusUrl` | string
`branding` | { [key: string]: any; }

## Example

```typescript
import type { WorkflowRunResponse } from '@xr7/sdk'

// TODO: Update the object below with actual values
const example = {
  "artistId": null,
  "runId": null,
  "status": null,
  "statusUrl": null,
  "branding": null,
} satisfies WorkflowRunResponse

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as WorkflowRunResponse
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


