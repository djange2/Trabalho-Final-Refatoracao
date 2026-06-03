"""
Tracker simples de bola com predição linear por velocidade.

Quando a bola sai do campo de visão, prediz a posição usando o vetor de
velocidade do último frame detectado — evita perder o rastro em oclusões curtas.
"""


class BallTracker:
    """
    Rastreia a bola com predição de posição por velocidade constante.

    Quando a bola não é detectada, propaga a última posição + vetor de
    velocidade por até `max_missing` frames antes de perder completamente.
    """

    def __init__(self, max_missing: int = 10) -> None:
        self._last_box: list[float] | None = None
        self._velocity: tuple[float, float] = (0.0, 0.0)
        self._missing_frames: int = 0
        self._max_missing = max_missing

    def update(
        self,
        frame_idx: int,
        detections: list[list[float]],
    ) -> list[float] | None:
        """
        Atualiza o tracker com as detecções da bola no frame atual.

        Args:
            frame_idx: Índice do frame atual (reservado para compatibilidade de interface).
            detections: Lista de [x1,y1,x2,y2]. Usa apenas a primeira detecção.

        Returns:
            Bounding box [x1,y1,x2,y2] da bola (detectada ou predita), ou None se perdida.
        """
        if detections:
            return self._update_from_detection(detections[0])
        return self._predict_or_lose()

    def _update_from_detection(self, box: list[float]) -> list[float]:
        cx = (box[0] + box[2]) / 2
        cy = (box[1] + box[3]) / 2

        if self._last_box is not None:
            prev_cx = (self._last_box[0] + self._last_box[2]) / 2
            prev_cy = (self._last_box[1] + self._last_box[3]) / 2
            self._velocity = (cx - prev_cx, cy - prev_cy)

        self._last_box = box
        self._missing_frames = 0
        return box

    def _predict_or_lose(self) -> list[float] | None:
        if self._last_box is None or self._missing_frames >= self._max_missing:
            self._last_box = None
            return None

        vx, vy = self._velocity
        self._last_box = [
            self._last_box[0] + vx,
            self._last_box[1] + vy,
            self._last_box[2] + vx,
            self._last_box[3] + vy,
        ]
        self._missing_frames += 1
        return self._last_box
