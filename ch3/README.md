# ch3 · YOLO 감지 JSON 파이프라인

## 학습 목표 & 핵심 개념
- Ultralytics YOLO를 사용해 단일 이미지 또는 배치에서 객체를 감지하고, 바운딩 박스 + 신뢰도를 확보합니다.
- YOLO CLI/결과물을 파싱해 구조화된 JSON으로 변환하고, 신뢰도 기준으로 정제·정렬합니다.
- 감지 결과를 다른 시스템과 연동할 수 있도록 표준화된 스키마(클래스, 좌표, 신뢰도, 메타 정보)를 설계합니다.

> 최종 목표는 감지 결과 이미지를 넘어서, 활용 가능한 `detections_refined.json`을 생성하는 데이터 파이프라인을 만드는 것입니다.

## 사전 준비
- 루트에서 가상환경을 활성화합니다: `source .venv/bin/activate`
- 필수 패키지 설치:
  ```bash
  pip install ultralytics opencv-python pandas
  ```
- `yolo help` 또는 `python -m ultralytics --help`로 CLI 사용 가능 여부를 확인합니다.
- `data/inputs/`에 감지할 이미지(예: `data/inputs/input.webp`)가 준비돼 있어야 합니다.

## 실습 플로우
1. **YOLO로 원시 감지 실행**
   - 명령:
     ```bash
     yolo predict ^
       model=yolov8n.pt ^
       source=data/inputs/input.webp ^
       project=data/outputs/ch3 ^
       name=raw ^
       save=True ^
       save_txt=True ^
       save_conf=True
     ```
     > CLI 구문은 `옵션=값` 형태만 허용합니다. 대체로 `python -m ultralytics predict … save_txt=True save_conf=True`로 실행해도 동일한 결과를 얻을 수 있습니다.
   - 결과: `data/outputs/ch3/raw/` 하위에 감지 이미지(`*.jpg`)와 같은 이름의 `labels/*.txt` 파일이 생성됩니다. TXT 포맷은 `class cx cy w h conf` 순서를 따릅니다.
2. **TXT → JSON 변환**
   - 스크립트: `ch3/scripts/export_detections.py`
   - 목적: YOLO TXT 파일을 읽어 각 감지의 클래스, 박스, 신뢰도를 픽셀 좌표로 환산한 JSON(`detections_raw.json`)을 생성합니다.
   - 실행 예시:
     ```bash
     python ch3/scripts/export_detections.py ^
       --runs-dir data/outputs/ch3/raw ^
       --output data/outputs/ch3/detections_raw.json
     ```
3. **신뢰도 필터링 & 정제**
   - 스크립트: `ch3/scripts/refine_detections.py`
   - 목적: `detections_raw.json`에서 신뢰도 임계값과 클래스 필터를 적용하고, 필요 시 좌표를 정규화해 `detections_refined.json`으로 저장합니다.
   - 실행 예시:
     ```bash
     python ch3/scripts/refine_detections.py ^
       --input data/outputs/ch3/detections_raw.json ^
       --output data/outputs/ch3/detections_refined.json ^
       --min-conf 0.5 ^
       --classes person,car
     ```
   - `detections_raw.json` 파일에 `class_name`이 빠져있음. 그래서 `detection_refined.json`에 아무런 객체도 필터링 되지 않음
   - `yolov8n.pt` 파일 안에 `class` 정보가 담겨있음. `model.names`로 꺼내 매칭
4. **요약 리포트 생성 (선택)**
   - 스크립트: `ch3/scripts/detection_summary.py`
   - 목적: 정제된 JSON을 바탕으로 클래스별 감지 수와 평균 신뢰도를 요약 표로 출력하거나 CSV/이미지(바 차트)로 저장합니다.
   - 실행 예시:
     ```bash
     python ch3/scripts/detection_summary.py ^
       --input data/outputs/ch3/detections_refined.json ^
       --output data/outputs/ch3/summary.csv
     ```

### JSON 스키마 예시
```json
{
  "image": "input.webp",
  "width": 1280,
  "height": 720,
  "detections": [
    {
      "class_id": 0,
      "class_name": "person",
      "confidence": 0.87,
      "bbox": {"x1": 234, "y1": 120, "x2": 540, "y2": 660},
      "bbox_norm": {"cx": 0.30, "cy": 0.54, "w": 0.24, "h": 0.62}
    }
  ]
}
```

## 산출물 체크리스트
- YOLO 원시 결과(`data/outputs/ch3/raw/`)와 생성된 TXT 라벨
- 변환된 감지 JSON (`data/outputs/ch3/detections_raw.json`)
- 필터링 및 정제된 JSON (`data/outputs/ch3/detections_refined.json`)
- 선택 리포트(예: `data/outputs/ch3/summary.csv` 또는 그래프 이미지)
- 분석 노트: 정제 기준, 제거된 감지 수, 추가 실험 아이디어 (`notes/ch3_observations.md` 권장)

## 확장 과제 (선택)
- 동일 파이프라인을 비디오 프레임 다중 이미지에 적용하고, 프레임별 JSON을 하나의 JSONLines 파일로 묶어보세요.
- JSON을 REST API, 데이터베이스 등에 전달하는 간단한 파이프라인을 작성해 후속 시스템과 연동하세요.
- `refine_detections.py`에 IoU 기반 중복 제거(NMS 후처리)를 추가해 겹치는 박스를 정리해 보세요.

## 참고 자료
- Ultralytics Docs: YOLOv8 Predict & Export
- OpenCV Docs: Coordinate Systems, Drawing functions
- Pandas Docs: JSON/CSV 변환

## 다음 단계 준비
- `ch3/scripts/` 내 스크립트를 구현하면서 테스트 데이터를 `data/inputs/`에 다양하게 추가하세요.
- ch4(실시간 감지)를 진행할 계획이라면, `detections_refined.json`을 실시간 스트림에 적용할 방법을 미리 구상해 두세요.
