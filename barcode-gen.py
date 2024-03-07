try:
    import subprocess
    import re
    from fpdf import FPDF
    from pathlib import Path
    from barcode import EAN13, EAN14
    from barcode.itf import ITF
    from barcode.writer import ImageWriter
except ImportError as error:
    print( "ImportError: Para utilizar este script instale as dependências em requirements.txt")
    exit(0)


EAN13_OUTPUT_OPTIONS = {
    'module_width': 0.5
}

ITF_OUTPUT_OPTIONS = {
    'module_width': 0.3
}

OUTPUT_FOLDER = Path('output')

if not OUTPUT_FOLDER.exists():
    OUTPUT_FOLDER.mkdir()


class Barcode:
    def __init__(self, minified_code, description, ean13):
        self.minified_code = minified_code
        self.description = description
        self.ean13 = ean13
        self.ean13.writer.set_options(EAN13_OUTPUT_OPTIONS)
    
    def get_full_description(self):
        return "{} - {} - {}".format(self.minified_code, self.ean13.ean, self.description)

    def get_description(self):
        return "{} - {}".format(self.minified_code, self.description)

    def save(self, additional=''):
        self.ean13.save(OUTPUT_FOLDER / self.get_description() + additional)


def verify_file(file):
    if not file.exists():
        file.touch()


if __name__ == '__main__':
    code_file = Path('codigos.txt')

    subprocess.run(['notepad.exe', code_file])
    
    matched = []
    unmatched_rows = []

    print("Verificando códigos...")

    with code_file.open('r') as f:
        pattern = re.compile(r"([0-9]{1,6})(\s?-\s?)?(.*?)([0-9]+,?[0-9]*k?g)$", flags=re.I)
        for line, row in enumerate(f.readlines()):
            match = pattern.match(row)
            if match:
                matched.append(match)
            else:
                unmatched_rows.append((line, row))
    
    if matched:
        generate_itf = input("\nGerar código DUN-14 (S/n)? ")

        if generate_itf in ('s', 'sim', 'y'):
            generate_itf = True
        else:
            generate_itf = False

        print("\nGerando códigos...")

        log_file = open('log.txt', '+a')
        barcodes = []

        for match in matched:
            groups = match.groups()

            barcodes.append(
                Barcode(
                    groups[0],
                    groups[2].upper().lstrip() + groups[3].lower(),
                    EAN13(
                        '7' + '0' * (11 - len(groups[0])) + groups[0],
                        writer=ImageWriter()
                    )
                )
            )
        
        for barcode in barcodes:
            log_file.write(barcode.get_full_description() + "\n")
            barcode.save()

        log_file.close()

    if unmatched_rows:
        print("[ AVISO ] Foram encontrado códigos com erro, verifique o arquivo de log...")
