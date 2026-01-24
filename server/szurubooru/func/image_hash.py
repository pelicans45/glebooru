import os
from io import BytesIO
from typing import Any, List

import numpy as np
# pillow-heif provides both HEIF and AVIF support
import pillow_heif
import pdqhash
from PIL import Image, UnidentifiedImageError

from szurubooru import errors

try:
    import cv2
except Exception:
    cv2 = None

pillow_heif.register_heif_opener()  # Also registers AVIF opener

PDQ_HASH_BITS = 256
PDQ_WORD_BITS = 16
PDQ_WORD_COUNT = PDQ_HASH_BITS // PDQ_WORD_BITS

# Recommended PDQ threshold is ~31 bits; expose normalized cutoff.
DISTANCE_CUTOFF_BITS = 31
DISTANCE_CUTOFF = DISTANCE_CUTOFF_BITS / PDQ_HASH_BITS

SIG_NUMS = PDQ_HASH_BITS

NpMatrix = np.ndarray

_DEFAULT_BACKEND = os.getenv("SZURUBOORU_IMAGE_HASH_BACKEND", "").strip().lower()
if not _DEFAULT_BACKEND:
    _DEFAULT_BACKEND = "opencv" if cv2 is not None else "pillow"


def _preprocess_image_rgb_pillow(content: bytes) -> NpMatrix:
    img = Image.open(BytesIO(content))
    return np.asarray(img.convert("RGB"), dtype=np.uint8)


def _preprocess_image_rgb_opencv(content: bytes) -> NpMatrix:
    if cv2 is None:
        raise ValueError("OpenCV is not available")
    arr = np.frombuffer(content, dtype=np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("OpenCV decode failed")
    return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)


def _preprocess_image_rgb(content: bytes) -> NpMatrix:
    if _DEFAULT_BACKEND == "opencv":
        try:
            return _preprocess_image_rgb_opencv(content)
        except Exception:
            # Some formats (e.g. HEIF/AVIF) may require Pillow; fall back.
            pass
    try:
        return _preprocess_image_rgb_pillow(content)
    except (IOError, ValueError, UnidentifiedImageError) as ex:
        raise errors.ProcessingError(
            "Unable to generate a signature hash for this image"
        ) from ex


def generate_signature(content: bytes) -> NpMatrix:
    try:
        rgb = _preprocess_image_rgb(content)
        signature, _quality = pdqhash.compute(rgb)
        return np.asarray(signature, dtype=np.uint8)
    except Exception as ex:
        raise errors.ProcessingError(
            "Unable to generate a signature hash for this image"
        ) from ex


def generate_words(signature: NpMatrix) -> List[int]:
    packed = np.packbits(signature, bitorder="big")
    return np.frombuffer(packed, dtype=">u2").astype(int).tolist()


def normalized_distance(
    target_array: Any, vec: NpMatrix, nan_value: float = 1.0
) -> List[float]:
    target_array = np.asarray(target_array, dtype=np.uint8)
    vec = np.asarray(vec, dtype=np.uint8)
    if target_array.ndim == 1:
        target_array = target_array.reshape(1, -1)
    if vec.ndim != 1:
        vec = vec.reshape(-1)
    diffs = np.count_nonzero(target_array != vec, axis=1)
    distances = diffs / float(PDQ_HASH_BITS)
    return distances.tolist()


def pack_signature(signature: NpMatrix) -> bytes:
    return np.packbits(signature, bitorder="big").tobytes()


def unpack_signature(packed: bytes) -> NpMatrix:
    bits = np.unpackbits(np.frombuffer(packed, dtype=np.uint8), bitorder="big")
    return bits[:PDQ_HASH_BITS].astype(np.uint8)
