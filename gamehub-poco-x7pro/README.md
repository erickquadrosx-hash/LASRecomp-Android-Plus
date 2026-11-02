# GameHub 6.3.2 — POCO X7 Pro (experimental)

**Projeto de teste pessoal, não oficial; sem afiliação com a GameSir.**

Esta compilação **não** modifica código de driver Vulkan, configuração GPU Mali, DXVK, Wine/Proton/FEX ou o mecanismo de emulação do GameHub. A única modificação é de **empacotamento e carregamento de bibliotecas nativas**: converte as 25 bibliotecas `lib/arm64-v8a/*.so` de DEFLATED para STORED, alinha os dados em páginas de 16 KiB e troca `android:extractNativeLibs` de `true` para `false` no manifesto binário. Isso permite que o Android tente carregar essas bibliotecas diretamente do APK sem extrair cópias para a pasta de instalação. Pode reduzir o espaço utilizado após instalação, mas aumenta o tamanho do APK. O ganho de desempenho é **não comprovado**.

## Versão de origem e validação

- Arquivo do usuário: `GameHub_6.3.2_b8cc9d9f2bdfbc5eaf91799a5ea69c10.apk`.
- SHA-256 obrigatório do APK de origem: `e51456bd3fb1c041dbdf3c756878ce1ddb37dfdb933b266142b22354b7d50ed2`.
- Pacote original `com.xiaoji.egggame`, versão `6.3.2`, código 143, minSdk 29, targetSdk 36.
- Testes feitos localmente: alteração binária do manifesto, 25 arquivos ELF em ARM64, 16 KiB de alinhamento ZIP, CRC de todos os arquivos ZIP, assinatura APK v2 criada e validada por implementação de referência Python.
- **Não testado em Android real.** A assinatura alterada invalida atualização direta sobre o APK oficial; fazer backup antes de qualquer eventual desinstalação.
- O aplicativo pode realizar checagem de integridade e impedir o funcionamento de builds modificadas; não há garantia de compatibilidade.

## Build local

Python 3, sem dependências para o patch (apenas bibliotecas padrão):

```bash
python3 repack.py GameHub_6.3.2_original.apk GameHub_poco_unsigned.apk
```

Para assinar, prefira o `zipalign` e `apksigner` oficiais do Android SDK:

```bash
zipalign -P 16 -f 4 GameHub_poco_unsigned.apk GameHub_poco_aligned.apk
apksigner sign --ks minha_chave_privada.jks --out GameHub_poco_signed.apk GameHub_poco_aligned.apk
apksigner verify --verbose GameHub_poco_signed.apk
```

Uma assinatura diferente da oficial exige instalação separada após desinstalar o GameHub antigo (mesmo package ID). Isso pode apagar contas, downloads, bibliotecas e jogos, portanto **faça backup completo antes**.

## GitHub Actions

O arquivo `.github/workflows/gamehub-poco-x7pro.yml` permite baixar uma cópia do APK-base de URL HTTPS fornecida manualmente na página **Actions → Build GameHub Poco X7 Pro → Run workflow**. É obrigatório o SHA-256 exato, que é verificado antes de qualquer transformação. O workflow não inclui o APK proprietário nem a chave privada no repositório.

**Assinatura no CI:** a workflow gera uma chave temporária (não publicada) para a compilação de teste. Para instalar atualizações futuras por cima do mesmo APK personalizado, você precisaria manter uma chave privada fixa e configurada em Secrets (o workflow não dá essa garantia).

Para um APK que continua usando recursos proprietários do GameHub, respeite os termos aplicáveis ao download e à redistribuição. Evite publicar APKs modificados sem autorização.

## Perfil manual recomendado para Mali-G720

Em cada jogo, iniciar com driver de GPU do sistema (Vulkan Mali), resolução 1280×720 ou 960×544 e 30 FPS; diminuir efeitos de água e reflexos caso existam artefatos. O perfil de 30 FPS não pode ser forçado pelo reempacotamento do APK.