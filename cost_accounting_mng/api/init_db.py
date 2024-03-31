from .models import Account, Operations, User, Category


default_categories = [
    "Забота о себе",
    "Зарплата",
    "Здоровье и фитнес",
    "Кафе и рестораны",
    "Машина",
    "Образование",
    "Отдых и развлечения",
    "Платежи, комиссии",
    "Покупки: одежда, техника",
    "Продукты",
    "Проезд",
]


def add_test_records():
    usertest = User.objects.filter(username='usertest').first()

    if not usertest:
        usertest = User.objects.create_user('usertest')
    else:
        print('User already exists.')

    for category in default_categories:
        if not Category.objects.filter(title=category).first():
            Category.objects.create(title=category.lower())

    for category in Category.objects.filter(inf='D').all():
        usertest.category.add(category)
    usertest.save()

    if not Account.objects.filter(user=usertest):
        print("NO BALANCE YET")
        Account.objects.create(user=usertest, balance=0, categories={"categories": []})


    if Account.objects.filter(user=usertest):
        print("User's balance exists.")


add_test_records()