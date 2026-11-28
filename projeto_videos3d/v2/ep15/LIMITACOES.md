# Limitações conhecidas — vídeo 15 (Você decide · O último ônibus · Parte 2)

- Resolução: render nativo em 1080x1920 na skill Xavier (Remotion + three.js, `teste_xavier/src/videos/onibus2/`, composição `Onibus2Short`), 30 fps, 2279 quadros, sem ampliação. Títulos (`mograph.py`) e legenda também desenhados em 1080x1920.
- História de ficção em segunda pessoa, sem fatos reais nem números. Aviso "história de ficção" na tela no começo.
- Ônibus, empresa, linha e garagem são genéricos: o letreiro diz só "NOTURNO" / "FORA DE SERVIÇO", e a placa da garagem diz só "GARAGEM".
- Continuidade com o Ep. 1: mensagens às 00:11, 00:12 e 00:13; a nova ("BOA ESCOLHA. AGORA NÃO OLHA PRO RETROVISOR.") é às 00:16. No chat aparecem só as 2 últimas mensagens, para a mão não cobrir a nova.
- O passageiro do banco do fundo é uma pessoa comum sentada (boné, jaqueta escura, expressão séria), no lugar da silhueta preta da primeira versão, a pedido do usuário. Não faz nada nem é mostrado de perto.
- Narração: MP3 do usuário (`narracao/15_narracao.mp3`, 75,96 s), sem mudança de velocidade e sem cortes. A transcrição (faster-whisper) bate palavra por palavra com o roteiro.
- Som: efeitos sintetizados (motor seguindo a velocidade, cliques das lâmpadas, lâmpada do fundo piscando, grilos na rua escura, zumbido das lâmpadas de sódio, porta pneumática, freio, vibração e toque genérico do celular, contagem, passos) e trilha de tensão (`lib/tensao.py`, 24 deixas). Nenhum toque de fabricante.
- Avisos novos (dado do Instagram do Ep. 1: metade sai por volta dos 36 s): "no final, você decide de novo" (3,6–8 s) e "no final: A ou B" (28–40 s). Ainda não medidos.
- O motorista continua só de costas e pelos olhos no retrovisor; a fala "ÚLTIMA PARADA" aparece como texto na tela.
- Revisão 2 (pedido do usuário): saiu a pergunta fixa do topo "PRA ONDE ELE TÁ INDO?". O aviso "NO FINAL: A OU B" (28–40 s) passou para o lugar dela, no topo, com fundo escuro. Versão anterior: `v2/ep15/mograph_v1_bak.py` e `v2/ep15/out/15_ultimo_onibus_parte2_v1_com_pergunta.mp4` (local, fora do git). QC da revisão aprovado (mesmos valores).
