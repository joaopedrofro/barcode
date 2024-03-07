try:
    import subprocess
    from fpdf import FPDF
    from pathlib import Path
    from barcode import EAN13, EAN14
    from barcode.itf import ITF
    from barcode.writer import ImageWriter
except ImportError as error:
    print( "ImportError: Para utilizar este script instale as dependências em requirements.txt")
    exit(0)

# ([0-9]{6})(\s?-\s?)?([[:alnum:]\s]*?([0-9]+,?[0-9]*(k?g?)))$