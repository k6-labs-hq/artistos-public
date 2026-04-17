
# ParserPluginSchema


## Properties

Name | Type
------------ | -------------
`id` | string
`artistId` | string
`parserType` | string
`pluginName` | string
`pluginEntrypoint` | string
`pluginSignature` | string
`enabled` | boolean
`createdAt` | Date
`updatedAt` | Date

## Example

```typescript
import type { ParserPluginSchema } from '@xr7/sdk'

// TODO: Update the object below with actual values
const example = {
  "id": null,
  "artistId": null,
  "parserType": null,
  "pluginName": null,
  "pluginEntrypoint": null,
  "pluginSignature": null,
  "enabled": null,
  "createdAt": null,
  "updatedAt": null,
} satisfies ParserPluginSchema

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as ParserPluginSchema
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)
