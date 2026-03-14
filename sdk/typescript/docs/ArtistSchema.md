
# ArtistSchema


## Properties

Name | Type
------------ | -------------
`id` | string
`name` | string
`email` | string
`role` | string
`ipiNumber` | string
`stageNames` | Array&lt;string&gt;
`createdAt` | Date
`status` | [ArtistLifecycleStatus](ArtistLifecycleStatus.md)
`onboardedAt` | Date
`activatedAt` | Date
`celeroCustomerVaultId` | string

## Example

```typescript
import type { ArtistSchema } from '@xr7/sdk'

// TODO: Update the object below with actual values
const example = {
  "id": null,
  "name": null,
  "email": null,
  "role": null,
  "ipiNumber": null,
  "stageNames": null,
  "createdAt": null,
  "status": null,
  "onboardedAt": null,
  "activatedAt": null,
  "celeroCustomerVaultId": null,
} satisfies ArtistSchema

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as ArtistSchema
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


