# GitHub Pages 이미지 호스팅 전환 설계

**날짜:** 2026-04-12
**상태:** 승인됨

## 배경

Instagram API는 이미지 URL을 직접 fetch해야 한다. 기존 GitHub Releases URL은 S3 CDN으로 리다이렉트되는데, HEAD 요청으로는 최종 URL을 얻을 수 없고, 서명된 S3 URL은 만료 위험이 있다. GitHub Pages는 안정적이고 영구적인 공개 URL을 제공한다.

## 목표

- 이미지 호스팅을 GitHub Releases → GitHub Pages로 교체
- 당일 이미지만 유지, 이전 날짜 이미지 자동 삭제
- GitHub Releases는 Pages 안정 확인 후 별도로 제거

## 아키텍처

### 신규: `services/github_pages.py`

```
upload_images_to_pages(image_paths) -> list[str]
  ├── _ensure_gh_pages_branch()     # 브랜치 없으면 orphan으로 생성
  ├── _cleanup_old_images()         # 오늘 날짜 아닌 images/* 폴더 삭제
  └── _upload_image(path, folder)   # Contents API PUT으로 파일 업로드
```

### 변경: `main.py`

```python
# 변경 전
from services.github_release import create_release_and_upload
image_urls = create_release_and_upload(images)

# 변경 후
from services.github_pages import upload_images_to_pages
image_urls = upload_images_to_pages(images)
```

### 유지: `services/github_release.py`

삭제 없이 그대로 유지. GitHub Pages 안정 확인 후 별도 제거.

### 유지: `.github/workflows/daily.yml`

`permissions: contents: write` 이미 있어 변경 불필요.

## URL 형식

```
https://{owner}.github.io/{repo_name}/images/{YYYY-MM-DD-HHMM}/{filename}
```

예시:
```
https://pgmjun.github.io/instagram-invest-news/images/2026-04-12-0800/card1_20260412_0800.png
```

## 데이터 흐름

1. `_ensure_gh_pages_branch()` — GitHub API로 `gh-pages` 브랜치 존재 확인. 없으면 빈 트리로 orphan 브랜치 생성.
2. `_cleanup_old_images()` — `GET /repos/{repo}/contents/images?ref=gh-pages`로 폴더 목록 조회. 오늘 날짜(`YYYY-MM-DD`)로 시작하지 않는 폴더의 파일을 `DELETE /repos/{repo}/contents/{path}` API로 삭제.
3. `_upload_image()` — `PUT /repos/{repo}/contents/images/{folder}/{filename}`으로 Base64 인코딩된 이미지 업로드.
4. `time.sleep(30)` — GitHub Pages CDN 전파 대기.
5. Pages URL 목록 반환.

## 에러 처리

- 모든 GitHub API 호출은 `raise_for_status()`로 실패 즉시 예외 발생.
- `images/` 폴더가 아직 없는 경우 (첫 실행) cleanup 단계는 스킵.

## 제약 사항

- GitHub Pages 전파 지연: 업로드 후 최대 1분 소요 가능. `sleep(30)`으로 대응.
- 레포는 public이어야 GitHub Pages가 무료 플랜에서 동작.
- Instagram이 이미지에 접근하려면 Pages 사이트가 public이어야 함.
