
# ReviewItemSchema


## Properties

Name | Type
------------ | -------------
`id` | string
`artistId` | string
`sourceType` | string
`sourceId` | string
`reason` | string
`priorityScore` | number
`status` | [ReviewItemStatus](ReviewItemStatus.md)
`assignedAnalystEmail` | string
`payload` | { [key: string]: any; }
`createdAt` | Date
`updatedAt` | Date
`resolvedAt` | Date

## Example

```typescript
import type { ReviewItemSchema } from '@xr7/sdk'

// TODO: Update the object below with actual values
const example = {
  "id": null,
  "artistId": null,
  "sourceType": null,
  "sourceId": null,
  "reason": null,
  "priorityScore": null,
  "status": null,
  "assignedAnalystEmail": null,
  "payload": null,
  "createdAt": null,
  "updatedAt": null,
  "resolvedAt": null,
} satisfies ReviewItemSchema

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as ReviewItemSchema
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


