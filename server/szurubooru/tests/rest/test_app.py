import io
import json

import pytest

from szurubooru.rest import app, errors


def _make_multipart_env(parts):
    boundary = "----glebooru-boundary"
    body_chunks = []
    for part in parts:
        headers = [
            f'Content-Disposition: form-data; name="{part["name"]}"',
        ]
        if "filename" in part:
            headers[0] += f'; filename="{part["filename"]}"'
        if "content_type" in part:
            headers.append(f'Content-Type: {part["content_type"]}')
        body_chunks.append(f"--{boundary}\r\n".encode("utf-8"))
        body_chunks.append(("\r\n".join(headers) + "\r\n\r\n").encode("utf-8"))
        body_chunks.append(part["body"])
        body_chunks.append(b"\r\n")
    body_chunks.append(f"--{boundary}--\r\n".encode("utf-8"))
    body = b"".join(body_chunks)
    return {
        "REQUEST_METHOD": "POST",
        "PATH_INFO": "/uploads/",
        "CONTENT_TYPE": f"multipart/form-data; boundary={boundary}",
        "CONTENT_LENGTH": str(len(body)),
        "wsgi.input": io.BytesIO(body),
    }


def test_create_context_parses_uploaded_file():
    env = _make_multipart_env(
        [
            {
                "name": "content",
                "filename": "test.png",
                "content_type": "image/png",
                "body": b"png-bytes",
            }
        ]
    )

    ctx = app._create_context(env)

    assert ctx.get_file("content") == b"png-bytes"


def test_create_context_parses_metadata_blob_and_file():
    metadata = {"safety": "safe", "tags": ["tag1", "tag2"]}
    env = _make_multipart_env(
        [
            {
                "name": "content",
                "filename": "test.png",
                "content_type": "image/png",
                "body": b"png-bytes",
            },
            {
                "name": "metadata",
                "filename": "blob",
                "content_type": "application/json",
                "body": json.dumps(metadata).encode("utf-8"),
            },
        ]
    )

    ctx = app._create_context(env)

    assert ctx.get_file("content") == b"png-bytes"
    assert ctx.get_param("safety") == "safe"
    assert ctx.get_param_as_list("tags") == ["tag1", "tag2"]


def test_create_context_raises_for_empty_multipart():
    env = _make_multipart_env([])

    with pytest.raises(errors.HttpBadRequest) as ex:
        app._create_context(env)

    assert ex.value.description == "No files attached"
