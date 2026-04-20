
# CatalogConfirmationSchema


## Properties

Name | Type
------------ | -------------
`id` | string
`artistId` | string
`workId` | string
`ownershipConfirmed` | string
`splitsConfirmed` | string
`publisherConfirmed` | string
`adminConfirmed` | string
`correctionNotes` | string
`confirmedAt` | Date

## Example

```typescript
import type { CatalogConfirmationSchema } from '@xr7/sdk'

// TODO: Update the object below with actual values
const example = {
  "id": null,
  "artistId": null,
  "workId": null,
  "ownershipConfirmed": null,
  "splitsConfirmed": null,
  "publisherConfirmed": null,
  "adminConfirmed": null,
  "correctionNotes": null,
  "confirmedAt": null,
} satisfies CatalogConfirmationSchema

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as CatalogConfirmationSchema
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)
