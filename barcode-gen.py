import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import tkinter.font as tkFont
from pathlib import Path
from fpdf import FPDF
import barcode
from barcode.writer import ImageWriter
import os
import platform


class Barcode:
    def __init__(self, code, description, barcode_format):
        self.code = code
        self.description = description
        self.format = barcode_format
        self.writer_options = {}
        
        format_code = code
        match barcode_format:
            case "ean13":
                format_code = '7' + '0' * (11 - len(code)) + code
                self.writer_options['font_size'] = 10
                self.writer_options['module_width'] = 0.4
                self.writer_options['text_distance'] = 4.6
                self.writer_options['module_height'] = 11.0
            case "code128":
                self.writer_options['font_size'] = 10
                self.writer_options['module_width'] = 0.4
                self.writer_options['text_distance'] = 4.6
                self.writer_options['module_height'] = 11.0
            case "ean14":
                format_code = '17' + '0' * (11 - len(code)) + code
                self.writer_options['module_width'] = 0.6
                self.writer_options['font_size'] = 14
                self.writer_options['text_distance'] = 7
            
        self.barcode = barcode.get_barcode_class(self.format)(format_code)
        self.barcode.writer = ImageWriter()


class BarcodeService:
    def save_barcodes(self, barcodes: list):
        log_file = Path('log.txt')
        output_folder = Path('output')
        
        if not output_folder.exists():
            output_folder.mkdir()
    
        for out_barcode in barcodes:
            output_file = output_folder / f"{out_barcode.code} - {out_barcode.description}"

            out_barcode.barcode.save(
                filename=output_file,
                options=out_barcode.writer_options
            )

            pdf = FPDF('P', unit='mm', format='A4')
            pdf.add_page()
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(0, 0, out_barcode.description, align='C')
            pdf.image(f"{output_file}.png", x=70, y=13, w=70, type="PNG")
            pdf.output(f"{output_file}.pdf", 'F')

            with log_file.open('a') as lf:
                lf.write(f"{out_barcode.code} - {out_barcode.barcode.get_fullcode()} - {out_barcode.description}\n")
        
    def get_barcodes_from_text(self, text: str, barcode_format: str) -> list:
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        barcode_list = []
        for line in lines:
            try:
                code, description = line.split('-')
                barcode_list.append(Barcode(code.strip(), description.strip(), barcode_format))
            except ValueError:
                pass  # ignora linhas inválidas
        return barcode_list


class BarcodeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Gerador de Códigos de Barras")
        self.root.geometry("600x520")

        self.barcode_service = BarcodeService()

        # Seleção de formato
        ttk.Label(root, text="Formato do Código de Barras:").pack(pady=5)
        self.format_var = tk.StringVar()
        self.combo_format = ttk.Combobox(
            root,
            textvariable=self.format_var,
            values=["code128", "ean13", "ean14"],
            state="readonly"
        )
        self.combo_format.current(0)
        self.combo_format.pack(pady=5)

        # Área de texto para códigos
        ttk.Label(root, text="Digite os códigos no formato: CODIGO - DESCRIÇÃO").pack(pady=5)
        self.text_area = tk.Text(root, height=15, width=70, font=("Arial", 12))
        self.text_area.pack(pady=5)

        # Botões
        frame_buttons = ttk.Frame(root)
        frame_buttons.pack(pady=10)

        ttk.Button(frame_buttons, text="Carregar Arquivo", command=self.load_file).grid(row=0, column=0, padx=5)
        ttk.Button(frame_buttons, text="Gerar Códigos", command=self.generate_barcodes).grid(row=0, column=1, padx=5)
        ttk.Button(frame_buttons, text="Abrir Pasta", command=self.open_output_folder).grid(row=0, column=2, padx=5)

    def load_file(self):
        file_path = filedialog.askopenfilename(title="Selecione o arquivo de códigos", filetypes=[("Text Files", "*.txt")])
        if file_path:
            with open(file_path, "r") as f:
                self.text_area.delete("1.0", tk.END)
                self.text_area.insert(tk.END, f.read())

    def generate_barcodes(self):
        text = self.text_area.get("1.0", tk.END)
        barcode_format = self.format_var.get()
        barcodes = self.barcode_service.get_barcodes_from_text(text, barcode_format)

        if not barcodes:
            messagebox.showerror("Erro", "Nenhum código válido encontrado!")
            return

        self.barcode_service.save_barcodes(barcodes)

        self.open_output_folder()

        messagebox.showinfo("Sucesso", f"{len(barcodes)} código(s) gerados na pasta 'output'.")

    def open_output_folder(self):
        output_folder = Path("output").absolute()
        if platform.system() == "Windows":
            os.startfile(output_folder)
        elif platform.system() == "Darwin":
            os.system(f"open {output_folder}")
        else:
            os.system(f"xdg-open {output_folder}")


if __name__ == "__main__":
    root = tk.Tk()

    default_font = tkFont.nametofont("TkDefaultFont")
    default_font.config(family="Arial", size=12)
    root.option_add("*Font", default_font)

    app = BarcodeApp(root)

    root.mainloop()
