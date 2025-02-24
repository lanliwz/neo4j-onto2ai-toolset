from typing import List
import os

import boto3  # type: ignore


def list_gcs_buckets(
    google_access_key_id: str, google_access_key_secret: str
) -> List[str]:
    """Lists all Cloud Storage buckets using AWS SDK for Python (boto3)
    Positional arguments:
        google_access_key_id: hash-based message authentication code (HMAC) access ID
        google_access_key_secret: HMAC access secret

    Returned value is a list of strings, one for each bucket name.

    To use this sample:
    1. Create a Cloud Storage HMAC key: https://cloud.google.com/storage/docs/authentication/managing-hmackeys#create
    2. Change endpoint_url to a Google Cloud Storage XML API endpoint.

    To learn more about HMAC: https://cloud.google.com/storage/docs/authentication/hmackeys#overview
    """
    client = boto3.client(
        "s3",
        region_name="auto",
        endpoint_url="https://storage.googleapis.com",
        aws_access_key_id=google_access_key_id,
        aws_secret_access_key=google_access_key_secret,
    )

    # Call GCS to list current buckets
    response = client.list_buckets()

    # Return list of bucket names
    results = []
    for bucket in response["Buckets"]:
        results.append(bucket["Name"])
        print(bucket["Name"])  # Can remove if not needed after development
    return results


# list_gcs_buckets(os.getenv('aws_access_key_id'),os.getenv('aws_secret_access_key'))