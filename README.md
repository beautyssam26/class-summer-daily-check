# 고1 여름방학 하루 자기점검 웹앱 - Apps Script 저장 방식

이 버전은 Google Cloud 서비스 계정 JSON 키를 만들 필요가 없습니다.
Google Sheets의 Apps Script 웹앱 URL을 통해 학생 제출 내용을 저장합니다.

## 파일 구성
- app.py: Streamlit 웹앱 코드
- requirements.txt: 필요한 패키지
- google_apps_script_code.gs: Google Sheets Apps Script에 붙여넣을 코드
- .streamlit/secrets.toml.example: Streamlit Secrets 예시

## Streamlit Secrets 예시

```toml
admin_password = "선생님용_비밀번호"

[apps_script]
web_app_url = "Apps Script 배포 후 생성된 웹앱 URL"
secret_token = "선생님이_정한_긴_비밀문자"
```
