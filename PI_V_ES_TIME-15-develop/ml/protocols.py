"""
Interfaces (Protocolos) do pipeline de vídeo.

Princípios demonstrados:
  - ISP: cada protocolo tem responsabilidade mínima e coesa
  - OCP: novos detectores/trackers implementam o protocolo sem alterar callers
  - DIP: VideoPipeline depende dessas abstrações, não de classes concretas
"""
from typing import Protocol, runtime_checkable
import numpy as np


@runtime_checkable
class IDetector(Protocol):
    """Contrato para detectores de jogadores no frame."""

    def detect(self, frame: np.ndarray) -> tuple[list, list]:
        """
        Retorna (detections, balls).
        detections: lista de [[x1,y1,w,h], conf, cls]
        balls: lista de [x1,y1,x2,y2]
        """
        ...


@runtime_checkable
class IBallDetector(Protocol):
    """Contrato para detectores especializados de bola."""

    def detect(self, frame: np.ndarray) -> list[list[float]]:
        """Retorna lista de [x1,y1,x2,y2] para cada bola detectada."""
        ...


@runtime_checkable
class ITracker(Protocol):
    """Contrato para trackers de objetos entre frames."""

    def update(
        self, detections: list, frame: np.ndarray
    ) -> list[tuple[int, int, int, int, int | str]]:
        """
        Retorna lista de (l, t, r, b, track_id) para tracks confirmados.
        """
        ...


@runtime_checkable
class IColorExtractor(Protocol):
    """
    Contrato para extratores de cor predominante.

    Padrão GoF demonstrado: Strategy
    Permite trocar o algoritmo de extração (média simples vs K-Means)
    sem modificar o código que chama.
    """

    def extract_color(self, image_bgr: np.ndarray) -> str | None:
        """Retorna a cor dominante em formato '#rrggbb', ou None se inválida."""
        ...

    def color_distance(self, hex1: str, hex2: str) -> float:
        """
        Distância perceptual entre duas cores hex no espaço LAB.
        Retorna 999.0 em caso de erro de parsing.
        """
        ...


class IPipelineObserver(Protocol):
    """
    Contrato para observadores do ciclo de vida do pipeline.

    Padrão GoF demonstrado: Observer
    O pipeline notifica o observador sem conhecer sua implementação concreta.
    """

    def on_player_found(self) -> None:
        """Chamado quando o jogador-alvo é identificado (Passo 2 concluído)."""
        ...

    def on_clip_generated(self, clip_dict: dict) -> None:
        """Chamado a cada clipe gerado com seu dicionário de metadados."""
        ...

    def on_extracting_start(self) -> None:
        """Chamado quando o Passo 4 (extração de clipes) começa."""
        ...

    def on_candidate_found(self, candidate: dict) -> None:
        """Chamado no fast_scan quando um novo candidato é encontrado."""
        ...
