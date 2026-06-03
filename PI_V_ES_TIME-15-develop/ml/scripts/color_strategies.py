"""
Estratégias de extração de cor predominante de imagens.

Padrão GoF: Strategy (Comportamento)
Problema: o VideoPipeline precisava de dois algoritmos de extração de cor
(média simples para tracking, K-Means para identificação inicial), mas
ambos estavam misturados como métodos privados na classe orquestradora,
violando SRP e impedindo substituição sem modificar o pipeline.

Solução: cada algoritmo vira uma classe concreta que implementa IColorExtractor.
O pipeline recebe a estratégia via injeção de dependência — sem conhecer
qual algoritmo está em uso.
"""
import cv2
import numpy as np


class MeanColorExtractor:
    """
    Extrai cor média do torso via cv2.mean — O(n) nos pixels, muito rápido.

    Estratégia padrão para tracking: chamada a cada OCR_INTERVAL frames
    para todos os jogadores do lote. Neutraliza estampas e dobras tirando
    a média de todos os pixels da região do ombro/peito.
    """

    def extract_color(self, image_bgr: np.ndarray) -> str | None:
        if image_bgr is None or image_bgr.size == 0:
            return None

        h, w = image_bgr.shape[:2]
        margem_lateral = int(w * 0.15)
        altura_ombros = int(h * 0.40)

        shoulders_crop = image_bgr[
            0 : max(1, altura_ombros),
            margem_lateral : max(margem_lateral + 1, w - margem_lateral),
        ]
        if shoulders_crop.size == 0:
            shoulders_crop = image_bgr

        mean_bgr = cv2.mean(shoulders_crop)[:3]
        return "#%02x%02x%02x" % (int(mean_bgr[2]), int(mean_bgr[1]), int(mean_bgr[0]))

    def color_distance(self, hex1: str, hex2: str) -> float:
        """Distância perceptual Euclidiana no espaço LAB entre dois HEX."""
        try:
            lab1 = self._hex_to_lab(hex1)
            lab2 = self._hex_to_lab(hex2)
            return float(np.linalg.norm(lab1 - lab2))
        except Exception:
            return 999.0

    @staticmethod
    def _hex_to_lab(h: str) -> np.ndarray:
        h = h.lstrip("#")
        b, g, r = tuple(int(h[i : i + 2], 16) for i in (4, 2, 0))
        pixel_bgr = np.array([[[b, g, r]]], dtype=np.uint8)
        pixel_lab = cv2.cvtColor(pixel_bgr, cv2.COLOR_BGR2LAB)
        return pixel_lab[0][0].astype(float)


class KMeansColorExtractor:
    """
    Extrai cor dominante via clustering K-Means — mais preciso, mais lento.

    Estratégia preferida para fast_scan: separa melhor a cor real da camisa
    do fundo (gramado, publicidade) em detecções de baixa qualidade onde a
    média simples seria distorcida por pixels de fundo.
    """

    def __init__(self, k: int = 3) -> None:
        self.k = k

    def extract_color(self, image_bgr: np.ndarray) -> str | None:
        if image_bgr is None or image_bgr.size == 0:
            return None

        h, w = image_bgr.shape[:2]
        max_dim = 50
        if max(h, w) > max_dim:
            scale = max_dim / max(h, w)
            image_bgr = cv2.resize(image_bgr, (int(w * scale), int(h * scale)))

        image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
        pixels = image_rgb.reshape((-1, 3)).astype(np.float32)
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
        best_labels = np.empty(0, dtype=np.int32)
        _, labels, centers = cv2.kmeans(
            pixels, self.k, best_labels, criteria, 10, cv2.KMEANS_RANDOM_CENTERS
        )
        labels = labels.flatten()
        dominant_idx = int(np.argmax(np.bincount(labels)))
        r, g, b = [int(c) for c in centers[dominant_idx]]
        return f"#{r:02x}{g:02x}{b:02x}"

    def color_distance(self, hex1: str, hex2: str) -> float:
        """Reutiliza a lógica LAB da MeanColorExtractor."""
        try:
            return float(np.linalg.norm(
                MeanColorExtractor._hex_to_lab(hex1) - MeanColorExtractor._hex_to_lab(hex2)
            ))
        except Exception:
            return 999.0
