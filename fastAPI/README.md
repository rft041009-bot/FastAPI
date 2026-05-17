# Course Records API (FastAPI)

수강기록(course records)을 JSON 파일로 관리하는 간단한 REST API 서버입니다.

## 기능

- `GET /courses` : 전체 수강기록 조회
- `POST /courses` : 새 수강기록 추가 (파일에 반영됨)

## 프로젝트 구조

```
fastapi-courses/
├── main.py            # FastAPI 서버 코드
├── courses.json       # 수강기록 데이터
├── requirements.txt   # 의존성 목록
├── .gitignore
└── README.md
```

## 실행 방법

### 1. 가상환경 생성 및 활성화 (선택)

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate
```

### 2. 의존성 설치

```bash
pip install -r requirements.txt
```

### 3. 서버 실행

```bash
# 방법 1
python main.py

# 방법 2
uvicorn main:app --reload
```

서버는 기본적으로 `http://127.0.0.1:8000` 에서 실행됩니다.

## API 명세

### GET /courses

전체 수강기록을 반환합니다.

**요청 예시 (Postman)**
- Method: `GET`
- URL: `http://127.0.0.1:8000/courses`

**응답 예시**
```json
[
  {
    "course_name": "자료구조",
    "year": "2025",
    "semester": "2",
    "grade": "A+"
  },
  {
    "course_name": "빅데이터프로그래밍",
    "year": "2025",
    "semester": "1",
    "grade": "A0"
  }
]
```

### POST /courses

새로운 수강기록을 추가합니다.

**요청 예시 (Postman)**
- Method: `POST`
- URL: `http://127.0.0.1:8000/courses`
- Headers: `Content-Type: application/json`
- Body (raw, JSON):

```json
{
  "course_name": "인간로봇상호작용",
  "year": "2026",
  "semester": "2",
  "grade": "A+"
}
```

**응답 예시**
```json
{
  "message": "Course added successfully",
  "added": {
    "course_name": "인간로봇상호작용",
    "year": "2026",
    "semester": "2",
    "grade": "A+"
  },
  "total_courses": 3
}
```

## 오류 처리

- 잘못된 형식의 요청(필드 누락, 타입 오류 등)은 FastAPI/Pydantic이 자동으로 `422 Unprocessable Entity` 응답을 반환합니다.
- 파일 입출력 오류는 `500` 응답으로 처리됩니다.
- 어떤 오류 상황에서도 **서버가 강제 종료되지 않습니다.**

## 자동 생성 문서

서버 실행 후 다음 주소에서 API 문서를 확인할 수 있습니다.

- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`
