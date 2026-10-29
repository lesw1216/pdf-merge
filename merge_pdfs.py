#!/usr/bin/env python3
"""폴더 안의 PDF 파일들을 이름 오름차순(자연 정렬)으로 하나의 PDF로 합친다.

Ghostscript(gs)가 필요하다. 사용법:
    ./merge_pdfs.py <입력 폴더> [-o merged.pdf] [--lexical]
"""
import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path


def natural_key(path: Path):
    # file2.pdf < file10.pdf 가 되도록 숫자 구간은 정수로 비교
    parts = re.split(r"(\d+)", path.name.lower())
    return [int(p) if p.isdigit() else p for p in parts]


def main() -> int:
    parser = argparse.ArgumentParser(description="폴더 내 PDF를 이름순으로 병합")
    parser.add_argument("input_dir", type=Path, help="PDF가 들어 있는 폴더")
    parser.add_argument("-o", "--output", type=Path, default=None,
                        help="결과 PDF 경로 (기본값: <입력 폴더>/merged.pdf)")
    parser.add_argument("--lexical", action="store_true",
                        help="자연 정렬 대신 단순 문자열 순서로 정렬")
    args = parser.parse_args()

    if shutil.which("gs") is None:
        print("Ghostscript(gs)가 설치되어 있지 않습니다.", file=sys.stderr)
        return 1
    if not args.input_dir.is_dir():
        print(f"폴더를 찾을 수 없습니다: {args.input_dir}", file=sys.stderr)
        return 1

    output = (args.output or args.input_dir / "merged.pdf").resolve()
    files = [p for p in args.input_dir.iterdir()
             if p.is_file() and p.suffix.lower() == ".pdf" and p.resolve() != output]
    files.sort(key=(lambda p: p.name.lower()) if args.lexical else natural_key)
    if not files:
        print("합칠 PDF 파일이 없습니다.", file=sys.stderr)
        return 1

    for i, f in enumerate(files, 1):
        print(f"{i:>3}. {f.name}")

    cmd = ["gs", "-q", "-dNOPAUSE", "-dBATCH", "-dSAFER",
           "-sDEVICE=pdfwrite", f"-sOutputFile={output}",
           *map(str, files)]
    result = subprocess.run(cmd)
    if result.returncode != 0:
        print("병합 중 오류가 발생했습니다.", file=sys.stderr)
        return result.returncode
    print(f"완료: {output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
