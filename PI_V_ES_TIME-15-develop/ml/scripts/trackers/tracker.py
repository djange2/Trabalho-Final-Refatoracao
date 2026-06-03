"""
Tracker de jogadores baseado em Deep SORT.

Implementa ITracker: recebe detecções de um frame e retorna tracks confirmados
com IDs persistentes entre frames consecutivos.
"""
import numpy as np
from deep_sort_realtime.deepsort_tracker import DeepSort


class PlayerTracker:
    """
    Rastreia jogadores entre frames usando Deep SORT.

    Mantém IDs persistentes por até `max_age` frames sem detecção nova,
    permitindo acumular votos de OCR por jogador ao longo do vídeo.
    """

    def __init__(self, max_age: int = 30) -> None:
        self._tracker = DeepSort(max_age=max_age)

    def update(
        self,
        detections: list[list],
        frame: np.ndarray,
    ) -> list[tuple[int, int, int, int, int]]:
        """
        Atualiza o estado do tracker com as detecções do frame atual.

        Args:
            detections: Lista de [[x1,y1,w,h], conf, cls] no espaço de processamento.
            frame: Frame atual (usado pelo re-ID do Deep SORT).

        Returns:
            Lista de (l, t, r, b, track_id) para cada track confirmado.
        """
        tracks = self._tracker.update_tracks(detections, frame=frame)
        return [
            (int(l), int(t), int(r), int(b), track.track_id)
            for track in tracks
            if track.is_confirmed()
            for l, t, r, b in [track.to_ltrb()]
        ]
