import streamlit as st
import pandas as pd
from datetime import datetime, date
from pathlib import Path
import requests

st.set_page_config(page_title="여름방학 하루 점검", page_icon="✅", layout="wide")

CHECK_ITEMS = [
    "정해진 시간에 일어났다",
    "오늘할 공부 개수를 완료했다",
    "계획한 시간에 공부를 시작했다",
    "휴대폰 사용 시간을 조절했다",
    "20분 이상 몸을 움직였다",
    "어제 밤늦게까지 깨어 있지 않았다",
    "오늘 하루를 간단히 돌아봤다",
]

COLUMNS = ["제출시각", "날짜", "반", "번호", "이름", *CHECK_ITEMS, "점수", "한줄소감"]
LOCAL_CSV = Path("data.csv")


def use_apps_script():
    return (
        "apps_script" in st.secrets
        and "web_app_url" in st.secrets["apps_script"]
        and "secret_token" in st.secrets["apps_script"]
    )


def get_script_config():
    return st.secrets["apps_script"]["web_app_url"], st.secrets["apps_script"]["secret_token"]


def read_data():
    if use_apps_script():
        url, token = get_script_config()
        try:
            response = requests.get(url, params={"token": token, "action": "read"}, timeout=20)
            response.raise_for_status()
            result = response.json()
            if result.get("status") != "ok":
                st.error("Google Sheets에서 데이터를 읽지 못했습니다: " + str(result))
                return pd.DataFrame(columns=COLUMNS)
            df = pd.DataFrame(result.get("records", []))
        except Exception as e:
            st.error(f"Google Sheets 읽기 오류: {e}")
            return pd.DataFrame(columns=COLUMNS)
    else:
        if LOCAL_CSV.exists():
            df = pd.read_csv(LOCAL_CSV)
        else:
            df = pd.DataFrame(columns=COLUMNS)

    for col in COLUMNS:
        if col not in df.columns:
            df[col] = ""

    if not df.empty:
        df["번호"] = pd.to_numeric(df["번호"], errors="coerce").astype("Int64")
        df["점수"] = pd.to_numeric(df["점수"], errors="coerce").fillna(0).astype(int)

    return df[COLUMNS]


def append_data(row):
    if use_apps_script():
        url, token = get_script_config()
        payload = {"token": token, "action": "append", "row": row}
        response = requests.post(url, json=payload, timeout=20)
        response.raise_for_status()
        result = response.json()
        if result.get("status") != "ok":
            raise RuntimeError(str(result))
    else:
        df = read_data()
        df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
        df.to_csv(LOCAL_CSV, index=False, encoding="utf-8-sig")


def student_page():
    st.title("✅ 여름방학 하루 자기점검")
    st.caption("하루에 한 번, 30초만 체크하면 됩니다. 생활리듬이 무너지지 않게 확인하는 용도입니다.")

    with st.form("daily_check_form", clear_on_submit=False):
        st.subheader("1. 기본 정보")
        col1, col2, col3, col4 = st.columns([1, 1, 1, 1.2])
        with col1:
            class_name = st.text_input("반", value="1반", max_chars=10)
        with col2:
            number = st.number_input("번호", min_value=1, max_value=40, step=1)
        with col3:
            name = st.text_input("이름", placeholder="홍길동")
        with col4:
            check_date = st.date_input("점검 날짜", value=date.today())

        st.subheader("2. 오늘의 체크")
        results = {}
        for item in CHECK_ITEMS:
            results[item] = st.checkbox(item)

        score = sum(1 for v in results.values() if v)

        st.subheader("3. 한 줄 소감")
        comment = st.text_input("오늘 하루를 한 줄로 적어보세요. 예: 수학 문제집은 했는데 늦게 잤다.", max_chars=80)

        submitted = st.form_submit_button("제출하기")

    if submitted:
        if not name.strip():
            st.error("이름을 입력해야 제출할 수 있습니다.")
            return

        row = {
            "제출시각": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "날짜": check_date.strftime("%Y-%m-%d"),
            "반": class_name.strip(),
            "번호": int(number),
            "이름": name.strip(),
            **{item: "O" if results[item] else "X" for item in CHECK_ITEMS},
            "점수": score,
            "한줄소감": comment.strip(),
        }

        try:
            append_data(row)
            st.success(f"{name} 학생, 제출 완료! 오늘 점수는 {score}/7점입니다.")
            if score >= 6:
                st.balloons()
                st.info("오늘은 생활리듬을 잘 지킨 날입니다. 내일도 이 정도만 유지하면 충분합니다.")
            elif score >= 4:
                st.info("괜찮습니다. 방학은 완벽함보다 다시 시작하는 힘이 중요합니다.")
            else:
                st.warning("오늘은 조금 무너진 날입니다. 내일은 '기상 시간'과 '공부 시작' 두 가지만 먼저 회복해 봅시다.")
        except Exception as e:
            st.error(f"제출 중 오류가 발생했습니다: {e}")


def calculate_missing_numbers(df, text):
    try:
        text = text.replace(" ", "")
        if "-" in text and "," not in text:
            start, end = text.split("-")
            expected = set(range(int(start), int(end) + 1))
        else:
            expected = set(int(x) for x in text.split(",") if x)
        submitted = set(pd.to_numeric(df["번호"], errors="coerce").dropna().astype(int).tolist())
        return sorted(expected - submitted)
    except Exception:
        return None


def admin_page():
    st.title("📊 담임교사용 확인 화면")
    admin_password = st.secrets.get("admin_password", "1234")
    password = st.text_input("관리자 비밀번호", type="password")

    if password != admin_password:
        st.info("관리자 비밀번호를 입력하면 제출 현황을 볼 수 있습니다.")
        return

    df = read_data()
    if df.empty:
        st.warning("아직 제출된 기록이 없습니다.")
        return

    st.success("관리자 인증 완료")

    available_dates = sorted(df["날짜"].dropna().unique(), reverse=True)
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        selected_date = st.selectbox("날짜 선택", options=["전체"] + available_dates)
    with col2:
        selected_class = st.selectbox("반 선택", options=["전체"] + sorted(df["반"].dropna().unique().tolist()))
    with col3:
        expected_numbers = st.text_input("우리 반 번호 입력", value="1-30", help="예: 1-30 또는 1,2,3,5,8")

    filtered = df.copy()
    if selected_date != "전체":
        filtered = filtered[filtered["날짜"] == selected_date]
    if selected_class != "전체":
        filtered = filtered[filtered["반"] == selected_class]

    latest = filtered.sort_values("제출시각").drop_duplicates(subset=["날짜", "반", "번호", "이름"], keep="last")

    st.subheader("1. 제출 현황 요약")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("제출 건수", f"{len(filtered)}건")
    m2.metric("제출 학생 수", f"{len(latest)}명")
    m3.metric("평균 점수", f"{latest['점수'].mean():.1f}/7" if len(latest) else "0/7")
    m4.metric("6점 이상", f"{(latest['점수'] >= 6).sum()}명")

    st.subheader("2. 항목별 실천률")
    if len(latest) > 0:
        rate_df = pd.DataFrame([
            {"항목": item, "실천률(%)": round((latest[item] == "O").mean() * 100, 1)}
            for item in CHECK_ITEMS
        ])
        st.dataframe(rate_df, use_container_width=True, hide_index=True)
        st.bar_chart(rate_df.set_index("항목"))

    st.subheader("3. 미제출 번호 확인")
    missing_numbers = calculate_missing_numbers(latest, expected_numbers)
    if missing_numbers is None:
        st.caption("번호 입력 형식이 맞지 않아 미제출 번호를 계산하지 못했습니다.")
    elif len(missing_numbers) == 0:
        st.success("입력한 번호 기준으로 미제출자가 없습니다.")
    else:
        st.warning("미제출 번호: " + ", ".join(map(str, missing_numbers)))

    st.subheader("4. 학생별 제출 내용")
    display_cols = ["제출시각", "날짜", "반", "번호", "이름", "점수", *CHECK_ITEMS, "한줄소감"]
    st.dataframe(latest[display_cols].sort_values(["반", "번호", "이름"]), use_container_width=True, hide_index=True)

    csv = latest[display_cols].to_csv(index=False, encoding="utf-8-sig")
    st.download_button("현재 화면 자료 CSV 다운로드", csv, "방학_자기점검_제출현황.csv", "text/csv")


def main():
    st.sidebar.title("메뉴")
    page = st.sidebar.radio("화면 선택", ["학생 자기점검", "담임 확인"])
    st.sidebar.divider()
    st.sidebar.caption("담임 확인 화면은 비밀번호가 필요합니다.")

    if not use_apps_script():
        st.sidebar.warning("Google Apps Script 연결 전입니다. 현재는 임시 CSV 저장 모드입니다.")

    if page == "학생 자기점검":
        student_page()
    else:
        admin_page()


if __name__ == "__main__":
    main()
