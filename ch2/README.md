# ch2 · YOLO + OpenCV로 2D 경계선 추출

## 학습 목표 & 핵심 개념
- Ultralytics YOLO로 객체의 대략적인 위치(바운딩 박스)와 클래스 정보를 빠르게 확보합니다.
- YOLO가 제시한 관심 영역(ROI)을 기반으로 OpenCV 전처리(리사이즈, 회색조, 블러)를 적용해 노이즈를 줄입니다.
- Canny 에지 검출과 HSV 마스킹을 결합해 대상 객체의 외곽선을 선명하게 추출합니다.

> YOLO가 잡아 준 박스를 출발점으로 삼아 OpenCV에서 경계선을 정제하면, 2D 이미지에서도 직관적인 윤곽 라인을 안정적으로 얻을 수 있습니다.

## 사전 준비
- 프로젝트 루트에서 가상환경을 활성화합니다: `source .venv/bin/activate`
- Ultralytics CLI와 OpenCV 패키지를 설치합니다:
  ```bash
  pip install ultralytics opencv-python
  ```
- 설치 후 `yolo --help` 또는 `python -m ultralytics --help`로 CLI가 동작하는지 확인하세요.

## 실습 플로우
모든 스텝은 동일한 입력 파일 `data/inputs/input.webp`를 사용합니다.

1. **YOLO로 경계 후보 추출**
   - 명령:
     ```bash
     yolo predict model=yolov8n.pt source=data/inputs/input.webp project=data/outputs/ch2 name=yolo --save-txt
     ```
   - 목적: 객체 바운딩 박스 좌표와 감지 이미지를 `data/outputs/ch2/yolo/`에 저장합니다. 텍스트 좌표는 이후 ROI 정제에 활용합니다.
2. **ROI 주석 및 경계 기준선 확보**
   - 스크립트: `ch2/scripts/image_annotation.py`
   - 목적: YOLO 결과를 참고해 중심 박스와 타임스탬프를 덧씌워 경계선 추출 영역을 시각적으로 확인합니다.
   - 실행:
     ```bash
     python ch2/scripts/image_annotation.py --source data/inputs/input.webp --label "YOLO ROI"
     ```
3. **전처리 & 에지 추출**
   - 스크립트: `ch2/scripts/preprocess_pipeline.py`
   - 목적: 리사이즈·회색조·블러로 노이즈를 줄인 뒤 Canny 에지 맵을 생성해 `data/outputs/ch2/`에 단계별 이미지를 저장합니다.
   - 실행:
     ```bash
     python ch2/scripts/preprocess_pipeline.py \
       --source data/inputs/input.webp \
       --scale 0.6 \
       --blur-kernel 9 \
       --canny-thresholds 80,160
     ```
4. **HSV 마스크로 윤곽 강조 (선택)**
   - 스크립트: `ch2/scripts/color_mask_demo.py`
   - 목적: 특정 색상 범위를 마스킹해 경계선 주변 영역을 강조하거나 배경을 제거합니다.
   - 실행:
     ```bash
     python ch2/scripts/color_mask_demo.py \
       --source data/inputs/input.webp \
       --lower-hsv 35,80,80 \
       --upper-hsv 90,255,255
     ```

## 산출물 체크리스트
- YOLO 추론 결과 이미지와 좌표 (`data/outputs/ch2/yolo/`)
- 주석 처리된 ROI 이미지 (`data/outputs/ch2/annotated.jpg`)
- 전처리 & 에지 단계별 산출물 (`data/outputs/ch2/input_step*.png`, `data/outputs/ch2/input_edges.png` 등)
- HSV 마스크 전/후 이미지 (`data/outputs/ch2/input_mask_before.png`, `data/outputs/ch2/input_mask_after.png`)
- 실습 소감 3줄 이상 (`notes/ch2_reflection.md`)

## 확장 과제 (선택)
- YOLO TXT 좌표를 파싱해 ROI를 자동으로 잘라내고, 그 영역만 에지 검출해 보세요.
- 에지 맵에 `cv2.morphologyEx`(close/open)를 적용해 경계선을 더욱 매끄럽게 다듬어 보세요.
- 색상 마스크 대신 밝기나 채도 기반 threshold를 적용해 다양한 경계 조건을 비교해 보세요.

## 참고 자료
- Ultralytics Docs: YOLOv8 Predict
- OpenCV Docs: Canny Edge Detection, Morphological Transformations
- PyImageSearch: "YOLO + OpenCV for custom edge pipelines"

## 다음 단계 준비
- `data/inputs/` 폴더에 다양한 테스트 이미지를 추가해 경계선 추출 성능을 비교합니다.
- ch3에서 사용할 실시간·배치 감지 스크립트(`ch3/scripts/…`)를 실행해 YOLO 결과를 연속 프레임에도 적용할 준비를 합니다.
