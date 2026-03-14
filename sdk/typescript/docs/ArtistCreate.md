
# ArtistCreate


## Properties

Name | Type
------------ | -------------
`name` | string
`email` | string
`role` | string
`ipiNumber` | string
`stageNames` | Array&lt;string&gt;

## Example

```typescript
import type { ArtistCreate } from '@xr7/sdk'

// TODO: Update the object below with actual values
const example = {
  "name": null,
  "email": null,
  "role": null,
  "ipiNumber": null,
  "stageNames": null,
} satisfies ArtistCreate

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as ArtistCreate
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


