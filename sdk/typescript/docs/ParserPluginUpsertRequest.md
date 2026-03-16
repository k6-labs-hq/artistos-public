
# ParserPluginUpsertRequest


## Properties

Name | Type
------------ | -------------
`parserType` | string
`pluginName` | string
`pluginEntrypoint` | string
`pluginSignature` | string
`enabled` | boolean

## Example

```typescript
import type { ParserPluginUpsertRequest } from '@xr7/sdk'

// Example values shown below; adjust for your use case
const example = {
  "parserType": null,
  "pluginName": null,
  "pluginEntrypoint": null,
  "pluginSignature": null,
  "enabled": null,
} satisfies ParserPluginUpsertRequest

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as ParserPluginUpsertRequest
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


