# C4 Context — SmartScout Video Pipeline

> **Nível 1 — Contexto do Sistema:** mostra quem usa o SmartScout e com quais sistemas externos ele se comunica.

```mermaid
flowchart TD
    User(["👤 Treinador / Analista\nSolicita clipes via web app"])

    subgraph SYS ["🎯  SmartScout"]
        direction TB
        Core["Processa vídeos de futebol\ne gera clipes do jogador-alvo"]
    end

    YOLO["⚡ YOLO\nulytralytics\nDetecção de jogadores e bola"]
    DS["🔁 Deep SORT\nRastreamento de identidade\nentre frames"]
    FF["🎬 FFmpeg\nRe-encoding dos clipes\npara H.264"]
    FS["💾 Sistema de Arquivos\nVídeos de entrada\ne clipes gerados"]

    User      -->|"HTTP/REST — vídeo + nº camisa"| SYS
    SYS       -->|"Python API — inferência"| YOLO
    SYS       -->|"Python API — tracking"| DS
    SYS       -->|"subprocess"| FF
    SYS       -->|"I/O local"| FS

    classDef person   fill:#1a3a5c,color:#fff,stroke:#0d2540,rx:20
    classDef system   fill:#1168bd,color:#fff,stroke:#0a4f96
    classDef external fill:#4a4a4a,color:#fff,stroke:#333

    class User person
    class Core system
    class YOLO,DS,FF,FS external
```

| Elemento | Tipo | Descrição |
|----------|------|-----------|
| Treinador / Analista | Pessoa | Usuário final que solicita os clipes |
| SmartScout | Sistema | Pipeline de IA (este projeto) |
| YOLO | Sistema externo | Modelo de detecção de objetos |
| Deep SORT | Sistema externo | Algoritmo de rastreamento multi-objeto |
| FFmpeg | Sistema externo | Re-encoding de vídeo |
| Sistema de Arquivos | Sistema externo | Persistência de vídeos e clipes |
