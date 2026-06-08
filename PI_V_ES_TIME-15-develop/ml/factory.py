"""
Factory para montagem do VideoPipeline.

Padrão GoF: Factory Method (Criação)
Problema: VideoPipeline acumulava conhecimento de como instanciar cada
componente pesado (YOLO, DeepSORT), misturando criação com orquestração.
Testes unitários exigiam patches invasivos só para construir o objeto.

Solução: PipelineFactory centraliza a montagem. Callers recebem um pipeline
pronto sem conhecer quais implementações concretas foram usadas.
"""
from ml.scripts.video_pipeline import VideoPipeline
from ml.detector import YoloDetector, BallDetector
from ml.scripts.jersey_reader import JerseyReader
from ml.scripts.ball_event_detector import BallEventDetector
from ml.scripts.kinematic_analyzer import KinematicAnalyzer
from ml.scripts.clip_writer import ClipWriter
from ml.scripts.color_strategies import MeanColorExtractor
from ml.scripts.detection_filter import DetectionFilter
from ml.protocols import IColorExtractor


class PipelineFactory:
    """
    Monta e injeta todas as dependências do VideoPipeline.

    Uso:
        pipeline = PipelineFactory.create()
        clips = pipeline.process(video_path="video.mp4", ...)

    Para substituir a estratégia de cor (ex: K-Means no fast_scan):
        pipeline = PipelineFactory.create(color_extractor=KMeansColorExtractor())
    """

    @staticmethod
    def create(color_extractor: IColorExtractor | None = None) -> VideoPipeline:
        """
        Cria um VideoPipeline com todas as dependências padrão instanciadas.

        Args:
            color_extractor: Estratégia de cor customizada.
                             Se None, usa MeanColorExtractor (padrão para tracking).
        """
        detector = YoloDetector()
        return VideoPipeline(
            detector=detector,
            ball_detector=BallDetector(),
            jersey_reader=JerseyReader(),
            ball_event_detector=BallEventDetector(),
            kinematic_analyzer=KinematicAnalyzer(),
            clip_writer=ClipWriter(),
            color_extractor=color_extractor or MeanColorExtractor(),
            detection_filter=DetectionFilter(detector=detector),
        )
