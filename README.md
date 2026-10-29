# pdf-merge

폴더 안의 PDF 파일들을 이름 오름차순으로 하나의 PDF로 합치는 스크립트입니다.

## 요구 사항

- Python 3 (표준 라이브러리만 사용)
- Ghostscript (`gs`)

설치 확인:

```bash
gs --version
```

설치되어 있지 않다면:

```bash
sudo apt install ghostscript
```

## 사용법

```bash
./merge_pdfs.py <입력 폴더> [-o 출력파일] [--lexical]
```

| 옵션 | 설명 | 기본값 |
|------|------|--------|
| `<입력 폴더>` | 합칠 PDF들이 들어 있는 폴더 | (필수) |
| `-o`, `--output` | 결과 PDF 경로 | `<입력 폴더>/merged.pdf` |
| `--lexical` | 자연 정렬 대신 단순 문자열 순서로 정렬 | 꺼짐 |

### 예시

```bash
# ~/docs 안의 PDF를 합쳐 ~/docs/merged.pdf 생성
./merge_pdfs.py ~/docs

# 출력 파일 지정
./merge_pdfs.py ~/docs -o ~/result/all.pdf

# 단순 문자열 순서로 정렬
./merge_pdfs.py ~/docs --lexical
```

실행하면 합쳐지는 파일 목록이 순서대로 출력됩니다.

```
  1. file1.pdf
  2. file2.pdf
  3. file10.pdf
완료: /home/user/docs/merged.pdf
```

## 정렬 방식

- 기본값은 **자연 정렬**입니다. 이름 속 숫자를 크기로 비교하므로 `file2.pdf`가 `file10.pdf`보다 앞에 옵니다.
- `--lexical`을 쓰면 문자열 순서라서 `file10.pdf`가 `file2.pdf`보다 앞에 옵니다.
- 대소문자는 구분하지 않습니다.

## 참고

- 입력 폴더 바로 아래의 `.pdf` 파일만 대상이며, 하위 폴더는 탐색하지 않습니다.
- 출력 파일이 입력 폴더 안에 있어도 입력에서 제외됩니다.
- Ghostscript로 PDF를 다시 만들기 때문에 원본의 북마크나 폼 필드는 유지되지 않을 수 있습니다.
- 출력 경로에 같은 이름의 파일이 있으면 덮어씁니다.
