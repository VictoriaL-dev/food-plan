from django.db import transaction
from django.core.management.base import BaseCommand
from apps.menu.models import Menu, Recipe, Ingredient, Allergen


class Command(BaseCommand):
    help = "Наполнение базы данных 16 тестовыми блюдами по 4 на каждое меню."

    def handle(self, *args, **options):
        self.stdout.write("Удаление старых данных...")
        with transaction.atomic():
            Ingredient.objects.all().delete()
            Recipe.objects.all().delete()
            Menu.objects.all().delete()

        allergens = [
            "Рыба и морепродукты",
            "Мясо",
            "Зерновые",
            "Продукты пчеловодства",
            "Орехи и бобовые",
            "Молочные продукты"
        ]

        for name in allergens:
            Allergen.objects.get_or_create(name=name)

        raw_dishes = [
            # ================= Классическое меню (4 блюда) =================
            {
                "title": "Овсяная каша с ягодами и медом",
                "instructions": "Залейте овсяные хлопья молоком. Доведите до кипения, варите 5-7 минут. Добавьте мед и украсьте свежими ягодами.",
                "calories": 320,
                "meal_type": Recipe.MealTypes.BREAKFAST,
                "menu_name": "Классическое",
                "ingredients": [("Овсяные хлопья", "50г"), ("Молоко 2.5%", "150мл"), ("Мед", "1 ч.л."), ("Ягоды", "30г")]
            },
            {
                "title": "Куриная грудка гриль с киноа",
                "instructions": "Обжарьте куриную грудку на сковороде-гриль по 5 минут с каждой стороны. Отварите киноа (1:2) 15 минут. Подавайте вместе.",
                "calories": 480,
                "meal_type": Recipe.MealTypes.LUNCH,
                "menu_name": "Классическое",
                "ingredients": [("Куриная грудка", "180г"), ("Крупа киноа", "60г"), ("Оливковое масло", "1 ч.л.")]
            },
            {
                "title": "Салат Цезарь с креветками",
                "instructions": "Обжарьте креветки. Нарвите листья салата, добавьте черри, сухарики, заправьте соусом и посыпьте пармезаном.",
                "calories": 380,
                "meal_type": Recipe.MealTypes.DINNER,
                "menu_name": "Классическое",
                "ingredients": [("Креветки", "150г"), ("Салат Романо", "100г"), ("Помидоры черри", "50г"), ("Соус Цезарь", "2 ст.л.")]
            },
            {
                "title": "Домашние блинчики с творожной начинкой",
                "instructions": "Испеките тонкие блины. Смешайте творог с сахаром, заверните начинку в блинчики. Слегка обжарьте на сливочном масле.",
                "calories": 420,
                "meal_type": Recipe.MealTypes.DESSERT,
                "menu_name": "Классическое",
                "ingredients": [("Мука пшеничная", "100г"), ("Молоко", "200мл"), ("Творог 5%", "150г"), ("Сахар", "1 ст.л.")]
            },
            # ================= Низкоуглеводное меню (4 блюда) =================
            {
                "title": "Скрембл со шпинатом и томатами",
                "instructions": "Взбейте яйца, вылейте на сковороду. Добавьте свежий шпинат и нарезанные черри, постоянно помешивайте до готовности.",
                "calories": 290,
                "meal_type": Recipe.MealTypes.BREAKFAST,
                "menu_name": "Низкоуглеводное",
                "ingredients": [("Яйца куриные", "3 шт"), ("Шпинат свежий", "50г"), ("Помидоры черри", "40г")]
            },
            {
                "title": "Стейк из лосося с запеченной спаржей",
                "instructions": "Посолите стейк лосося, сбрызните лимоном. Запекайте в духовке вместе со спаржей 15 минут при 180°C.",
                "calories": 550,
                "meal_type": Recipe.MealTypes.LUNCH,
                "menu_name": "Низкоуглеводное",
                "ingredients": [("Стейк лосося", "200г"), ("Свежая спаржа", "100г"), ("Лимон", "0.5 шт")]
            },
            {
                "title": "Запеченная треска с цветной капустой",
                "instructions": "Филе трески выложите в форму, вокруг разложите соцветия цветной капусты. Сбрызните маслом и запекайте 20 минут.",
                "calories": 340,
                "meal_type": Recipe.MealTypes.DINNER,
                "menu_name": "Низкоуглеводное",
                "ingredients": [("Филе трески", "200г"), ("Цветная капуста", "150г"), ("Оливковое масло", "1 ст.л.")]
            },
            {
                "title": "Ягодное желе со стевией",
                "instructions": "Растворите желатин в теплой воде. Добавьте пюре из свежих ягод и стевию. Разлейте по формам и уберите в холод на 2 часа.",
                "calories": 90,
                "meal_type": Recipe.MealTypes.DESSERT,
                "menu_name": "Низкоуглеводное",
                "ingredients": [("Ягоды (малина/клубника)", "100г"), ("Желатин", "10г"), ("Стевия", "по вкусу")]
            },
            # ================= Вегетарианское меню (4 блюда) =================
            {
                "title": "Смузи-боул с бананом и гранолой",
                "instructions": "Взбейте в блендере замороженный банан и растительное молоко. Налейте в глубокую миску, сверху украсьте гранолой.",
                "calories": 310, 
                "meal_type": Recipe.MealTypes.BREAKFAST, 
                "menu_name": "Вегетарианское",
                "ingredients": [("Банан", "1 шт"), ("Кокосовое молоко", "100мл"), ("Гранола", "30г")]
            },
            {
                "title": "Крем-суп из шампиньонов",
                "instructions": "Обжарьте грибы с луком. Отварите картофель, добавьте грибы, залейте нежирными сливками и пробейте блендером.",
                "calories": 360, 
                "meal_type": Recipe.MealTypes.LUNCH, 
                "menu_name": "Вегетарианское",
                "ingredients": [("Шампиньоны", "250г"), ("Картофель", "1 шт"), ("Сливки 10%", "100мл"), ("Лук репчатый", "1 шт")]
            },
            {
                "title": "Запеченный тофу с брокколи",
                "instructions": "Нарежьте тофу кубиками, смешайте с брокколи. Полейте соевым соусом и запекайте 20 минут при 200°C.",
                "calories": 290, 
                "meal_type": Recipe.MealTypes.DINNER, 
                "menu_name": "Вегетарианское",
                "ingredients": [("Тофу твердый", "150г"), ("Капуста брокколи", "200г"), ("Соевый соус", "3 ст.л.")]
            },
            {
                "title": "Чиа-пудинг на миндальном молоке",
                "instructions": "Смешайте семена чиа с миндальным молоком, оставьте в холодильнике на ночь. Перед подачей добавьте кусочки манго.",
                "calories": 210, 
                "meal_type": Recipe.MealTypes.DESSERT, 
                "menu_name": "Вегетарианское",
                "ingredients": [("Семена чиа", "2 ст.л."), ("Миндальное молоко", "150мл"), ("Манго", "50г")]
            },
            # ================= Кето меню (4 блюда) =================
            {
                "title": "Французский омлет с пармезаном",
                "instructions": "Взбейте яйца. Разогрейте сливочное масло, вылейте яйца. В центр выложите тертый сыр, сложите омлет пополам.",
                "calories": 410, 
                "meal_type": Recipe.MealTypes.BREAKFAST,
                "menu_name": "Кето",
                "ingredients": [("Яйца куриные", "3 шт"), ("Сливочное масло", "15г"), ("Сыр Пармезан", "30г")]
            },
            {
                "title": "Свиные ребрышки в маринаде",
                "instructions": "Натрите ребрышки солью, чесноком и паприкой. Запекайте в духовке под фольгой 1.5 часа при 160°C, затем 15 минут без фольги.",
                "calories": 680, 
                "meal_type": Recipe.MealTypes.LUNCH,
                "menu_name": "Кето",
                "ingredients": [("Свиные ребрышки", "300г"), ("Чеснок", "2 зубчика"), ("Растительное масло", "1 ст.л.")]
            },
            {
                "title": "Салат из авокадо с беконом",
                "instructions": "Обжарьте бекон до хрустящей корочки. Нарежьте кубиками авокадо и огурец, заправьте домашним жирным майонезом.",
                "calories": 510,
                "meal_type": Recipe.MealTypes.DINNER,
                "menu_name": "Кето",
                "ingredients": [("Авокадо", "1 шт"), ("Бекон", "50г"), ("Огурец", "1 шт"), ("Майонез 67%", "1.5 ст.л.")]
            },
            {
                "title": "Шоколадный протеиновый мусс",
                "instructions": "Взбейте в блендере спелый авокадо, шоколадный протеин, какао-порошок и немного миндального молока до состояния крема.",
                "calories": 260, 
                "meal_type": Recipe.MealTypes.DESSERT,
                "menu_name": "Кето",
                "ingredients": [("Спелый авокадо", "1 шт"), ("Протеин шоколадный", "30г"), ("Какао-порошок", "1 ст.л.")]
            }
        ]
        self.stdout.write("Автоматическое создание типов меню в БД...")
        unique_menu_names = set(d_data["menu_name"] for d_data in raw_dishes)

        menus = {}
        for name in unique_menu_names:
            menu_obj, _ = Menu.objects.get_or_create(name=name)
            menus[name] = menu_obj

        self.stdout.write("Заполнение базы блюдами...")
        for dish_data in raw_dishes:
            recipe = Recipe.objects.create(
                title=dish_data["title"],
                instructions=dish_data["instructions"],
                calories=dish_data["calories"],
                meal_type=dish_data["meal_type"],
                menu_type=menus[dish_data["menu_name"]]
            )

            for ing_name, ing_amount in dish_data["ingredients"]:
                Ingredient.objects.create(
                    recipe=recipe,
                    name=ing_name,
                    amount=ing_amount
                )

        self.stdout.write(self.style.SUCCESS(f"База успешно наполнена! Добавлено {len(raw_dishes)} блюд и {len(allergens)} аллергенов."))
