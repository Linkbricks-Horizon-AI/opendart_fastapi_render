# LINKBRICKS HORIZON-AI DART Financial Data API

LINKBRICKS HORIZON-AI가 개발한 FastAPI 기반 애플리케이션을 사용하여 한국 금융감독원 DART 시스템의 기업 공시 정보에 접근할 수 있는 API입니다.
(powered by OpenDartReader)

## 기능

1. 기업 공시 정보 조회 (disclosure)
2. 정기 보고서 조회 (report)
3. 기업 개황 정보 조회 (company_info)
4. 단일 기업 개황 정보 조회 (company)
5. 사업보고서 내용 조회 (report_content)
6. 기업 고유번호 조회 (company_code)
7. 대량보유 상황 조회 (major_shareholder)
8. 임원ㆍ주요주주 소유보고 조회 (major_shareholder_exec)
9. 임원 현황 조회 (executive)
10. 배당 정보 조회 (dividend)
11. 자본금 변동사항 조회 (capital)
12. 재무제표 특정 항목 조회 (section_financial)
13. 전체 재무제표 조회 (full_financial)
14. 사업보고서 주요정보 조회 (report_key)
15. 특정 날짜 공시 목록 조회 (disclosure_date)
16. 특정 날짜 공시 목록 조회 (확장) (disclosure_date_ex)
17. 특정 종목코드 공시 목록 조회 (disclosure_ticker)
18. 첨부문서 목록 조회 (sub_docs)
19. 첨부 문서 리스트 조회 (attach_docs)
20. 첨부 파일 리스트 조회 (attach_files)
21. 공시 원문 다운로드 URL 제공 (download)
22. 공시서류 원문 조회 (document)
23. 공시 원문 텍스트 추출 (retrieve)
24. 다중회사 재무제표 조회 (multi_financial)
25. 외부감사인 조회 (audit)
26. 상장폐지 현황 조회 (stock_suspension)
27. 증자(감자) 현황 조회 (stock_change)
28. 사업의 내용 조회 (biz_overview)
29. 주요사항보고서 조회 (event)
30. 증권신고서 조회 (regstate)

## 설치 및 실행

### 로컬 환경에서 실행

1. 필요한 패키지 설치:
   ```bash
   pip install -r requirements.txt
   ```

2. 환경 변수 설정:
   ```bash
   export DART_API_KEY="your_dart_api_key"
   ```

3. 서버 실행:
   ```bash
   uvicorn main:app --reload
   ```

## Render.com에 배포하기

### GitHub 리포지토리 연동 방식

1. Render.com 계정에 로그인하세요.
2. 새로운 웹 서비스(New Web Service) 생성을 선택하세요.
3. GitHub 리포지토리를 연결하세요.
4. 설정:
   - **Environment**: Python
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT --workers 4`
5. 환경 변수 설정 (선택사항):
   - `DART_API_KEY`: 금융감독원에서 발급받은 DART API 키
   - 참고: DART API 키가 없어도 API 서버는 시작되지만, 실제 DART 데이터를 조회할 때 키가 필요합니다.
6. 서비스 생성 버튼을 클릭하세요.

### render.yaml 사용 방식

프로젝트에 `render.yaml` 파일을 포함시켜 배포할 수도 있습니다:

1. GitHub 리포지토리에 `render.yaml` 파일이 있는지 확인하세요.
2. Render.com Dashboard에서 "Blueprint" 옵션을 선택하세요.
3. GitHub 리포지토리를 연결하세요.
4. 환경 변수를 설정하세요 (선택사항):
   - `DART_API_KEY`: 금융감독원에서 발급받은 DART API 키
5. Apply 버튼을 클릭하여 배포를 시작하세요.

## 인증

모든 API 요청은 인증키를 포함해야 합니다. 통합 API(`/api/dart`)는 요청 본문에 인증키를 포함해야 하며, 파일 URL 조회 API는 쿼리 파라미터로 인증키를 전달해야 합니다.

유효한 인증키: `linkbricks-saxoji-benedict-ji-01034726435!@#$%231%$#@%`

예시:
```json
{
  "company": "삼성전자",
  "query_type": "disclosure",
  "auth_key": "linkbricks-saxoji-benedict-ji-01034726435!@#$%231%$#@%",
  "start_date": "20250101"
}
```

## API 엔드포인트

### 1. 통합 DART 조회 API

**POST** `/api/dart`

통합 엔드포인트로 `query_type` 파라미터를 통해 다양한 조회 기능을 제공합니다.

### 2. 첨부파일 다운로드 URL 조회

**GET** `/api/dart/file/{rcept_no}?auth_key=linkbricks-saxoji-benedict-ji-01034726435!@#$%231%$#@%`

특정 공시 보고서의 첨부파일 다운로드 URL을 제공합니다. 인증키는 쿼리 파라미터로 전달합니다.

## 주요 기능 별 요청 예시

### 1. 기업 공시정보 조회 (`disclosure`)
```json
{
  "company": "삼성전자",
  "query_type": "disclosure",
  "auth_key": "linkbricks-saxoji-benedict-ji-01034726435!@#$%231%$#@%",
  "start_date": "20250101",
  "end_date": "20250401",
  "kind": "A",
  "kind_detail": "5",
  "final": true
}
```

**참고:**
- `kind`: 공시유형
  - 'A'=정기공시
  - 'B'=주요사항보고
  - 'C'=발행공시
  - 'D'=지분공시
  - 'E'=기타공시
  - 'F'=외부감사관련
  - 'G'=펀드공시
  - 'H'=자산유동화
  - 'I'=거래소공시
  - 'J'=공정위공시
- `kind_detail`: 공시 상세 유형
  - '5'=정기공시
  - '3'=주요사항보고
  - '11'=발행공시
  - '4'=지분공시
  - '9'=기타공시
  - '5'=외부감사관련
  - '3'=펀드공시
  - '6'=자산유동화
  - '6'=거래소공시
  - '5'=공정위공시
- `final`: 최종보고서 여부(기본값: true), false면 중간 변경 보고서를 포함

### 2. 정기 보고서 조회 (`report`)
```json
{
  "company": "삼성전자",
  "query_type": "report",
  "auth_key": "linkbricks-saxoji-benedict-ji-01034726435!@#$%231%$#@%",
  "start_date": "20250101",
  "end_date": "20250401"
}
```

### 3. 기업 개황정보 조회 (`company_info`)
```json
{
  "company": "삼성전자",
  "query_type": "company_info",
  "auth_key": "linkbricks-saxoji-benedict-ji-01034726435!@#$%231%$#@%"
}
```

### 4. 단일 기업 개황정보 조회 (`company`)
```json
{
  "company": "삼성전자",
  "query_type": "company",
  "auth_key": "linkbricks-saxoji-benedict-ji-01034726435!@#$%231%$#@%"
}
```

### 5. 사업보고서 내용 조회 (`report_content`)
```json
{
  "company": "삼성전자",
  "query_type": "report_content",
  "auth_key": "linkbricks-saxoji-benedict-ji-01034726435!@#$%231%$#@%",
  "bsns_year": "2023",
  "reprt_code": "11011"
}
```

**보고서 코드(reprt_code) 값:**
- "11011": 사업보고서 (연간)
- "11012": 반기보고서
- "11013": 1분기보고서
- "11014": 3분기보고서

### 6. 기업 고유번호 조회 (`company_code`)
```json
{
  "company": "삼성전자",
  "query_type": "company_code",
  "auth_key": "linkbricks-saxoji-benedict-ji-01034726435!@#$%231%$#@%"
}
```

### 7. 대량보유 상황 조회 (`major_shareholder`)
```json
{
  "company": "삼성전자",
  "query_type": "major_shareholder",
  "auth_key": "linkbricks-saxoji-benedict-ji-01034726435!@#$%231%$#@%"
}
```

### 8. 임원ㆍ주요주주 소유보고 조회 (`major_shareholder_exec`)
```json
{
  "company": "삼성전자",
  "query_type": "major_shareholder_exec",
  "auth_key": "linkbricks-saxoji-benedict-ji-01034726435!@#$%231%$#@%"
}
```

### 9. 임원 현황 조회 (`executive`)
```json
{
  "company": "삼성전자",
  "query_type": "executive",
  "auth_key": "linkbricks-saxoji-benedict-ji-01034726435!@#$%231%$#@%"
}
```

### 10. 배당 정보 조회 (`dividend`)
```json
{
  "company": "삼성전자",
  "query_type": "dividend",
  "auth_key": "linkbricks-saxoji-benedict-ji-01034726435!@#$%231%$#@%"
}
```

### 11. 자본금 변동사항 조회 (`capital`)
```json
{
  "company": "삼성전자",
  "query_type": "capital",
  "auth_key": "linkbricks-saxoji-benedict-ji-01034726435!@#$%231%$#@%"
}
```

### 12. 재무제표 특정 항목 조회 (`section_financial`)
```json
{
  "company": "삼성전자",
  "query_type": "section_financial",
  "auth_key": "linkbricks-saxoji-benedict-ji-01034726435!@#$%231%$#@%",
  "bsns_year": "2023",
  "fs_div": "CFS"
}
```

**참고:**
- `fs_div`는 개별/연결구분으로 "CFS"(연결) 또는 "OFS"(개별)로 입력합니다. 기본값은 "CFS"입니다.

### 13. 전체 재무제표 조회 (`full_financial`)
```json
{
  "company": "삼성전자",
  "query_type": "full_financial",
  "auth_key": "linkbricks-saxoji-benedict-ji-01034726435!@#$%231%$#@%",
  "bsns_year": "2023",
  "reprt_code": "11011",
  "separate": false
}
```

**참고:**
- `separate`는 개별/연결 구분으로 true(개별) 또는 false(연결)로 입력합니다. 기본값은 false입니다.

### 14. 사업보고서 주요정보 조회 (`report_key`)
```json
{
  "company": "삼성전자",
  "query_type": "report_key",
  "auth_key": "linkbricks-saxoji-benedict-ji-01034726435!@#$%231%$#@%",
  "bsns_year": "2023",
  "key_word": "배당",
  "reprt_code": "11011"
}
```

**참고:**
- `key_word`는 필수 파라미터로, 다음 중 하나의 값을 입력해야 합니다:
  - `'증자'`: 증자(감자) 현황
  - `'배당'`: 배당에 관한 사항
  - `'자기주식'`: 자기주식 취득 및 처분 현황
  - `'최대주주'`: 최대주주 현황
  - `'최대주주변동'`: 최대주주 변동 현황
  - `'소액주주'`: 소액주주현황
  - `'임원'`: 임원현황
  - `'직원'`: 직원현황
  - `'임원개인보수'`: 이사ㆍ감사의 개인별 보수 현황
  - `'임원전체보수'`: 이사ㆍ감사 전체의 보수현황
  - `'개인별보수'`: 개인별 보수지급 금액(5억이상 상위5인)
  - `'타법인출자'`: 타법인 출자현황

### 15. 특정 날짜 공시 목록 조회 (`disclosure_date`)
```json
{
  "company": "삼성전자",
  "query_type": "disclosure_date",
  "auth_key": "linkbricks-saxoji-benedict-ji-01034726435!@#$%231%$#@%",
  "date": "20230501"
}
```

**참고:**
- `date` 파라미터는 YYYYMMDD 형식으로 입력합니다.

### 16. 특정 날짜 공시 목록 조회 (확장) (`disclosure_date_ex`)
```json
{
  "company": "삼성전자",
  "query_type": "disclosure_date_ex",
  "auth_key": "linkbricks-saxoji-benedict-ji-01034726435!@#$%231%$#@%",
  "date": "20230501"
}
```

**참고:**
- `date` 파라미터는 YYYYMMDD 형식으로 입력합니다.
- 공시가 게시된 시간 정보를 포함합니다.

### 17. 특정 종목코드 공시 목록 조회 (`disclosure_ticker`)
```json
{
  "company": "삼성전자",
  "query_type": "disclosure_ticker",
  "auth_key": "linkbricks-saxoji-benedict-ji-01034726435!@#$%231%$#@%",
  "start_date": "20230101",
  "end_date": "20230630"
}
```

**참고:**
- `ticker` 파라미터는 선택적입니다. 입력하지 않으면 `company` 값을 기준으로 자동으로 종목코드를 찾습니다.
- 수동으로 종목코드를 지정하고 싶은 경우 `ticker` 파라미터에 입력할 수 있습니다 (예: "005930").
- 비상장 기업의 경우에도 `company` 값만 입력하면 고유번호(corp_code)를 자동으로 찾아 공시 목록을 조회합니다.
- `start_date`와 `end_date`는 선택적 파라미터입니다.

### 18. 첨부문서 목록 조회 (`sub_docs`)
```json
{
  "company": "삼성전자",
  "query_type": "sub_docs",
  "auth_key": "linkbricks-saxoji-benedict-ji-01034726435!@#$%231%$#@%",
  "rcept_no": "20230515001050"
}
```

**참고:**
- `rcept_no`는 공시 접수번호를 의미합니다.

### 19. 첨부 문서 리스트 조회 (`attach_docs`)
```json
{
  "company": "삼성전자",
  "query_type": "attach_docs",
  "auth_key": "linkbricks-saxoji-benedict-ji-01034726435!@#$%231%$#@%",
  "rcept_no": "20230515001050"
}
```

**참고:**
- `rcept_no`는 공시 접수번호를 의미합니다.

### 20. 첨부 파일 리스트 조회 (`attach_files`)
```json
{
  "company": "삼성전자",
  "query_type": "attach_files",
  "auth_key": "linkbricks-saxoji-benedict-ji-01034726435!@#$%231%$#@%",
  "rcept_no": "20230515001050"
}
```

**참고:**
- `rcept_no`는 공시 접수번호를 의미합니다.

### 22. 공시서류 원문 조회 (XML) (`document`)
```json
{
  "company": "삼성전자",
  "query_type": "document",
  "auth_key": "linkbricks-saxoji-benedict-ji-01034726435!@#$%231%$#@%",
  "rcept_no": "20230515001050"
}
```

**참고:**
- `rcept_no`는 공시 접수번호를 의미합니다.
- 결과는 XML 형식으로 반환됩니다.

### 23. 공시 원문 텍스트 추출 (`retrieve`)
```json
{
  "company": "삼성전자",
  "query_type": "retrieve",
  "auth_key": "linkbricks-saxoji-benedict-ji-01034726435!@#$%231%$#@%",
  "rcept_no": "20230515001050",
  "extract_text": true
}
```

**참고:**
- `rcept_no`는 공시 접수번호를 의미합니다.
- `extract_text`는 텍스트 추출 여부로, 기본값은 true입니다.

### 22. 다중회사 재무제표 조회 (`multi_financial`)
```json
{
  "company": "삼성전자", 
  "query_type": "multi_financial",
  "auth_key": "linkbricks-saxoji-benedict-ji-01034726435!@#$%231%$#@%",
  "corp_codes": "00126380,00164779,00164742",
  "bsns_year": "2023",
  "reprt_code": "11011",
  "account_nm": "매출액"
}
```

**참고:**
- `corp_codes`는 콤마로 구분된 기업 고유번호 목록입니다.
- `account_nm`은 선택적 파라미터로, 특정 계정과목을 조회할 때 사용합니다. 입력하지 않으면 주요 재무제표 항목 전체를 조회합니다.

### 23. 외부감사인 조회 (`audit`)
```json
{
  "company": "삼성전자",
  "query_type": "audit",
  "auth_key": "linkbricks-saxoji-benedict-ji-01034726435!@#$%231%$#@%",
  "includes_exec": false
}
```

**참고:**
- `includes_exec`는 선택적 파라미터로, true로 설정하면 전체 감사인 내역을 조회합니다. 기본값은 false입니다.

### 24. 상장폐지 현황 조회 (`stock_suspension`)
```json
{
  "company": "삼성전자",
  "query_type": "stock_suspension",
  "auth_key": "linkbricks-saxoji-benedict-ji-01034726435!@#$%231%$#@%"
}
```

### 25. 증자(감자) 현황 조회 (`stock_change`)
```json
{
  "company": "삼성전자",
  "query_type": "stock_change",
  "auth_key": "linkbricks-saxoji-benedict-ji-01034726435!@#$%231%$#@%"
}
```

### 26. 사업의 내용 조회 (`biz_overview`)
```json
{
  "company": "삼성전자",
  "query_type": "biz_overview",
  "auth_key": "linkbricks-saxoji-benedict-ji-01034726435!@#$%231%$#@%",
  "bsns_year": "2023",
  "rpt_type": "1"
}
```

**참고:**
- `rpt_type`은 보고서 유형으로 "1"(사업), "2"(반기), "3"(분기)로 입력합니다. 기본값은 "1"입니다.

### 27. 주요사항보고서 조회 (`event`)
```json
{
  "company": "삼성전자",
  "query_type": "event",
  "auth_key": "linkbricks-saxoji-benedict-ji-01034726435!@#$%231%$#@%",
  "event_type": "유상증자",
  "start_date": "20230101",
  "end_date": "20231231"
}
```

**참고:**
- `event_type`은 필수 파라미터로, 다음 중 하나의 값을 입력할 수 있습니다:
  - '부도발생', '영업정지', '회생절차', '해산사유', '유상증자', '무상증자', '유무상증자', '감자', '관리절차개시', '소송'
  - '해외상장결정', '해외상장폐지결정', '해외상장', '해외상장폐지', '전환사채발행', '신주인수권부사채발행', '교환사채발행'
  - '관리절차중단', '조건부자본증권발행', '자산양수도', '타법인증권양도', '유형자산양도', '유형자산양수', '타법인증권양수'
  - '영업양도', '영업양수', '자기주식취득신탁계약해지', '자기주식취득신탁계약체결', '자기주식처분', '자기주식취득', '주식교환', '회사분할합병', '회사분할', '회사합병', '사채권양수', '사채권양도결정' 등

### 28. 증권신고서 조회 (`regstate`)
```json
{
  "company": "삼성전자",
  "query_type": "regstate",
  "auth_key": "linkbricks-saxoji-benedict-ji-01034726435!@#$%231%$#@%",
  "key_word": "지분증권",
  "start_date": "20230101",
  "end_date": "20231231"
}
```

**참고:**
- `key_word`는 필수 파라미터로, 다음 중 하나의 값을 입력해야 합니다:
  - '주식의포괄적교환이전', '합병', '증권예탁증권', '채무증권', '지분증권', '분할'

## 응답 형식

성공적인 응답:
```json
{
  "status": "success",
  "data": [...]
}
```

오류 응답:
```json
{
  "detail": "오류 메시지"
}
```

## OpenDartReader 라이브러리

이 API는 [OpenDartReader](https://github.com/FinanceData/OpenDartReader) 라이브러리를 사용하여 DART 시스템에 접근합니다. 더 자세한 정보는 해당 라이브러리의 문서를 참조하세요.
