"""
수강기록 관리 REST API 서버
- GET  /courses : 전체 수강기록 조회
- POST /courses : 새 수강기록 추가
- 데이터는 courses.json 파일에 저장
"""

import json
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

app = FastAPI(title="Course Records API", version="1.0.0")

# courses.json 파일 경로 (main.py와 같은 디렉토리)
DATA_FILE = Path(__file__).parent / "courses.json"


# ----------------------------
# 요청 Body 모델 (자동 검증)
# ----------------------------
class Course(BaseModel):
    course_name: str = Field(..., min_length=1, description="과목명")
    year: str = Field(..., min_length=4, max_length=4, description="이수연도 (예: 2026)")
    semester: str = Field(..., min_length=1, description="이수학기 (예: 1, 2)")
    grade: str = Field(..., min_length=1, description="성적 (예: A+, A0, B+ 등)")


# ----------------------------
# 파일 입출력 유틸
# ----------------------------
def load_courses() -> list:
    """JSON 파일에서 수강기록 리스트를 읽어온다.
    파일이 없거나 깨져 있어도 서버가 죽지 않도록 빈 리스트 반환."""
    try:
        if not DATA_FILE.exists():
            return []
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        # 파일 내용이 list 형태가 아니면 빈 리스트로 처리
        if not isinstance(data, list):
            return []
        return data
    except (json.JSONDecodeError, OSError) as e:
        print(f"[load_courses] 파일 읽기 실패: {e}")
        return []


def save_courses(data: list) -> None:
    """수강기록 리스트를 JSON 파일에 덮어쓴다."""
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ----------------------------
# 엔드포인트
# ----------------------------
@app.get("/courses")
def get_courses():
    """전체 수강기록(JSON list)을 반환."""
    return load_courses()


@app.post("/courses", status_code=201)
def add_course(course: Course):
    """새로운 수강기록을 추가하고, 변경된 전체 리스트를 반환."""
    try:
        data = load_courses()
        new_course = course.model_dump()
        data.append(new_course)
        save_courses(data)
        return {
            "message": "Course added successfully",
            "added": new_course,
            "total_courses": len(data),
        }
    except OSError as e:
        # 파일 저장 실패 시에도 서버는 살아 있도록 500 응답만 반환
        raise HTTPException(status_code=500, detail=f"파일 저장 실패: {e}")


# ----------------------------
# 전역 예외 핸들러
#  - 예상치 못한 예외가 발생해도 서버가 죽지 않고
#    500 JSON 응답을 돌려주도록 안전망을 둔다.
# ----------------------------
@app.exception_handler(Exception)
async def unhandled_exception_handler(request, exc):
    print(f"[unhandled] {type(exc).__name__}: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "서버 내부 오류가 발생했습니다.", "error": str(exc)},
    )


# ----------------------------
# 로컬 실행 (python main.py)
# ----------------------------
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
