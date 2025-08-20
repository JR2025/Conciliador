import threading
import tkinter as tk
from tkinter import filedialog, messagebox
from back import process_all

class App:
    def __init__(self, master):
        self.master = master
        master.title('Conciliador de Guias e Comprovantes')

        # Campos de seleção de pastas
        tk.Label(master, text='Pasta de Guias:').grid(row=0, column=0, padx=5, pady=5, sticky='e')
        self.guides_entry = tk.Entry(master, width=50)
        self.guides_entry.grid(row=0, column=1, padx=5, pady=5)
        tk.Button(master, text='Selecionar', command=self.select_guides).grid(row=0, column=2, padx=5)

        tk.Label(master, text='Pasta de Comprovantes:').grid(row=1, column=0, padx=5, pady=5, sticky='e')
        self.receipts_entry = tk.Entry(master, width=50)
        self.receipts_entry.grid(row=1, column=1, padx=5, pady=5)
        tk.Button(master, text='Selecionar', command=self.select_receipts).grid(row=1, column=2, padx=5)

        tk.Label(master, text='Pasta de Saída:').grid(row=2, column=0, padx=5, pady=5, sticky='e')
        self.output_entry = tk.Entry(master, width=50)
        self.output_entry.grid(row=2, column=1, padx=5, pady=5)
        tk.Button(master, text='Selecionar', command=self.select_output).grid(row=2, column=2, padx=5)

        # Botão iniciar
        self.start_button = tk.Button(master, text='Iniciar Conciliação', command=self.start_process)
        self.start_button.grid(row=3, column=1, pady=15)

    def select_guides(self):
        path = filedialog.askdirectory()
        if path:
            self.guides_entry.delete(0, tk.END)
            self.guides_entry.insert(0, path)

    def select_receipts(self):
        path = filedialog.askdirectory()
        if path:
            self.receipts_entry.delete(0, tk.END)
            self.receipts_entry.insert(0, path)

    def select_output(self):
        path = filedialog.askdirectory()
        if path:
            self.output_entry.delete(0, tk.END)
            self.output_entry.insert(0, path)

    def start_process(self):
        guides_dir = self.guides_entry.get()
        receipts_dir = self.receipts_entry.get()
        output_dir = self.output_entry.get()
        if not (guides_dir and receipts_dir and output_dir):
            messagebox.showerror('Erro', 'Preencha todas as pastas antes de iniciar.')
            return

        # Desabilita botão para evitar múltiplos cliques
        self.start_button.config(state='disabled')
        # Inicia o processamento em thread separada
        thread = threading.Thread(
            target=self.run_backend,
            args=(guides_dir, receipts_dir, output_dir),
            daemon=True
        )
        thread.start()

    def run_backend(self, guides_dir, receipts_dir, output_dir):
        try:
            process_all(guides_dir, receipts_dir, output_dir)
            # Atualiza UI na thread principal
            self.master.after(0, lambda: messagebox.showinfo('Concluído', 'Processamento finalizado!'))
        except Exception as e:
            self.master.after(0, lambda: messagebox.showerror('Erro', f'Falha no processamento: {e}'))
        finally:
            # Reabilita botão
            self.master.after(0, lambda: self.start_button.config(state='normal'))

if __name__ == '__main__':
    root = tk.Tk()
    app = App(root)
    root.mainloop()
