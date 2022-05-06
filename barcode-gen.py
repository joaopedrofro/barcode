try:
    # from PIL import Image
    # from io import BytesIO
    from fpdf import FPDF
    import argparse
    from os.path import abspath, splitext
    import barcode
    from barcode.writer import ImageWriter
except ImportError:
    print("""\
[ERROR] - [ImportError]

* Para executar este programa é necessário instalar todas
as dependências abaixo:
    fpdf
    Pillow
    python-barcode

* Execute o seguinte comando para instalar as dependências:
    pip install -r requirements.txt
""")
    exit(0)


def codigo_itf(codigo):
    itf = '1700000' + codigo
    soma = 0

    for i in range(0, len(itf)):
        c = int(itf[i])
        if i%2 == 0:
            soma += c * 3
        else:
            soma += c * 1

    itf = itf + str(((soma//10 + 1) * 10) - soma)

    return itf


def criar_codigo_barras(codigo, descricao, tipo):
    nome_arquivo = '{} - {}'.format(codigo, descricao)

    if tipo=='itf':
        barcode.generate(
            tipo,
            codigo_itf(codigo),
            writer=ImageWriter(),
            output=nome_arquivo,
            writer_options={
                'module_width': 0.2,
                'module_height': 11.0,
                'font_size': 12,
                'text_distance': 1.0
            }
        )
    else:
        barcode.generate(
            tipo,
            '700000' + codigo,
            writer=ImageWriter(),
            output=nome_arquivo,
            writer_options={
                'module_width': 0.3,
                'module_height': 11.0,
                'font_size': 12,
                'text_distance': 1.0
            }
        )

    pdf = FPDF('P', unit='mm', format='A4')
    pdf.add_page()
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 0, descricao, align='C')
    pdf.image('{}.png'.format(nome_arquivo), x=70, y=13, w=70, type="PNG")
    pdf.output('{}.pdf'.format(nome_arquivo), 'F')



def codigo_descricao(texto):
    codigo, descricao = texto.replace('\n', '').split('-')
    codigo = codigo.lstrip().rstrip()
    descricao = descricao.lstrip().rstrip()
    return codigo, descricao


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='Barcode Generator', description='Script que gera códigos de barras em PDF e PNG.')
    parser.add_argument('--arquivo', '-a', help="Informe o nome ou caminho de um arquivo que contenha os códigos separados por uma nova linha.")
    parser.add_argument('--tipo', '-t', help="Informe o tipo do código de barras a ser gerado", default="ean13")
    parser.add_argument('--descricao', '-d', help="Adiciona a descrição do código acima do código de barras", action='store_true')
    args = parser.parse_args()

    if args.arquivo:
        if splitext(abspath(args.arquivo))[1] == '.txt':
            # try:
            arquivo = open(abspath(args.arquivo), 'r')
            codigos = arquivo.readlines()
            arquivo.close()
            for codigo in codigos:
                codigo_txt, descricao = codigo_descricao(codigo)
                criar_codigo_barras(codigo_txt, descricao, args.tipo)
            # except:
            #     print('Não foi possível ler o arquivo!')
        else:
            print('Arquivo inválido!')
            exit(0)