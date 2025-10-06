import base64
import threading
import tkinter as tk
from datetime import datetime
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from ollama import chat
from PIL import Image, ImageTk


class MultimodalChatApp:
  def __init__(self) -> None:
    self.root = tk.Tk()
    self.root.title("Analisador de Imagens com Ollama")
    self.root.geometry("600x500")

    self.image_path: Path | None = None
    self.preview_photo: ImageTk.PhotoImage | None = None
    self.history: list[dict[str, str]] = []

    self._build_ui()

  def _build_ui(self) -> None:
    main_frame = ttk.Frame(self.root, padding=16)
    main_frame.pack(fill=tk.BOTH, expand=True)

    prompt_label = ttk.Label(main_frame, text="Prompt")
    prompt_label.pack(anchor=tk.W)

    self.prompt_text = tk.Text(main_frame, height=5, wrap=tk.WORD)
    self.prompt_text.insert(
      tk.END,
      "Descreva com detalhes o conteúdo desta imagem.",
    )
    self.prompt_text.pack(fill=tk.X, pady=(0, 12))

    image_frame = ttk.Frame(main_frame)
    image_frame.pack(fill=tk.X, pady=(0, 12))

    self.image_path_var = tk.StringVar(value="Nenhuma imagem selecionada.")
    image_label = ttk.Label(image_frame, textvariable=self.image_path_var)
    image_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))

    self.select_button = ttk.Button(
      image_frame,
      text="Selecionar imagem",
      command=self.select_image,
    )
    self.select_button.pack(side=tk.RIGHT)

    preview_frame = ttk.LabelFrame(main_frame, text="Pré-visualização", padding=12)
    preview_frame.pack(fill=tk.BOTH, expand=False, pady=(0, 12))

    self.preview_label = ttk.Label(
      preview_frame,
      text="Nenhuma imagem carregada",
      anchor=tk.CENTER,
      justify=tk.CENTER,
    )
    self.preview_label.pack(fill=tk.BOTH, expand=True)

    self.run_button = ttk.Button(
      main_frame,
      text="Analisar imagem",
      command=self.analyze_image,
    )
    self.run_button.pack(fill=tk.X)
    history_frame = ttk.LabelFrame(main_frame, text="Histórico", padding=12)
    history_frame.pack(fill=tk.BOTH, expand=True)

    list_frame = ttk.Frame(history_frame)
    list_frame.pack(side=tk.LEFT, fill=tk.Y, expand=False, padx=(0, 12))

    self.history_list = tk.Listbox(list_frame, height=10)
    self.history_list.pack(side=tk.LEFT, fill=tk.Y)
    self.history_list.bind("<<ListboxSelect>>", self._on_history_select)

    scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.history_list.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    self.history_list.configure(yscrollcommand=scrollbar.set)

    response_frame = ttk.Frame(history_frame)
    response_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    response_label = ttk.Label(response_frame, text="Resposta")
    response_label.pack(anchor=tk.W)

    self.response_text = tk.Text(response_frame, height=12, wrap=tk.WORD, state=tk.DISABLED)
    self.response_text.pack(fill=tk.BOTH, expand=True)

    self.status_var = tk.StringVar(value="Pronto")
    status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
    status_bar.pack(fill=tk.X, side=tk.BOTTOM)

  def select_image(self) -> None:
    file_path = filedialog.askopenfilename(
      title="Selecione uma imagem",
      filetypes=[
        ("Imagens", "*.png;*.jpg;*.jpeg;*.bmp;*.gif"),
        ("Todos os arquivos", "*.*"),
      ],
    )

    if file_path:
      self.image_path = Path(file_path)
      self.image_path_var.set(str(self.image_path))
      self._show_image_preview(self.image_path)
    else:
      self.image_path = None
      self.image_path_var.set("Nenhuma imagem selecionada.")
      self._clear_image_preview()

  def analyze_image(self) -> None:
    prompt = self.prompt_text.get("1.0", tk.END).strip()
    if not prompt:
      messagebox.showwarning("Prompt vazio", "Digite um prompt para a análise.")
      return

    if not self.image_path or not self.image_path.exists():
      messagebox.showwarning(
        "Imagem não encontrada",
        "Selecione uma imagem válida antes de iniciar a análise.",
      )
      return

    self._set_running_state(True)
    self._write_response("Processando...")
    threading.Thread(target=self._run_analysis, args=(prompt, self.image_path), daemon=True).start()

  def _run_analysis(self, prompt: str, image_path: Path) -> None:
    try:
      img_b64 = base64.b64encode(image_path.read_bytes()).decode()
      response = chat(
        model="llava",
        messages=[
          {
            "role": "user",
            "content": prompt,
            "images": [img_b64],
          }
        ],
      )

      content = getattr(response.message, "content", str(response))
      self.root.after(0, lambda: self._write_response(content))
      self.root.after(0, lambda: self._append_history(prompt, content))
      self.root.after(0, lambda: self.status_var.set("Análise concluída."))
    except Exception as exc:  # pylint: disable=broad-except
      self.root.after(
        0,
        lambda: self._write_response(f"Ocorreu um erro durante a análise:\n{exc}"),
      )
      self.root.after(0, lambda: self.status_var.set("Erro"))
    finally:
      self.root.after(0, lambda: self._set_running_state(False))

  def _write_response(self, text: str) -> None:
    self.response_text.configure(state=tk.NORMAL)
    self.response_text.delete("1.0", tk.END)
    self.response_text.insert(tk.END, text)
    self.response_text.configure(state=tk.DISABLED)

  def _set_running_state(self, running: bool) -> None:
    state = tk.DISABLED if running else tk.NORMAL
    self.run_button.configure(state=state)
    self.select_button.configure(state=state)
    self.status_var.set("Analisando..." if running else "Pronto")

  def _show_image_preview(self, image_path: Path) -> None:
    try:
      image = Image.open(image_path)
      image.thumbnail((250, 250))
      self.preview_photo = ImageTk.PhotoImage(image)
      self.preview_label.configure(image=self.preview_photo, text="")
    except Exception as exc:  # pylint: disable=broad-except
      self.preview_photo = None
      self.preview_label.configure(text=f"Não foi possível carregar a imagem:\n{exc}", image="")

  def _clear_image_preview(self) -> None:
    self.preview_photo = None
    self.preview_label.configure(text="Nenhuma imagem carregada", image="")

  def _append_history(self, prompt: str, response: str) -> None:
    timestamp = datetime.now().strftime("%H:%M:%S")
    summary = f"[{timestamp}] {prompt[:40]}" + ("..." if len(prompt) > 40 else "")
    self.history.append({"prompt": prompt, "response": response, "timestamp": timestamp})
    self.history_list.insert(tk.END, summary)
    last_index = self.history_list.size() - 1
    self.history_list.selection_clear(0, tk.END)
    self.history_list.selection_set(last_index)
    self.history_list.activate(last_index)
    self.history_list.see(last_index)

  def _on_history_select(self, event: tk.Event) -> None:  # type: ignore[attr-defined]
    selection = event.widget.curselection()
    if not selection:
      return
    index = selection[0]
    if 0 <= index < len(self.history):
      item = self.history[index]
      self._write_response(item["response"])


  def run(self) -> None:
    self.root.mainloop()


if __name__ == "__main__":
  MultimodalChatApp().run()