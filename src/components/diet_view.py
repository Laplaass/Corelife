import flet as ft
from data.store import store
from components.diet_quiz_view import DietQuizView

class DietView(ft.Column):
    """
    Страница диеты в основном меню приложения.
    Показывает текущие предпочтения и позволяет пройти тест заново.
    """
    def __init__(self, page: ft.Page, user_info: dict):
        super().__init__()
        self.page_ref = page
        self.user_info = user_info
        
        self.expand = True
        self.spacing = 20
        self.scroll = ft.ScrollMode.AUTO
        
        # Получаем предпочтения из БД
        self.preferences = store.get_diet_preferences(user_info["id"])
        
        # Создаём UI
        self.build_ui()
    
    def build_ui(self):
        """Строит интерфейс страницы диеты"""
        # Заголовок
        header = ft.Row(
            controls=[
                ft.Text(
                    "🍽️ Your Diet Plan",
                    size=28,
                    weight=ft.FontWeight.BOLD
                ),
                ft.Container(expand=True),
                ft.IconButton(
                    icon=ft.Icons.REFRESH,
                    tooltip="Retake Quiz",
                    on_click=self.retake_quiz
                )
            ]
        )
        
        self.controls.append(header)
        self.controls.append(ft.Divider())
        
        # Если предпочтений нет - показываем приглашение пройти тест
        if not self.preferences:
            self.show_empty_state()
        else:
            self.show_preferences()
    
    def show_empty_state(self):
        """Показывает пустое состояние (тест не пройден)"""
        empty_container = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Icon(ft.Icons.RESTAURANT_MENU, size=80, color=ft.Colors.GREY_400),
                    ft.Container(height=20),
                    ft.Text(
                        "No diet preferences set",
                        size=22,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.GREY_700
                    ),
                    ft.Container(height=10),
                    ft.Text(
                        "Take our quick quiz to get personalized diet recommendations!",
                        size=14,
                        color=ft.Colors.GREY_600,
                        text_align=ft.TextAlign.CENTER,
                        width=400
                    ),
                    ft.Container(height=30),
                    ft.ElevatedButton(
                        text="Take Diet Quiz",
                        icon=ft.Icons.QUIZ,
                        on_click=self.retake_quiz,
                        style=ft.ButtonStyle(
                            color=ft.Colors.WHITE,
                            bgcolor=ft.Colors.GREEN_600,
                        )
                    )
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER
            ),
            alignment=ft.alignment.center,
            expand=True
        )
        
        self.controls.append(empty_container)
    
    def show_preferences(self):
        """Показывает текущие предпочтения"""
        # Секция: Тип питания
        meal_pref = self.preferences.get("meal_preference", [])
        
        # ✅ ИСПРАВЛЕНО: meal_preference теперь список, а не строка
        if isinstance(meal_pref, str):
            meal_pref = [meal_pref]
        
        meal_labels = {
            "vegetarian": "🥗 Vegetarian",
            "vegan": "🌱 Vegan",
            "pescatarian": "🐟 Pescatarian",
            "meat": "🍖 Meat-based",
            "balanced": "⚖️ Balanced"
        }
        
        # ✅ ИСПРАВЛЕНО: Создаём chips для каждого выбранного типа питания
        meal_chips = ft.Row(
            controls=[
                ft.Chip(
                    label=ft.Text(meal_labels.get(meal, meal)),
                    bgcolor=ft.Colors.GREEN_100,
                    padding=10
                )
                for meal in meal_pref
            ],
            wrap=True,
            spacing=10
        )
        
        meal_section = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text("Meal Type", size=18, weight=ft.FontWeight.BOLD),
                    ft.Container(height=10),
                    meal_chips
                ]
            ),
            padding=20,
            border=ft.border.all(1, ft.Colors.GREY_300),
            border_radius=10
        )
        
        self.controls.append(meal_section)
        
        # Секция: Любимые кухни
        cuisines = self.preferences.get("cuisine_preference", [])
        cuisine_labels = {
            "asian": "🍜 Asian",
            "italian": "🍝 Italian",
            "mexican": "🌮 Mexican",
            "mediterranean": "🫒 Mediterranean",
            "american": "🍔 American",
            "indian": "🍛 Indian"
        }
        
        if cuisines:
            cuisine_chips = ft.Row(
                controls=[
                    ft.Chip(
                        label=ft.Text(cuisine_labels.get(c, c)),
                        bgcolor=ft.Colors.BLUE_100
                    )
                    for c in cuisines
                ],
                wrap=True,
                spacing=10
            )
            
            cuisine_section = ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Text("Favorite Cuisines", size=18, weight=ft.FontWeight.BOLD),
                        ft.Container(height=10),
                        cuisine_chips
                    ]
                ),
                padding=20,
                border=ft.border.all(1, ft.Colors.GREY_300),
                border_radius=10
            )
            
            self.controls.append(cuisine_section)
        
        # Секция: Ограничения
        avoid = self.preferences.get("avoid_foods", [])
        avoid_labels = {
            "dairy": "🥛 Dairy",
            "gluten": "🌾 Gluten",
            "nuts": "🥜 Nuts",
            "seafood": "🦐 Seafood",
            "spicy": "🌶️ Spicy"
        }
        
        if avoid and "none" not in avoid:
            avoid_chips = ft.Row(
                controls=[
                    ft.Chip(
                        label=ft.Text(avoid_labels.get(a, a)),
                        bgcolor=ft.Colors.RED_100
                    )
                    for a in avoid if a != "none"
                ],
                wrap=True,
                spacing=10
            )
            
            avoid_section = ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Text("Foods to Avoid", size=18, weight=ft.FontWeight.BOLD),
                        ft.Container(height=10),
                        avoid_chips
                    ]
                ),
                padding=20,
                border=ft.border.all(1, ft.Colors.GREY_300),
                border_radius=10
            )
            
            self.controls.append(avoid_section)
        
        # Секция: Частота приёма пищи
        meal_freq = self.preferences.get("meal_frequency", "3")
        
        freq_section = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text("Meals per Day", size=18, weight=ft.FontWeight.BOLD),
                    ft.Container(height=10),
                    ft.Text(f"🍽️ {meal_freq} meals", size=16)
                ]
            ),
            padding=20,
            border=ft.border.all(1, ft.Colors.GREY_300),
            border_radius=10
        )
        
        self.controls.append(freq_section)
        
        # Секция: Медицинские ограничения
        medical = self.preferences.get("medical_notes", "")
        
        if medical:
            medical_section = ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Text("Medical Restrictions", size=18, weight=ft.FontWeight.BOLD),
                        ft.Container(height=10),
                        ft.Text(medical, size=14, color=ft.Colors.GREY_700)
                    ]
                ),
                padding=20,
                border=ft.border.all(1, ft.Colors.ORANGE_300),
                border_radius=10,
                bgcolor=ft.Colors.ORANGE_50
            )
            
            self.controls.append(medical_section)
        
        # Кнопка "Get AI Recommendations" (будущий функционал)
        ai_button = ft.Container(
            content=ft.ElevatedButton(
                text="Get AI Diet Recommendations",
                icon=ft.Icons.PSYCHOLOGY,
                on_click=self.get_ai_recommendations,
                style=ft.ButtonStyle(
                    color=ft.Colors.WHITE,
                    bgcolor=ft.Colors.PURPLE_600,
                )
            ),
            alignment=ft.alignment.center,
            padding=20
        )
        
        self.controls.append(ai_button)
    
    def retake_quiz(self, e):
        """Открывает тест заново"""
        # Очищаем страницу и показываем тест
        self.page_ref.clean()
        
        def on_complete():
            # После завершения теста перезагружаем страницу диеты
            self.page_ref.clean()
            from components.layout import AppLayout
            from components.header import Header
            from components.chat import ChatWidget
            
            # Пересоздаём layout и возвращаемся на страницу Diet
            app_layout = AppLayout(self.page_ref, self.user_info, lambda e: None)
            app_layout.set_view("Diet")
            
            self.page_ref.appbar = Header(
                self.page_ref,
                lambda: app_layout.set_view("Account"),
                on_menu_click=lambda e: app_layout.toggle_sidebar()
            )
            
            main_stack = ft.Stack(
                [
                    app_layout,
                    ft.Container(
                        content=ChatWidget(self.page_ref, on_refresh=app_layout.refresh_active_view),
                        right=20,
                        bottom=20,
                    )
                ],
                expand=True
            )
            
            self.page_ref.add(main_stack)
            self.page_ref.update()
        
        quiz = DietQuizView(self.page_ref, self.user_info, on_complete)
        self.page_ref.add(quiz)
        self.page_ref.update()
    
    def get_ai_recommendations(self, e):
        """Получает рекомендации от AI (будущий функционал)"""
        # TODO: Интеграция с AI для генерации рекомендаций по диете
        snack = ft.SnackBar(
            content=ft.Text("🚀 AI Diet Recommendations coming soon!"),
            bgcolor=ft.Colors.BLUE_400
        )
        self.page_ref.open(snack)