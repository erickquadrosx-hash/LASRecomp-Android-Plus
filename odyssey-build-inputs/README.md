# Odyssey ARM64 — pacotes de compilação (3 partes)

Esta pasta recebe as três partes do ZIP de 65.961.624 bytes preparado a partir dos arquivos já recuperados da conversa.

## Arquivos esperados nesta pasta

| Arquivo | Bytes | SHA-256 |
|---|---:|---|
| `odyssey-inputs.zip.part01` | 22.000.000 | `ed9c148d5e0b8757aba63daa2804bcd8ecfe4b54d60c2439729e2491db4c352a` |
| `odyssey-inputs.zip.part02` | 22.000.000 | `32bdbc2c95f100e4b8c0056e445900e49c6aa5f267115177c7075efe93d7ff6c` |
| `odyssey-inputs.zip.part03` | 21.961.624 | `64cac84d52323e7324ced145066175e59a8346031b2731abcdc133e9c054a352` |

SHA-256 do ZIP completo: `dbbf3c8f6463fcea3c7d760e7849a7988fa6361f5070344930a90654d899f022`.

## Fluxo automático

1. A pessoa responsável adiciona os três arquivos **nesta pasta e nesta ramificação**.
2. O GitHub Actions é iniciado por um push em `odyssey-build-inputs/**`.
3. O runner reúne as partes, confere SHA-256 e extrai apenas os arquivos de código C/SDK gerado e os objetos ARM64 necessários.
4. O compilador do Android gera uma nova `libsmo.so` a partir do runtime com o patch Vulkan. Somente então o APK é assinado e publicado como artefato.

Somente os arquivos gerados para o jogo são necessários, **não envie chaves de console, credenciais, saves ou dados pessoais**.

**Aviso de direitos:** este repositório é público. Compartilhe conteúdo derivado do jogo apenas se possuir os direitos/permissões necessários. Se não puder publicar, use repositório privado.

## Upload pelo navegador do celular

Abra a pasta no GitHub, escolha Add file > Upload files e selecione as três partes. Mantenha os nomes exatamente como listados acima. Confirme o commit na ramificação `odyssey-mali-g720-pipeline-20261107`.

Local do workflow: `.github/workflows/odyssey-mali-g720-native.yml`.
