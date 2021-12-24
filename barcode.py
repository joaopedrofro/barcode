from PIL import Image
from io import BytesIO
from fpdf import FPDF
import requests


def ean13(reduzido):
    EAN13 = '7' + '0' * (11 - len(str(reduzido))) + str(reduzido)

    soma_codigos = 0

    for i in range(0, 12):
        if i%2 == 0:
            soma_codigos += int(EAN13[i]) * 1
        else:
            soma_codigos += int(EAN13[i]) * 3

    DIGITO_VERIFICADOR = (soma_codigos // 10 + 1) * 10 - soma_codigos

    if DIGITO_VERIFICADOR % 10 == 0:
        EAN13 += '0'
    else:
        EAN13 += str(DIGITO_VERIFICADOR)
    
    return EAN13

def criar_pdf(produto):
    pdf = FPDF('P', unit='mm', format='A4')
    pdf.add_page()
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 0, produto.descricao, align='C')
    pdf.image(barcode_api(produto), x=68, y=13, w=70, type="PNG")
    pdf.output('{} - {}.pdf'.format(produto.reduzido, produto.descricao), 'F')

def barcode_api(produto):
    code_params = {
        'token': '256|PvJFdbmDYwt5Q8N93qJCTI72RFacK7VV',
        'text': produto.codigo_barras,
        'type': 'ean13',
        'font': 'arial',
        'font_size': 12
    }

    r = requests.get('https://api.invertexto.com/v1/barcode', params=code_params)

    i = Image.open(BytesIO(r.content))
    nome_arquivo = '{} - {}.png'.format(produto.reduzido, produto.descricao)
    i.save(nome_arquivo)

    return nome_arquivo


class Produto:
    reduzido = ''
    descricao = ''
    codigo_barras = ''

    def __init__(self, reduzido, descricao):
        self.reduzido = reduzido
        self.descricao = descricao
        self.codigo_barras = ean13(self.reduzido)


if __name__ == '__main__':
    while True:
        MSG = 'Digite as informações do produto: '
        
        try:
            info = str(input(MSG))
        except KeyboardInterrupt:
            exit(0)

        try:
            reduzido, descricao = info.split('-')
            reduzido = reduzido.rstrip()
            descricao = descricao.lstrip().upper()
        except ValueError:
            print('ERROR: Infomações incorretas, verifique se está de acordo com os padrões!\n')
        
        produto = Produto(reduzido, descricao)
        print('{0:>{1}}{2}'.format('Código reduzido: ', len(MSG), produto.reduzido))
        print('{0:>{1}}{2}'.format('Descrição: ', len(MSG), produto.descricao))
        print('{0:>{1}}{2}\n\n'.format('(EAN13) Código de barras: ', len(MSG), produto.codigo_barras))
        criar_pdf(produto)
