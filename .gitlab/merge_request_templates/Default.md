## Status

Ready

## Aha/Jira/Trello Reference

https://eleven.aha.io/features/DEOP-263

## Description

On origin response security headers for secure.guestinternet.com for Cloudfront Distribution ES0G8W1ZPTB5R secure.guestinternet.com.  Replacing arn:aws:lambda:us-east-1:615423619382:function:cloudfront-edge-OnOriginResponse-19X3WD0INPIOJ:2 Cloudfront Lambda@edge


## Risk

medium

- Performance (DB, etc.)
Saves money

- Security / Compliance
Applies Security Headers

## Test plan:

Verify headers match what is currently implemented by the Lambda@edge.
Verify Securityheaders.com reports an A

## Deployment Todos

- Run [erad-frmod-ci-director](https://ci.gd1.io/job/erad-frmod-ci-director/)

## Rollback plan
- Revert changes
- run [erad-frmod-ci-director](https://ci.gd1.io/job/erad-frmod-ci-director/)
Template example above, just copy paste it