
# NotificationPreferenceSchema


## Properties

Name | Type
------------ | -------------
`id` | string
`artistId` | string
`email` | string
`phone` | string
`notifyAnomalyDetected` | boolean
`notifyUrgentSol` | boolean
`notifyDepositReceived` | boolean
`notifyClaimAdvanced` | boolean
`quietHoursStart` | string
`quietHoursEnd` | string
`createdAt` | Date
`updatedAt` | Date

## Example

```typescript
import type { NotificationPreferenceSchema } from '@xr7/sdk'

// TODO: Update the object below with actual values
const example = {
  "id": null,
  "artistId": null,
  "email": null,
  "phone": null,
  "notifyAnomalyDetected": null,
  "notifyUrgentSol": null,
  "notifyDepositReceived": null,
  "notifyClaimAdvanced": null,
  "quietHoursStart": null,
  "quietHoursEnd": null,
  "createdAt": null,
  "updatedAt": null,
} satisfies NotificationPreferenceSchema

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as NotificationPreferenceSchema
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


