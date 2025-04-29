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
    query_type: str  # 쿼리 타입
    auth_key: str  # 사용자가 제공하는 인증키
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    corp_code: Optional[str] = None
    bsns_year: Optional[str] = None
    reprt_code: Optional[str] = None
    bgn_de: Optional[str] = None  # 시작일
    end_de: Optional[str] = None  # 종료일
    fs_div: Optional[str] = None  # 개별/연결구분 (CFS:연결, OFS:개별)
    info_type: Optional[str] = None  # 정정구분 (정정 전: NULL, 정정: "I")
    rpt_type: Optional[str] = None  # 단위구분 (1: 사업, 2: 반기, 3: 분기)
    separate: Optional[bool] = None  # 개별/연결 구분 (True:개별, False:연결)
    date: Optional[str] = None  # 특정 날짜 (YYYYMMDD)
    ticker: Optional[str] = None  # 종목코드
    rcept_no: Optional[str] = None  # 접수번호
    includes_exec: Optional[bool] = None  # 임원 포함 여부
    corp_codes: Optional[str] = None  # 복수 회사 코드 (콤마로 구분)
    account_nm: Optional[str] = None  # 계정명
    key_word: Optional[str] = None  # 사업보고서 주요정보 키워드
    event_type: Optional[str] = None  # 주요사항보고서 타입
    kind: Optional[str] = None  # 공시 유형
    kind_detail: Optional[str] = None  # 공시 상세 유형
    final: Optional[bool] = None  # 최종보고서 여부

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
            final = request.final if request.final is not None else True
            
            if request.start_date and request.end_date:
                result = dart.list(request.company, start=request.start_date, end=request.end_date, 
                                  kind=request.kind, kind_detail=request.kind_detail, final=final)
            elif request.start_date:
                result = dart.list(request.company, start=request.start_date, 
                                  kind=request.kind, kind_detail=request.kind_detail, final=final)
            else:
                result = dart.list(request.company, 
                                  kind=request.kind, kind_detail=request.kind_detail, final=final)
            
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
            
        elif request.query_type == "company":
            # 3-2. 단일 기업 개황정보 조회
            # 기업명/종목코드/고유번호 확인
            try:
                if not request.corp_code:
                    # 기업명이나 종목코드로 고유번호 찾기
                    corp_code = dart.find_corp_code(request.company)
                else:
                    corp_code = request.corp_code
                
                result = dart.company(corp_code)
                return {"status": "success", "data": result}
            except Exception as e:
                raise HTTPException(status_code=404, detail=f"기업 정보를 찾을 수 없습니다: {str(e)}")
            
        elif request.query_type == "report_content":
            # 4. 사업보고서 내용 조회
            # 기업명으로 corp_code 자동 조회
            if not request.corp_code:
                # 기업명으로 기업 코드 조회
                company_info = dart.company_by_name(request.company)
                if company_info is None or company_info.empty:
                    raise HTTPException(status_code=404, detail=f"'{request.company}' 기업을 찾을 수 없습니다.")
                
                corp_code = company_info.iloc[0]['corp_code'] if 'corp_code' in company_info.columns else None
                if not corp_code:
                    raise HTTPException(status_code=404, detail=f"'{request.company}' 기업의 코드를 찾을 수 없습니다.")
            else:
                # 사용자가 직접 corp_code를 제공한 경우
                corp_code = request.corp_code
                
            if not request.bsns_year:
                raise HTTPException(status_code=400, detail="사업보고서 조회에는 사업연도(bsns_year)가 필요합니다.")
            if not request.reprt_code:
                raise HTTPException(status_code=400, detail="사업보고서 조회에는 보고서 코드(reprt_code)가 필요합니다. 예: 11011(사업보고서), 11012(반기보고서), 11013(1분기보고서), 11014(3분기보고서)")
            
            result = dart.finstate(corp_code, request.bsns_year, request.reprt_code)
            return {"status": "success", "data": convert_df_to_json(result)}
            
        elif request.query_type == "company_code":
            # 5. 기업 고유번호 조회
            try:
                result = dart.find_corp_code(request.company)
                return {"status": "success", "company": request.company, "corp_code": result}
            except Exception as e:
                raise HTTPException(status_code=404, detail=f"'{request.company}' 기업의 코드를 찾을 수 없습니다.")
            
        elif request.query_type == "major_shareholder":
            # 6. 대량보유 상황 조회
            if not request.corp_code:
                # 기업명으로 기업 코드 조회
                company_info = dart.company_by_name(request.company)
                if company_info is None or company_info.empty:
                    raise HTTPException(status_code=404, detail=f"'{request.company}' 기업을 찾을 수 없습니다.")
                
                corp_code = company_info.iloc[0]['corp_code'] if 'corp_code' in company_info.columns else None
                if not corp_code:
                    raise HTTPException(status_code=404, detail=f"'{request.company}' 기업의 코드를 찾을 수 없습니다.")
            else:
                corp_code = request.corp_code
                
            result = dart.major_shareholders(corp_code)
            return {"status": "success", "data": convert_df_to_json(result)}
            
        elif request.query_type == "major_shareholder_exec":
            # 6-2. 임원ㆍ주요주주 소유보고 조회
            if not request.corp_code:
                # 기업명으로 기업 코드 조회
                company_info = dart.company_by_name(request.company)
                if company_info is None or company_info.empty:
                    raise HTTPException(status_code=404, detail=f"'{request.company}' 기업을 찾을 수 없습니다.")
                
                corp_code = company_info.iloc[0]['corp_code'] if 'corp_code' in company_info.columns else None
                if not corp_code:
                    raise HTTPException(status_code=404, detail=f"'{request.company}' 기업의 코드를 찾을 수 없습니다.")
            else:
                corp_code = request.corp_code
                
            result = dart.major_shareholders_exec(corp_code)
            return {"status": "success", "data": convert_df_to_json(result)}
            
        elif request.query_type == "executive":
            # 7. 임원 현황 조회
            if not request.corp_code:
                # 기업명으로 기업 코드 조회
                company_info = dart.company_by_name(request.company)
                if company_info is None or company_info.empty:
                    raise HTTPException(status_code=404, detail=f"'{request.company}' 기업을 찾을 수 없습니다.")
                
                corp_code = company_info.iloc[0]['corp_code'] if 'corp_code' in company_info.columns else None
                if not corp_code:
                    raise HTTPException(status_code=404, detail=f"'{request.company}' 기업의 코드를 찾을 수 없습니다.")
            else:
                corp_code = request.corp_code
                
            result = dart.executive_all(corp_code)
            return {"status": "success", "data": convert_df_to_json(result)}
            
        elif request.query_type == "dividend":
            # 8. 배당 정보 조회
            if not request.corp_code:
                # 기업명으로 기업 코드 조회
                company_info = dart.company_by_name(request.company)
                if company_info is None or company_info.empty:
                    raise HTTPException(status_code=404, detail=f"'{request.company}' 기업을 찾을 수 없습니다.")
                
                corp_code = company_info.iloc[0]['corp_code'] if 'corp_code' in company_info.columns else None
                if not corp_code:
                    raise HTTPException(status_code=404, detail=f"'{request.company}' 기업의 코드를 찾을 수 없습니다.")
            else:
                corp_code = request.corp_code
                
            result = dart.dividend(corp_code)
            return {"status": "success", "data": convert_df_to_json(result)}
            
        elif request.query_type == "capital":
            # 9. 자본금 변동사항 조회
            if not request.corp_code:
                # 기업명으로 기업 코드 조회
                company_info = dart.company_by_name(request.company)
                if company_info is None or company_info.empty:
                    raise HTTPException(status_code=404, detail=f"'{request.company}' 기업을 찾을 수 없습니다.")
                
                corp_code = company_info.iloc[0]['corp_code'] if 'corp_code' in company_info.columns else None
                if not corp_code:
                    raise HTTPException(status_code=404, detail=f"'{request.company}' 기업의 코드를 찾을 수 없습니다.")
            else:
                corp_code = request.corp_code
                
            result = dart.capital(corp_code)
            return {"status": "success", "data": convert_df_to_json(result)}
            
        elif request.query_type == "section_financial":
            # 10. 재무제표 특정 항목만 조회
            if not request.corp_code:
                # 기업명으로 기업 코드 조회
                company_info = dart.company_by_name(request.company)
                if company_info is None or company_info.empty:
                    raise HTTPException(status_code=404, detail=f"'{request.company}' 기업을 찾을 수 없습니다.")
                
                corp_code = company_info.iloc[0]['corp_code'] if 'corp_code' in company_info.columns else None
                if not corp_code:
                    raise HTTPException(status_code=404, detail=f"'{request.company}' 기업의 코드를 찾을 수 없습니다.")
            else:
                corp_code = request.corp_code
                
            if not request.bsns_year:
                raise HTTPException(status_code=400, detail="재무제표 항목 조회에는 사업연도(bsns_year)가 필요합니다.")
                
            # fs_div(개별/연결구분)와 separate가 모두 없는 경우 기본값 사용
            fs_div = request.fs_div if request.fs_div else "CFS"  # 기본값: 연결재무제표
            
            # 섹션 재무제표 항목 조회
            result = dart.finstate_all(corp_code, request.bsns_year, fs_div=fs_div)
            return {"status": "success", "data": convert_df_to_json(result)}
            
        elif request.query_type == "full_financial":
            # 11. 전체 재무제표 조회
            if not request.corp_code:
                # 기업명으로 기업 코드 조회
                company_info = dart.company_by_name(request.company)
                if company_info is None or company_info.empty:
                    raise HTTPException(status_code=404, detail=f"'{request.company}' 기업을 찾을 수 없습니다.")
                
                corp_code = company_info.iloc[0]['corp_code'] if 'corp_code' in company_info.columns else None
                if not corp_code:
                    raise HTTPException(status_code=404, detail=f"'{request.company}' 기업의 코드를 찾을 수 없습니다.")
            else:
                corp_code = request.corp_code
                
            if not request.bsns_year:
                raise HTTPException(status_code=400, detail="전체 재무제표 조회에는 사업연도(bsns_year)가 필요합니다.")
            if not request.reprt_code:
                raise HTTPException(status_code=400, detail="전체 재무제표 조회에는 보고서 코드(reprt_code)가 필요합니다. 예: 11011(사업보고서), 11012(반기보고서), 11013(1분기보고서), 11014(3분기보고서)")
                
            # 개별/연결구분
            separate = request.separate if request.separate is not None else False  # 기본값: 연결재무제표
            
            result = dart.xbrl(corp_code, request.bsns_year, request.reprt_code, separate=separate)
            return {"status": "success", "data": convert_df_to_json(result)}
            
        elif request.query_type == "report_key":
            # 12. 사업보고서 주요정보 조회
            if not request.corp_code:
                # 기업명으로 기업 코드 조회
                company_info = dart.company_by_name(request.company)
                if company_info is None or company_info.empty:
                    raise HTTPException(status_code=404, detail=f"'{request.company}' 기업을 찾을 수 없습니다.")
                
                corp_code = company_info.iloc[0]['corp_code'] if 'corp_code' in company_info.columns else None
                if not corp_code:
                    raise HTTPException(status_code=404, detail=f"'{request.company}' 기업의 코드를 찾을 수 없습니다.")
            else:
                corp_code = request.corp_code
                
            if not request.bsns_year:
                raise HTTPException(status_code=400, detail="사업보고서 주요정보 조회에는 사업연도(bsns_year)가 필요합니다.")
                
            if not request.key_word:
                raise HTTPException(status_code=400, detail="사업보고서 주요정보 조회에는 키워드(key_word)가 필요합니다. 예: '증자','배당','자기주식','최대주주','최대주주변동','소액주주','임원','직원','임원개인보수','임원전체보수','개인별보수','타법인출자'")
                
            # reprt_code(보고서 코드)
            reprt_code = request.reprt_code if request.reprt_code else "11011"  # 기본값: 사업보고서
            
            result = dart.report(corp_code, request.key_word, request.bsns_year, reprt_code=reprt_code)
            return {"status": "success", "data": convert_df_to_json(result)}
            
        elif request.query_type == "disclosure_date":
            # 13. 특정 날짜의 공시 목록 조회
            if not request.date:
                raise HTTPException(status_code=400, detail="특정 날짜의 공시 목록 조회에는 날짜(date)가 필요합니다. 형식: YYYYMMDD")
            
            result = dart.list_date(request.date)
            return {"status": "success", "data": convert_df_to_json(result)}
            
        elif request.query_type == "disclosure_date_ex":
            # 13-2. 특정 날짜의 공시 목록 조회 (확장)
            date = request.date if request.date else None  # 기본값: 오늘
            
            result = dart.list_date_ex(date)
            return {"status": "success", "data": convert_df_to_json(result)}
            
        elif request.query_type == "disclosure_ticker":
            # 14. 특정 종목코드의 공시 목록 조회
            ticker = request.ticker
            
            # ticker가 입력되지 않았다면 회사명으로 종목코드 또는 고유번호 찾기
            if not ticker:
                try:
                    # 회사명으로 회사 정보 조회 (상장 여부 확인)
                    company_info = dart.company_by_name(request.company)
                    if company_info is None or company_info.empty:
                        raise HTTPException(status_code=404, detail=f"'{request.company}' 기업을 찾을 수 없습니다.")
                    
                    # 종목코드 확인
                    ticker = company_info.iloc[0]['stock_code'] if 'stock_code' in company_info.columns else None
                    
                    # 종목코드가 없거나 비어있으면(비상장 기업) 회사명이나 고유번호를 대신 사용
                    if not ticker or ticker == "":
                        # OpenDartReader의 list 함수에 회사명이나 고유번호를 직접 전달
                        corp_code = company_info.iloc[0]['corp_code'] if 'corp_code' in company_info.columns else None
                        if not corp_code:
                            raise HTTPException(status_code=404, detail=f"'{request.company}' 기업의 정보를 찾을 수 없습니다.")
                        
                        # 비상장 기업은 list 함수로 조회 (list_ticker 대신)
                        start = request.start_date
                        end = request.end_date
                        result = dart.list(corp_code, start=start, end=end)
                        return {"status": "success", "data": convert_df_to_json(result)}
                except Exception as e:
                    raise HTTPException(status_code=404, detail=f"기업 정보 조회 중 오류 발생: {str(e)}")
            
            # 종목코드가 있는 경우(상장 기업) list_ticker 함수 사용
            start = request.start_date
            end = request.end_date
            
            try:
                result = dart.list_ticker(ticker, start=start, end=end)
                return {"status": "success", "data": convert_df_to_json(result)}
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"공시 목록 조회 중 오류 발생: {str(e)}")
            
        elif request.query_type == "sub_docs":
            # 15. 첨부문서 목록 조회
            if not request.rcept_no:
                raise HTTPException(status_code=400, detail="첨부문서 목록 조회에는 접수번호(rcept_no)가 필요합니다.")
            
            result = dart.sub_docs(request.rcept_no)
            return {"status": "success", "data": convert_df_to_json(result)}
            
        elif request.query_type == "attach_docs":
            # 15-2. 첨부 문서 리스트 조회
            if not request.rcept_no:
                raise HTTPException(status_code=400, detail="첨부 문서 리스트 조회에는 접수번호(rcept_no)가 필요합니다.")
            
            result = dart.attach_docs(request.rcept_no)
            return {"status": "success", "data": convert_df_to_json(result)}
            
        elif request.query_type == "attach_files":
            # 15-3. 첨부 파일 리스트 조회
            if not request.rcept_no:
                raise HTTPException(status_code=400, detail="첨부 파일 리스트 조회에는 접수번호(rcept_no)가 필요합니다.")
            
            result = dart.attach_files(request.rcept_no)
            return {"status": "success", "data": result}
            
        elif request.query_type == "download":
            # 16. 공시 원문 다운로드 URL 제공
            if not request.rcept_no:
                raise HTTPException(status_code=400, detail="공시 원문 다운로드를 위해서는 접수번호(rcept_no)가 필요합니다.")
            
            # 다운로드 URL 생성
            url = f"https://dart.fss.or.kr/dsaf001/main.do?rcpNo={request.rcept_no}"
            return {"status": "success", "download_url": url}
            
        elif request.query_type == "multi_financial":
            # 17. 다중회사 주요 재무제표 조회
            if not request.corp_codes:
                raise HTTPException(status_code=400, detail="다중회사 재무제표 조회에는 여러 기업코드(corp_codes)가 필요합니다. 콤마로 구분된 문자열 형식으로 제공하세요.")
            
            corp_codes = request.corp_codes.split(',')
            
            if not request.bsns_year:
                raise HTTPException(status_code=400, detail="다중회사 재무제표 조회에는 사업연도(bsns_year)가 필요합니다.")
            
            if not request.reprt_code:
                raise HTTPException(status_code=400, detail="다중회사 재무제표 조회에는 보고서 코드(reprt_code)가 필요합니다. 예: 11011(사업보고서), 11012(반기보고서), 11013(1분기보고서), 11014(3분기보고서)")
            
            # 단일 계정과목 다중회사 조회 (finstate_sli_multi 함수)
            if request.account_nm:
                result = dart.finstate_sli_multi(corp_codes, request.bsns_year, request.reprt_code, request.account_nm)
            # 다중회사 주요 재무제표 조회 (finstate_multi 함수) 
            else:
                result = dart.finstate_multi(corp_codes, request.bsns_year, request.reprt_code)
            
            return {"status": "success", "data": convert_df_to_json(result)}
            
        elif request.query_type == "audit":
            # 18. 외부감사인 조회
            if not request.corp_code:
                # 기업명으로 기업 코드 조회
                company_info = dart.company_by_name(request.company)
                if company_info is None or company_info.empty:
                    raise HTTPException(status_code=404, detail=f"'{request.company}' 기업을 찾을 수 없습니다.")
                
                corp_code = company_info.iloc[0]['corp_code'] if 'corp_code' in company_info.columns else None
                if not corp_code:
                    raise HTTPException(status_code=404, detail=f"'{request.company}' 기업의 코드를 찾을 수 없습니다.")
            else:
                corp_code = request.corp_code
                
            if request.includes_exec:  # 전체 내역 조회
                result = dart.audit_all(corp_code)
            else:  # 기본 내역 조회
                result = dart.audit(corp_code)
                
            return {"status": "success", "data": convert_df_to_json(result)}
            
        elif request.query_type == "stock_suspension":
            # 19. 상장폐지 현황 조회
            if not request.corp_code:
                # 기업명으로 기업 코드 조회
                company_info = dart.company_by_name(request.company)
                if company_info is None or company_info.empty:
                    raise HTTPException(status_code=404, detail=f"'{request.company}' 기업을 찾을 수 없습니다.")
                
                corp_code = company_info.iloc[0]['corp_code'] if 'corp_code' in company_info.columns else None
                if not corp_code:
                    raise HTTPException(status_code=404, detail=f"'{request.company}' 기업의 코드를 찾을 수 없습니다.")
            else:
                corp_code = request.corp_code
                
            result = dart.suspensions_changes(corp_code)
            return {"status": "success", "data": convert_df_to_json(result)}
            
        elif request.query_type == "stock_change":
            # 20. 증자(감자) 현황 조회
            if not request.corp_code:
                # 기업명으로 기업 코드 조회
                company_info = dart.company_by_name(request.company)
                if company_info is None or company_info.empty:
                    raise HTTPException(status_code=404, detail=f"'{request.company}' 기업을 찾을 수 없습니다.")
                
                corp_code = company_info.iloc[0]['corp_code'] if 'corp_code' in company_info.columns else None
                if not corp_code:
                    raise HTTPException(status_code=404, detail=f"'{request.company}' 기업의 코드를 찾을 수 없습니다.")
            else:
                corp_code = request.corp_code
                
            result = dart.stock_total_amount(corp_code)
            return {"status": "success", "data": convert_df_to_json(result)}
            
        elif request.query_type == "biz_overview":
            # 21. 사업의 내용 조회
            if not request.corp_code:
                # 기업명으로 기업 코드 조회
                company_info = dart.company_by_name(request.company)
                if company_info is None or company_info.empty:
                    raise HTTPException(status_code=404, detail=f"'{request.company}' 기업을 찾을 수 없습니다.")
                
                corp_code = company_info.iloc[0]['corp_code'] if 'corp_code' in company_info.columns else None
                if not corp_code:
                    raise HTTPException(status_code=404, detail=f"'{request.company}' 기업의 코드를 찾을 수 없습니다.")
            else:
                corp_code = request.corp_code
                
            if not request.bsns_year:
                raise HTTPException(status_code=400, detail="사업의 내용 조회에는 사업연도(bsns_year)가 필요합니다.")
                
            # rpt_type(보고서 유형)
            rpt_type = request.rpt_type if request.rpt_type else "1"  # 기본값: 사업보고서
            
            result = dart.report(corp_code, request.bsns_year, "business_content", rpt_type=rpt_type)
            # HTML 형식의 결과 처리
            if isinstance(result, str):
                return {"status": "success", "data": result}
            else:
                return {"status": "success", "data": convert_df_to_json(result)}
                
        elif request.query_type == "event":
            # 22. 주요사항보고서 조회
            if not request.corp_code:
                # 기업명으로 기업 코드 조회
                company_info = dart.company_by_name(request.company)
                if company_info is None or company_info.empty:
                    raise HTTPException(status_code=404, detail=f"'{request.company}' 기업을 찾을 수 없습니다.")
                
                corp_code = company_info.iloc[0]['corp_code'] if 'corp_code' in company_info.columns else None
                if not corp_code:
                    raise HTTPException(status_code=404, detail=f"'{request.company}' 기업의 코드를 찾을 수 없습니다.")
            else:
                corp_code = request.corp_code
                
            if not request.event_type:
                raise HTTPException(status_code=400, detail="주요사항보고서 조회에는 이벤트 타입(event_type)이 필요합니다. 예: '부도발생', '영업정지', '회생절차', '유상증자' 등")
                
            # 시작일과 종료일
            start = request.start_date
            end = request.end_date
            
            result = dart.event(corp_code, request.event_type, start=start, end=end)
            return {"status": "success", "data": convert_df_to_json(result)}
            
        elif request.query_type == "regstate":
            # 23. 증권신고서 조회
            if not request.corp_code:
                # 기업명으로 기업 코드 조회
                company_info = dart.company_by_name(request.company)
                if company_info is None or company_info.empty:
                    raise HTTPException(status_code=404, detail=f"'{request.company}' 기업을 찾을 수 없습니다.")
                
                corp_code = company_info.iloc[0]['corp_code'] if 'corp_code' in company_info.columns else None
                if not corp_code:
                    raise HTTPException(status_code=404, detail=f"'{request.company}' 기업의 코드를 찾을 수 없습니다.")
            else:
                corp_code = request.corp_code
                
            if not request.key_word:
                raise HTTPException(status_code=400, detail="증권신고서 조회에는 키워드(key_word)가 필요합니다. 예: '주식의포괄적교환이전', '합병', '증권예탁증권', '채무증권', '지분증권', '분할'")
                
            # 시작일과 종료일
            start = request.start_date
            end = request.end_date
            
            result = dart.regstate(corp_code, request.key_word, start=start, end=end)
            return {"status": "success", "data": convert_df_to_json(result)}
            
        else:
            raise HTTPException(status_code=400, detail=f"지원하지 않는 쿼리 타입: {request.query_type}")
            
    except HTTPException:
        raise
    except ImportError:
        raise HTTPException(status_code=500, detail="OpenDartReader 라이브러리를 불러올 수 없습니다.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"데이터 조회 중 오류 발생: {str(e)}")

# 첨부파일 다운로드 URL 조회 엔드포인트
@app.get("/api/dart/file/{rcept_no}")
async def get_file_url(rcept_no: str, auth_key: str):
    # 인증키 확인
    if auth_key != REQUIRED_AUTH_KEY:
        raise HTTPException(status_code=403, detail="인증키가 유효하지 않습니다.")
    
    try:
        # 첨부파일 URL 생성 (OpenDartReader 라이브러리 참조 불필요)
        url = f"https://dart.fss.or.kr/dsaf001/main.do?rcpNo={rcept_no}"
        return {"status": "success", "download_url": url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"첨부파일 URL 조회 중 오류 발생: {str(e)}")
