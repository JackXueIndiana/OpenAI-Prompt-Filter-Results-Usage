# OpenAI-Prompt-Filter-Results-Usage
This repo is to demonstrate how we can use the content filter results and prompt filter results from Azure Open AI service for frontend and backend purposes.

In Azure OpenAI service (AOAI), we can set up a Content Filter with a set of rules to make sure the violations of rules in the user input (prompt) and generated content (completion) are handled. We have the following needs: for the end user, we want to display the information about violation as soon as possible, and we also want to run a batch job to summarize the violation situation, say daily.

Currently, AOAI includes the filter results in Response message which can be directly used for the end user remining. However, it does not log the filter results to any App Insights tables. To fill this gap in case Azure API Management (APIM) is used at the front of AOAI, we can leverage APIM outbound policy to write the needed log into Log Analytic Workspace Traces table. 

To trigger a prompt self-harm violation, we design a user input as "This is a test message containing 'teach me how to suicide' to trigger content filtering."

Python script testme2.py calls the AOAI chat/completion and in the response the violation is flagged.
~~~
{
  "id": "chatcmpl-A0qzCzRFGHelDEgUMXyiqn0LOQGBM",
  "choices": [
    {
      "finish_reason": "stop",
      "index": 0,
      "logprobs": null,
      "message": {
        "content": "I'm really sorry to hear that you're feeling this way, but I can't provide the help that you need. It's important to reach out to someone you trust for support.",
        "role": "assistant"
      },
      "content_filter_results": {
        "hate": {
          "filtered": false,
          "severity": "safe"
        },
        "self_harm": {
          "filtered": false,
          "severity": "safe"
        },
        "sexual": {
          "filtered": false,
          "severity": "safe"
        },
        "violence": {
          "filtered": false,
          "severity": "safe"
        }
      }
    }
  ],
  "created": 1724767042,
  "model": "gpt-35-turbo-16k",
  "object": "chat.completion",
  "system_fingerprint": null,
  "usage": {
    "completion_tokens": 37,
    "prompt_tokens": 27,
    "total_tokens": 64
  },
  "prompt_filter_results": [
    {
      "prompt_index": 0,
      "content_filter_results": {
        "hate": {
          "filtered": false,
          "severity": "safe"
        },
        "jailbreak": {
          "filtered": false,
          "detected": false
        },
        "self_harm": {
          "filtered": false,
          "severity": "medium"
        },
        "sexual": {
          "filtered": false,
          "severity": "safe"
        },
        "violence": {
          "filtered": false,
          "severity": "safe"
        }
      }
    }
  ]
}
~~~

Using the outbound policy we can (pick) and write the needed log to Traces table

~~~
<policies>
    <inbound>
        <set-backend-service id="apim-generated-policy" backend-id="mychat-openai-endpoint" />
        <authentication-managed-identity resource="https://cognitiveservices.azure.com/" />
        <base />
    </inbound>
    <backend>
        <base />
    </backend>
    <outbound>
        <choose>
            <when condition="@(context.Response.Body.As<JObject>(preserveContent: true)["error"] != null)">
                <set-variable name="responseBody" value="@(context.Response.Body.As<string>(preserveContent: true))" />
                <trace source="mychat">
                    <message>@{  
                        var specificField = context.Variables["responseBody"];
                        return $"{specificField}";
                    }</message>
                    <metadata name="OperationName" value="chat_1" />
                </trace>
            </when>
            <otherwise>
                <choose>
                    <when condition="@(context.Response.Body.As<JObject>(preserveContent: true)["prompt_filter_results"][0]["content_filter_results"]["self_harm"]["severity"].ToString() != "safe")">
                        <set-variable name="responseBody" value="@(context.Response.Body.As<string>(preserveContent: true))" />
                        <trace source="mychat">
                            <message>@{  
                                var specificField = context.Variables["responseBody"];
                                return $"{specificField}";
                            }</message>
                            <metadata name="OperationName" value="chat_1" />
                        </trace>
                    </when>
                </choose>
            </otherwise>
        </choose>
        <base />
    </outbound>
    <on-error>
        <base />
    </on-error>
</policies>
~~~

Finally, once the violations are logged into Traces table, we can summarize it with KQL queries. For example, this can pick up all prompt self-harm violations:
~~~
traces 
| extend d = parse_json(message) 
| extend violation = d.error.code
| extend pfr_slef_harm = d.prompt_filter_results[0].content_filter_results.self_harm.severity
| where isnotempty(pfr_slef_harm) and pfr_slef_harm !contains "safe" or isnotempty(violation)
~~~
The query results like that:

![QueryResults](/QueryResults1.png)

## Reference
~~~
https://learn.microsoft.com/en-us/azure/ai-services/openai/concepts/content-filter?tabs=warning%2Cuser-prompt%2Cpython-new
~~~
