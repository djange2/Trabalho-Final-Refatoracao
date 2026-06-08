# Trabalho Final — Refatoração SmartScout

Refatoração arquitetural do sistema SmartScout aplicando **SOLID**, **Clean Code** e **padrões GoF** como evidência para o Trabalho Final da disciplina de Arquitetura de Software.

## Instalação e execução do pipeline

### Pré-requisitos
- Python 3.11+
- CUDA (opcional, mas recomendado)
- FFmpeg instalado no PATH

### 1. Instalar dependências
```bash
cd PI_V_ES_TIME-15-develop/backend
pip install -r requirements.txt
```

### 2. Colocar os modelos em `ml/models/`
- `ml/models/best.pt` — leitura de número de camisa (YOLO customizado)
- `ml/models/ball_tracker.pt` — detecção de bola (YOLO customizado)

### 3. Iniciar o backend
```bash
cd PI_V_ES_TIME-15-develop/backend
python -m uvicorn app.main:app --reload
```

### 4. Iniciar o frontend
```bash
cd PI_V_ES_TIME-15-develop/frontend
npm install
npm run dev
```

### 5. Rodar os testes
```bash
cd PI_V_ES_TIME-15-develop
python -m pytest tests/ -v
```

### Uso programático do pipeline
```python
from ml.factory import PipelineFactory

pipeline = PipelineFactory.create()
clips = pipeline.process(
    video_path="entrada.mp4",
    target_number=10,
    output_dir="saida/",
)
```

## Padrões GoF aplicados

| Padrão | Categoria | Arquivo |
|--------|-----------|---------|
| Strategy | Comportamento | `ml/scripts/color_strategies.py` |
| Factory Method | Criação | `ml/factory.py` |
| Observer | Comportamento | `ml/scripts/pipeline_observer.py` |
| Facade | Estrutura | `ml/scripts/video_pipeline.py` |
| Template Method | Comportamento | `ml/scripts/video_pipeline.py` |

## Princípios SOLID

| Princípio | Arquivo | Evidência |
|-----------|---------|-----------|
| SRP | `ml/scripts/detection_filter.py` | `DetectionFilter` — única responsabilidade: filtrar detecções |
| OCP | `ml/protocols.py` | `IColorExtractor` — novos extratores sem modificar callers |
| LSP | `ml/detector.py` | `YoloDetector` e `BallDetector` satisfazem `IDetector`/`IBallDetector` |
| ISP | `ml/protocols.py` | 4 protocolos coesos em vez de 1 interface monolítica |
| DIP | `ml/factory.py` | `PipelineFactory.create()` injeta abstrações, não concreções |

## Diagramas

- [`PI_V_ES_TIME-15-develop/diagrams/c4-context.md`](PI_V_ES_TIME-15-develop/diagrams/c4-context.md) — Visão de contexto C4
- [`PI_V_ES_TIME-15-develop/diagrams/class-gof.md`](PI_V_ES_TIME-15-develop/diagrams/class-gof.md) — Classes e padrões GoF
- [`PI_V_ES_TIME-15-develop/diagrams/sequence-process.md`](PI_V_ES_TIME-15-develop/diagrams/sequence-process.md) — Sequência do `process()`
- [`PI_V_ES_TIME-15-develop/adrs/`](PI_V_ES_TIME-15-develop/adrs/) — Decisões arquiteturais (ADR-001 a ADR-005)