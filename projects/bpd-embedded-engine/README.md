# BPD POCO Integrated Core — v0.4 experimental

Este projeto integra um **launcher Pokémon no mesmo APK Android ARM64 que compila o núcleo C++ do emulador Lemon Lite**. O APK passa a oferecer biblioteca NSP/XCI e emulação em um único aplicativo, sem depender de um emulador instalado separadamente.

**Não é um port nativo do Pokémon Brilliant Diamond.** A aplicação é ARM64 nativa; o hardware e os serviços do Nintendo Switch continuam emulados pelo Lemon.

## Origem e licenciamento
- Núcleo de código aberto [Lemon Project](https://github.com/Ghael-V/Lemon-Project), sob GPL-3.0-or-later.
- Fonte upstream fixada em commit: 891be721eea35e0c075ed0d99e6b4f48a0a7843e.
- Launcher Java e script de integração também sob GPL-3.0-or-later.
- Mantém o código-fonte e avisos/licenças originais do Lemon. Se distribuir o APK modificado, disponibilize o código-fonte correspondente e todos os créditos exigidos pelas licenças.

## Recursos
- Tela inicial personalizada BPD POCO Core.
- Importação de referências de ROMs NSP/XCI pelo seletor oficial de arquivos Android (SAF).
- Biblioteca local com botões Jogar / Remover.
- Execução pela EmulationActivity **interna**, nativa do núcleo Lemon; sem intenção de abrir outro aplicativo.
- Acesso às configurações completas do emulador Lemon pela tela inicial.
- Build flavor Lite (sem aplicativo spoof de benchmark), GPU Mali, ARM64, Vulkan.
- Nome de pacote único: br.com.bdpmobile.pocoembedded.

## Limites e uso responsável
- Não inclui ROMs, jogos, chaves prod.keys, firmware, dump de console, SDK proprietário ou dados do Pokémon.
- O usuário precisa configurar separadamente os arquivos obtidos legalmente em seu próprio console.
- Não permite ignorar proteção, não fornece chaves nem burla.
- O desempenho pode variar; 30 FPS e resolução 1× são apenas pontos de partida, não parâmetros aplicados automaticamente.
- A aplicação não foi testada num POCO X7 Pro físico.
- Dependências Android SDK/NDK e C++ tornam a compilação demorada e sujeita a falhas de terceiros.

## GitHub Actions
No repositório de desenvolvimento, abra **Actions > BPD POCO Integrated ARM64 Emulator**, ramificação `experiment/bpd-poco-x7pro-embedded-emulator-v04`. Quando o job terminar com sucesso, baixe o artifact `BPD-POCO-Integrated-Core-v0.4-ARM64`, extraia o APK e instale.

O processo de compilação:
1. Faz checkout da ramificação experimental.
2. Clona a fonte GPL do Lemon e fixa a revisão.
3. Aplica o launcher Java e as alterações de nome de pacote.
4. Compila Kotlin/Java + motor C++ via Gradle/CMake/NDK para arm64-v8a.
5. Só publica APK se houver arquivo válido com biblioteca nativa .so.

Para testar Brilliant Diamond, adicione seu dump NSP/XCI, configure o emulador e use JOGAR no aplicativo.
