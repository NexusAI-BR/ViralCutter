# 🚀 ViralCutter - Versão Modernizada (v2.0)

Bem-vindo à nova era do ViralCutter! Esta versão foi completamente reconstruída por uma squad de agentes de elite para transformar um protótipo funcional em uma aplicação robusta, modular e de alta performance.

## 🌟 Principais Novidades

### 🏎️ Aceleração Universal de Hardware (AMD/NVIDIA)
Chega de sofrer com o processamento lento na CPU. O ViralCutter agora detecta automaticamente seu hardware:
- **AMD (AMF)**: Otimização nativa para placas como a **RX 5700 XT**.
- **NVIDIA (NVENC)**: Suporte completo para placas GeForce/RTX.
- **Apple Silicon (MPS)**: Suporte para chips M1/M2/M3.
- **Intel (QSV)**: Suporte para processadores com QuickSync.

### 📊 Nova Gerência de Projetos (SQLite)
Substituímos a lógica de arquivos soltos por um banco de dados robusto:
- **Busca & Filtros**: Encontre seus projetos por nome ou etapa (Transcrevendo, Analisando, Concluído).
- **Persistência**: Status salvos em tempo real.
- **Exclusão Permanente**: Limpeza segura de arquivos e registros no banco.

### 🎨 Interface Premium Glassmorphism
Uma WebUI completamente redesenhada com:
- **Tema Escuro Moderno**: Tons de *Cyber Blue* e *Orange*.
- **Galeria Inteligente**: Grid responsivo com scores virais destacados.
- **Editor de Legendas**: Refinado para ajustes finos antes da renderização final.

---

## 🛠️ Guia do Motor Core

### `core/hardware.py`
O utilitário que orquestra os encoders. Ele garante que o FFmpeg e o Torch utilizem o melhor recurso disponível no seu sistema.

### `core/engine.py` (ViralCutterCore)
A classe central que gerencia cada etapa do pipeline:
1. **Download**: Captura do YouTube com yt-dlp.
2. **Transcription**: WhisperX acelerado.
3. **Analysis**: Processamento paralelo de chunks com Gemini/G4F.
4. **Cutting/Editing**: Renderização via GPU (AMF/NVENC).

---

## 🚀 Como Começar

1. **Instalação**:
   ```bash
   pip install -r requirements.txt
   pip install sqlalchemy
   ```
2. **GPU (AMD)**: Certifique-se de que os drivers da sua Radeon estão atualizados. O FFmpeg detectará `h264_amf` automaticamente.
3. **Execução**:
   ```bash
   python webui/app.py
   ```

## 📋 Roadmap de Modernização
- [x] Sprint 1: Auditoria de Segurança e Planejamento.
- [x] Sprint 2: Banco de Dados e UI Base.
- [x] Sprint 3: Performance Core e Aceleração GPU.
- [x] Sprint 4: Refinamento de UX, Filtros e Entrega Final.

---
*Desenvolvido com foco em qualidade, velocidade e privacidade 100% local.*
