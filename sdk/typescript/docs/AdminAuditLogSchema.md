
# AdminAuditLogSchema


## Properties

Name | Type
------------ | -------------
`id` | string
`actor` | string
`action` | string
`resourceType` | string
`resourceId` | string
`details` | { [key: string]: any; }
`createdAt` | Date

## Example

```typescript
import type { AdminAuditLogSchema } from '@xr7/sdk'

// TODO: Update the object below with actual values
const example = {
  "id": null,
  "actor": null,
  "action": null,
  "resourceType": null,
  "resourceId": null,
  "details": null,
  "createdAt": null,
} satisfies AdminAuditLogSchema

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as AdminAuditLogSchema
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


