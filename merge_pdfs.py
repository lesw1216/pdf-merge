#!/usr/bin/env python3
"""폴더 안의 PDF 파일들을 이름 오름차순(자연 정렬)으로 하나의 PDF로 합친다.

pypdf가 필요하다. 사용법:
    ./merge_pdfs.py <입력 폴더> [-o merged.pdf] [--lexical]
"""
import argparse
import math
import re
import sys
from collections import Counter
from pathlib import Path

try:
    from pypdf import PdfWriter
except ImportError:
    PdfWriter = None


def natural_key(path: Path):
    # file2.pdf < file10.pdf 가 되도록 숫자 구간은 정수로 비교
    parts = re.split(r"(\d+)", path.name.lower())
    return [int(p) if p.isdigit() else p for p in parts]


def text_angle(page):
    """페이지 글자가 읽히는 방향(반시계 기준 0/90/180/270도)을 글자 수 기준 다수결로 구한다.

    글자가 없으면(스캔본 등) None.
    """
    votes = Counter()

    def visitor(text, cm, tm, font_dict, font_size):
        if not text.strip():
            return
        a = tm[0] * cm[0] + tm[1] * cm[2]
        b = tm[0] * cm[1] + tm[1] * cm[3]
        votes[round(math.degrees(math.atan2(b, a)) / 90) % 4 * 90] += len(text)

    page.extract_text(visitor_text=visitor)
    return votes.most_common(1)[0][0] if votes else None


def progress(label: str, done: int, total: int, detail: str = "", inline: bool = False):
    width = 30
    filled = width * done // total
    bar = "█" * filled + "░" * (width - filled)
    line = f"{label} [{bar}] {done}/{total} {detail}"
    if inline and sys.stdout.isatty():
        # 같은 줄을 덮어쓴다 (이전 줄이 더 길면 남지 않도록 지움)
        print("\r\033[K" + line, end="", flush=True)
        if done == total:
            print()
    else:
        print(line, flush=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="폴더 내 PDF를 이름순으로 병합")
    parser.add_argument("input_dir", type=Path, help="PDF가 들어 있는 폴더")
    parser.add_argument("-o", "--output", type=Path, default=None,
                        help="결과 PDF 경로 (기본값: <입력 폴더>/merged.pdf)")
    parser.add_argument("--lexical", action="store_true",
                        help="자연 정렬 대신 단순 문자열 순서로 정렬")
    parser.add_argument("--no-auto-rotate", action="store_true",
                        help="글자 방향에 따른 페이지 자동 회전을 끈다")
    args = parser.parse_args()

    if PdfWriter is None:
        print("pypdf가 설치되어 있지 않습니다. (pip install pypdf)", file=sys.stderr)
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

    try:
        with PdfWriter() as writer:
            to_rotate = []  # (페이지, 필요한 회전 각도)
            for i, f in enumerate(files, 1):
                start = len(writer.pages)
                # 파일명을 북마크 제목으로 달고, 원본 북마크는 그 아래로 유지
                writer.append(f, outline_item=f.stem, import_outline=True)
                progress("병합", i, len(files), f.name)
                if not args.no_auto_rotate:
                    # 세로 용지에 가로 도면이 옆으로 누워 있는 경우: 글자가 가로로 읽히도록 회전
                    for page in writer.pages[start:]:
                        angle = text_angle(page)
                        if angle:
                            to_rotate.append((page, angle))
            if to_rotate:
                for i, (page, angle) in enumerate(to_rotate, 1):
                    page.rotate((angle - page.rotation) % 360)
                    progress("회전", i, len(to_rotate), inline=True)
                print(f"글자 방향에 맞게 {len(to_rotate)}페이지를 회전했습니다.")
            print("저장 중...", flush=True)
            writer.write(output)
    except Exception as e:
        print(f"병합 중 오류가 발생했습니다: {e}", file=sys.stderr)
        return 1
    print(f"완료: {output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
