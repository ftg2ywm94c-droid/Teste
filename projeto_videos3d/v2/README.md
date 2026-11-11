# v2 — produção de vídeos 3D no Blender (Cycles)

Fluxo: **tema → roteiro aprovado → MP3 do usuário → animação guiada pelo áudio → render → som + legenda → MP4 + QC**.

## Preparar um container novo
```
bash tools/setup_env.sh            # Blender 4.2.3 LTS, libEGL, numpy/scipy/opencv, faster-whisper
python3 tools/fetch_polyhaven.py   # assets CC0 (texturas, céu HDRI, árvores, arbustos, postes, bola) -> assets/polyhaven
python3 v2/make_textures.py        # rostos dos personagens e placas (desenhados por código)
```

## Do MP3 ao MP4 (vídeo 01 como exemplo)
```
python3 scripts/transcribe.py narracao/01_narracao.mp3 analysis/narracao/01_words.json medium   # tempo de cada palavra
python3 v2/captions.py roteiros/01_distancia_de_parada.md analysis/narracao/01_words.json v2/out/legenda.ass
bash v2/preview_all.sh                                      # prévia em movimento 180x320 -> v2/preview/preview.mp4 (~17 min)
bash v2/stills.sh "C:400 H:1700" /tmp/folha.png             # quadros de checagem
setsid nohup bash v2/render_all.sh > v2/frames/render.log 2>&1 &   # render final 720x1280, retomável (~15 s/quadro em 4 núcleos)
python3 v2/audio.py                                         # efeitos + música sintetizados a partir da cinemática
python3 v2/assemble.py                                      # 1080x1920 (ampliado), legenda, voz original, ducking, -14 LUFS
python3 v2/qc.py v2/out/01_distancia_de_parada_1080x1920.mp4
```

## Arquivos
| Arquivo | Papel |
|---|---|
| `lib/story.py` | Física da história (reação 1,5 s; 7 m/s²), trajetória do menino e da bola, checagem de colisão. Sem Blender. |
| `shots.py` | Os planos: intervalo na narração, mapa tempo-da-narração → tempo-da-história (câmera lenta/congelado), câmera. |
| `lib/build.py` | Cena: materiais PBR (Poly Haven), rua, casas, cercas, carro procedural, personagens com armature, rótulos 3D. |
| `render.py` | Monta a cena, anima um plano quadro a quadro e renderiza (prévia ou final). Pula quadros prontos. |
| `audio.py` | Design sonoro dirigido pelos mesmos dados da animação. |
| `captions.py` | Legenda ASS a partir do texto aprovado + tempos do Whisper (alinhamento palavra a palavra). |
| `assemble.py`, `qc.py` | Montagem final e controle de qualidade (inclui checagem de que a narração não foi deslocada nem acelerada). |

## Para um tema novo
1. Roteiro em `roteiros/NN_tema.md` (seção "Narração").
2. Física/trajetórias em `lib/story.py` (ou um módulo novo) e planos em `shots.py`, amarrados aos tempos de `analysis/narracao/NN_words.json`.
3. Reaproveitar `lib/build.py` (rua, carro, personagens) e acrescentar cenários/modelos conforme o tema.
