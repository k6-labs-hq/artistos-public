
# TeamMemberSchema


## Properties

Name | Type
------------ | -------------
`id` | string
`artistId` | string
`userEmail` | string
`role` | [TeamRole](TeamRole.md)
`createdAt` | Date

## Example

```typescript
import type { TeamMemberSchema } from '@xr7/sdk'

// TODO: Update the object below with actual values
const example = {
  "id": null,
  "artistId": null,
  "userEmail": null,
  "role": null,
  "createdAt": null,
} satisfies TeamMemberSchema

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as TeamMemberSchema
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)
