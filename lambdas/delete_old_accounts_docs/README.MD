# ESImport Delete old docs
### What we need to achieve ?
The docs in `account` index has to be deleted that are older than 18 months.

### How it works ?
We use lambda & cloudwatch events to achieve this.

The `template.yaml` is a SAM template that deploys the lambda function plus cloudwatch events rule that we use to trigger the lambda function every week. 

### How to deploy ?
1. Execute `deploy.sh` script. Check script file for parameters.
2. After deploying the stack, we need to add the DeleteDocs lambda role to the ES cluster's domain access policy allow list.