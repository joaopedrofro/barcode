try:
    import subprocess
    from fpdf import FPDF
    from pathlib import Path
    from barcode import EAN13
    from barcode.writer import ImageWriter
except ImportError as error:
    print("{}\n\nImportError: Para utilizar este script instale \
          as dependências em requirements.txt".format(error))
    print("\t# pip install -r requirements.txt")
    exit(0)


class Barcode:
    def __init__(self, code, description):
        self.code = code
        self.description = description
        barcode = '7' + '0' * (11-len(self.code)) + self.code
        self.barcode = EAN13(barcode, writer=ImageWriter())


class BarcodeGenerator:
    def generate(self, barcode: Barcode):
        log_file = Path('log.txt')
        output_folder = Path('output')
        output_file = output_folder / '{} - {}'.format(barcode.code, barcode.description)

        if not output_folder.exists():
            output_folder.mkdir()

        barcode.barcode.save(
            output_file,
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
        pdf.cell(0, 0, barcode.description, align='C')
        pdf.image('{}.png'.format(output_file), x=70, y=13, w=70, type="PNG")
        pdf.output('{}.pdf'.format(output_file), 'F')

        with log_file.open('a') as lf:
            lf.write('{} - {} - {}\n'.format(
                barcode.code,
                barcode.barcode.get_fullcode(),
                barcode.description)
            )


if __name__ == '__main__':
    code_file = Path('codigos.txt')

    if not code_file.exists():
        code_file.touch()

    subprocess.run(['notepad.exe', code_file])
    barcode_list = []

    with code_file.open('r') as cf:
        for linha in cf.readlines():
            if linha != '':
                code, description = linha.replace('\n', '').split('-')
                code = code.lstrip().rstrip()
                description = description.lstrip().rstrip()
                barcode_list.append(Barcode(code, description))

    barcode_generator = BarcodeGenerator()

    for barcode in barcode_list:
        barcode_generator.generate(barcode)

    subprocess.run(['explorer.exe', Path('output')])
    subprocess.run(['notepad', Path('log.txt')])
