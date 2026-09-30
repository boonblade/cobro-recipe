# 도메인 팩

cobro-recipe는 **범용 스킬**이다. 업종·업무마다 다른 것(비유를 가져올 곳, 현업 독자, 리뷰어, 손그림 테마)은 도메인 팩으로 분리하고, 스킬 본체는 바꾸지 않는다.

## 1. 팩 선택

- `recipe.yaml`의 `pack` 필드로 지정한다. 생략하면 `general`.
- 팩 파일: `packs/<id>.yaml`

| 팩 | 용도 | 비유 원천 | 손그림 주인공 |
|---|---|---|---|
| `general` (기본) | 웹·ERP·인프라·데이터 등 업종 무관 | 일상·사무 (택배, 창구, 번호표, 이사) | 연필 |
| `garment-3d` | DXF 패턴, Three.js 3D 착장 | 옷·원단·봉제 | 바늘 (실 땀 경로) |

## 2. 팩 파일 구조

```yaml
id: general                     # 파일명과 같게
name: 범용
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

1. 레시피의 팩(`pack`) 사전에서 찾는다.
2. 없으면 `general` 사전에서 찾는다.
3. 둘 다 없으면 팩의 `metaphor_source`에서 새 비유를 만들고 **해당 팩 사전에 추가**한다 (`review: false`).
4. 팩 `reviewer`가 확인하면 `review: true`로 바꾼다.

## 4. 새 팩 추가 기준

- 같은 업무 영역의 레시피가 **3건 이상** 쌓였고, 일반 비유보다 그 업무의 말로 설명하는 게 더 잘 통할 때 만든다.
- 예상 후보: `erp` (회계·재고·결재, Delphi/Oracle), `retail` (매장·POS·물류), `infra` (서버·네트워크·보안).
