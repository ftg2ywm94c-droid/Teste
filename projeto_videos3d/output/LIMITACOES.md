# Relatório de limitações — prova de conceito

## Bloqueios do ambiente
1. **Blender não está instalado e não pôde ser instalado** (sem acesso de rede para pacotes; `bpy` ausente). A prova foi renderizada com um renderizador 3D próprio em NumPy. É 3D real (geometria, perspectiva, sombras por raio), mas não é EEVEE.
2. **Narração pendente — será gravada na ElevenLabs** (`narracao/ROTEIRO_ELEVENLABS.md`) e aplicada com `scripts/add_narration.py`. Situação original: Não há TTS em português offline e o edge-tts exige rede. O ffmpeg tem `flite`, que só fala inglês; não foi usado. O MP4 tem trilha de efeitos e música sintetizadas, sem voz.
3. **Legendas com tempo estimado (só no `poc_540x960.mp4`).** O `add_narration.py` refaz a legenda com os tempos da voz gravada. Sem áudio de voz não existe sincronia a conferir; os tempos saem do roteiro em `shots/shots.json`.
4. **Sem Whisper.** A narração das referências foi lida por OCR das legendas queimadas, não transcrita do áudio.
5. **Máquina**: 2 núcleos de CPU, 7 GB de RAM, sem GPU.

## Limitações do renderizador próprio (frente ao que o documento pede)
- Só primitivas analíticas (esfera/elipsoide, caixa, cilindro, cápsula, plano). Sem malhas arbitrárias, sem shape keys, sem texturas de imagem; rosto e detalhes são shaders procedurais.
- Sem oclusão de ambiente, sem motion blur, sem profundidade de campo, sem luz indireta, sem cenas noturnas com várias fontes de luz (hoje só o sol).
- Sombra dura com leve desfoque em espaço de tela; contorno por detecção de borda de id/profundidade.
- Custo medido: 3,3–4,8 s por frame em 540x960 com supersampling 2x. Um vídeo de 62 s levaria ~1h45 nesse formato; em 1080x1920 com a mesma qualidade, ~7 h nesta máquina.
- O rig é procedural (IK de 2 ossos nas pernas, FK nos braços), não um armature com skinning.

## Defeitos conhecidos neste teste
- Entrega em 540x960 (resolução de preview do documento), não 1080x1920.
- S1: o carro ao fundo é pequeno demais para ser lido como ameaça.
- S2: a placa fica entre a câmera e o carro durante a freada.
- S3: do carro só aparece a frente no canto; a legenda cobre as pernas do personagem em alguns quadros.
- Casas e árvores são simples e repetidas; não há outros personagens nem motorista no carro.
- Áudio sintetizado é funcional, não tem acabamento de sound design.

## O que foi verificado
- `qc_report.json`: 10,0 s, 300 frames, H.264 540x960 30 fps, AAC 48 kHz, 0 trechos pretos, 0 congelados, movimento em todos os frames, pico −2,6 dBFS.
- Passos do áudio disparados pelo instante de contato do pé calculado na animação; rodas giram pela distância percorrida; frenagem com desaceleração constante.

## Não verificado
- `blender/poc_blender.py` passou só em checagem de sintaxe. Nunca foi executado.
