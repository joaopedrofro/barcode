try:
    import subprocess
    from fpdf import FPDF
    from pathlib import Path
    import barcode
    from barcode.writer import ImageWriter
    from barcode.base import Barcode
except ImportError as error:
    print("{}\n\nImportError: Para utilizar este script instale \
          as dependências em requirements.txt".format(error))
    print("\t# pip install -r requirements.txt")
    exit(0)


def get_barcodes(code_lines, barcode_format="code128"):
    barcode_list = []
    
    for line in code_lines.copy():
        code, description = line.replace("\n", "").split("-")
        code = code.strip()
        description = description.strip()
        
        if barcode_format == "ean13":
            code = '7' + '0' * (11-len(code)) + code

        barcode_list.append(Barcode(code, description, barcode_format))
    
    return barcode_list


def get_lines_from_file(file) -> list:
    lines = []

    with file.open('r') as arq:
        for line in arq.readlines():
            if line != '':
                lines.append(line.replace('\\n', ''))
                
    return lines


class Barcode:
    def __init__(self, code, description, barcode_format):
        self.code = code
        self.description = description
        self.format = barcode_format
        self.barcodefull = barcode.get_barcode_class(self.format)(self.code)
        self.barcodefull.writer = ImageWriter()


class BarcodeGenerator:
    def generate(self, new_barcode: Barcode):
        log_file = Path('log.txt')
        output_folder = Path('output')
        output_file = output_folder / '{} - {}'.format(new_barcode.code, new_barcode.description)

        if not output_folder.exists():
            output_folder.mkdir()

        new_barcode.barcodefull.save(
            filename=output_file,
            options={
                'module_width': 0.4,
                'module_height': 11.0,
                'font_size': 10,
                'text_distance': 4.6
            }
        )

        pdf = FPDF('P', unit='mm', format='A4')
        pdf.add_page()
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 0, new_barcode.description, align='C')
        pdf.image('{}.png'.format(output_file), x=70, y=13, w=70, type="PNG")
        pdf.output('{}.pdf'.format(output_file), 'F')

        with log_file.open('a') as lf:
            lf.write('{} - {} - {}\n'.format(
                new_barcode.code,
                new_barcode.barcodefull.get_fullcode(),
                new_barcode.description)
            )


if __name__ == '__main__':
    print("Escolha o formato do código de barras a ser gerado: \n")
    
    for i, v in enumerate(barcode.PROVIDED_BARCODES):
        print("{} - {}".format(i, v))
        
    barcode_format = ""
    
    try:
        barcode_format = barcode.PROVIDED_BARCODES[int(input("\nDigite: "))]
    except IndexError or ValueError:
        print("Valor inválido!")
        input()
        exit(0)
    
    input_file = Path('codigos.txt')
    
    if not input_file.exists():
        input_file.touch()

    subprocess.run(['notepad.exe', input_file])
    
    lines = get_lines_from_file(input_file)
    
    barcode_generated_list = get_barcodes(lines, barcode_format)

    barcode_generator = BarcodeGenerator()

    for new_barcode in barcode_generated_list:
        barcode_generator.generate(new_barcode)

    subprocess.run(['explorer.exe', Path('output')])
    subprocess.run(['notepad', Path('log.txt')])
