import logging
import re
import urllib.parse
from datetime import datetime
from typing import Any, Callable, Dict, Optional, Tuple

import numpy as np
import orjson as json

from szurubooru import db
from szurubooru.func import util
from szurubooru.rest import context, errors, middleware, routes


def _json_serializer(obj: Any) -> str:
    """JSON serializer for objects not serializable by default JSON code"""
    if isinstance(obj, datetime):
        return obj.isoformat("T") + "Z"
    if isinstance(obj, np.float64):
        return json.dumps(obj.item())
    if isinstance(obj, bytes):
        return obj.decode("utf-8")
    raise TypeError("Type not serializable")


def _dump_json(obj: Any) -> str:
    # return orig_json.dumps(obj, default=_json_serializer, indent=2)
    return json.dumps(obj, default=_json_serializer)


def _get_headers(env: Dict[str, Any]) -> Dict[str, str]:
    """
    headers = {}  # type: Dict[str, str]
    for key, value in env.items():
        if key.startswith("HTTP_"):
            key = util.snake_case_to_upper_train_case(key[5:])
            headers[key] = value
    return headers
    """
    return {
        util.snake_case_to_upper_train_case(key[5:]): value
        for key, value in env.items() if key.startswith("HTTP_")
    }


def _parse_multipart(env: Dict[str, Any]) -> Tuple[Dict[str, Any], bytes]:
    """Parse multipart form data using python-multipart library."""
    files = {}
    body = None

    content_type = env.get("CONTENT_TYPE", "")
    content_length = int(env.get("CONTENT_LENGTH", 0))

    if content_length == 0:
        raise errors.HttpBadRequest("ValidationError", "No content")

    # Read the entire body
    raw_body = env["wsgi.input"].read(content_length)

    # Parse using multipart
    def on_field(field):
        nonlocal body
        if field.field_name == b"metadata":
            body = field.value
        else:
            files[field.field_name.decode("utf-8")] = field.value

    def on_file(file):
        files[file.field_name.decode("utf-8")] = file.file_object.read()

    # Extract boundary from content-type header
    boundary = None
    for part in content_type.split(";"):
        part = part.strip()
        if part.startswith("boundary="):
            boundary = part[9:].strip('"')
            break

    if not boundary:
        raise errors.HttpBadRequest("ValidationError", "No multipart boundary")

    # Create parser
    callbacks = {
        "on_field": on_field,
        "on_file": on_file,
    }

    # Simple custom parsing approach
    parts = raw_body.split(b"--" + boundary.encode())
    for part in parts[1:-1]:  # Skip first empty and last closing parts
        if b"\r\n\r\n" not in part:
            continue
        header_section, content = part.split(b"\r\n\r\n", 1)
        # Remove trailing \r\n from content
        if content.endswith(b"\r\n"):
            content = content[:-2]

        # Parse headers
        headers_text = header_section.decode("utf-8", errors="ignore")
        name = None
        filename = None
        for line in headers_text.split("\r\n"):
            if "Content-Disposition:" in line:
                for item in line.split(";"):
                    item = item.strip()
                    if item.startswith("name="):
                        name = item[5:].strip('"')
                    elif item.startswith("filename="):
                        filename = item[9:].strip('"')

        if name:
            if name == "metadata":
                body = content
            else:
                files[name] = content

    if not files and body is None:
        raise errors.HttpBadRequest("ValidationError", "No files attached")

    return files, body


def _create_context(env: Dict[str, Any]) -> context.Context:
    method = env["REQUEST_METHOD"]
    path = "/" + env["PATH_INFO"].lstrip("/")
    path = path.encode("latin-1").decode("utf-8")  # PEP-3333
    headers = _get_headers(env)

    files = {}
    params = dict(urllib.parse.parse_qsl(env.get("QUERY_STRING", "")))

    if "multipart" in env.get("CONTENT_TYPE", ""):
        files, body = _parse_multipart(env)
    else:
        body = env["wsgi.input"].read()

    if body:
        try:
            if isinstance(body, bytes):
                body = body.decode("utf-8")

            #for key, value in json.loads(body).items():
            #    params[key] = value
            params.update(json.loads(body))
        except (ValueError, UnicodeDecodeError):
            raise errors.HttpBadRequest(
                "ValidationError",
                "Could not decode the request body. The JSON "
                "was incorrect or was not encoded as UTF-8.",
            )

    return context.Context(env, method, path, headers, params, files)


def application(
    env: Dict[str, Any], start_response: Callable[[str, Any], Any]
) -> Tuple[bytes]:
    try:
        ctx = _create_context(env)
        """
        accept_header = ctx.get_header("Accept")
        if "application/json" not in accept_header and "*/*" not in accept_header:
            raise errors.HttpNotAcceptable(
                "ValidationError", "This API only supports JSON responses"
            )
        """

        for url, allowed_methods in routes.routes.items():
            match = re.fullmatch(url, ctx.url)
            if match:
                if ctx.method not in allowed_methods:
                    raise errors.HttpMethodNotAllowed(
                        "ValidationError",
                        "Allowed methods: %r" % allowed_methods,
                    )
                handler = allowed_methods[ctx.method]
                break
        else:
            raise errors.HttpNotFound(
                "ValidationError",
                "Requested path " + ctx.url + " was not found",
            )

        try:
            ctx.session = db.session()
            try:
                for hook in middleware.pre_hooks:
                    hook(ctx)
                try:
                    response = handler(
                        ctx,
                        {
                            key: urllib.parse.unquote(value)
                            for key, value in match.groupdict().items()
                        },
                    )
                except Exception:
                    ctx.session.rollback()
                    raise
                finally:
                    for hook in middleware.post_hooks:
                        hook(ctx)
            finally:
                db.session.remove()

            if response.get("return_type") == "custom":
                content_type = response.get("content_type", "text/html")
                start_response(response.get("status_code", "200"), [("content-type", content_type)])
                return (response.get("content", "").encode("utf-8"),)

            # Build response headers, including cache control if specified
            headers = [("content-type", "application/json")]
            if "_cache" in response:
                headers.append(("cache-control", response.pop("_cache")))

            start_response("200", headers)
            return (_dump_json(response),)

        except Exception as ex:
            for exception_type, ex_handler in errors.error_handlers.items():
                if isinstance(ex, exception_type):
                    ex_handler(ex)
            raise

    except errors.BaseHttpError as ex:
        start_response(
            "%d %s" % (ex.code, ex.reason),
            [("content-type", "application/json")],
        )
        blob = {
            "name": ex.name,
            "title": ex.title,
            "description": ex.description,
        }
        if ex.extra_fields is not None:
            for key, value in ex.extra_fields.items():
                blob[key] = value

        if not errors.can_ignore_error(ex):
            logging.exception(ex)
        return (_dump_json(blob),)
