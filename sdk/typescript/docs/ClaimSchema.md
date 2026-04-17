
# ClaimSchema


## Properties

Name | Type
------------ | -------------
`id` | string
`artistId` | string
`anomalyId` | string
`claimType` | string
`status` | [ClaimStatus](ClaimStatus.md)
`recoveredAmount` | number
`currency` | string
`contingencyFee` | number
`platformFeePercent` | number
`platformFeeAmount` | number
`artistNetAmount` | number
`remittanceMethod` | string
`remittanceReferenceNumber` | string
`remittanceReceivedAt` | Date
`trolleyPaymentId` | string
`trolleyPaymentStatus` | string
`trolleyFxRate` | number
`trolleyLocalAmount` | number
`trolleyLocalCurrency` | string
`payoutRetryCount` | number
`payoutFailureReason` | string
`evidence` | { [key: string]: any; }
`payerName` | string
`payerContact` | string
`originalDueDate` | Date
`proofSubmittedAt` | Date
`gracePeriodDays` | number
`solDeadline` | Date
`governingLawState` | string
`contractType` | string
`infringementDate` | Date
`discoveryDate` | Date
`solWindowYears` | number
`solCitationSource` | string
`communications` | Array&lt;{ [key: string]: any; }&gt;
`anomalyReport` | { [key: string]: any; }
`supportingDocuments` | Array&lt;{ [key: string]: any; }&gt;
`attorneyFileGenerated` | boolean
`attorneyFileGeneratedAt` | Date
`createdAt` | Date
`updatedAt` | Date

## Example

```typescript
import type { ClaimSchema } from '@xr7/sdk'

// TODO: Update the object below with actual values
const example = {
  "id": null,
  "artistId": null,
  "anomalyId": null,
  "claimType": null,
  "status": null,
  "recoveredAmount": null,
  "currency": null,
  "contingencyFee": null,
  "platformFeePercent": null,
  "platformFeeAmount": null,
  "artistNetAmount": null,
  "remittanceMethod": null,
  "remittanceReferenceNumber": null,
  "remittanceReceivedAt": null,
  "trolleyPaymentId": null,
  "trolleyPaymentStatus": null,
  "trolleyFxRate": null,
  "trolleyLocalAmount": null,
  "trolleyLocalCurrency": null,
  "payoutRetryCount": null,
  "payoutFailureReason": null,
  "evidence": null,
  "payerName": null,
  "payerContact": null,
  "originalDueDate": null,
  "proofSubmittedAt": null,
  "gracePeriodDays": null,
  "solDeadline": null,
  "governingLawState": null,
  "contractType": null,
  "infringementDate": null,
  "discoveryDate": null,
  "solWindowYears": null,
  "solCitationSource": null,
  "communications": null,
  "anomalyReport": null,
  "supportingDocuments": null,
  "attorneyFileGenerated": null,
  "attorneyFileGeneratedAt": null,
  "createdAt": null,
  "updatedAt": null,
} satisfies ClaimSchema

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as ClaimSchema
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)
