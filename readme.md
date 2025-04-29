# LINKBRICKS HORIZON AI DART Financial Data API 


Linkbricks Horizon AI가 개발한 FastAPI 애플리케이션을 사용하여 한국 금융감독원 DART 시스템의 기업 공시 정보에 접근할 수 있는 API입니다.
powered by OpenDartReader

## 기능

1. 기업 공시 정보 조회
2. 정기 보고서 조회
3. 기업 개황 정보 조회
4. 첨부 파일 URL 조회
5. 사업보고서 내용 조회
6. 기업 고유번호 조회
7. 대량보유 상황 조회
8. 임원 현황 조회
9. 배당 정보 조회
10. 자본금 변동사항 조회
11. 재무제표 특정 항목 조회
12. 전체 재무제표 조회
13. 사업의 내용 조회

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

요청 본문 예시:
```json
{
  "company": "삼성전자",
  "query_type": "disclosure",
  "auth_key": "linkbricks-saxoji-benedict-ji-01034726435!@#$%231%$#@%",
  "start_date": "20250101",
  "end_date": "20250401"
}
```

`query_type` 값에 따른 기능:

1. **공시정보 조회** (`"query_type": "disclosure"`)
   ```json
   {
     "company": "삼성전자",
     "query_type": "disclosure",
     "auth_key": "linkbricks-saxoji-benedict-ji-01034726435!@#$%231%$#@%",
     "start_date": "20250101",
     "end_date": "20250401"
   }
   ```

2. **정기 최종 보고서 조회** (`"query_type": "report"`)
   ```json
   {
     "company": "삼성전자",
     "query_type": "report",
     "auth_key": "linkbricks-saxoji-benedict-ji-01034726435!@#$%231%$#@%",
     "start_date": "20250101",
     "end_date": "20250401"
   }
   ```

3. **기업 개황정보 조회** (`"query_type": "company_info"`)
   ```json
   {
     "company": "삼성전자",
     "query_type": "company_info",
     "auth_key": "linkbricks-saxoji-benedict-ji-01034726435!@#$%231%$#@%"
   }
   ```

4. **사업보고서 내용 조회** (`"query_type": "report_content"`)
   ```json
   {
     "company": "삼성전자",
     "query_type": "report_content",
     "auth_key": "linkbricks-saxoji-benedict-ji-01034726435!@#$%231%$#@%",
     "bsns_year": "2023",
     "reprt_code": "11011"
   }
   ```
   
   **참고:**
   - `corp_code`는 선택적으로 입력 가능합니다. 입력하지 않으면 `company` 값을 기준으로 자동 조회합니다.
   
   **보고서 코드(reprt_code) 값:**
   - "11011": 사업보고서 (연간)
   - "11012": 반기보고서
   - "11013": 1분기보고서
   - "11014": 3분기보고서

5. **기업 고유번호 조회** (`"query_type": "company_code"`)
   ```json
   {
     "company": "삼성전자",
     "query_type": "company_code",
     "auth_key": "linkbricks-saxoji-benedict-ji-01034726435!@#$%231%$#@%"
   }
   ```

6. **대량보유 상황 조회** (`"query_type": "major_shareholder"`)
   ```json
   {
     "company": "삼성전자",
     "query_type": "major_shareholder",
     "auth_key": "linkbricks-saxoji-benedict-ji-01034726435!@#$%231%$#@%"
   }
   ```
   **참고:** `corp_code`는 선택적으로 입력 가능합니다. 입력하지 않으면 `company` 값을 기준으로 자동 조회합니다.

7. **임원 현황 조회** (`"query_type": "executive"`)
   ```json
   {
     "company": "삼성전자",
     "query_type": "executive",
     "auth_key": "linkbricks-saxoji-benedict-ji-01034726435!@#$%231%$#@%"
   }
   ```
   **참고:** `corp_code`는 선택적으로 입력 가능합니다. 입력하지 않으면 `company` 값을 기준으로 자동 조회합니다.

8. **배당 정보 조회** (`"query_type": "dividend"`)
   ```json
   {
     "company": "삼성전자",
     "query_type": "dividend",
     "auth_key": "linkbricks-saxoji-benedict-ji-01034726435!@#$%231%$#@%"
   }
   ```
   **참고:** `corp_code`는 선택적으로 입력 가능합니다. 입력하지 않으면 `company` 값을 기준으로 자동 조회합니다.

9. **자본금 변동사항 조회** (`"query_type": "capital"`)
   ```json
   {
     "company": "삼성전자",
     "query_type": "capital",
     "auth_key": "linkbricks-saxoji-benedict-ji-01034726435!@#$%231%$#@%"
   }
   ```
   **참고:** `corp_code`는 선택적으로 입력 가능합니다. 입력하지 않으면 `company` 값을 기준으로 자동 조회합니다.

10. **재무제표 특정 항목 조회** (`"query_type": "section_financial"`)
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
    - `corp_code`는 선택적으로 입력 가능합니다. 입력하지 않으면 `company` 값을 기준으로 자동 조회합니다.
    - `fs_div`는 개별/연결구분으로 "CFS"(연결) 또는 "OFS"(개별)로 입력합니다. 기본값은 "CFS"입니다.

11. **전체 재무제표 조회** (`"query_type": "full_financial"`)
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
    - `corp_code`는 선택적으로 입력 가능합니다. 입력하지 않으면 `company` 값을 기준으로 자동 조회합니다.
    - `separate`는 개별/연결 구분으로 true(개별) 또는 false(연결)로 입력합니다. 기본값은 false입니다.

12. **사업의 내용 조회** (`"query_type": "biz_overview"`)
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
    - `corp_code`는 선택적으로 입력 가능합니다. 입력하지 않으면 `company` 값을 기준으로 자동 조회합니다.
    - `rpt_type`은 보고서 유형으로 "1"(사업), "2"(반기), "3"(분기)로 입력합니다. 기본값은 "1"입니다.

### 2. 첨부파일 다운로드 URL 조회

**GET** `/api/dart/file/{rcp_no}?auth_key=linkbricks-saxoji-benedict-ji-01034726435!@#$%231%$#@%`

특정 공시 보고서의 첨부파일 다운로드 URL을 제공합니다. 인증키는 쿼리 파라미터로 전달합니다.

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
