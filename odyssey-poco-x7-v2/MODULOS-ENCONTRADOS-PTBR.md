# Odyssey POCO X7 Pro — módulos públicos incorporados (07/11/2026)

## Situação verificada

**Repositório de trabalho:** ramo isolado `odyssey-poco-x7pro-v2-20261107` (a branch `main` do LASRecomp não foi alterada).

### Disponíveis, adicionados ou automatizados

| Componente | Local nesta branch | Origem |
| --- | --- | --- |
| Renderizador NVN → Vulkan, shaders e cache | `odyssey-poco-x7-v2/upstream/runtime/` | Deez-coder/SMO-android-port, **B0.2** |
| Lifter ARM64 → C e geradores do SDK | `odyssey-poco-x7-v2/upstream/tools/lifter/` | Mesmo submódulo |
| Scripts de compilação de biblioteca e APK | `odyssey-poco-x7-v2/upstream/tools/android/` | Mesmo submódulo |
| Decodificação BC4/BC5 com menos buffers | `odyssey-poco-x7-v2/apply_native_v2.py` | Patch V2, aplicado após checkout |
| Proteção de alocação da textura | Mesmo arquivo | Patch V2 |
| Meta Android ADPF de 30/60 FPS | Mesmo arquivo | Patch V2 |
| Comparação dos decodificadores (8.000 casos) | `odyssey-poco-x7-v2/test_bc45_against_upstream.py` | Teste público sem arquivos do jogo |
| Instalação do submódulo e verificações | `.github/workflows/odyssey-v2-public-modules.yml` | GitHub Actions |
| Shaderc / glslang / SPIRV-Tools | Fontes incluídas no **Android NDK 28.2.13676358**; scripts em `upstream/tools/android/build_shaderc.py` | Google Android NDK e projeto shaderc |

O submódulo usa o commit fixo **4f71d3d67bdfb87f08449994ac64dcc8a7d18f28** correspondente à tag B0.2. Isso impede que mudanças futuras em `main` alterem silenciosamente a compilação.

**Não foram encontrados para redistribuição pública:** `build/android/lift/main/*.c`, `build/android/arm64-v8a/obj/main/*.obj` (aprox. 257 objetos), `build/android/gen/*`, dumps `main.elf`/`sdk.elf`, chaves e assets do jogo. São gerados **a partir da sua cópia da versão 1.0.0**. O APK original de 24 MB contém `libsmo.so` já linkado, mas não os objetos ou o código C gerado para efetuar o relink.

Nenhum arquivo do jogo é procurado em sites de terceiros nem incluído no repositório público.

## Como obter os módulos públicos

```bash
git clone --branch odyssey-poco-x7pro-v2-20261107 --recurse-submodules https://github.com/erickquadrosx-hash/LASRecomp-Android-Plus.git
cd LASRecomp-Android-Plus
git submodule update --init --recursive
python odyssey-poco-x7-v2/apply_native_v2.py odyssey-poco-x7-v2/upstream
python odyssey-poco-x7-v2/apply_native_v2.py odyssey-poco-x7-v2/upstream --write
```

A primeira chamada verifica compatibilidade; a segunda aplica as correções nativas. O script salva backups `*.x7backup`, edita apenas texturas/memória/ADPF e **não altera as comparações de profundidade nem a sincronização Vulkan**.

## Compilação com sua própria cópia do jogo — somente no seu PC

1. Instale Python 3, JDK 17, Android SDK plataforma 35 e Android NDK **28.2.13676358**. Configure `ANDROID_HOME` e `ANDROID_NDK`; o build também necessita dos módulos Python descritos no `BUILDING.md` do submódulo.
2. A partir da sua cópia própria de Odyssey **1.0.0**, gere os ELF `main.elf` e `sdk.elf` (e outros módulos disponíveis) usando as ferramentas do port. Se o jogo foi importado no Android, esses ELF podem existir em `Android/data/com.mobileodyssey.game/files/dump/base/elf`; o acesso depende das restrições do Android.
3. Execute **no computador**, com os arquivos privados apenas no disco local:

```bash
python odyssey-poco-x7-v2/build_with_owned_game.py --owned-elf-dir "/CAMINHO/PARA/SEUS/ELF" --jobs 6
```

O script copia os ELF somente para a pasta `build/` ignorada pelo Git, gera a lista de funções, traduz as instruções para C, gera as tabelas, compila shaderc, compila os módulos ARM64 e tenta linkar `libsmo.so` e criar o APK. Esse fluxo **não foi executado de ponta a ponta com arquivos reais** neste ambiente; pode precisar de outras dependências locais apontadas pelo projeto original.

**Não execute isso em GitHub Actions de um repositório público com chaves ou dumps:** os logs e artefatos precisam permanecer privados. Para instalar o APK recompilado, preserve antes o save, a assinatura e a versão estável.

## Links de referência

- Port 1.0.0 (fonte principal): https://github.com/Deez-coder/SMO-android-port
- Instruções de build: https://github.com/Deez-coder/SMO-android-port/blob/B0.2/BUILDING.md
- Recompilador de referência: https://github.com/Coz-0/smo-recomp (atualmente usa outra versão do jogo)
- Outro port Android: https://github.com/nepotira/smo-recomp-android (versão 1.4.1, **incompatível** com os módulos 1.0.0)
- Shaderc: https://github.com/google/shaderc
- Android NDK: https://developer.android.com/ndk/downloads
