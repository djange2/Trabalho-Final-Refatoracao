"""
Filtragem e validação de detecções brutas do YOLO.

Princípio SOLID demonstrado: SRP
Antes, a lógica de filtrar detecções inválidas (aspect ratio, dead zones)
estava misturada dentro de VideoPipeline, junto com OCR, tracking e clipes.

Ao extrair para DetectionFilter, cada classe tem uma única razão de mudar:
- VideoPipeline muda quando a lógica de orquestração muda
- DetectionFilter muda apenas quando os critérios de validação mudam
"""
import numpy as np
from ml.protocols import IDetector
from ml.scripts.config import (
    MAX_PLAYER_ASPECT_RATIO,
    SCOREBOARD_ZONE_BOTTOM,
    SCOREBOARD_ZONE_TOP,
    TORSO_Y_END,
    TORSO_Y_START,
)


class DetectionFilter:
    """
    Filtra detecções do YOLO, descartando bboxes incompatíveis com jogadores.

    Dois critérios de rejeição:
      1. Aspect ratio: bboxes mais largos que altos (overlay de transmissão)
      2. Dead zones: torso que intersecta a região do placar (topo/base do frame)
    """

    def __init__(self, detector: IDetector) -> None:
        self._detector = detector

    def get_valid_detections(
        self, frame: np.ndarray, scale: float
    ) -> tuple[list[dict], list]:
        """
        Roda o detector e retorna apenas as detecções geometricamente válidas.

        Args:
            frame: Frame redimensionado (espaço de processamento do YOLO).
            scale: Fator frame_orig.width / frame.width para escalar coordenadas.

        Returns:
            (valid_detections, bolas_yolo)
            valid_detections: lista de {"box_yolo", "bbox_orig", "conf", "cls"}
            bolas_yolo: lista de [x1,y1,x2,y2] (passada diretamente ao BallTracker)
        """
        detections, bolas_yolo = self._detector.detect(frame)
        frame_h = frame.shape[0]

        valid_detections = []
        for box, conf, cls in detections:
            x1, y1, w, h = box
            if not self._is_valid_player(x1, y1, w, h, frame_h):
                continue
            bbox_orig = (
                int(x1 * scale),
                int(y1 * scale),
                int((x1 + w) * scale),
                int((y1 + h) * scale),
            )
            valid_detections.append({
                "box_yolo": box,
                "bbox_orig": bbox_orig,
                "conf": conf,
                "cls": cls,
            })

        return valid_detections, bolas_yolo

    def _is_valid_player(
        self, x1: float, y1: float, w: float, h: float, frame_h: float
    ) -> bool:
        """
        Retorna True se o bbox é geometricamente compatível com um jogador.

        Rejeita:
        - Aspect ratio horizontal (w/h > MAX_PLAYER_ASPECT_RATIO)
        - Torso que toca a dead zone do placar (topo ou base do frame)
        """
        if h > 0 and (w / h) > MAX_PLAYER_ASPECT_RATIO:
            return False

        torso_y1 = y1 + h * TORSO_Y_START
        torso_y2 = y1 + h * TORSO_Y_END
        dead_top = frame_h * SCOREBOARD_ZONE_TOP
        dead_bottom = frame_h * (1 - SCOREBOARD_ZONE_BOTTOM)

        if torso_y1 < dead_top:
            return False
        if torso_y2 > dead_bottom:
            return False

        return True
