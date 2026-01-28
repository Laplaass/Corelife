import flet as ft
import random
from data.store import store
from services.ai_service import AIService

class ChatWidget(ft.Column):
    MOTIVATION_QUOTES = [
        "🌟 Great planning leads to great results!",
        "💪 You've got this! Let's organize your day.",
        "🎯 Success is the sum of small efforts repeated daily.",
        "⚡ Time management is life management!",
        "🚀 Small steps today, big achievements tomorrow!",
    ]

    def __init__(self, page: ft.Page, on_refresh=None):
        super().__init__()
        self.page_ref = page
        self.on_refresh = on_refresh
        self.ai_service = AIService()
        self.horizontal_alignment = ft.CrossAxisAlignment.END
        self.spacing = 10
        
        self.chat_history = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True)
        self.input_field = ft.TextField(
            hint_text="Ask me to schedule something...",
            expand=True,
            on_submit=self.send_message,
            border_radius=20,
            content_padding=10,
            text_style=ft.TextStyle(color=ft.Colors.BLACK),
            cursor_color=ft.Colors.BLACK,
            hint_style=ft.TextStyle(color=ft.Colors.GREY_600)
        )
        
        self.chat_window = ft.Container(
            content=ft.Column(
                [
                    ft.Container(
                        content=ft.Text("AI Assistant", weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                        bgcolor=ft.Colors.BLUE,
                        padding=10,
                        border_radius=ft.border_radius.only(top_left=10, top_right=10)
                    ),
                    ft.Container(
                        content=self.chat_history,
                        expand=True,
                        padding=10,
                    ),
                    ft.Container(
                        content=ft.Row(
                            [
                                self.input_field,
                                ft.IconButton(ft.Icons.SEND, on_click=self.send_message, icon_color=ft.Colors.BLUE)
                            ]
                        ),
                        padding=10,
                        border=ft.border.only(top=ft.border.BorderSide(1, ft.Colors.GREY_300))
                    )
                ],
                spacing=0
            ),
            width=350,
            height=500,
            bgcolor=ft.Colors.WHITE,
            border_radius=10,
            shadow=ft.BoxShadow(blur_radius=10, color=ft.Colors.BLACK12),
            visible=False,
            animate_opacity=300,
        )

        self.fab = ft.FloatingActionButton(
            icon=ft.Icons.CHAT,
            on_click=self.toggle_chat,
            bgcolor=ft.Colors.BLUE,
        )

        self.controls = [
            self.chat_window,
            self.fab
        ]
        
        # Initial greeting
        self.add_message(
            "👋 Welcome to Corelife!\n\n"
            "⏰ Did you know? Proper time management can:\n"
            "• Reduce stress by 47%\n"
            "• Boost productivity by 100%\n"
            "• Improve your mood by 65%\n\n"
            "🎯 I'm here to help you:\n"
            "✓ Schedule smart - I'll find the best time\n"
            "✓ Stay organized - Never miss a deadline\n"
            "✓ Balance life - Work, study, rest in harmony\n\n"
            "💪 Let's make today productive! What's on your mind?",
            is_user=False,
            update=False
        )

        if random.random() < 0.3:  # 30% шанс показать цитату
            self.add_message(
                random.choice(self.MOTIVATION_QUOTES),
                is_user=False,
                update=False
            )

    def find_event_by_title(self, title_to_find):
        """Ищет событие по частичному совпадению названия в текущем и следующих 2 месяцах"""
        from datetime import datetime

        title_lower = (title_to_find or "").lower()
        if not title_lower:
            return None

        now = datetime.now()

        # Проверяем текущий месяц и следующие 2 месяца
        for month_offset in range(3):
            month = now.month + month_offset
            year = now.year

            # Корректируем год если месяц больше 12
            while month > 12:
                month -= 12
                year += 1

            events = store.get_events_for_month(year, month)

            for event in events:
                if title_lower in event["title"].lower():
                    return event

        return None

    def toggle_chat(self, e):
        self.chat_window.visible = not self.chat_window.visible
        self.update()

    def add_message(self, text, is_user=True, update=True):
        self.chat_history.controls.append(
            ft.Row(
                [
                    ft.Container(
                        content=ft.Text(text, color=ft.Colors.WHITE if is_user else ft.Colors.BLACK),
                        bgcolor=ft.Colors.BLUE if is_user else ft.Colors.GREY_200,
                        padding=10,
                        border_radius=10,
                        width=250 if len(text) > 30 else None
                    )
                ],
                alignment=ft.MainAxisAlignment.END if is_user else ft.MainAxisAlignment.START
            )
        )
        if update:
            self.update()

    def send_message(self, e):
        text = self.input_field.value
        if not text:
            return
        
        self.add_message(text, is_user=True)
        self.input_field.value = ""
        self.update()
        
        # Process command
        self.process_command(text)

    def process_command(self, text):
        try:
            # Используем AI для обработки команды
            result = self.ai_service.process_message(text)
            
            if result["action"] == "chat":
                # Просто чат, не создаём событие
                self.add_message(result["response_message"], is_user=False)
                return
            
            if result["action"] == "create":
                # Создаём событие или задачу
                store.add_event(
                    title=result["title"],
                    start_date=result["start"],
                    end_date=result["end"],
                    description=result.get("description", ""),
                    event_type=result["type"],
                    priority=result.get("priority", "Medium"),
                    category=result.get("category", "Personal")
                )
                
                # Показываем подтверждение
                self.add_message(result["response_message"], is_user=False)
                
                # Обновляем календарь
                if self.on_refresh:
                    self.on_refresh()
                else:
                    self.page_ref.update()
            
            if result["action"] == "delete":
                found_event = self.find_event_by_title(result.get("title", ""))
                
                if found_event:
                    store.delete_event(found_event["id"])
                    self.add_message(f"Deleted: {found_event['title']}", is_user=False)
                    
                    # Обновляем календарь
                    if self.on_refresh:
                        self.on_refresh()
                    else:
                        self.page_ref.update()
                else:
                    self.add_message(f"Could not find event with name '{result.get('title')}'", is_user=False)
            
            if result["action"] == "reschedule":
                found_event = self.find_event_by_title(result.get("title", ""))
                
                if found_event:
                    # Обновляем время события
                    updates = {
                        "start": result["new_start"],
                        "end": result["new_end"]
                    }
                    
                    success = store.update_event(found_event["id"], updates)
                    
                    if success:
                        self.add_message(result["response_message"], is_user=False)
                        
                        # Обновляем календарь
                        if self.on_refresh:
                            self.on_refresh()
                        else:
                            self.page_ref.update()
                    else:
                        self.add_message("Failed to reschedule event. Please try again.", is_user=False)
                else:
                    self.add_message(f"Could not find event with name '{result.get('title')}'", is_user=False)
                
        except Exception as e:
            self.add_message("Sorry, I encountered an error. Please try again.", is_user=False)
            print(f"Error in process_command: {e}")
