# Audit S3 Buckets for Public Access and Notify

## Objective

Detect publicly accessible S3 buckets and send alerts via Amazon SNS.

## AWS Services Used

- Amazon S3
- AWS Lambda (Python 3.12)
- Amazon SNS
- Amazon EventBridge
- Amazon CloudWatch
- IAM

## Features

- Lists all S3 buckets in the account.
- Checks Block Public Access configuration.
- Checks bucket policy status.
- Checks ACL grants.
- Sends an SNS notification if a bucket is public.
- Runs automatically every day using EventBridge.

## Architecture

EventBridge → Lambda → S3 Audit → SNS → Email

## IAM Permissions

- s3:ListAllMyBuckets
- s3:GetBucketPublicAccessBlock
- s3:GetBucketPolicyStatus
- s3:GetBucketAcl
- sns:Publish

## Testing

1. Disabled Block Public Access on a test bucket.
2. Added a public-read bucket policy.
3. Triggered the Lambda function manually.
4. Verified that an SNS email alert was received.
5. Re-enabled Block Public Access and removed the bucket policy.

## Discussion

Amazon S3 provides built-in Block Public Access controls and organization-wide policies to prevent accidental exposure.

Lambda is preferred when custom security checks, centralized notifications, compliance requirements, or integrations with other AWS services are needed.

## Screenshots

- SNS topic and email subscription
- IAM role and policy
- Lambda code
- Lambda execution
- CloudWatch logs
- EventBridge schedule
- Email alert

                    EventBridge
                   (Daily Trigger)
                          │
                          ▼
                ┌──────────────────┐
                │   AWS Lambda     │
                │   S3 Auditor     │
                └────────┬─────────┘
                         │
         ┌───────────────┼───────────────┐
         │               │               │
         ▼               ▼               ▼

  Check Public     Check Bucket    Check ACL
  Access Block      Policy Status   Grants

         └───────────────┼───────────────┘
                         │
             Public bucket detected?
                         │
                    Yes ─┘
                         ▼
                  Amazon SNS
                         │
                         ▼
                     Email Alert
