import os
import json
from typing import Optional, List
from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.security import APIKeyHeader
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import OpenDartReader
import datetime
import pandas as pd
from io import BytesIO

# API 설정 상수
SWAGGER_HEADERS = {
    "title": "LINKBRICKS HORIZON-AI DART API",
    "version": "1.0.0",
    "description": "OpenDART 공시·기업정보 조회 엔진 (Powered by FinanceData OpenDartReader)",
    "contact": {
        "name": "Linkbricks HORIZON AI",
        "url": "https://www.horizonai.ai",
        "email": "contact@horizonai.ai",
    },
}

app = FastAPI(**SWAGGER_HEADERS)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API 키 인증 설정
API_KEY_NAME = "X-API-KEY"
# 고정 인증키 사용
REQUIRED_AUTH_KEY = "linkbricks-saxoji-benedict-ji-01034726435!@#$%231%$#@%"

# DART API 키 설정
DART_API_KEY = os.environ.get("DART_API_KEY")

# OpenDartReader 초기화
dart = OpenDartReader(DART_API_KEY)

# 인증 의존성 함수 제거 (직접 요청에서 인증키 확인으로 대체)

# 입력 모델 정의
class DartRequest(BaseModel):
    company: str
    query_type: str  # "disclosure", "report", "company_info", "report_content", "company_code"
    auth_key: str  # 사용자가 제공하는 인증키
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    corp_code: Optional[str] = None
    bsns_year: Optional[str] = None
    reprt_code: Optional[str] = None

# Pandas DataFrame을 JSON 변환 함수
def convert_df_to_json(df):
    if df is None or df.empty:
        return []
    
    # NaN 값 처리
    df = df.fillna("")
    
    # 날짜 타입 처리
    for col in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            df[col] = df[col].dt.strftime('%Y-%m-%d')
    
    return json.loads(df.to_json(orient='records', force_ascii=False))

# 메인 라우트
@app.get("/")
async def root():
    return {"message": "LINKBRICKS HORIZON-AI DART API에 오신 것을 환영합니다"}

# 통합 API 엔드포인트
@app.post("/api/dart")
async def query_dart(request: DartRequest):
    # 인증키 확인
    if request.auth_key != REQUIRED_AUTH_KEY:
        raise HTTPException(status_code=403, detail="인증키가 유효하지 않습니다.")
        
    try:
        # 조회 종류에 따라 다른 처리
        if request.query_type == "disclosure":
            # 1. 기업 공시정보 조회
            if request.start_date and request.end_date:
                result = dart.list(request.company, start=request.start_date, end=request.end_date)
            elif request.start_date:
                result = dart.list(request.company, start=request.start_date)
            else:
                result = dart.list(request.company)
            
            return {"status": "success", "data": convert_df_to_json(result)}
            
        elif request.query_type == "report":
            # 2. 정기 최종 보고서 조회
            if request.start_date and request.end_date:
                result = dart.list(request.company, start=request.start_date, end=request.end_date, kind='A')
            elif request.start_date:
                result = dart.list(request.company, start=request.start_date, kind='A')
            else:
                result = dart.list(request.company, kind='A')
            
            return {"status": "success", "data": convert_df_to_json(result)}
            
        elif request.query_type == "company_info":
            # 3. 기업 개황정보 조회
            result = dart.company_by_name(request.company)
            return {"status": "success", "data": convert_df_to_json(result)}
            
        elif request.query_type == "report_content":
            # 4. 사업보고서 내용 조회
            if not (request.corp_code and request.bsns_year and request.reprt_code):
                raise HTTPException(status_code=400, detail="사업보고서 조회에는 corp_code, bsns_year, reprt_code가 필요합니다.")
            
            result = dart.finstate(request.corp_code, request.bsns_year, request.reprt_code)
            return {"status": "success", "data": convert_df_to_json(result)}
            
        elif request.query_type == "company_code":
            # 5. 기업 고유번호 조회
            result = dart.company_by_name(request.company)
            if result is None or result.empty:
                raise HTTPException(status_code=404, detail=f"'{request.company}' 기업을 찾을 수 없습니다.")
            
            corp_code = result.iloc[0]['corp_code'] if 'corp_code' in result.columns else None
            if not corp_code:
                raise HTTPException(status_code=404, detail=f"'{request.company}' 기업의 코드를 찾을 수 없습니다.")
            
            return {"status": "success", "company_name": request.company, "corp_code": corp_code}
            
        else:
            raise HTTPException(status_code=400, detail=f"지원하지 않는 쿼리 타입: {request.query_type}")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"데이터 조회 중 오류 발생: {str(e)}")

# 첨부파일 다운로드 URL 조회 엔드포인트
@app.get("/api/dart/file/{rcp_no}")
async def get_file_url(rcp_no: str, auth_key: str):
    # 인증키 확인
    if auth_key != REQUIRED_AUTH_KEY:
        raise HTTPException(status_code=403, detail="인증키가 유효하지 않습니다.")
    
    try:
        # 첨부파일 URL 생성 (OpenDartReader 라이브러리 참조)
        url = f"https://dart.fss.or.kr/dsaf001/main.do?rcpNo={rcp_no}"
        return {"status": "success", "download_url": url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"첨부파일 URL 조회 중 오류 발생: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    # Render.com에서는 PORT 환경변수를 자동으로 설정합니다
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
