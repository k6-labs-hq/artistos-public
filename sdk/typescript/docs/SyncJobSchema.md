
# SyncJobSchema


## Properties

Name | Type
------------ | -------------
`id` | string
`artistId` | string
`integration` | string
`status` | string
`attempts` | number
`maxAttempts` | number
`lastError` | string
`payloadJson` | string
`resultJson` | string
`queueBackend` | string
`lastTaskId` | string
`enqueuedAt` | Date
`nextRunAt` | Date
`startedAt` | Date
`completedAt` | Date
`createdAt` | Date
`updatedAt` | Date

## Example

```typescript
import type { SyncJobSchema } from '@xr7/sdk'

// TODO: Update the object below with actual values
const example = {
  "id": null,
  "artistId": null,
  "integration": null,
  "status": null,
  "attempts": null,
  "maxAttempts": null,
  "lastError": null,
  "payloadJson": null,
  "resultJson": null,
  "queueBackend": null,
  "lastTaskId": null,
  "enqueuedAt": null,
  "nextRunAt": null,
  "startedAt": null,
  "completedAt": null,
  "createdAt": null,
  "updatedAt": null,
} satisfies SyncJobSchema

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as SyncJobSchema
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


