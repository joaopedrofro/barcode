import barcode.base


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


class Barcode:
    def __init__(self, code, description, barcode_format):
        self.code = code
        self.description = description
        self.format = barcode_format
        self.writer_options = barcode.base.Barcode.default_writer_options
        
        format_code = code
        match barcode_format:
            case "ean13":
                format_code = '7' + '0' * (11-len(code)) + code
                self.writer_options['font_size'] = 10
                self.writer_options['module_width'] = 0.4
                self.writer_options['text_distance'] = 4.6
                self.writer_options['module_height'] = 11.0
            case "code128":
                self.writer_options['font_size'] = 10
                self.writer_options['module_width'] = 0.4
                self.writer_options['text_distance'] = 4.6
                self.writer_options['module_height'] = 11.0
            case "itf":
                format_code = '17' + '0' * (11-len(code)) + code
                self.writer_options['font_size'] = 16
                self.writer_options['module_width'] = 0.32
                self.writer_options['text_distance'] = 7.5
            
        self.barcode = barcode.get_barcode_class(self.format)(format_code)
        self.barcode.writer = ImageWriter()


class BarcodeService:
    def save_barcodes(self, barcodes: list):
        log_file = Path('log.txt')
        output_folder = Path('output')
        
        if not output_folder.exists():
            output_folder.mkdir()
    
        for out_barcode in barcodes:
            output_file = output_folder / '{} - {}'.format(out_barcode.code, out_barcode.description)

            out_barcode.barcode.save(
                filename=output_file,
                options=out_barcode.writer_options
            )

            pdf = FPDF('P', unit='mm', format='A4')
            pdf.add_page()
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(0, 0, out_barcode.description, align='C')
            pdf.image('{}.png'.format(output_file), x=70, y=13, w=70, type="PNG")
            pdf.output('{}.pdf'.format(output_file), 'F')

            with log_file.open('a') as lf:
                lf.write('{} - {} - {}\n'.format(
                    out_barcode.code,
                    out_barcode.barcode.get_fullcode(),
                    out_barcode.description)
                )
        
    def get_barcodes_from_file(self, file) -> list:
        lines = []

        with file.open('r') as arq:
            for line in arq.readlines():
                if line != '':
                    lines.append(line.replace('\\n', ''))
     
        barcode_list = []
    
        for line in lines.copy():
            code, description = line.replace('\n', '').split('-')
            barcode_list.append(Barcode(code.strip(), description.strip(), barcode_format))
        
        return barcode_list


if __name__ == '__main__':
    print("Escolha o formato do código de barras a ser gerado: \n")
    
    provided_barcodes = {
        1: 'code128',
        2: 'ean13',
        3: 'itf'
    }
    
    for k, v in provided_barcodes.items():
        print("{} - {}".format(k, v))
        
    barcode_format = ""
    
    try:
        barcode_format = provided_barcodes[int(input("\nDigite: "))]
    except (ValueError, IndexError):
        print("Valor inválido!")
        input()
        exit(0)
    
    input_file = Path('codigos.txt')
    
    if not input_file.exists():
        input_file.touch()

    subprocess.run(['notepad.exe', input_file])
    
    barcode_service = BarcodeService()
    
    barcode_service.save_barcodes(barcode_service.get_barcodes_from_file(input_file))

    subprocess.run(['explorer.exe', Path('output')])
    subprocess.run(['notepad', Path('log.txt')])
