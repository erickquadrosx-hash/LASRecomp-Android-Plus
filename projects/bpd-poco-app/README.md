# BPD POCO X7 Pro Tools (v0.1 experimental)

Este projeto compila um **APK auxiliar de diagnostico e configuracao**, NAO o Pokemon Brilliant Diamond ou uma modificacao interna do `bpdpkg1.1.apk`.

## Funcionalidades
- Mostra modelo do aparelho, SoC, RAM aproximada e presenca de feature Vulkan;
- Encontra aplicativos instalados com nomes relacionados a BPD/Pokemon/Brilliant Diamond;
- Abre o APK original instalado (quando o Android permite);
- Recomenda perfis de 30 FPS e resolucoes para o POCO X7 Pro;
- Copia comandos ADB opcionais para escalonamento de tela, com restauracao;
- Preserva APK original, saves e `BDP_MOBILE_DATA.zip`.

## Instalacao
1. Abra GitHub > Actions > BPD POCO X7 Pro - APK auxiliar > execucao concluida.
2. Baixe o artefato `BPD-POCO-X7-Pro-Tools-v0.1-debug` e extraia o ZIP.
3. Instale `app-debug.apk` no Android apos confirmar a origem e assinatura.
4. Deixe o BPD Mobile 1.1 instalado separadamente com dados importados.
5. Abra BPD POCO Tools e identifique o pacote do BPD Mobile.
6. Opcional: copie os comandos ADB para um PC com Platform-Tools.

**Limites:** o app nao pode mudar as configuracoes internas do jogo, substituir drivers, alterar FPS diretamente nem aplicar `adb shell` sem permissao especial. Android pode nao suportar o comando `cmd game set` no firmware. A opcao de escala Android nao equivale a resolucao interna do Unity.

**Sem distribuicao de assets do jogo:** todo o codigo aqui e independente.
