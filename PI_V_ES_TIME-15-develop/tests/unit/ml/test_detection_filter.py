"""
Testes unitários para DetectionFilter.

Migrados de TestIsValidPlayerDetection em test_video_pipeline.py,
agora testando a classe responsável diretamente.
"""
from unittest.mock import MagicMock

import numpy as np
import pytest

from ml.scripts.detection_filter import DetectionFilter
from ml.scripts.config import (
    MAX_PLAYER_ASPECT_RATIO,
)


@pytest.fixture
def detection_filter():
    return DetectionFilter(detector=MagicMock())


class TestIsValidPlayer:
    def test_wide_bbox_rejected_by_aspect_ratio(self, detection_filter):
        assert detection_filter._is_valid_player(10, 10, 200, 50, 720) is False

    def test_ratio_just_above_threshold_rejected(self, detection_filter):
        w = int(MAX_PLAYER_ASPECT_RATIO * 100) + 1
        h = 100
        assert detection_filter._is_valid_player(10, 200, w, h, 720) is False

    def test_player_torso_in_top_dead_zone_rejected(self, detection_filter):
        # frame_h=720, dead_top=72, y1=0, h=80 → torso_y1=12 < 72
        assert detection_filter._is_valid_player(100, 0, 60, 80, 720) is False

    def test_player_torso_in_bottom_dead_zone_rejected(self, detection_filter):
        # frame_h=720, dead_bottom=648, y1=620, h=80 → torso_y2=664 > 648
        assert detection_filter._is_valid_player(100, 620, 60, 80, 720) is False

    def test_valid_player_in_center_accepted(self, detection_filter):
        # y1=200, h=120 → torso_y1=218>72, torso_y2=266<648, ratio=0.5<threshold
        assert detection_filter._is_valid_player(100, 200, 60, 120, 720) is True

    def test_zero_height_does_not_raise(self, detection_filter):
        result = detection_filter._is_valid_player(100, 100, 50, 0, 720)
        assert isinstance(result, bool)

    def test_valid_player_small_frame(self, detection_filter):
        # frame_h=480, dead_top=48, dead_bottom=432
        assert detection_filter._is_valid_player(50, 150, 40, 100, 480) is True


class TestGetValidDetections:
    def test_filters_out_wide_detections(self):
        mock_detector = MagicMock()
        mock_detector.detect.return_value = (
            [[[10, 10, 300, 50], 0.9, 0]],  # aspect ratio 6.0 > threshold
            [],
        )
        df = DetectionFilter(detector=mock_detector)
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        valid, balls = df.get_valid_detections(frame, scale=1.0)
        assert valid == []
        assert balls == []

    def test_passes_valid_player_detection(self):
        mock_detector = MagicMock()
        mock_detector.detect.return_value = (
            [[[100, 200, 60, 120], 0.9, 0]],  # válido
            [],
        )
        df = DetectionFilter(detector=mock_detector)
        frame = np.zeros((720, 640, 3), dtype=np.uint8)
        valid, balls = df.get_valid_detections(frame, scale=1.0)
        assert len(valid) == 1
        assert valid[0]["conf"] == 0.9
