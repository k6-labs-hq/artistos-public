# xr7_sdk.PayersApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**payer_behavior_payers_payer_id_behavior_get**](PayersApi.md#payer_behavior_payers_payer_id_behavior_get) | **GET** /payers/{payer_id}/behavior | Payer Behavior
[**payer_risk_payers_payer_id_risk_get**](PayersApi.md#payer_risk_payers_payer_id_risk_get) | **GET** /payers/{payer_id}/risk | Payer Risk


# **payer_behavior_payers_payer_id_behavior_get**
> object payer_behavior_payers_payer_id_behavior_get(payer_id)

Payer Behavior

### Example


```python
import xr7_sdk
from xr7_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = xr7_sdk.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with xr7_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = xr7_sdk.PayersApi(api_client)
    payer_id = 'payer_id_example' # str |

    try:
        # Payer Behavior
        api_response = api_instance.payer_behavior_payers_payer_id_behavior_get(payer_id)
        print("The response of PayersApi->payer_behavior_payers_payer_id_behavior_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PayersApi->payer_behavior_payers_payer_id_behavior_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **payer_id** | **str**|  |

### Return type

**object**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **payer_risk_payers_payer_id_risk_get**
> object payer_risk_payers_payer_id_risk_get(payer_id)

Payer Risk

### Example


```python
import xr7_sdk
from xr7_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = xr7_sdk.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with xr7_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = xr7_sdk.PayersApi(api_client)
    payer_id = 'payer_id_example' # str |

    try:
        # Payer Risk
        api_response = api_instance.payer_risk_payers_payer_id_risk_get(payer_id)
        print("The response of PayersApi->payer_risk_payers_payer_id_risk_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PayersApi->payer_risk_payers_payer_id_risk_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **payer_id** | **str**|  |

### Return type

**object**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)
