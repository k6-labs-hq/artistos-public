
# ReviewAssignmentSchema


## Properties

Name | Type
------------ | -------------
`id` | string
`reviewItemId` | string
`analystEmail` | string
`assignedAt` | Date
`unassignedAt` | Date

## Example

```typescript
import type { ReviewAssignmentSchema } from '@xr7/sdk'

// Example values shown below; adjust for your use case
const example = {
  "id": null,
  "reviewItemId": null,
  "analystEmail": null,
  "assignedAt": null,
  "unassignedAt": null,
} satisfies ReviewAssignmentSchema

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as ReviewAssignmentSchema
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


