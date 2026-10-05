import streamlit as st
import database

# Настройки страницы
st.set_page_config(
    page_title="StudyPlan",
    page_icon="📚",
    layout="centered"
)

# Создаем базу и таблицы при запуске
database.init_db()

# Заголовок и описание проекта
st.title("📚 StudyPlan")
st.write("Онлайн-планировщик учебы для студентов.")

st.write(
    "Здесь можно будет хранить расписание занятий, "
    "записывать задания и следить за сроками сдачи."
)

# Меню разделов
section = st.sidebar.radio(
    "Выбери раздел",
    ["Главная", "Расписание", "Задания", "Ближайшие сроки"]
)

if section == "Главная":
    st.header("Главная")
    st.write("Добро пожаловать в StudyPlan!")
    st.info(
        "Первая версия: можно добавить задание "
        "и сохранить его в базе данных."
    )

elif section == "Расписание":
    st.header("Расписание")
    st.write("Здесь будет список занятий по дням недели.")

elif section == "Задания":
    st.header("Задания")

    # Форма добавления задания
    with st.form("task_form", clear_on_submit=False):
        title = st.text_input("Название задания")
        subject = st.text_input("Предмет")

        due = st.date_input(
            "Срок сдачи",
            value=None,
            format="DD.MM.YYYY"
        )

        submitted = st.form_submit_button("Сохранить задание")

    # Проверка и сохранение
    if submitted:
        try:
            database.add_task(title, subject, due)
            st.success("Задание сохранено!")
        except ValueError as error:
            st.error(str(error))

    # Список заданий из базы
    st.subheader("Сохраненные задания")
    tasks = database.get_tasks()

    if tasks:
        rows = []

        for task in tasks:
            rows.append({
                "Задание": task[0],
                "Предмет": task[1],
                "Срок сдачи": ".".join(
                    reversed(task[2].split("-"))
                )
            })

        st.table(rows)
    else:
        st.info("Пока нет сохраненных заданий.")

elif section == "Ближайшие сроки":
    st.header("Ближайшие сроки")
    st.write(
        "Здесь будут задания, которые нужно выполнить скоро."
    )