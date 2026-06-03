"""
ColorExtractor — wrapper de retrocompatibilidade sobre KMeansColorExtractor.

Para uso no pipeline, prefira ml.scripts.color_strategies.KMeansColorExtractor
ou MeanColorExtractor diretamente, injetado via PipelineFactory.
"""
import numpy as np

from ml.scripts.color_strategies import KMeansColorExtractor


class ColorExtractor(KMeansColorExtractor):
    """
    Mantém o nome original para não quebrar imports existentes.
    Expõe o método legado get_dominant_color_hex como alias de extract_color.
    """

    def get_dominant_color_hex(self, image_bgr: np.ndarray) -> str | None:
        return self.extract_color(image_bgr)
