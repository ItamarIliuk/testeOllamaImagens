# Teste Ollama GUI

Aplicação simples em Python que demonstra como enviar uma imagem e um prompt de texto para o modelo multimodal `llava` disponível no Ollama, por meio de uma interface gráfica.

## Requisitos

- Python 3.10 ou superior
- [Ollama](https://ollama.com/) instalado e executando o modelo `llava`
- Bibliotecas Python necessárias:

```powershell
pip install ollama pillow
```

## Como usar

1. Inicie o servidor do Ollama e certifique-se de que o modelo `llava` está disponível.
2. Execute o aplicativo:

```powershell
python multimodalchat.py
```

3. Na janela da aplicação:
   - Escreva ou ajuste o prompt na área de texto.
   - Clique em **Selecionar imagem** para escolher o arquivo a ser analisado e confira a miniatura gerada.
   - Pressione **Analisar imagem** para enviar o prompt e a imagem ao modelo.
4. Cada resultado fica salvo no painel de **Histórico**. Clique em um item para revisar respostas anteriores.
5. Aguarde a resposta atual, exibida no painel à direita.

## Notas

- O processamento do modelo pode levar alguns segundos. Os botões ficam desativados enquanto a requisição está em andamento.
- Mensagens de erro são exibidas quando o prompt está vazio ou quando nenhum arquivo de imagem é selecionado.
- Se a imagem for muito grande, apenas uma miniatura redimensionada é exibida na área de pré-visualização.
