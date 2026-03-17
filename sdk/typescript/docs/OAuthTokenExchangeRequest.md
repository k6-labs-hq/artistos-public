
# OAuthTokenExchangeRequest


## Properties

Name | Type
------------ | -------------
`state` | string
`code` | string
`externalAccountId` | string
`tenantId` | string
`grantedScopes` | Array&lt;string&gt;
`allowPartialScopeGrant` | boolean
`accessToken` | string
`refreshToken` | string
`tokenType` | string
`expiresInSeconds` | number
`displayName` | string
`profileMetadata` | { [key: string]: string; }

## Example

```typescript
import type { OAuthTokenExchangeRequest } from '@xr7/sdk'

// TODO: Update the object below with actual values
const example = {
  "state": null,
  "code": null,
  "externalAccountId": null,
  "tenantId": null,
  "grantedScopes": null,
  "allowPartialScopeGrant": null,
  "accessToken": null,
  "refreshToken": null,
  "tokenType": null,
  "expiresInSeconds": null,
  "displayName": null,
  "profileMetadata": null,
} satisfies OAuthTokenExchangeRequest

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as OAuthTokenExchangeRequest
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


