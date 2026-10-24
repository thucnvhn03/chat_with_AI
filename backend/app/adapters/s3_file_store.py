"""Adapter FileStore cho kho đối tượng tương thích S3 (RustFS/MinIO khi phát triển, S3 thật khi chạy)."""

from typing import TYPE_CHECKING, Any, BinaryIO

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError

if TYPE_CHECKING:
    from mypy_boto3_s3 import S3Client


class S3FileStore:
    def __init__(
        self,
        bucket: str,
        endpoint_url: str | None,
        access_key: str | None,
        secret_key: str | None,
        region: str,
        server_side_encryption: str = "",
    ) -> None:
        self._bucket = bucket
        self._sse = server_side_encryption
        self._client: S3Client = boto3.client(
            "s3",
            endpoint_url=endpoint_url,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region,
            config=Config(
                s3={"addressing_style": "path"},
                retries={"max_attempts": 3, "mode": "standard"},
                connect_timeout=5,
                read_timeout=30,
            ),
        )

    def ensure_bucket(self) -> None:
        try:
            self._client.head_bucket(Bucket=self._bucket)
        except ClientError:
            self._client.create_bucket(Bucket=self._bucket)

    def put(self, key: str, data: BinaryIO) -> None:
        extra: dict[str, Any] = {"ContentType": "application/pdf"}
        if self._sse:
            extra["ServerSideEncryption"] = self._sse
        self._client.upload_fileobj(data, self._bucket, key, ExtraArgs=extra)

    def get(self, key: str) -> bytes:
        response = self._client.get_object(Bucket=self._bucket, Key=key)
        return response["Body"].read()

    def delete(self, key: str) -> None:
        # S3 trả thành công cả khi khóa không tồn tại, nên xóa lần hai không lỗi.
        self._client.delete_object(Bucket=self._bucket, Key=key)

    def exists(self, key: str) -> bool:
        try:
            self._client.head_object(Bucket=self._bucket, Key=key)
        except ClientError as exc:
            if exc.response.get("Error", {}).get("Code") in ("404", "NoSuchKey", "NotFound"):
                return False
            raise
        return True

    def check(self) -> None:
        self._client.head_bucket(Bucket=self._bucket)
