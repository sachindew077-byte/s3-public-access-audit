import boto3
import json
import os
from botocore.exceptions import ClientError

s3 = boto3.client("s3")
sns = boto3.client("sns")

SNS_TOPIC_ARN = os.environ["SNS_TOPIC_ARN"]


def lambda_handler(event, context):

    public_buckets = []

    response = s3.list_buckets()

    for bucket in response["Buckets"]:

        bucket_name = bucket["Name"]

        print(f"Checking bucket: {bucket_name}")

        is_public = False
        reasons = []

        # Check Block Public Access

        try:
            pab = s3.get_public_access_block(
                Bucket=bucket_name
            )

            config = pab["PublicAccessBlockConfiguration"]

            if not all(config.values()):
                is_public = True
                reasons.append(
                    "Block Public Access is disabled"
                )

        except ClientError as e:

            if e.response["Error"]["Code"] == \
                    "NoSuchPublicAccessBlockConfiguration":

                is_public = True
                reasons.append(
                    "No Public Access Block configuration"
                )

        # Check bucket policy

        try:

            policy_status = s3.get_bucket_policy_status(
                Bucket=bucket_name
            )

            if policy_status["PolicyStatus"]["IsPublic"]:
                is_public = True
                reasons.append(
                    "Bucket policy is public"
                )

        except ClientError:
            pass

        # Check ACLs

        try:

            acl = s3.get_bucket_acl(
                Bucket=bucket_name
            )

            for grant in acl["Grants"]:

                grantee = grant.get("Grantee", {})

                uri = grantee.get("URI", "")

                if (
                    "AllUsers" in uri or
                    "AuthenticatedUsers" in uri
                ):
                    is_public = True
                    reasons.append(
                        "Public ACL detected"
                    )

        except ClientError:
            pass

        if is_public:

            public_buckets.append(
                {
                    "bucket": bucket_name,
                    "reasons": reasons
                }
            )

    if public_buckets:

        message = json.dumps(
            public_buckets,
            indent=2
        )

        sns.publish(
            TopicArn=SNS_TOPIC_ARN,
            Subject="S3 Public Bucket Alert",
            Message=message
        )

        print("SNS alert sent")

    else:

        print(
            "No public buckets found"
        )

    return {
        "statusCode": 200,
        "public_buckets": public_buckets
    }