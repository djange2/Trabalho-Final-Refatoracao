"""
Testes unitários para PipelineFactory.

Verifica que a Factory cria um VideoPipeline corretamente configurado,
sem carregar modelos YOLO reais (testes rápidos, sem GPU).
"""
from unittest.mock import MagicMock, patch

import pytest


class TestPipelineFactory:
    def test_create_returns_video_pipeline(self):
        with patch("ml.detector.YOLO"), patch("ml.scripts.jersey_reader.YOLO"):
            from ml.factory import PipelineFactory
            from ml.scripts.video_pipeline import VideoPipeline

            pipeline = PipelineFactory.create(color_extractor=MagicMock())
            assert isinstance(pipeline, VideoPipeline)

    def test_create_uses_mean_extractor_by_default(self):
        with patch("ml.detector.YOLO"), patch("ml.scripts.jersey_reader.YOLO"):
            from ml.factory import PipelineFactory
            from ml.scripts.color_strategies import MeanColorExtractor

            pipeline = PipelineFactory.create()
            assert isinstance(pipeline.color_extractor, MeanColorExtractor)

    def test_create_accepts_custom_color_extractor(self):
        with patch("ml.detector.YOLO"), patch("ml.scripts.jersey_reader.YOLO"):
            from ml.factory import PipelineFactory
            from ml.scripts.color_strategies import KMeansColorExtractor

            extractor = KMeansColorExtractor()
            pipeline = PipelineFactory.create(color_extractor=extractor)
            assert pipeline.color_extractor is extractor

    def test_pipeline_has_all_required_components(self):
        with patch("ml.detector.YOLO"), patch("ml.scripts.jersey_reader.YOLO"):
            from ml.factory import PipelineFactory

            pipeline = PipelineFactory.create(color_extractor=MagicMock())
            assert pipeline.detector is not None
            assert pipeline.ball_detector is not None
            assert pipeline.jersey_reader is not None
            assert pipeline.ball_event_detector is not None
            assert pipeline.kinematic_analyzer is not None
            assert pipeline.clip_writer is not None
