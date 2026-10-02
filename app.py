import flet as ft
import sqlite3
from docx import Document
import os

def main(page: ft.Page):
    page.title = "پەندی پێشینان"
    page.window.width = 420
    page.window.height = 720
    page.window.resizable = False
    page.theme_mode = ft.ThemeMode.LIGHT
    page.rtl = True
    page.padding = 15
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    # بەستنەوە بە داتابەیس
    conn = sqlite3.connect("proverbs.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS proverbs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT UNIQUE,
            meaning TEXT
        )
    ''')
    conn.commit()

    # ۱. بەشی پێشاندانی واتا
    result_title = ft.Text(value="واتای پەندەکە", size=18, weight=ft.FontWeight.BOLD, color="teal800")
    result_meaning = ft.Text(value="گەڕان بکە یان کلیک لەسەر پەندێک بکە بۆ دیدەنی واتاكەی...", size=14, color="grey700")

    meaning_card = ft.Card(
        content=ft.Container(
            content=ft.Column([
                result_title,
                ft.Divider(),
                result_meaning
            ]),
            padding=15,
        ),
        elevation=3
    )

    # ۲. لیستی ئەنجامەکان
    results_list = ft.ListView(expand=True, spacing=5)

    def display_meaning(title, meaning):
        result_title.value = title
        result_meaning.value = meaning
        page.update()

    def on_search(e):
        query = e.control.value.strip()
        results_list.controls.clear()
        
        if query:
            cursor.execute("SELECT title, meaning FROM proverbs WHERE title LIKE ? LIMIT 20", (f"%{query}%",))
            rows = cursor.fetchall()
            for title, meaning in rows:
                results_list.controls.append(
                    ft.ListTile(
                        title=ft.Text(title, weight=ft.FontWeight.W_500),
                        on_click=lambda _, t=title, m=meaning: display_meaning(t, m)
                    )
                )
        page.update()

    # خانەی گەڕان
    search_bar = ft.TextField(
        hint_text="بگەڕێ بۆ پەندی پێشینان...",
        border_radius=10,
        on_change=on_search
    )

    # ۳. بەشی هاوردەکردنی (Import) فایلی Word بە ئاسانی
    file_path_input = ft.TextField(
        hint_text="ناوی فایلی Word بنووسە (نموونە: data.docx)...",
        border_radius=10,
        expand=True
    )

    def import_word_file(e):
        file_path = file_path_input.value.strip()
        if not file_path:
            page.open(ft.SnackBar(content=ft.Text("تکایە ناوی فایلەکە بنووسە!")))
            page.update()
            return
        
        if not file_path.endswith(".docx"):
            file_path += ".docx"

        if not os.path.exists(file_path):
            page.open(ft.SnackBar(content=ft.Text("فایلەکە نەدۆزرایەوە! دڵنیا ببەرەوە لە ناوی فایلەکە.")))
            page.update()
            return

        try:
            doc = Document(file_path)
            count = 0
            for p in doc.paragraphs:
                line = p.text.strip()
                if ":" in line:
                    parts = line.split(":", 1)
                    title = parts[0].strip()
                    meaning = parts[1].strip()
                    try:
                        cursor.execute("INSERT INTO proverbs (title, meaning) VALUES (?, ?)", (title, meaning))
                        count += 1
                    except sqlite3.IntegrityError:
                        pass
            conn.commit()
            page.open(ft.SnackBar(content=ft.Text(f"بە سەرکەوتوویی {count} پەندی نوێ هاوردەکران!")))
            file_path_input.value = ""
        except Exception as ex:
            page.open(ft.SnackBar(content=ft.Text(f"هەڵەیەک ڕوویدا: {str(ex)}")))
        page.update()

    import_btn = ft.Button(
        content=ft.Text("هاوردەکردن (Import)"),
        on_click=import_word_file
    )

    # کۆنتێنەری سەرەکی بۆ ڕێکخستنی شاشەکە
    main_container = ft.Container(
        width=380,
        content=ft.Column(
            controls=[
                search_bar,
                meaning_card,
                ft.Text("ئەنجامەکانی گەڕان:", size=12, color="grey600"),
                ft.Container(content=results_list, height=220),
                ft.Divider(),
                ft.Text("هاوردەکردنی پەند لە فایلی Word (.docx):", size=12, weight=ft.FontWeight.BOLD),
                ft.Row([file_path_input, import_btn])
            ],
            spacing=10
        )
    )

    page.add(main_container)

if __name__ == "__main__":
    if hasattr(ft, "run"):
        ft.run(main)
    else:
        ft.app(target=main)