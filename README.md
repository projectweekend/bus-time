# bus-time

## Example Config File
```json
{
    "api_key": "real cta bustracker api key",
    "stop_id": "cta bus stop id for predictions",
    "s3_bucket": "s3 bucket name where predictions are saved",
    "aws": {
        "region_name": "for use with s3 resource client",
        "aws_access_key_id": "for user with permission to s3_bucket",
        "aws_secret_access_key": "for user with permission to s3_bucket"
    }
}
```
