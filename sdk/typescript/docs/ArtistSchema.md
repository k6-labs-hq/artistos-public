
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
`firstName` | string
`lastName` | string
`countryCode` | string
`trolleyRecipientId` | string
`payoutAccountStatus` | string
`payoutMethodType` | string
`payoutLast4` | string
`taxFormStatus` | string
`defaultAttorneyGracePeriodDays` | number
`primaryJurisdiction` | string
`preferredContractType` | string
`xr7FutureLeakagePrevented` | number
`isFounder` | boolean
`founderSlotNumber` | number
`founderLockedAt` | Date
`contingencyFeePercent` | number
`primaryVertical` | string
`tvfilmRole` | string
`organizationType` | string
`enterpriseModeEnabled` | boolean

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
  "firstName": null,
  "lastName": null,
  "countryCode": null,
  "trolleyRecipientId": null,
  "payoutAccountStatus": null,
  "payoutMethodType": null,
  "payoutLast4": null,
  "taxFormStatus": null,
  "defaultAttorneyGracePeriodDays": null,
  "primaryJurisdiction": null,
  "preferredContractType": null,
  "xr7FutureLeakagePrevented": null,
  "isFounder": null,
  "founderSlotNumber": null,
  "founderLockedAt": null,
  "contingencyFeePercent": null,
  "primaryVertical": null,
  "tvfilmRole": null,
  "organizationType": null,
  "enterpriseModeEnabled": null,
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


