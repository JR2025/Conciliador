import re
from pathlib import Path
from PyPDF2 import PdfReader, PdfWriter

def list_pdfs(directory: str) -> list[Path]:
    """
    Retorna lista de Paths para arquivos .pdf no diretório informado,
    ordenados pelo comprimento do nome (stem), do menor para o maior.
    """
    path = Path(directory)
    return sorted(
        path.glob('*.pdf'),
        key=lambda p: len(p.stem)
    )

def load_pdf(path: Path) -> PdfReader:
    """Abre o PDF e retorna um PdfReader."""
    try:
        return PdfReader(str(path))
    except Exception as e:
        print(f"Erro ao carregar PDF {path}: {e}")
        raise

def match_receipt_to_guide(guide_path: Path, receipts_dir: str) -> Path | None:
    """
    Encontra o comprovante correspondente à guia, buscando pelo prefixo comum no nome.
    Ex.: 'Nfe_..._Guia' → 'Nfe_..._Comprovante.pdf'
    """
    prefix_pattern = r"(?P<prefix>.*)_Guia$"
    match = re.match(prefix_pattern, guide_path.stem)
    if not match:
        return None

    key = match.group('prefix')
    candidate = Path(receipts_dir) / f"{key}_Comprovante.pdf"
    return candidate if candidate.exists() else None

def merge_pdfs(guide_pdf: PdfReader, receipt_pdf: PdfReader, output_dir: str, output_name: str) -> None:
    """Une duas instâncias de PdfReader em um único PDF."""
    writer = PdfWriter()
    # Adiciona páginas da guia
    for page in guide_pdf.pages:
        writer.add_page(page)
    # Adiciona páginas do comprovante
    for page in receipt_pdf.pages:
        writer.add_page(page)

    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    output_file = out_path / f"{output_name}.pdf"
    try:
        with open(output_file, 'wb') as f:
            writer.write(f)
    except Exception as e:
        print(f"Erro ao salvar PDF unido {output_file}: {e}")
        raise

def process_all(guides_dir: str, receipts_dir: str, output_dir: str) -> None:
    """
    Processa cada guia:
    - carrega o PDF da guia
    - encontra o comprovante correspondente
    - une os dois PDFs
    - salva o resultado com '_Guia' substituído por '_PB'
    """
    for guide_path in list_pdfs(guides_dir):
        try:
            guide_pdf = load_pdf(guide_path)
            receipt_path = match_receipt_to_guide(guide_path, receipts_dir)
            if not receipt_path:
                print(f"Comprovante não encontrado para guia: {guide_path.name}")
                continue
            receipt_pdf = load_pdf(receipt_path)

            # transforma o nome de saída: Nfe_..._Guia → Nfe_..._PB
            output_name = re.sub(r"_Guia$", "_PB", guide_path.stem)
            merge_pdfs(guide_pdf, receipt_pdf, output_dir, output_name)
            print(f"Processado: {output_name}.pdf")
        except Exception as e:
            print(f"Erro no processamento de {guide_path.name}: {e}")
            continue

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Une guias e comprovantes em PDFs.")
    parser.add_argument("guides_dir", help="Pasta com arquivos de guia (.pdf)")
    parser.add_argument("receipts_dir", help="Pasta com arquivos de comprovante (.pdf)")
    parser.add_argument("output_dir", help="Pasta de saída para arquivos unidos")
    args = parser.parse_args()

    process_all(args.guides_dir, args.receipts_dir, args.output_dir)
