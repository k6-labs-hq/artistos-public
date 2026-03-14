
# AnomalySchema


## Properties

Name | Type
------------ | -------------
`id` | string
`artistId` | string
`category` | [AnomalyCategory](AnomalyCategory.md)
`subtype` | string
`severity` | [AnomalySeverity](AnomalySeverity.md)
`expectedAmount` | number
`actualAmount` | number
`estimatedRecoverable` | number
`confidenceScore` | number
`timeWindowStart` | Date
`timeWindowEnd` | Date
`territory` | string
`status` | [AnomalyStatus](AnomalyStatus.md)
`description` | string
`anomalyScore` | number
`modelVersion` | string
`featureSnapshot` | string
`createdAt` | Date

## Example

```typescript
import type { AnomalySchema } from '@xr7/sdk'

// TODO: Update the object below with actual values
const example = {
  "id": null,
  "artistId": null,
  "category": null,
  "subtype": null,
  "severity": null,
  "expectedAmount": null,
  "actualAmount": null,
  "estimatedRecoverable": null,
  "confidenceScore": null,
  "timeWindowStart": null,
  "timeWindowEnd": null,
  "territory": null,
  "status": null,
  "description": null,
  "anomalyScore": null,
  "modelVersion": null,
  "featureSnapshot": null,
  "createdAt": null,
} satisfies AnomalySchema

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as AnomalySchema
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


