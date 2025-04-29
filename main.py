import os
import json
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, HTTPException, Query, Depends
from pydantic import BaseModel
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

# 고정 인증키 사용
REQUIRED_AUTH_KEY = "linkbricks-saxoji-benedict-ji-01034726435!@#$%231%$#@%"

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
def convert_df_to_json(df: pd.DataFrame) -> List[Dict[str, Any]]:
    if df is None or df.empty:
        return []
    
    # NaN 값 처리
    df = df.fillna("")
    
    # 날짜 타입 처리
    for col in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            df[col] = df[col].dt.strftime('%Y-%m-%d')
    
    return json.loads(df.to_json(orient='records', force_ascii=False))

# API 상태 확인용 메인 라우트
@app.get("/")
async def root():
    # OpenDartReader import는 가능한 늦게 수행
    try:
        import OpenDartReader
        return {
            "message": "LINKBRICKS HORIZON-AI DART API에 오신 것을 환영합니다", 
            "status": "active",
            "opendartreader_imported": True
        }
    except ImportError:
        return {
            "message": "LINKBRICKS HORIZON-AI DART API에 오신 것을 환영합니다", 
            "status": "active",
            "opendartreader_imported": False
        }

# 통합 API 엔드포인트
@app.post("/api/dart")
async def query_dart(request: DartRequest):
    # 인증키 확인
    if request.auth_key != REQUIRED_AUTH_KEY:
        raise HTTPException(status_code=403, detail="인증키가 유효하지 않습니다.")
    
    try:
        # 필요할 때만 OpenDartReader 가져오기
        import OpenDartReader
        
        # DART API 키 가져오기 (환경 변수에서)
        DART_API_KEY = os.environ.get("DART_API_KEY", "")
        if not DART_API_KEY:
            raise HTTPException(status_code=500, detail="DART API 키가 설정되지 않았습니다. 환경 변수 DART_API_KEY를 설정해주세요.")
        
        # 매 요청마다 새 클라이언트 인스턴스 생성
        try:
            dart = OpenDartReader(DART_API_KEY)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"DART API 연결 실패: {str(e)}")
            
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
            if not request.corp_code:
                raise HTTPException(status_code=400, detail="사업보고서 조회에는 기업 고유번호(corp_code)가 필요합니다.")
            if not request.bsns_year:
                raise HTTPException(status_code=400, detail="사업보고서 조회에는 사업연도(bsns_year)가 필요합니다.")
            if not request.reprt_code:
                raise HTTPException(status_code=400, detail="사업보고서 조회에는 보고서 코드(reprt_code)가 필요합니다. 예: 11011(사업보고서), 11012(반기보고서), 11013(1분기보고서), 11014(3분기보고서)")
            
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
    except ImportError:
        raise HTTPException(status_code=500, detail="OpenDartReader 라이브러리를 불러올 수 없습니다.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"데이터 조회 중 오류 발생: {str(e)}")

# 첨부파일 다운로드 URL 조회 엔드포인트
@app.get("/api/dart/file/{rcp_no}")
async def get_file_url(rcp_no: str, auth_key: str):
    # 인증키 확인
    if auth_key != REQUIRED_AUTH_KEY:
        raise HTTPException(status_code=403, detail="인증키가 유효하지 않습니다.")
    
    try:
        # 첨부파일 URL 생성 (OpenDartReader 라이브러리 참조 불필요)
        url = f"https://dart.fss.or.kr/dsaf001/main.do?rcpNo={rcp_no}"
        return {"status": "success", "download_url": url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"첨부파일 URL 조회 중 오류 발생: {str(e)}")
