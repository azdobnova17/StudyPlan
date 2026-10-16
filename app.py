from datetime import date, datetime, time, timedelta
from html import escape
from zoneinfo import ZoneInfo
import time as clock
import base64

import streamlit as st
import database


st.set_page_config(
    page_title="StudyPlan",
    page_icon="🌿",
    layout="wide"
)

DAYS = [
    "Понедельник",
    "Вторник",
    "Среда",
    "Четверг",
    "Пятница",
    "Суббота",
    "Воскресенье"
]

MONTHS = [
    "января", "февраля", "марта", "апреля",
    "мая", "июня", "июля", "августа",
    "сентября", "октября", "ноября", "декабря"
]

today = datetime.now(ZoneInfo("Europe/Moscow")).date()

illustration_svg = """
<svg viewBox="0 0 500 390" xmlns="http://www.w3.org/2000/svg">
<rect width="500" height="390" fill="#cbd6c0"/>
<circle cx="440" cy="5" r="140" fill="#b8c7ad"/>
<circle cx="15" cy="380" r="135" fill="#dce3cf"/>
<path d="M375 0C370 60 448 70 500 135" fill="none" stroke="#a0b294" stroke-width="2"/>
<path d="M398 0C390 51 460 64 500 107" fill="none" stroke="#a0b294" stroke-width="2"/>
<ellipse cx="240" cy="315" rx="166" ry="27" fill="#8d9d7f" opacity=".18"/>
<g transform="rotate(-9 220 205)">
<rect x="87" y="59" width="226" height="265" rx="13" fill="#788d6c"/>
<rect x="97" y="52" width="222" height="265" rx="12" fill="#fffaf0"/>
<rect x="97" y="52" width="20" height="265" rx="8" fill="#e7e2d4"/>
<g stroke="#a6ae99" stroke-width="3" fill="none">
<path d="M92 80h21M92 112h21M92 144h21M92 176h21M92 208h21M92 240h21M92 272h21"/>
</g>
<text x="140" y="96" fill="#4d6848" font-family="sans-serif" font-size="16" font-weight="700">МОЯ НЕДЕЛЯ</text>
<rect x="140" y="111" width="139" height="2" fill="#d8dcca"/>
<g fill="#edf0e4" stroke="#c9d3bc">
<rect x="141" y="136" width="18" height="18" rx="5"/>
<rect x="141" y="176" width="18" height="18" rx="5"/>
<rect x="141" y="216" width="18" height="18" rx="5"/>
</g>
<g stroke="#537b4d" stroke-width="2.5" fill="none" stroke-linecap="round">
<path d="M146 145l4 4 6-8M146 185l4 4 6-8"/>
</g>
<g fill="#cbd3c0">
<rect x="171" y="140" width="104" height="5" rx="2"/>
<rect x="171" y="150" width="67" height="3" rx="1"/>
<rect x="171" y="180" width="93" height="5" rx="2"/>
<rect x="171" y="190" width="76" height="3" rx="1"/>
<rect x="171" y="220" width="109" height="5" rx="2"/>
<rect x="171" y="230" width="57" height="3" rx="1"/>
</g>
<rect x="141" y="265" width="135" height="22" rx="7" fill="#e4ebd8"/>
<text x="151" y="280" fill="#708463" font-family="sans-serif" font-size="9">ОДИН ШАГ ЗА ДРУГИМ</text>
</g>
<g transform="rotate(16 345 220)">
<rect x="337" y="122" width="12" height="166" rx="4" fill="#db7039"/>
<rect x="337" y="122" width="12" height="17" rx="4" fill="#f0b693"/>
<path d="M337 288h12l-6 20z" fill="#ead7b6"/>
<path d="M341 302h4l-2 6z" fill="#59634d"/>
</g>
<ellipse cx="413" cy="298" rx="51" ry="17" fill="#8b9b7e" opacity=".22"/>
<ellipse cx="409" cy="278" rx="58" ry="36" fill="#ede9dc"/>
<path d="M449 226c42-7 44 46 5 41" fill="none" stroke="#fff9ed" stroke-width="13"/>
<path d="M373 218h72v46c-2 33-67 34-72 0z" fill="#fff9ed"/>
<ellipse cx="409" cy="220" rx="36" ry="17" fill="#e3d6bf"/>
<ellipse cx="409" cy="220" rx="29" ry="12" fill="#9b6741"/>
<path d="M392 220c12-15 31-9 23 2-8 11-25 6-17-2 5-6 16-2 12 3" fill="none" stroke="#f2d7a7" stroke-width="3" stroke-linecap="round"/>
<g stroke="#65815a" stroke-width="3" fill="#829b71">
<path d="M416 151c-7-39-18-67-42-93" fill="none"/>
<path d="M388 83c-31-3-35-22-39-31 23-2 38 8 39 31z"/>
<path d="M399 105c22-17 37-10 47-5-13 21-31 22-47 5z"/>
<path d="M409 129c-25 0-36-12-42-24 25-5 36 5 42 24z"/>
</g>
</svg>
"""

illustration_url = (
    "data:image/svg+xml;base64,"
    + base64.b64encode(illustration_svg.encode()).decode()
)

st.html("""
<style>
.stApp {
    --primary-color: #42654f;
    --text-color: #263b2d;
    --background-color: #f8f5ed;
    --secondary-background-color: #eeeade;
    background: #f8f5ed;
    color: #263b2d;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    color-scheme: light;
}
[data-testid="stHeader"] { background: rgba(248,245,237,.96); }
[data-testid="stMainBlockContainer"] { max-width: 1220px; padding: 2rem 2.5rem 3rem; }
[data-testid="stSidebar"] { background: #e7ecdf; border-right: 1px solid #d5ddcd; }
[data-testid="stSidebar"] [role="radiogroup"] { gap: 6px; }
[data-testid="stSidebar"] [role="radiogroup"] label { padding: 11px 14px; border-radius: 12px; }
[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) { background: #cfdac6; }
[data-testid="stSidebar"] h2 { color: #365a42; }
[data-testid="stWidgetLabel"] p { color: #3a4b3d !important; }
h1, h2, h3 { color: #263b2d !important; letter-spacing: -.6px; }
[data-testid="stCaptionContainer"] { color: #687462; }
[data-testid="stForm"] { background: #fffdf8; border: 1px solid #e1dfd4; border-radius: 22px; padding: 24px; }
[data-baseweb="input"], [data-baseweb="select"] > div { background: #f5f3eb !important; border-color: #d8dccf !important; border-radius: 10px !important; }
input, [data-baseweb="select"] { color: #263b2d !important; }
[data-testid="stButton"] button { background: #e48a52; color: #332114; border: 1px solid #e48a52; border-radius: 12px; min-height: 46px; padding: 0 20px; }
[data-testid="stButton"] button:hover { background: #d97c43; border-color: #d97c43; color: #332114; }
[data-testid="stFormSubmitButton"] button { background: #42654f; border: 1px solid #42654f; color: white; border-radius: 11px; min-height: 44px; }
[data-testid="stFormSubmitButton"] button:hover { background: #34523f; border-color: #34523f; color: white; }
[data-testid="stButton"] button p { color: #332114; }
[data-testid="stFormSubmitButton"] button p { color: white; }
[data-testid="stButton"] button:focus-visible, [data-testid="stFormSubmitButton"] button:focus-visible { outline: 3px solid #ddac86; outline-offset: 3px; }
[data-testid="stExpander"] { background: #fffdf8; border-radius: 16px; }
.brand { display: flex; align-items: center; gap: 10px; margin: 5px 0 17px; }
.brand-mark { display: grid; place-items: center; width: 39px; height: 39px; border-radius: 13px; color: #fffdf8; background: #42654f; font-size: 17px; font-weight: 700; }
.brand-name { font-size: 23px; font-weight: 700; letter-spacing: -.6px; color: #2f4d39; }
.brand-note { font-size: 12px; color: #6d7b64; margin-top: 1px; }
.topline { display: flex; justify-content: space-between; align-items: center; gap: 12px; flex-wrap: wrap; margin-bottom: 22px; }
.overline { font-size: 10px; font-weight: 700; letter-spacing: 2px; color: #76816e; }
.date-tag { font-size: 12px; color: #5c6d55; padding: 7px 12px; border: 1px solid #d6decd; border-radius: 30px; }
.hero { display: grid; grid-template-columns: 1.12fr 1fr; align-items: center; gap: 35px; margin: 4px 0 8px; }
.hero h1 { font-size: clamp(36px, 4vw, 58px); font-weight: 750; line-height: 1.08; letter-spacing: -2px; padding: 0; margin: 12px 0 18px; }
.hero h1 span { color: #668065; }
.hero p { color: #6c7464; font-size: 15px; line-height: 1.7; max-width: 385px; margin-bottom: 18px; }
.mini-label { display: inline-block; color: #56734d; background: #e7eddd; border-radius: 30px; font-size: 11px; padding: 6px 11px; }
.visual { overflow: hidden; background: #cbd6c0; border-radius: 85px 25px 85px 25px; border: 1px solid #bdcab2; }
.visual img { display: block; width: 100%; height: auto; }
.hero-notes { display: flex; flex-wrap: wrap; gap: 18px; color: #617357; font-size: 12px; margin-top: 15px; }
.stats { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin: 22px 0 8px; }
.stat { padding: 19px 20px; background: #fffdf8; border: 1px solid #e2dfd2; border-radius: 18px; }
.stat:nth-child(2) { background: #e8eddf; border-color: #d9e0ce; }
.stat:nth-child(3) { background: #f1eadb; }
.stat:nth-child(4) { background: #f7e9de; border-color: #eddbcd; }
.number { display: block; font-size: 30px; font-weight: 650; letter-spacing: -1px; color: #344d37; margin-bottom: 5px; }
.stat-label { font-size: 12px; color: #73765f; }
.panel-heading { display: flex; align-items: center; justify-content: space-between; gap: 10px; padding: 12px 0; margin-top: 12px; }
.panel-heading strong { font-size: 21px; letter-spacing: -.6px; color: #2f4433; }
.panel-heading span { font-size: 12px; color: #7a826e; }
.task { border: 1px solid #e2dfd2; border-radius: 16px; padding: 17px 18px; margin-bottom: 10px; background: #fffdf8; }
.task.done { background: #eff3e9; border-color: #d9e3ce; }
.task.overdue { border-color: #edcfbc; background: #fcf1e8; }
.task-top { display: flex; justify-content: space-between; gap: 10px; flex-wrap: wrap; align-items: flex-start; }
.task-title { font-size: 15px; font-weight: 650; color: #344834; overflow-wrap: anywhere; flex: 1; min-width: 160px; }
.task-meta { color: #7c806b; font-size: 12px; margin-top: 7px; overflow-wrap: anywhere; }
.badge { font-size: 10px; border: 1px solid #dfe3d3; padding: 4px 8px; border-radius: 20px; color: #63754f; background: #eef2e4; white-space: nowrap; }
.done .badge { color: #406045; background: #dfe9d7; border-color: #cddcc4; }
.overdue .badge { color: #9a592f; background: #f6dfcd; border-color: #ebcdb5; }
.empty { border: 1px dashed #cbd4bd; padding: 27px 20px; border-radius: 17px; color: #7a846c; background: #f1f3e9; font-size: 13px; line-height: 1.6; }
.empty strong { display: block; font-size: 15px; color: #526549; margin-bottom: 5px; }
.lesson { padding: 16px 18px; border: 1px solid #e2dfd2; background: #fffdf8; border-radius: 16px; margin-bottom: 10px; display: flex; gap: 16px; align-items: center; }
.lesson-time { background: #e8eddf; color: #53704b; font-size: 12px; padding: 8px 10px; border-radius: 9px; white-space: nowrap; }
.lesson-name { font-weight: 650; font-size: 14px; color: #344834; overflow-wrap: anywhere; }
.note { background: #dfe7d5; border-radius: 18px; padding: 23px; margin-top: 16px; color: #53684b; font-size: 13px; line-height: 1.7; }
.note strong { display: block; font-size: 17px; color: #354f38; margin-bottom: 6px; }
.week { display: grid; grid-template-columns: repeat(7, 1fr); gap: 6px; margin: 6px 0 14px; }
.week-day { text-align: center; border: 1px solid #dfdfcf; background: #fffdf8; border-radius: 12px; padding: 11px 3px; color: #7b826d; font-size: 10px; }
.week-day b { display: block; font-size: 16px; color: #4c6445; margin-top: 4px; }
.week-day.current { background: #42654f; border-color: #42654f; color: #d8e3cb; }
.week-day.current b { color: #fffdf8; }
.footer { margin-top: 35px; padding-top: 18px; border-top: 1px solid #dedfd1; display: flex; justify-content: space-between; gap: 12px; flex-wrap: wrap; color: #8b907b; font-size: 11px; }
@media (max-width: 750px) {
    [data-testid="stMainBlockContainer"] { padding: 1.5rem 1rem 2rem; }
    .hero { grid-template-columns: 1fr; gap: 20px; }
    .hero h1 { font-size: 39px; letter-spacing: -1.5px; }
    .visual { max-width: 420px; width: 100%; border-radius: 50px 20px 50px 20px; }
    .stats { grid-template-columns: repeat(2, 1fr); }
    .stat { padding: 16px; }
    .lesson { flex-wrap: wrap; gap: 10px; }
    [data-testid="stForm"] { padding: 18px; }
}
</style>
""")

try:
    configured_url = st.secrets.get("database_url")
except FileNotFoundError:
    configured_url = None

try:
    database.init_db(configured_url)
except (ValueError, database.DatabaseError):
    st.error(
        "Не удалось подключиться к базе. "
        "Проверь настройки подключения в Secrets."
    )
    st.stop()


def load_data(action, *args):
    try:
        return action(*args)
    except database.DatabaseError:
        st.error("Не удалось загрузить записи. Попробуй позже.")
        st.stop()


def empty_state(title, text):
    st.html(
        '<div class="empty">'
        f'<strong>{escape(title)}</strong>'
        f'{escape(text)}</div>'
    )


def heading(title, subtitle=""):
    st.html(
        '<div class="panel-heading">'
        f'<strong>{escape(title)}</strong>'
        f'<span>{escape(subtitle)}</span>'
        '</div>'
    )


def show_tasks(tasks):
    for task in tasks:
        due = date.fromisoformat(task["due"])
        state = ""
        label = "Не выполнено"

        if task["done"]:
            state = "done"
            label = "Выполнено"
        elif due < today:
            state = "overdue"
            label = "Просрочено"
        elif due == today:
            label = "На сегодня"

        st.html(
            f'<div class="task {state}">'
            '<div class="task-top">'
            f'<div class="task-title">{escape(task["title"])}</div>'
            f'<span class="badge">{label}</span>'
            '</div>'
            '<div class="task-meta">'
            f'{escape(task["subject"])} · '
            f'Сдать до {due.strftime("%d.%m.%Y")}'
            '</div></div>'
        )


def show_lessons(lessons):
    for lesson in lessons:
        room = (
            f'Аудитория {lesson["room"]}'
            if lesson["room"]
            else "Аудитория не указана"
        )

        st.html(
            '<div class="lesson">'
            '<div class="lesson-time">'
            f'{lesson["start"]} – {lesson["end"]}'
            '</div>'
            '<div>'
            f'<div class="lesson-name">{escape(lesson["subject"])}</div>'
            f'<div class="task-meta">{escape(room)}</div>'
            '</div></div>'
        )


def refresh_tasks(message):
    st.session_state["task_version"] = (
        st.session_state.get("task_version", 0) + 1
    )
    st.session_state["task_message"] = message
    st.rerun()


def refresh_lessons(message):
    st.session_state["lesson_version"] = (
        st.session_state.get("lesson_version", 0) + 1
    )
    st.session_state["lesson_message"] = message
    st.rerun()


def open_section(name):
    st.session_state["section"] = name


def end_session():
    for key in list(st.session_state):
        del st.session_state[key]


def begin_session(user):
    end_session()
    st.session_state["auth_user_id"] = user["id"]
    st.session_state["auth_last_seen"] = clock.monotonic()
    st.session_state["account_message"] = (
        f'Добро пожаловать, {user["name"]}!'
    )
    st.rerun()


if st.session_state.get("auth_user_id"):
    previous_activity = st.session_state.get("auth_last_seen", 0)

    if clock.monotonic() - previous_activity > 1800:
        end_session()
        st.session_state["login_notice"] = (
            "Для продолжения войди снова: "
            "прошло 30 минут без действий."
        )

user = None

if st.session_state.get("auth_user_id"):
    try:
        user = database.get_user(
            st.session_state["auth_user_id"]
        )
    except database.DatabaseError:
        st.error("Не удалось открыть аккаунт. Попробуй позже.")
        st.stop()

    if user is None:
        end_session()

if user is None:
    st.html(
        '<div class="brand">'
        '<span class="brand-mark">S</span>'
        '<div>'
        '<div class="brand-name">StudyPlan</div>'
        '<div class="brand-note">Учеба в своем ритме</div>'
        '</div></div>'
    )

    st.title("Твоя учеба — в одном месте")
    st.write(
        "Войди в аккаунт, чтобы открыть свое расписание, "
        "задания и ближайшие сроки."
    )

    notice = st.session_state.pop("login_notice", None)

    if notice:
        st.info(notice)

    login_tab, register_tab = st.tabs(
        ["Войти", "Зарегистрироваться"]
    )

    with login_tab:
        with st.form("login_form", clear_on_submit=True):
            login = st.text_input(
                "Логин",
                max_chars=32,
                key="login_username"
            )

            password = st.text_input(
                "Пароль",
                type="password",
                max_chars=128,
                key="login_password"
            )

            login_submitted = st.form_submit_button(
                "Войти в аккаунт"
            )

        if login_submitted:
            try:
                begin_session(
                    database.authenticate(login, password)
                )
            except ValueError as error:
                st.error(str(error))
            except database.DatabaseError:
                st.error("Не удалось войти. Попробуй позже.")

    with register_tab:
        with st.form("registration_form", clear_on_submit=True):
            name = st.text_input(
                "Как к тебе обращаться",
                max_chars=100,
                key="register_name"
            )

            new_login = st.text_input(
                "Придумай логин",
                max_chars=32,
                key="register_username"
            )

            st.caption(
                "От 3 до 32 латинских букв, цифр или знаков _. "
                "Регистр букв не важен."
            )

            new_password = st.text_input(
                "Придумай пароль",
                type="password",
                max_chars=128,
                key="register_password"
            )

            confirmation = st.text_input(
                "Повтори пароль",
                type="password",
                max_chars=128,
                key="register_confirmation"
            )

            st.caption(
                "Пароль от 12 символов. "
                "Восстановление пароля пока не предусмотрено."
            )

            register_submitted = st.form_submit_button(
                "Создать аккаунт"
            )

        if register_submitted:
            if new_password != confirmation:
                st.error("Пароли не совпадают.")
            else:
                try:
                    begin_session(
                        database.create_user(
                            new_login,
                            new_password,
                            name
                        )
                    )
                except ValueError as error:
                    st.error(str(error))
                except database.DatabaseError:
                    st.error(
                        "Не удалось создать аккаунт. "
                        "Попробуй позже."
                    )

    st.caption(
        "Учебная версия. Для проверки используй вымышленные "
        "данные. Старые общие записи не относятся "
        "к новым аккаунтам."
    )

    st.stop()

user_id = user["id"]
st.session_state["auth_last_seen"] = clock.monotonic()

st.sidebar.html(
    '<div class="brand">'
    '<span class="brand-mark">S</span>'
    '<div>'
    '<div class="brand-name">StudyPlan</div>'
    '<div class="brand-note">Учеба в своем ритме</div>'
    '</div></div>'
)

st.sidebar.html(
    '<div class="task-meta">'
    f'Аккаунт: <strong>{escape(user["name"])}</strong><br>'
    f'Логин: {escape(user["username"])}'
    '</div>'
)

st.sidebar.button(
    "Выйти",
    on_click=end_session,
    key="logout"
)

section = st.sidebar.radio(
    "Мой план",
    ["Главная", "Расписание", "Задания", "Ближайшие сроки"],
    key="section"
)

st.sidebar.divider()

st.sidebar.caption(
    "Добавь занятия, запиши задания "
    "и следи за ближайшими сроками."
)

st.sidebar.caption(
    "Личный учебный план. Здесь показаны "
    "только записи твоего аккаунта."
)

st.html(
    '<div class="topline">'
    '<span class="overline">МОЕ УЧЕБНОЕ ПРОСТРАНСТВО</span>'
    '<span class="date-tag">'
    f'{DAYS[today.weekday()]} · '
    f'{today.day} {MONTHS[today.month - 1]}'
    '</span></div>'
)

account_message = st.session_state.pop(
    "account_message",
    None
)

if account_message:
    st.success(account_message)

if section == "Главная":
    st.html(
        """
        <div class="hero">
            <div>
                <span class="mini-label">Планируй спокойно</span>
                <h1>
                    Учеба по плану.<br>
                    <span>Жизнь в своем<br>ритме.</span>
                </h1>
                <p>
                    Расписание, задания и сроки сдачи
                    в одном месте.
                    Чтобы меньше искать и больше успевать.
                </p>
                <div class="hero-notes">
                    <span>✓ Понятный план</span>
                    <span>✓ Все сроки рядом</span>
                </div>
            </div>
            <div class="visual">
                <img
                    alt="Блокнот и учебные принадлежности"
                    src="__STUDYPLAN_IMAGE__"
                >
            </div>
        </div>
        """.replace("__STUDYPLAN_IMAGE__", illustration_url)
    )

    st.button(
        "Добавить задание →",
        on_click=open_section,
        args=("Задания",)
    )

    tasks = load_data(database.get_tasks, user_id)

    upcoming = load_data(
        database.get_upcoming_tasks,
        user_id,
        today
    )

    overdue = load_data(
        database.get_overdue_tasks,
        user_id,
        today
    )

    completed = sum(task["done"] for task in tasks)

    stats = [
        (len(tasks), "Всего заданий"),
        (completed, "Выполнено"),
        (len(upcoming), "На ближайшие 7 дней"),
        (len(overdue), "Просрочено")
    ]

    stats_html = '<div class="stats">'

    for number, label in stats:
        stats_html += (
            '<div class="stat">'
            f'<span class="number">{number}</span>'
            f'<span class="stat-label">{label}</span>'
            '</div>'
        )

    st.html(stats_html + "</div>")

    if tasks:
        st.progress(
            completed / len(tasks),
            text=f"Выполнено {completed} из {len(tasks)} заданий"
        )

    left, right = st.columns([1.25, 1], gap="large")

    with left:
        heading("Ближайшие задания", "Следующие 7 дней")

        if upcoming:
            show_tasks(upcoming[:3])
        else:
            empty_state(
                "Здесь появятся ближайшие работы",
                "Добавь задание с датой сдачи "
                "в ближайшие семь дней."
            )

        st.button(
            "Все сроки →",
            on_click=open_section,
            args=("Ближайшие сроки",)
        )

    with right:
        heading("Занятия сегодня", DAYS[today.weekday()])

        lessons = [
            lesson
            for lesson in load_data(
                database.get_lessons,
                user_id
            )
            if lesson["weekday"] == today.isoweekday()
        ]

        if lessons:
            show_lessons(lessons)
        else:
            empty_state(
                "На сегодня занятий нет",
                "Добавь свое расписание или используй "
                "день для самостоятельной работы."
            )

        st.html(
            '<div class="note">'
            '<strong>Начни с малого</strong>'
            'Запиши одну работу, укажи срок и отметь ее '
            'после выполнения. Так постепенно появится '
            'понятный учебный план.'
            '</div>'
        )

elif section == "Расписание":
    st.header("Расписание")

    st.caption(
        "Твои занятия по дням недели. "
        "Можно добавить, исправить или удалить занятие."
    )

    message = st.session_state.pop("lesson_message", None)

    if message:
        st.success(message)

    version = st.session_state.get("lesson_version", 0)

    with st.form(f"lesson_form_{version}"):
        st.subheader("Добавить занятие")

        a, b = st.columns(2)

        subject = a.text_input(
            "Предмет",
            max_chars=100,
            key=f"new_lesson_subject_{version}"
        )

        day = b.selectbox(
            "День недели",
            DAYS,
            key=f"new_lesson_day_{version}"
        )

        a, b = st.columns(2)

        start = a.time_input(
            "Начало",
            value=time(9),
            step=60,
            key=f"new_lesson_start_{version}"
        )

        end = b.time_input(
            "Окончание",
            value=time(10, 30),
            step=60,
            key=f"new_lesson_end_{version}"
        )

        room = st.text_input(
            "Аудитория (необязательно)",
            max_chars=80,
            key=f"new_lesson_room_{version}"
        )

        submitted = st.form_submit_button(
            "Добавить в расписание"
        )

    if submitted:
        try:
            database.add_lesson(
                user_id,
                subject,
                DAYS.index(day) + 1,
                start,
                end,
                room
            )

            refresh_lessons("Занятие сохранено!")
        except ValueError as error:
            st.error(str(error))
        except database.DatabaseError:
            st.error(
                "Не удалось сохранить изменения. "
                "Попробуй еще раз."
            )

    lessons = load_data(database.get_lessons, user_id)

    if lessons:
        for weekday, day_name in enumerate(DAYS, start=1):
            day_lessons = [
                lesson
                for lesson in lessons
                if lesson["weekday"] == weekday
            ]

            if day_lessons:
                heading(day_name)
                show_lessons(day_lessons)

        heading("Управление расписанием")

        lessons_by_id = {
            lesson["id"]: lesson
            for lesson in lessons
        }

        selected_id = st.selectbox(
            "Выбери занятие для изменения",
            list(lessons_by_id),
            format_func=lambda value: (
                f'{DAYS[lessons_by_id[value]["weekday"] - 1]} · '
                f'{lessons_by_id[value]["start"]} · '
                f'{lessons_by_id[value]["subject"]} · №{value}'
            ),
            key=f"managed_lesson_{version}"
        )

        selected = lessons_by_id[selected_id]
        suffix = f"{selected_id}_{version}"

        with st.expander("Редактировать занятие"):
            with st.form(f"edit_lesson_form_{suffix}"):
                a, b = st.columns(2)

                edited_subject = a.text_input(
                    "Предмет",
                    value=selected["subject"],
                    max_chars=100,
                    key=f"edit_lesson_subject_{suffix}"
                )

                edited_day = b.selectbox(
                    "День недели",
                    DAYS,
                    index=selected["weekday"] - 1,
                    key=f"edit_lesson_day_{suffix}"
                )

                a, b = st.columns(2)

                edited_start = a.time_input(
                    "Начало",
                    value=time.fromisoformat(selected["start"]),
                    step=60,
                    key=f"edit_lesson_start_{suffix}"
                )

                edited_end = b.time_input(
                    "Окончание",
                    value=time.fromisoformat(selected["end"]),
                    step=60,
                    key=f"edit_lesson_end_{suffix}"
                )

                edited_room = st.text_input(
                    "Аудитория (необязательно)",
                    value=selected["room"],
                    max_chars=80,
                    key=f"edit_lesson_room_{suffix}"
                )

                saved = st.form_submit_button(
                    "Сохранить изменения занятия"
                )

            if saved:
                try:
                    database.update_lesson(
                        user_id,
                        selected_id,
                        edited_subject,
                        DAYS.index(edited_day) + 1,
                        edited_start,
                        edited_end,
                        edited_room
                    )

                    refresh_lessons(
                        "Изменения занятия сохранены!"
                    )
                except ValueError as error:
                    st.error(str(error))
                except database.DatabaseError:
                    st.error(
                        "Не удалось сохранить изменения. "
                        "Попробуй еще раз."
                    )

        with st.expander("Удалить занятие"):
            st.text(
                f'Выбрано: {selected["subject"]} · '
                f'{DAYS[selected["weekday"] - 1]} · '
                f'{selected["start"]}'
            )

            st.caption(
                "Восстановить удаленное занятие "
                "через сайт нельзя."
            )

            with st.form(f"delete_lesson_form_{suffix}"):
                confirmed = st.checkbox(
                    "Подтверждаю удаление выбранного занятия",
                    key=f"delete_lesson_confirm_{suffix}"
                )

                removed = st.form_submit_button(
                    "Удалить занятие"
                )

            if removed:
                if not confirmed:
                    st.error(
                        "Сначала поставь галочку "
                        "подтверждения удаления."
                    )
                else:
                    try:
                        database.delete_lesson(
                            user_id,
                            selected_id
                        )

                        refresh_lessons("Занятие удалено.")
                    except ValueError as error:
                        st.error(str(error))
                    except database.DatabaseError:
                        st.error(
                            "Не удалось сохранить изменения. "
                            "Попробуй еще раз."
                        )
    else:
        empty_state(
            "Расписание пока пустое",
            "Добавь первое занятие через форму выше."
        )

elif section == "Задания":
    st.header("Задания")

    st.caption(
        "Добавляй работы, меняй записи и выбирай нужные "
        "задания по предмету и статусу."
    )

    message = st.session_state.pop("task_message", None)

    if message:
        st.success(message)

    version = st.session_state.get("task_version", 0)

    with st.form(f"task_form_{version}"):
        st.subheader("Новое задание")

        title = st.text_input(
            "Название задания",
            placeholder="Например, подготовка к семинару",
            key=f"new_title_{version}"
        )

        a, b = st.columns(2)

        subject = a.text_input(
            "Предмет",
            placeholder="Основы интернет-экономики",
            key=f"new_subject_{version}"
        )

        due = b.date_input(
            "Срок сдачи",
            value=None,
            format="DD.MM.YYYY",
            key=f"new_due_{version}"
        )

        submitted = st.form_submit_button(
            "Сохранить задание"
        )

    if submitted:
        try:
            database.add_task(
                user_id,
                title,
                subject,
                due
            )

            refresh_tasks("Задание сохранено!")
        except ValueError as error:
            st.error(str(error))
        except database.DatabaseError:
            st.error(
                "Не удалось сохранить изменения. "
                "Попробуй еще раз."
            )

    tasks = load_data(database.get_tasks, user_id)

    if tasks:
        heading("Мои работы", "По сроку сдачи")

        a, b = st.columns(2)

        subjects = sorted(
            {task["subject"] for task in tasks},
            key=str.casefold
        )

        subject_filter = a.selectbox(
            "Предмет для просмотра",
            [None] + subjects,
            format_func=lambda value: (
                "Все предметы" if value is None else value
            ),
            key="subject_filter"
        )

        status_filter = b.selectbox(
            "Статус для просмотра",
            ["Все задания", "Не выполнено", "Выполнено"],
            key="status_filter"
        )

        filtered_tasks = [
            task
            for task in tasks
            if (
                subject_filter is None
                or task["subject"] == subject_filter
            )
            and (
                status_filter == "Все задания"
                or (
                    status_filter == "Выполнено"
                    and task["done"]
                )
                or (
                    status_filter == "Не выполнено"
                    and not task["done"]
                )
            )
        ]

        st.caption(
            f"Показано {len(filtered_tasks)} "
            f"из {len(tasks)} заданий."
        )

        if filtered_tasks:
            show_tasks(filtered_tasks)
        else:
            empty_state(
                "Подходящих заданий нет",
                "Выбери другой предмет или статус."
            )

        heading("Управление заданиями")

        st.caption(
            "Здесь можно выбрать любую сохраненную работу, "
            "независимо от фильтров."
        )

        tasks_by_id = {
            task["id"]: task
            for task in tasks
        }

        selected_id = st.selectbox(
            "Выбери задание для изменения",
            list(tasks_by_id),
            format_func=lambda value: (
                f'{tasks_by_id[value]["title"]} — '
                f'{tasks_by_id[value]["subject"]} · №{value}'
            ),
            key=f"managed_task_{version}"
        )

        selected = tasks_by_id[selected_id]
        suffix = f"{selected_id}_{version}"

        with st.expander("Редактировать задание"):
            with st.form(f"edit_form_{suffix}"):
                edited_title = st.text_input(
                    "Название задания",
                    value=selected["title"],
                    key=f"edit_title_{suffix}"
                )

                a, b = st.columns(2)

                edited_subject = a.text_input(
                    "Предмет",
                    value=selected["subject"],
                    key=f"edit_subject_{suffix}"
                )

                edited_due = b.date_input(
                    "Срок сдачи",
                    value=date.fromisoformat(selected["due"]),
                    format="DD.MM.YYYY",
                    key=f"edit_due_{suffix}"
                )

                save_edit = st.form_submit_button(
                    "Сохранить изменения"
                )

            if save_edit:
                try:
                    database.update_task(
                        user_id,
                        selected_id,
                        edited_title,
                        edited_subject,
                        edited_due
                    )

                    refresh_tasks("Изменения сохранены!")
                except ValueError as error:
                    st.error(str(error))
                except database.DatabaseError:
                    st.error(
                        "Не удалось сохранить изменения. "
                        "Попробуй еще раз."
                    )

        with st.expander(
            "Отметить выполнение или вернуть задание в работу"
        ):
            with st.form(f"status_form_{suffix}"):
                status = st.selectbox(
                    "Новый статус",
                    ["Не выполнено", "Выполнено"],
                    index=int(selected["done"]),
                    key=f"edit_status_{suffix}"
                )

                save_status = st.form_submit_button(
                    "Сохранить статус"
                )

            if save_status:
                try:
                    database.set_task_done(
                        user_id,
                        selected_id,
                        status == "Выполнено"
                    )

                    refresh_tasks("Статус сохранен!")
                except ValueError as error:
                    st.error(str(error))
                except database.DatabaseError:
                    st.error(
                        "Не удалось сохранить изменения. "
                        "Попробуй еще раз."
                    )

        with st.expander("Удалить задание"):
            st.text(
                f'Выбрано задание: {selected["title"]}'
            )

            st.caption(
                "После удаления восстановить запись "
                "через сайт нельзя."
            )

            with st.form(f"delete_form_{suffix}"):
                confirmed = st.checkbox(
                    "Подтверждаю удаление выбранного задания",
                    key=f"delete_confirm_{suffix}"
                )

                delete_submitted = st.form_submit_button(
                    "Удалить задание"
                )

            if delete_submitted:
                if not confirmed:
                    st.error(
                        "Сначала поставь галочку "
                        "подтверждения удаления."
                    )
                else:
                    try:
                        database.delete_task(
                            user_id,
                            selected_id
                        )

                        refresh_tasks("Задание удалено.")
                    except ValueError as error:
                        st.error(str(error))
                    except database.DatabaseError:
                        st.error(
                            "Не удалось сохранить изменения. "
                            "Попробуй еще раз."
                        )
    else:
        empty_state(
            "Начни с одной записи",
            "Добавь название работы, предмет и срок сдачи."
        )

elif section == "Ближайшие сроки":
    st.header("Ближайшие сроки")

    last_day = today + timedelta(days=6)

    st.caption(
        f'С {today.strftime("%d.%m.%Y")} '
        f'по {last_day.strftime("%d.%m.%Y")} включительно. '
        "Только невыполненные задания. Время московское."
    )

    week_html = '<div class="week">'

    for offset in range(7):
        day = today + timedelta(days=offset)
        current = "current" if offset == 0 else ""

        week_html += (
            f'<div class="week-day {current}">'
            f'{DAYS[day.weekday()][:2]}'
            f'<b>{day.day}</b>'
            '</div>'
        )

    st.html(week_html + "</div>")

    upcoming = load_data(
        database.get_upcoming_tasks,
        user_id,
        today
    )

    if upcoming:
        show_tasks(upcoming)
    else:
        empty_state(
            "На ближайшую неделю заданий нет",
            "Работы с подходящим сроком появятся "
            "здесь после добавления."
        )

    heading("Просроченные работы")

    overdue = load_data(
        database.get_overdue_tasks,
        user_id,
        today
    )

    if overdue:
        show_tasks(overdue)
    else:
        st.success("Просроченных заданий нет.")

st.html(
    '<div class="footer">'
    '<span>StudyPlan · Учеба в своем ритме</span>'
    '<span>Расписание · Задания · Ближайшие сроки</span>'
    '</div>'
)