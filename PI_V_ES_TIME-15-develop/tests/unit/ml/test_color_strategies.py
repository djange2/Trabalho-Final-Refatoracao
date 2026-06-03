"""
Testes unitários para as estratégias de extração de cor.

Testa MeanColorExtractor e KMeansColorExtractor via interface IColorExtractor,
sem dependência de modelos YOLO ou arquivos de vídeo.
"""
import numpy as np
import pytest

from ml.scripts.color_strategies import KMeansColorExtractor, MeanColorExtractor


@pytest.fixture
def mean_extractor():
    return MeanColorExtractor()


@pytest.fixture
def kmeans_extractor():
    return KMeansColorExtractor(k=2)


class TestMeanColorExtractor:
    def test_returns_hex_string(self, mean_extractor):
        img = np.zeros((50, 30, 3), dtype=np.uint8)
        result = mean_extractor.extract_color(img)
        assert result is not None
        assert result.startswith("#")
        assert len(result) == 7

    def test_none_on_empty_array(self, mean_extractor):
        assert mean_extractor.extract_color(np.array([])) is None

    def test_none_on_none_input(self, mean_extractor):
        assert mean_extractor.extract_color(None) is None

    def test_pure_red_image_returns_reddish_hex(self, mean_extractor):
        img = np.zeros((50, 30, 3), dtype=np.uint8)
        img[:, :, 2] = 255  # canal R no BGR
        result = mean_extractor.extract_color(img)
        assert result is not None
        r_val = int(result[1:3], 16)
        assert r_val > 200

    def test_same_color_zero_distance(self, mean_extractor):
        assert mean_extractor.color_distance("#ff0000", "#ff0000") == pytest.approx(0.0, abs=0.1)

    def test_black_white_large_distance(self, mean_extractor):
        assert mean_extractor.color_distance("#000000", "#ffffff") > 50

    def test_invalid_hex_returns_999(self, mean_extractor):
        assert mean_extractor.color_distance("invalid", "#ffffff") == 999.0

    def test_both_invalid_returns_999(self, mean_extractor):
        assert mean_extractor.color_distance("not_a_color", "also_not") == 999.0

    def test_similar_colors_small_distance(self, mean_extractor):
        assert mean_extractor.color_distance("#ff0000", "#ee0000") < 20

    def test_very_different_colors_large_distance(self, mean_extractor):
        assert mean_extractor.color_distance("#ff0000", "#0000ff") > 30


class TestKMeansColorExtractor:
    def test_returns_hex_string(self, kmeans_extractor):
        img = np.zeros((50, 30, 3), dtype=np.uint8)
        result = kmeans_extractor.extract_color(img)
        assert result is not None
        assert result.startswith("#")
        assert len(result) == 7

    def test_none_on_empty_array(self, kmeans_extractor):
        assert kmeans_extractor.extract_color(np.array([])) is None

    def test_none_on_none_input(self, kmeans_extractor):
        assert kmeans_extractor.extract_color(None) is None

    def test_invalid_hex_returns_999(self, kmeans_extractor):
        assert kmeans_extractor.color_distance("xyz", "#ffffff") == 999.0

    def test_same_color_zero_distance(self, kmeans_extractor):
        assert kmeans_extractor.color_distance("#ff0000", "#ff0000") == pytest.approx(0.0, abs=0.1)
