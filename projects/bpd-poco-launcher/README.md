# BPD POCO Launcher v0.2 (Android)

Um **launcher auxiliar** para abrir o port Android de Pokémon Brilliant Diamond (BPD Mobile) já instalado e orientar a importação do arquivo BDP_MOBILE_DATA.zip.

Não é um emulador, não executa NSP/XCI/PKG diretamente e não inclui o motor gráfico, as texturas, o áudio ou quaisquer dados do jogo. Não distribua o ZIP de dados pelo repositório.

## Recursos

- Botão **JOGAR AGORA** chama o Android para abrir o aplicativo BPD Mobile instalado, com seu package name real.
- Identificação automática de apps instalados com nome BPD, BDSP, Diamond, Brilliant, Pokémon; permite package name manual.
- Seletor seguro do ZIP via Android Storage Access Framework: **apenas salva o nome e a referência**, não extrai, importa ou transfere o conteúdo.
- Botão **Abrir BPD Mobile para importar os dados**: abre o port original, que é quem implementa a importação real.
- Perfis de referência para **POCO X7 Pro / Mali-G720**: equilibrado 30 FPS e desempenho 30 FPS.
- Comandos ADB opcionais (copiar) de downscale externo, com opção de restauração. Depende do suporte real de Android/HyperOS e não é aplicado pelo launcher.
- Diagnóstico básico do aparelho.
- Aplicativo independente, sem root, sem rede, sem permissões sensíveis.

## Como compilar
GitHub Actions: fluxo **BPD POCO X7 Pro - Launcher Android**. APK de depuração no artefato **BPD-POCO-X7-Pro-Launcher-v0.2-debug**.

## Como usar
1. Instale seu APK original de BPD Mobile.
2. Se ainda não importou os dados, mantenha **BDP_MOBILE_DATA.zip** no aparelho.
3. Instale o APK deste launcher.
4. Abra o launcher e toque em **Localizar BPD Mobile instalado**.
5. Selecione o jogo e, se necessário, abra-o para **importar o ZIP com o seletor interno do jogo**.
6. Volte ao launcher e toque em **JOGAR AGORA**.

**Limites:** não testado diretamente num POCO X7 Pro. A taxa de FPS não é garantida. Não modifica os assets nem as bibliotecas do port original. A seleção do ZIP aqui não substitui sua importação no jogo.

## Privacidade
Não contém chaves, ROM, licença proprietária ou arquivos do jogo. Não faz upload de nenhum dado nem usa Internet. Acesso ao arquivo é uma autorização local de leitura.
