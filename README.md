3개의 짧은 챕터로 YOLO와 OpenCV를 단계적으로 다뤄, 실습만 따라 해도 객체 탐지 파이프라인을 완성하도록 구성했습니다. 각 챕터 README에서 바로 실행 가능한 스텝을 안내하며, 학습자는 `main README → 해당 챕터 README → 스크립트` 순서로 진행하면 됩니다.

## 시작하기
1. 프로젝트 루트에서 가상환경을 생성하세요: `python -m venv .venv`
2. 가상환경을 활성화하세요: `source .venv/bin/activate` (Windows는 `.\.venv\Scripts\activate`)
3. 기본 의존성을 설치하세요: `pip install -r requirements.txt` (파일이 없다면 `pip install ultralytics opencv-python`으로 최소 패키지를 준비합니다.)
4. 설정이 끝났다면 `ch1/README.md`부터 순서대로 실습을 진행하세요. 각 챕터에서 안내하는 스크립트와 산출물 경로를 그대로 따라가면 됩니다.

## 프로젝트 구조
```
SmartCam Mini/
├── README.md                # 전체 로드맵과 진행 가이드
├── ch1/                     # 1챕터 실습 리소스 및 문서
│   ├── README.md
│   ├── scripts/
│   └── docs/
├── ch2/
├── ch3/
└── data/                    # 공통 예제 이미지·영상
```

- `ch1`~`ch3` 폴더: 해당 챕터의 개념 정리, 실습 절차, 제출 산출물을 README에 정리합니다.
- `data/`: 모든 실습에서 재사용하는 예제 데이터 저장소입니다. 필요 시 `data/outputs/`, `logs/` 등 폴더를 새로 만들어 산출물을 정리합니다.

## 챕터 로드맵 요약
| 챕터 | 핵심 목표 | 주요 실습 | 기대 산출물 |
| --- | --- | --- | --- |
| ch1 | YOLO & OpenCV 빠른 체험, 환경 셋업 | OpenCV로 이미지 I/O, YOLO 모델 최초 실행, 결과 시각화 | 환경 점검 리포트, 첫 감지 결과 이미지 |
| ch2 | YOLO & OpenCV 심화 전처리/후처리 | 박스/라벨 커스터마이징, 관심 영역 필터링, 속도 측정 | 비교용 전처리 결과 이미지, 추론 성능 정리표 |
| ch3 | YOLO & OpenCV 객체 탐지 고도화 | 영상 스트림/배치 처리, 다중 클래스 분석, 간단한 평가 지표 | 실시간/배치 감지 데모, 평가 메모 및 개선 아이디어 |

세 챕터는 서로 독립적으로 읽을 수 있지만, 순서대로 따라가면 자연스럽게 객체 탐지 파이프라인을 완성할 수 있습니다.

## 챕터 README 구성 가이드
각 챕터 README에는 다음 항목을 동일한 순서로 배치합니다.
1. **학습 목표 & 개념 핵심**: 챕터에서 다룰 YOLO·OpenCV 개념과 참고 링크
2. **실습 플로우**: 단계별 실행 명령, 스크립트 경로, 주의 사항
3. **제출 산출물 체크리스트**: 제출 파일·캡처 목록, 권장 저장 경로(`data/outputs/ch#/` 등)
4. **확장 과제(선택)**: 심화 학습 또는 챕터 간 연결 과제

이 틀에 맞춰 챕터별 README를 정리하면, 학습자가 어디서 시작해 어떤 결과물을 내야 하는지 명확해집니다.

## 공통 준비 & 반복 사용 커맨드
1. `python -m venv .venv` → `source .venv/bin/activate`
2. `pip install -r requirements.txt` (필요 시 각 챕터 README에서 추가 패키지 안내)
3. `data/` 폴더에 제공된 샘플 이미지·영상을 확인하거나, 학습자가 직접 데이터를 추가
4. 챕터 README 지침에 따라 스크립트를 실행 → 생성된 산출물은 `data/outputs/` 하위에 정리

### 터미널 실행 예시
- ch1 환경 점검:
  ```bash
  python ch1/scripts/check_opencv.py --source data/sample_images/input.jpg
  ```
- ch1 픽셀 리포트:
  ```bash
  python ch1/scripts/pixel_report.py --source data/sample_images/input.jpg --grid-size 5
  ```

## 최종 성과물 묶음(챕터3 완료 기준)
- YOLO & OpenCV 감지 파이프라인 스크립트와 구성 파일 (`ch3/scripts/`, 필요 시 `data/outputs/ch3/`)
- 영상/이미지 감지 결과, 간단한 평가 리포트, 개선 아이디어 메모
- 세 챕터 산출물 정리 노트(회고, 구현 이슈 등)

## 참고 자료
- [OpenCV 공식 문서](https://docs.opencv.org/)
- [Ultralytics YOLO 문서](https://docs.ultralytics.com/)
- [Python 공식 문서](https://docs.python.org/)
- 챕터별 README 하단에 챕터 전용 참고 링크를 추가해 주세요.
