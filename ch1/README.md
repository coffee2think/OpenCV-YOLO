# ch1 · YOLO & OpenCV 첫 체험

## 학습 목표 & 핵심 개념
- 컴퓨터 비전이 해결하는 문제 유형과 대표 활용 사례를 파악합니다.
- 이미지 데이터가 픽셀/채널/해상도라는 숫자 배열임을 이해하고, 간단한 변환이 어떤 효과를 내는지 확인합니다.
- 가상환경 생성 → 스크립트 실행 → 산출물 정리까지의 실습 워크플로를 익힙니다.

> 이미지는 숫자 배열이기 때문에, 회색조/블러 같은 기본 연산만으로도 전처리와 시각화 결과를 빠르게 검증할 수 있습니다.

## 실습 플로우
1. **OpenCV 환경 점검**
   - 스크립트: `ch1/scripts/check_opencv.py`
   - 목적: OpenCV 버전을 확인하고 입력 이미지를 회색조·블러로 변환해 `data/outputs/ch1/`에 저장합니다.
   - 실행:
     ```bash
     python ch1/scripts/check_opencv.py --source data/inputs/input.webp
     ```
2. **픽셀 리포트 출력**
   - 스크립트: `ch1/scripts/pixel_report.py`
   - 목적: 해상도, 평균 색상, 샘플 픽셀 그리드 등 이미지 속 숫자 정보를 콘솔/텍스트 파일로 정리합니다.
   - 실행:
     ```bash
     python ch1/scripts/pixel_report.py --source data/inputs/input.webp --grid-size 5
     ```
3. **환경 기록 정리**
   - 템플릿: `ch1/docs/env_report.md`
   - 목적: 실습 환경(OS, Python, 패키지 버전)과 실행 결과 캡처 경로를 기록할 로컬 보고서를 만듭니다.
   - 실행:
     ```bash
     cp ch1/docs/env_report.md ch1/docs/env_report_local.md
     ```
     완료 후 `env_report_local.md`를 편집해 내용을 채웁니다.

## 산출물 체크리스트
- 변환된 이미지 2장 이상 (`data/outputs/ch1/output_gray_*.jpg`, `data/outputs/ch1/output_blur_*.jpg`)
- 픽셀 리포트 로그 (`logs/ch1_pixel_report.txt` 권장)
- 환경 보고서 초안 (`ch1/docs/env_report_local.md`)

## 확장 과제 (선택)
- 픽셀 리포트 스크립트를 수정해 평균 RGB 대신 HSV 평균을 출력해 보세요.
- 블러 커널 크기를 3, 7, 11로 바꿔가며 결과 이미지를 비교하고, 가장 적합한 설정을 메모로 남겨 보세요.

## 참고 자료
- Microsoft Learn: *What is computer vision?*
- OpenCV 공식 Getting Started 가이드
- CS231n 강의 노트 1강: https://cs231n.github.io/

## 다음 단계 준비
- `data/sample_images/` 폴더에 테스트 이미지 최소 3장을 보관합니다.
- `yolo predict --source data/sample_images` 명령을 사전 테스트해 ch3 실습 대비를 마칩니다.
