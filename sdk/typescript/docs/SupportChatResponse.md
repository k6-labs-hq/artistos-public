
# SupportChatResponse


## Properties

Name | Type
------------ | -------------
`artistId` | string
`threadId` | string
`response` | string
`confidence` | number
`suggestedQuickReplies` | Array&lt;string&gt;
`escalateRecommended` | boolean

## Example

```typescript
import type { SupportChatResponse } from '@xr7/sdk'

// TODO: Update the object below with actual values
const example = {
  "artistId": null,
  "threadId": null,
  "response": null,
  "confidence": null,
  "suggestedQuickReplies": null,
  "escalateRecommended": null,
} satisfies SupportChatResponse

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as SupportChatResponse
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)
