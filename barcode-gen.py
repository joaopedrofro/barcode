try:
    import barcode
    import argparse
    import subprocess
    from fpdf import FPDF
    from pathlib import Path
    from barcode.writer import ImageWriter
except ImportError as error:
    print("{}\n\nImportError: Para utilizar este script instale as dependências em requirements.txt".format(error))
    print("\t# pip install -r requirements.txt")
    exit(0)


def itf_checksum(codigo):
    itf = '17' + '0' * (11-len(codigo)) + codigo
    soma = 0

    for i in range(0, len(itf)):
        c = int(itf[i])
        if i%2 == 0:
            soma += c * 3
        else:
            soma += c * 1

    itf = itf + str(((soma//10 + 1) * 10) - soma)

    return itf


class Produto:

    def __init__(self, reduzido, descricao):
        self.reduzido = reduzido
        self.descricao = descricao
       
    def gerar_codigo(self, tipo):
        codigo_barras_cru = ''

        if tipo == 'itf':
            codigo_barras_cru = itf_checksum(self.reduzido)
        else:
            codigo_barras_cru = '7' + '0' * (11-len(self.reduzido)) + self.reduzido

        self.codigo_barras = barcode.get_barcode(tipo, codigo_barras_cru, writer=ImageWriter())

    def salvar_codigo(self):
        log = Path('log.txt')
        pasta = Path('output')
        nome_arquivo = pasta / '{} - {}'.format(self.reduzido, self.descricao)

        if not pasta.exists():
            pasta.mkdir()

        self.codigo_barras.save(
            nome_arquivo,
            options={
                'module_width': 0.3,
                'module_height': 11.0,
                'font_size': 12,
                'text_distance': 1.0
            }
        )

        pdf = FPDF('P', unit='mm', format='A4')
        pdf.add_page()
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 0, self.descricao, align='C')
        pdf.image('{}.png'.format(nome_arquivo), x=70, y=13, w=70, type="PNG")
        pdf.output('{}.pdf'.format(nome_arquivo), 'F')

        with log.open('a') as log_file:
            log_file.write('{} - {} - {}\n'.format(
                self.reduzido,
                self.codigo_barras.get_fullcode(),
                self.descricao)
            )


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='Barcode Generator',
        description='Script que gera códigos de barras em PDF e PNG.'
    )

    parser.add_argument(
        '--tipo',
        '-t',
        help="Informe o tipo do código de barras a ser gerado",
        default="ean13"
    )

    args = parser.parse_args()

    codigos = Path('codigos.txt')

    if not codigos.exists():
        codigos.touch()

    subprocess.run(['notepad.exe', codigos])

    with codigos.open('r') as arquivo:
        for linha in arquivo.readlines():
            if linha != '':
                reduzido, descricao = linha.replace('\n', '').split('-')
                reduzido = reduzido.lstrip().rstrip()
                descricao = descricao.lstrip().rstrip()

                produto = Produto(reduzido, descricao)
                produto.gerar_codigo(args.tipo)
                produto.salvar_codigo()

    subprocess.run(['explorer.exe', Path('output')])
    subprocess.run(['notepad.exe', Path('log.txt')])
