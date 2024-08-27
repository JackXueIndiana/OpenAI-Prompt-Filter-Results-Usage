# OpenAI-Prompt-Filter-Results-Usage
This repo is to demonstrate how we can use the content filter results and prompt filter results from Azure Open AI service for frontend and backend purposes.

In Azure OpenAI service (AOAI), we can set up a Content Filter with a set of rules to make sure the violations of rules in the user input (prompt) and generated content (completion) are handeled. We have the folloiwng needs: for the end user, we want to dispaly the inforamtion about violation as soon as possible, and we also want to run a batch job to sumarize the violation situation, say daily.

Currently, AOAI includes the filter results in Response message which can be diretly used for the end user remining. However, it does not log the filter results to any App Insights tables. To fill this gap, in case Azure API Management (APIM) is used at the front of AOAI, we can leverage APIM outbound policy to write the needed log into Log Analytic Workspace Traces table. 
