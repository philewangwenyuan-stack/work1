import json
import os
import tempfile
import unittest

import cv2
import numpy as np

from grinder_scheduler import map_render_core
from grinder_scheduler.map_service import MapService


class _Point:
    def __init__(self, x=0.0, y=0.0):
        self.x = x
        self.y = y


class _Pose:
    def __init__(self):
        self.position = _Point()


class _Info:
    def __init__(self, width, height, resolution=0.1):
        self.width = width
        self.height = height
        self.resolution = resolution
        self.origin = _Pose()


class _Header:
    frame_id = "map"


class _Map:
    def __init__(self, grid):
        self.info = _Info(grid.shape[1], grid.shape[0])
        self.header = _Header()
        self.data = grid.reshape(-1).tolist()


def _python_occupancy_to_bgr(grid):
    image = np.zeros((grid.shape[0], grid.shape[1], 3), dtype=np.uint8)
    image[grid == 0] = (245, 245, 245)
    image[grid == 100] = (45, 45, 45)
    image[grid < 0] = (180, 180, 180)
    return cv2.flip(image, 0)


def _python_rotate(grid, origin_x, origin_y, resolution, yaw):
    map_render_core.configure(False)
    try:
        return MapService._rotate_grid_to_aligned_frame(
            grid,
            origin_x,
            origin_y,
            resolution,
            yaw,
        )
    finally:
        map_render_core.configure(True)


class MapRenderCoreTest(unittest.TestCase):
    def setUp(self):
        map_render_core.configure(True)

    def tearDown(self):
        map_render_core.configure(True)

    def _require_core(self):
        if not map_render_core.is_available():
            self.skipTest("grinder_map_render_core is not built in this environment")

    def test_rotate_grid_matches_python_reference(self):
        self._require_core()
        cases = [0.0, np.deg2rad(30.0), np.deg2rad(90.0)]
        grid = np.array(
            [
                [-1, 0, 100, 50],
                [0, 100, -1, 0],
                [100, 0, 0, -1],
            ],
            dtype=np.int16,
        )
        for yaw in cases:
            expected_grid, expected_x, expected_y = _python_rotate(grid, -0.2, 0.4, 0.05, yaw)
            actual = map_render_core.rotate_grid(grid, -0.2, 0.4, 0.05, yaw, -1)
            self.assertIsNotNone(actual)
            actual_grid, actual_x, actual_y = actual
            self.assertTrue(np.array_equal(actual_grid, expected_grid), yaw)
            self.assertAlmostEqual(actual_x, expected_x, places=9)
            self.assertAlmostEqual(actual_y, expected_y, places=9)

    def test_rotate_grid_empty_and_unknown_cases(self):
        self._require_core()
        self.assertIsNone(map_render_core.rotate_grid(np.zeros((0, 3), dtype=np.int16), 0, 0, 1, 0.5))
        grid = np.full((4, 5), -1, dtype=np.int16)
        actual = map_render_core.rotate_grid(grid, 0.0, 0.0, 0.1, np.deg2rad(30.0), -1)
        self.assertIsNotNone(actual)
        self.assertTrue(np.all(actual[0] == -1))

    def test_occupancy_to_bgr_matches_python_reference(self):
        self._require_core()
        grid = np.array([[-1, 0, 100, 50], [0, 100, -1, 0]], dtype=np.int16)
        image = map_render_core.occupancy_to_bgr(grid)
        self.assertIsNotNone(image)
        self.assertTrue(np.array_equal(image, _python_occupancy_to_bgr(grid)))

    def test_resize_and_encode_decodes_to_expected_size(self):
        self._require_core()
        image = np.zeros((80, 100, 3), dtype=np.uint8)
        image[:, :] = (10, 20, 30)
        for ext in ("jpg", "png"):
            result = map_render_core.resize_and_encode(image, 64, ext)
            self.assertIsNotNone(result)
            data, width, height = result
            decoded = cv2.imdecode(np.frombuffer(data, dtype=np.uint8), cv2.IMREAD_COLOR)
            self.assertIsNotNone(decoded)
            self.assertEqual((height, width), decoded.shape[:2])
            self.assertLessEqual(max(decoded.shape[:2]), 64)

    def test_write_map_image_outputs_nav_gray_values(self):
        self._require_core()
        grid = np.array([[-1, 0, 100], [100, 0, -1]], dtype=np.int16)
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "map.pgm")
            self.assertTrue(map_render_core.write_map_image(grid, path))
            decoded = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
            self.assertIsNotNone(decoded)
            expected = np.array([[0, 254, 205], [205, 254, 0]], dtype=np.uint8)
            self.assertTrue(np.array_equal(decoded, expected))

    def test_python_fallback_create_preview_still_works(self):
        map_render_core.configure(False)
        grid = np.array([[-1, 0, 100], [0, 100, -1]], dtype=np.int16)
        service = MapService()
        service.set_map_render_core_enabled(False)
        service.set_raw_map(_Map(grid))
        snapshot = service.create_preview(
            {"x": 0.0, "y": 0.0, "heading_deg": 0.0},
            max_edge=8,
            image_format="png",
            include_overlay=True,
        )
        self.assertTrue(snapshot.preview_data.startswith(b"\x89PNG\r\n\x1a\n"))
        overlay = json.loads(snapshot.overlay_json)
        self.assertEqual(overlay["raw_width"], 3)
        self.assertEqual(overlay["raw_height"], 2)

    def test_unavailable_core_falls_back_when_enabled(self):
        original_load = map_render_core._load
        map_render_core._load = lambda: None
        try:
            grid = np.array([[-1, 0, 100], [0, 100, -1]], dtype=np.int16)
            service = MapService()
            service.set_raw_map(_Map(grid))
            snapshot = service.create_preview(
                {"x": 0.0, "y": 0.0, "heading_deg": 0.0},
                max_edge=8,
                image_format="png",
                include_overlay=True,
            )
            self.assertTrue(snapshot.preview_data.startswith(b"\x89PNG\r\n\x1a\n"))
        finally:
            map_render_core._load = original_load


if __name__ == "__main__":
    unittest.main()
