# 도메인 팩

cobro-recipe는 **범용 스킬**이다. 업종·업무마다 다른 것(비유를 가져올 곳, 현업 독자, 리뷰어, 손그림 테마)은 도메인 팩으로 분리하고, 스킬 본체는 바꾸지 않는다.

## 1. 팩 선택

- 프로젝트에 `recipes/pack.yaml`(로컬 팩)이 있으면 그것을 쓴다. `/cobro-recipe init`으로 자동 추출한다 (§5).
- 없으면 `recipe.yaml`의 `pack` 필드로 내장 팩을 지정한다. 생략하면 `general`.
- 내장 팩 파일: `packs/<id>.yaml` — init의 시작점이자 작성 예시.

| 팩 | 용도 | 비유 원천 | 손그림 주인공 |
|---|---|---|---|
| `general` (기본) | 웹·ERP·인프라·데이터 등 업종 무관 | 일상·사무 (택배, 창구, 번호표, 이사) | 연필 |
| `garment-3d` | DXF 패턴, Three.js 3D 착장 | 옷·원단·봉제 | 바늘 (실 땀 경로) |
| `general-en` | 영어 사용 프로젝트 기본 | everyday office life (front desk, queue ticket, moving house) | 연필 |

## 2. 팩 파일 구조

```yaml
id: general                     # 파일명과 같게 (로컬 팩은 프로젝트 이름)
name: 범용
project:                        # 로컬 팩만 — init이 채운다. 첫 화면·서명·검색에 표시
  name: cobro-mcp               #   package.json name / 저장소 이름
  url: https://github.com/org/repo   # git remote → 근거 링크 기본 주소
lang: ko                        # 프로젝트 기본 언어 (ko | en)
description: 이 팩을 쓰는 레시피 범위
metaphor_source: 비유를 가져올 곳 (plain 설명 작성 기준)
business_readers: 이 팩의 비개발 독자 (예: 패턴실, 회계팀)
reviewer: 비유가 맞는지 확인할 사람
domain_knowledge_examples: [Gate S5 판단 예시]
sketch:
  protagonist: pencil | needle  # 손그림 스타일에서 경로를 따라가는 주인공
  trail: dash | stitch          # 지나간 길 표현
  doodles: [...]                # 배경 낙서 종류
terms:                          # 기술 용어 → 쉬운 비유 사전
  - { term: cache, plain: 자주 쓰는 서류를 책상 위에 올려 두기, review: false }
```

## 3. 비유 찾는 순서

1. 로컬 팩(`recipes/pack.yaml`) 또는 레시피의 팩(`pack`) 사전에서 찾는다.
2. 없으면 `general` 사전에서 찾는다.
3. 둘 다 없으면 팩의 `metaphor_source`에서 새 비유를 만들고 **해당 팩 사전에 추가**한다 (`review: false`).
4. 팩 `reviewer`가 확인하면 `review: true`로 바꾼다.

## 4. 내장 팩 추가 기준 (스킬 저장소)

- 여러 프로젝트의 로컬 팩에서 같은 업무 영역이 반복되면, 공통 부분을 내장 팩으로 올려 다음 init의 시작점으로 쓴다.
- 예상 후보: `erp` (회계·재고·결재, Delphi/Oracle), `retail` (매장·POS·물류), `infra` (서버·네트워크·보안).

## 5. 자동 추출 (`/cobro-recipe init`)

프로젝트당 1회. 결과는 `recipes/pack.yaml`에 저장하고 이후에는 다시 읽기만 한다 (토큰 절약).

1. **수집 (샘플링)**: README·docs 첫 부분, 디렉터리 구조, DB 테이블·클래스·화면명 상위 빈도 용어, 최근 커밋 메시지 50개. 파일 전체를 읽지 않는다.
2. **추출**: `project`(이름: package.json·저장소 이름, url: `git remote get-url origin`을 https로), `lang`(사용자의 대화 언어 기준, README 언어는 참고), `name`, `description`, `metaphor_source`, `business_readers`, `domain_knowledge_examples`, 주요 용어 10~20개와 비유 초안(`review: false`).
3. **내장 팩 참고**: 가장 가까운 내장 팩(`general` 등)의 용어·테마를 시작값으로 쓴다.
4. **확인**: 요약 1장을 사용자에게 보여 주고 수정·승인을 받은 뒤 저장한다.
5. **누적**: 레시피 작성 중 새 용어·비유가 생기면 로컬 팩에 추가한다.
