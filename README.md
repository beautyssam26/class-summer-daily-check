# 고1 여름방학 하루 자기점검 웹앱

학생들이 매일 체크하고, 담임교사가 제출 현황을 확인할 수 있는 Streamlit 웹앱입니다.

## 기능
- 학생 입력: 반, 번호, 이름, 날짜, 7개 점검 항목, 한 줄 소감
- 담임 확인: 날짜별 제출 현황, 평균 점수, 항목별 실천률, 미제출 번호 확인
- 저장 방식: Google Sheets 권장
- Google Sheets 설정이 없으면 `data.csv`에 임시 저장됩니다.

## 학생 점검 항목
1. 정해진 시간에 일어났다
2. 아침 식사를 했다
3. 계획한 공부를 시작했다
4. 휴대폰 사용 시간을 조절했다
5. 20분 이상 몸을 움직였다
6. 밤늦게까지 깨어 있지 않았다
7. 오늘 하루를 간단히 돌아봤다

## 배포 방법 요약

### 1. GitHub 저장소 만들기
아래 파일을 GitHub 저장소에 올립니다.

- app.py
- requirements.txt

### 2. Google Sheets 만들기
Google Drive에서 새 스프레드시트를 만들고 이름을 예를 들어 아래처럼 정합니다.

`방학_자기점검_응답`

첫 번째 워크시트 이름은 `responses`로 두면 됩니다.

### 3. Google Cloud 서비스 계정 만들기
Google Cloud Console에서 서비스 계정을 만들고 JSON 키를 발급받습니다.
발급받은 JSON의 `client_email` 주소를 복사해서, 위에서 만든 Google Sheets에 편집자로 공유합니다.

### 4. Streamlit Cloud Secrets 입력
Streamlit Cloud 앱 설정의 Secrets에 아래 형식으로 입력합니다.

```toml
admin_password = "선생님이_정할_비밀번호"

[gsheet]
spreadsheet_name = "방학_자기점검_응답"
worksheet_name = "responses"

[gcp_service_account]
type = "service_account"
project_id = "..."
private_key_id = "..."
private_key = "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
client_email = "..."
client_id = "..."
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "..."
universe_domain = "googleapis.com"
```

### 5. 학생에게 링크 배포
Streamlit Cloud에서 생성된 앱 링크를 학생들에게 공유합니다.
학생들은 `학생 자기점검` 화면에서 매일 제출하면 됩니다.

### 6. 담임 확인
같은 링크에서 왼쪽 메뉴의 `담임 확인`을 선택하고 비밀번호를 입력하면 제출 현황을 확인할 수 있습니다.
