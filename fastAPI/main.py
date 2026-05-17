"""
수강기록 관리 API
- GET  /        : 수강기록 페이지 (HTML)
- GET  /courses : 전체 수강기록 (JSON)
- POST /courses : 수강기록 추가
"""

import json
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel, Field

app = FastAPI(
    title="수강기록 API",
    description="JSON 파일 기반 수강기록 관리 API",
    version="1.0.0",
)

DATA_FILE = Path(__file__).parent / "courses.json"


# ----------------------------
# 요청 Body 모델
# ----------------------------
class Course(BaseModel):
    course_name: str = Field(..., min_length=1, description="과목명")
    year: str = Field(..., min_length=4, max_length=4, description="이수연도")
    semester: str = Field(..., min_length=1, description="이수학기")
    grade: str = Field(..., min_length=1, description="성적")


# ----------------------------
# 파일 입출력
# ----------------------------
def load_courses() -> list:
    """JSON 파일에서 수강기록을 읽어온다. 실패 시 빈 리스트 반환."""
    try:
        if not DATA_FILE.exists():
            return []
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, list):
            return []
        return data
    except (json.JSONDecodeError, OSError) as e:
        print(f"[load_courses] 파일 읽기 실패: {e}")
        return []


def save_courses(data: list) -> None:
    """수강기록 리스트를 JSON 파일에 저장."""
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ----------------------------
# 메인 페이지 HTML
# ----------------------------
INDEX_HTML = """<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>수강기록</title>
  <style>
    * { box-sizing: border-box; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Apple SD Gothic Neo',
                   'Malgun Gothic', 'Segoe UI', sans-serif;
      background: #ffffff;
      color: #1a1a1a;
      max-width: 560px;
      margin: 0 auto;
      padding: 56px 24px;
      line-height: 1.5;
      -webkit-font-smoothing: antialiased;
    }
    header { margin-bottom: 32px; }
    h1 {
      font-size: 22px;
      font-weight: 600;
      margin: 0 0 6px;
      letter-spacing: -0.01em;
    }
    .subtitle {
      color: #6b7280;
      font-size: 14px;
      margin: 0;
    }
    .count {
      font-size: 13px;
      color: #9ca3af;
      margin-bottom: 8px;
    }
    .course {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 14px 0;
      border-bottom: 1px solid #f0f0f0;
    }
    .course:last-child { border-bottom: none; }
    .name {
      font-weight: 500;
      font-size: 15px;
      margin-bottom: 2px;
    }
    .meta {
      color: #6b7280;
      font-size: 13px;
    }
    .grade {
      font-weight: 600;
      color: #2563eb;
      font-size: 14px;
    }
    .empty {
      color: #9ca3af;
      text-align: center;
      padding: 40px 0;
      font-size: 14px;
    }
    .footer {
      margin-top: 40px;
      padding-top: 16px;
      border-top: 1px solid #f0f0f0;
      font-size: 13px;
      color: #9ca3af;
    }
    .footer a {
      color: #2563eb;
      text-decoration: none;
      margin-right: 14px;
    }
    .footer a:hover { text-decoration: underline; }
  </style>
</head>
<body>
  <header>
    <h1>수강기록</h1>
    <p class="subtitle">현재까지 이수한 과목입니다.</p>
  </header>

  <div class="count" id="count"></div>
  <div id="list"></div>

  <div class="footer">
    <a href="/courses">/courses</a>
    <a href="/docs">API 문서</a>
  </div>

  <script>
    fetch('/courses')
      .then(r => r.json())
      .then(data => {
        const count = document.getElementById('count');
        const list = document.getElementById('list');

        if (!Array.isArray(data) || data.length === 0) {
          count.textContent = '';
          list.innerHTML = '<div class="empty">등록된 과목이 없습니다.</div>';
          return;
        }

        count.textContent = '총 ' + data.length + '개';
        list.innerHTML = data.map(c => (
          '<div class="course">' +
            '<div>' +
              '<div class="name">' + c.course_name + '</div>' +
              '<div class="meta">' + c.year + '년 ' + c.semester + '학기</div>' +
            '</div>' +
            '<div class="grade">' + c.grade + '</div>' +
          '</div>'
        )).join('');
      })
      .catch(() => {
        document.getElementById('list').innerHTML =
          '<div class="empty">불러오기 실패</div>';
      });
  </script>
</body>
</html>
"""


# ----------------------------
# 엔드포인트
# ----------------------------
@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def index():
    """수강기록 페이지를 보여준다."""
    return INDEX_HTML


@app.get("/courses", summary="전체 수강기록 조회")
def get_courses():
    """저장된 전체 수강기록을 반환합니다."""
    return load_courses()


@app.post("/courses", status_code=201, summary="수강기록 추가")
def add_course(course: Course):
    """새로운 수강기록을 추가하고 파일에 저장합니다."""
    try:
        data = load_courses()
        new_course = course.model_dump()
        data.append(new_course)
        save_courses(data)
        return {
            "message": "수강기록이 추가되었습니다.",
            "added": new_course,
            "total_courses": len(data),
        }
    except OSError as e:
        raise HTTPException(status_code=500, detail=f"파일 저장 실패: {e}")


# ----------------------------
# 전역 예외 핸들러 (서버가 죽지 않도록)
# ----------------------------
@app.exception_handler(Exception)
async def unhandled_exception_handler(request, exc):
    print(f"[unhandled] {type(exc).__name__}: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "서버 내부 오류가 발생했습니다.", "error": str(exc)},
    )


# ----------------------------
# 로컬 실행
# ----------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
