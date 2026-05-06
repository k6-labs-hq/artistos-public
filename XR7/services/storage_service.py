from __future__ import annotations

from datetime import datetime, timezone

import boto3
from botocore.client import Config

from xr7_common.logging import get_logger
from xr7_common.settings import settings

logger = get_logger(__name__)


class ObjectStorageService:
    """S3/MinIO compatible object storage helper for artifacts and packets."""

    def __init__(self) -> None:
        self.bucket = settings.s3_bucket
        self._client = boto3.client(
            "s3",
            region_name=settings.s3_region,
            endpoint_url=settings.s3_endpoint_url,
            aws_access_key_id=settings.s3_access_key_id,
            aws_secret_access_key=settings.s3_secret_access_key,
            use_ssl=settings.s3_use_ssl,
            config=Config(signature_version="s3v4"),
        )

    def ensure_bucket(self) -> None:
        try:
            self._client.head_bucket(Bucket=self.bucket)
        except Exception:  # noqa: BLE001
            logger.info("Creating missing object storage bucket", extra={"bucket": self.bucket})
            self._client.create_bucket(Bucket=self.bucket)

    def upload_bytes(
        self, key: str, data: bytes, content_type: str = "application/octet-stream"
    ) -> str:
        self.ensure_bucket()
        self._client.put_object(Bucket=self.bucket, Key=key, Body=data, ContentType=content_type)
        return f"s3://{self.bucket}/{key}"

    def upload_json(self, key: str, payload: str) -> str:
        return self.upload_bytes(key, payload.encode("utf-8"), content_type="application/json")

    def build_evidence_key(self, claim_id: str) -> str:
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        return f"evidence/{claim_id}/{stamp}.json"

    def build_statement_key(self, artist_id: str, file_hash: str, original_ext: str) -> str:
        """Content-addressed key for an uploaded statement file.

        Format: ``statements/{artist_id}/{file_hash}.{ext}``. See
        docs/decisions/statement-storage-and-retention.md §5.
        """
        ext = (original_ext or "").lstrip(".").lower() or "bin"
        return f"statements/{artist_id}/{file_hash}.{ext}"

    def download_bytes(self, key: str) -> bytes:
        """Read an object's contents as bytes. Raises if the object is absent."""
        resp = self._client.get_object(Bucket=self.bucket, Key=key)
        return resp["Body"].read()

    def s3_uri_to_key(self, s3_uri: str) -> str:
        """Strip the ``s3://<bucket>/`` prefix from a URI we issued."""
        prefix = f"s3://{self.bucket}/"
        if not s3_uri.startswith(prefix):
            raise ValueError(f"URI {s3_uri!r} is not in our bucket {self.bucket!r}")
        return s3_uri[len(prefix):]
