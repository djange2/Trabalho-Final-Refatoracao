"""
Adapter de callbacks individuais para o protocolo IPipelineObserver.

Padrão GoF: Observer (Comportamento)
Problema: process() e fast_scan() recebiam múltiplos Callable opcionais
espalhados na assinatura, acoplando o pipeline à interface de cada consumidor.
Adicionar um novo evento exigia modificar a assinatura de process() e de todos
os callers — violando OCP.

Solução: IPipelineObserver define o contrato de notificação. CallbackObserver
é um Adapter que encapsula os Callables legados no protocolo Observer,
mantendo compatibilidade com o backend existente sem alterar suas chamadas.
"""
from typing import Callable


class CallbackObserver:
    """
    Encapsula callbacks individuais no protocolo IPipelineObserver.

    Permite que o backend continue passando lambdas/funções sem implementar
    a interface explicitamente. Chamadas para métodos sem callback configurado
    são silenciosamente ignoradas (sem None-check espalhado pelo pipeline).
    """

    def __init__(
        self,
        on_player_found: Callable | None = None,
        on_clip_generated: Callable[[dict], None] | None = None,
        on_extracting_start: Callable | None = None,
        on_candidate_found: Callable[[dict], None] | None = None,
    ) -> None:
        self._on_player_found = on_player_found
        self._on_clip_generated = on_clip_generated
        self._on_extracting_start = on_extracting_start
        self._on_candidate_found = on_candidate_found

    def on_player_found(self) -> None:
        if self._on_player_found:
            self._on_player_found()

    def on_clip_generated(self, clip_dict: dict) -> None:
        if self._on_clip_generated:
            self._on_clip_generated(clip_dict)

    def on_extracting_start(self) -> None:
        if self._on_extracting_start:
            self._on_extracting_start()

    def on_candidate_found(self, candidate: dict) -> None:
        if self._on_candidate_found:
            self._on_candidate_found(candidate)
