
# ArtistPreferenceUpdateRequest


## Properties

Name | Type
------------ | -------------
`defaultAttorneyGracePeriodDays` | number
`primaryJurisdiction` | string
`preferredContractType` | string

## Example

```typescript
import type { ArtistPreferenceUpdateRequest } from '@xr7/sdk'

// TODO: Update the object below with actual values
const example = {
  "defaultAttorneyGracePeriodDays": null,
  "primaryJurisdiction": null,
  "preferredContractType": null,
} satisfies ArtistPreferenceUpdateRequest

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as ArtistPreferenceUpdateRequest
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)
