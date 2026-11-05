# BPD POCO ROM Launcher v0.3

Aplicativo auxiliar para Android/POCO X7 Pro, com duas maneiras de jogar:
1. Abrir o BPD Mobile instalado, que importa separadamente BDP_MOBILE_DATA.zip.
2. Organizar arquivos .NSP e .XCI locais e pedir que um emulador Android instalado os abra.

## Biblioteca NSP/XCI
- Botão "ABRIR BIBLIOTECA DE ROMS" no menu principal.
- Escolha ROMs locais com o seletor de arquivos oficial do Android (ACTION_OPEN_DOCUMENT).
- Mantém uma biblioteca de URIs de arquivos selecionados, com permissões persistentes de leitura quando disponíveis. Não copia jogos, não usa permissão ampla de armazenamento e não altera os arquivos.
- Mostra nome, formato, tamanho e opções Jogar ou Remover.
- "Jogar ROM" envia URI content:// com permissão temporária ao emulador Android instalado.
- Preferência: Automático, Eden, Citron, Yuzu, Sudachi ou "Escolher aplicativo Android".
- Compatibilidade do lançamento direto varia conforme emulador, versão e provedor de arquivos.

## Como usar
1. Instale um emulador compatível e faça a configuração exigida por ele com os seus próprios arquivos legalmente obtidos.
2. Instale o APK deste launcher.
3. Toque em ABRIR BIBLIOTECA DE ROMS e Adicionar NSP / XCI.
4. Selecione seu arquivo no armazenamento do celular.
5. Escolha o emulador e toque em JOGAR ROM.

O launcher não consegue emular Switch sozinho. Não processa nem converte ROMs, não fornece firmware, keys, assets, nem garante que um jogo rode no POCO X7 Pro. O jogo original BPD Mobile continua independente.

## Build
Workflow: BPD POCO X7 Pro - ROM Launcher.
Artefato: BPD-POCO-X7-Pro-ROM-Launcher-v0.3-debug.

Nota: usa novo applicationId para poder ser instalado ao lado da v0.2, pois as assinaturas debug do GitHub Actions podem variar por runner.
