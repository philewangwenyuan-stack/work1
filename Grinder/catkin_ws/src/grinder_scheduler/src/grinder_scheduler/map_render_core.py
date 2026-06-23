import ctypes
import os
from ctypes import c_char, c_char_p, c_double, c_int, c_int16, c_uint8, POINTER

import numpy as np


_LIB_NAME = "libgrinder_map_render_core.so"
_enabled = True
_lib = None
_load_error = ""
_warned = False


class _BufferResult(ctypes.Structure):
    _fields_ = [
        ("data", POINTER(c_uint8)),
        ("size", c_int),
        ("width", c_int),
        ("height", c_int),
        ("channels", c_int),
        ("status", c_int),
        ("message", c_char * 256),
    ]


class _GridResult(ctypes.Structure):
    _fields_ = [
        ("data", POINTER(c_int16)),
        ("width", c_int),
        ("height", c_int),
        ("origin_x", c_double),
        ("origin_y", c_double),
        ("status", c_int),
        ("message", c_char * 256),
    ]


def configure(enabled=True):
    global _enabled
    _enabled = bool(enabled)


def load_error():
    return _load_error


def _warn_once(message):
    global _warned
    if _warned:
        return
    _warned = True
    try:
        import rospy  # type: ignore

        rospy.logwarn("Map render C++ core unavailable, fallback to Python/OpenCV: %s", message)
    except Exception:
        pass


def _candidate_paths():
    env_path = os.environ.get("GRINDER_MAP_RENDER_CORE_PATH", "").strip()
    if env_path:
        yield env_path

    here = os.path.abspath(os.path.dirname(__file__))
    current = here
    for _ in range(8):
        yield os.path.join(current, "lib", _LIB_NAME)
        yield os.path.join(current, "devel", "lib", _LIB_NAME)
        yield os.path.join(current, "install", "lib", _LIB_NAME)
        parent = os.path.dirname(current)
        if parent == current:
            break
        current = parent

    yield _LIB_NAME


def _setup_prototypes(lib):
    lib.grinder_map_render_free_buffer.argtypes = [POINTER(c_uint8)]
    lib.grinder_map_render_free_buffer.restype = None
    lib.grinder_map_render_free_grid.argtypes = [POINTER(c_int16)]
    lib.grinder_map_render_free_grid.restype = None

    lib.grinder_map_render_rotate_grid_i16.argtypes = [
        POINTER(c_int16),
        c_int,
        c_int,
        c_double,
        c_double,
        c_double,
        c_double,
        c_int16,
        POINTER(_GridResult),
    ]
    lib.grinder_map_render_rotate_grid_i16.restype = c_int

    lib.grinder_map_render_occupancy_to_bgr_i16.argtypes = [
        POINTER(c_int16),
        c_int,
        c_int,
        POINTER(_BufferResult),
    ]
    lib.grinder_map_render_occupancy_to_bgr_i16.restype = c_int

    lib.grinder_map_render_resize_and_encode_u8.argtypes = [
        POINTER(c_uint8),
        c_int,
        c_int,
        c_int,
        c_int,
        c_char_p,
        c_int,
        POINTER(_BufferResult),
    ]
    lib.grinder_map_render_resize_and_encode_u8.restype = c_int

    lib.grinder_map_render_encode_map_png_i16.argtypes = [
        POINTER(c_int16),
        c_int,
        c_int,
        POINTER(_BufferResult),
    ]
    lib.grinder_map_render_encode_map_png_i16.restype = c_int

    lib.grinder_map_render_write_map_image_i16.argtypes = [
        POINTER(c_int16),
        c_int,
        c_int,
        c_char_p,
    ]
    lib.grinder_map_render_write_map_image_i16.restype = c_int


def _load():
    global _lib, _load_error
    if not _enabled:
        return None
    if _lib is not None:
        return _lib

    errors = []
    seen = set()
    for candidate in _candidate_paths():
        if not candidate or candidate in seen:
            continue
        seen.add(candidate)
        if os.path.isabs(candidate) and not os.path.exists(candidate):
            continue
        try:
            lib = ctypes.CDLL(candidate)
            _setup_prototypes(lib)
            _lib = lib
            _load_error = ""
            return _lib
        except Exception as exc:
            errors.append("{}: {}".format(candidate, exc))
    _load_error = "; ".join(errors[-3:]) if errors else "{} not found".format(_LIB_NAME)
    _warn_once(_load_error)
    return None


def is_available():
    return _load() is not None


def _as_i16_grid(grid):
    arr = np.ascontiguousarray(grid, dtype=np.int16)
    if arr.ndim != 2 or arr.size <= 0:
        return None
    return arr


def _buffer_to_bytes(lib, result):
    if result.status != 0 or not bool(result.data) or result.size <= 0:
        return None
    try:
        view = np.ctypeslib.as_array(result.data, shape=(int(result.size),))
        return bytes(view)
    finally:
        lib.grinder_map_render_free_buffer(result.data)


def rotate_grid(grid, origin_x, origin_y, resolution, yaw, fill_value=-1):
    lib = _load()
    arr = _as_i16_grid(grid)
    if lib is None or arr is None:
        return None
    result = _GridResult()
    rc = lib.grinder_map_render_rotate_grid_i16(
        arr.ctypes.data_as(POINTER(c_int16)),
        int(arr.shape[1]),
        int(arr.shape[0]),
        float(origin_x),
        float(origin_y),
        float(resolution),
        float(yaw),
        int(fill_value),
        ctypes.byref(result),
    )
    if rc != 0 or result.status != 0 or not bool(result.data):
        return None
    try:
        view = np.ctypeslib.as_array(result.data, shape=(int(result.height), int(result.width)))
        rotated = np.array(view, dtype=np.int16, copy=True)
        return rotated, float(result.origin_x), float(result.origin_y)
    finally:
        lib.grinder_map_render_free_grid(result.data)


def occupancy_to_bgr(grid):
    lib = _load()
    arr = _as_i16_grid(grid)
    if lib is None or arr is None:
        return None
    result = _BufferResult()
    rc = lib.grinder_map_render_occupancy_to_bgr_i16(
        arr.ctypes.data_as(POINTER(c_int16)),
        int(arr.shape[1]),
        int(arr.shape[0]),
        ctypes.byref(result),
    )
    if rc != 0 or result.status != 0 or not bool(result.data):
        return None
    try:
        shape = (int(result.height), int(result.width), int(result.channels))
        view = np.ctypeslib.as_array(result.data, shape=shape)
        return np.array(view, dtype=np.uint8, copy=True)
    finally:
        lib.grinder_map_render_free_buffer(result.data)


def resize_and_encode(image, max_edge, image_format, jpeg_quality=95):
    lib = _load()
    if lib is None:
        return None
    arr = np.ascontiguousarray(image, dtype=np.uint8)
    if arr.ndim == 2:
        height, width = arr.shape
        channels = 1
    elif arr.ndim == 3 and arr.shape[2] in (1, 3):
        height, width, channels = arr.shape
    else:
        return None
    ext = str(image_format or "jpg")
    if not ext.startswith("."):
        ext = "." + ext
    result = _BufferResult()
    rc = lib.grinder_map_render_resize_and_encode_u8(
        arr.ctypes.data_as(POINTER(c_uint8)),
        int(width),
        int(height),
        int(channels),
        int(max_edge),
        ext.encode("ascii", errors="ignore"),
        int(jpeg_quality),
        ctypes.byref(result),
    )
    if rc != 0:
        return None
    data = _buffer_to_bytes(lib, result)
    if data is None:
        return None
    return data, int(result.width), int(result.height)


def encode_map_png(grid):
    lib = _load()
    arr = _as_i16_grid(grid)
    if lib is None or arr is None:
        return None
    result = _BufferResult()
    rc = lib.grinder_map_render_encode_map_png_i16(
        arr.ctypes.data_as(POINTER(c_int16)),
        int(arr.shape[1]),
        int(arr.shape[0]),
        ctypes.byref(result),
    )
    if rc != 0:
        return None
    return _buffer_to_bytes(lib, result)


def write_map_image(grid, path):
    lib = _load()
    arr = _as_i16_grid(grid)
    if lib is None or arr is None:
        return False
    rc = lib.grinder_map_render_write_map_image_i16(
        arr.ctypes.data_as(POINTER(c_int16)),
        int(arr.shape[1]),
        int(arr.shape[0]),
        os.fsencode(path),
    )
    return rc == 0
