# PanVK G720 AHB — compilação experimental

**Não é uma versão testada em dispositivo.** Corrige experimentalmente a troca de buffers externos `AHardwareBuffer` do PanVK 26.3.1 com as GPUs Mali-G720. O log do POCO X7 Pro termina em `vkCreateSwapchainKHR` com `-1000072003`, que significa `VK_ERROR_INVALID_EXTERNAL_HANDLE`.

Todas as modificações são isoladas desta branch experimental. A versão aprovada `approved-poco-x7-pro-v1.2.0` e seu APK permanecem intactos.

A compilação automatizada deve publicar um artefato `PanVK_G720_AHB_Experimental_Android_ARM64.zip` cujo ZIP interno contém `meta.json` e `libvulkan_panfrost.so`. **O arquivo só é um driver se houver compilação bem-sucedida**. Hardware não validado. Em caso de crash, volte a `Driver da GPU: Sistema`, sem apagar saves.
