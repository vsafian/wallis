import random
import datetime
from string import ascii_letters
from time import sleep

from django.utils import timezone

import init_django_orm  # noqa F401

from json import dump

from production.models import (
    Worker,
    Workplace,
    Printer,
    Material,
    Order
)

from wallis.settings import BASE_DIR

FIXTURE_PATH = BASE_DIR / 'fixtures'

PRINTERS_COUNT = 32
WORKPLACES_COUNT = 8
PRINTERS_IN_WORKPLACE = 4
WORKERS_COUNT = 32
ADMINS_COUNT = 2
ORDERS_TO_PRINT_COUNT = 60
MATERIALS_COUNT = 10


def model_code(model) -> str:
    return f"{model._meta.app_label}.{model._meta.model_name}"


def write_fixture(fixture_name: str, data: list[dict]) -> None:
    with open(FIXTURE_PATH / f"{fixture_name}.json", "w") as file:
        dump(data, file, indent=4, ensure_ascii=False)


def workers_create(workplaces: bool):
    letters = ascii_letters[: len(ascii_letters) // 2]
    model_name = model_code(Worker)
    user_usernames = ["Can", "Eps", "Bro", "Rick", "Zero", "Lun"]
    user_first_names = ["Jack", "Mac", "Joanne", "Helen", "Peter"]
    workers = []
    for index in range(WORKERS_COUNT):
        workplace = None
        unique_username_part = random.sample(letters, 4)
        username = random.choice(user_usernames) + "".join(unique_username_part)
        first_name = random.choice(user_first_names)
        phone_number = "+380" + "".join(str(random.choice(range(9))) for _ in range(9))
        if workplaces:
            workplace = random.choice(range(1, WORKPLACES_COUNT + 1))
        worker = {
            "model": model_name,
            "pk": index + 2,
            "fields": {
                "password": f"{username}{phone_number}{random.choice("@#$!^")}",
                "last_login": str(datetime.datetime.now()),
                "is_superuser": False,
                "username": username,
                "first_name": first_name,
                "last_name": username,
                "email": f"{first_name}_{username}@email.com",
                "is_staff": False,
                "is_active": False,
                "date_joined": "2022-08-08T13:58:29Z",
                "phone_number": phone_number,
                "workplace": workplace,
                "groups": [],
                "user_permissions": []
            }
        }
        workers.append(worker)
    write_fixture("workers", workers)


def materials_create():
    model_name = model_code(Material)
    material_names = [
        "Vinyl", "Canvas", "Paper", "Silk", "Linen",
        "Textile", "PVC", "Fiberglass", "Nonwoven", "Metallic"
    ]

    materials = [
        {
            "model": model_name,
            "pk": index + 1,
            "fields": {
                "name": name,
                "type": random.choice(["Glossy", "Matte"]),
                "roll_width": round(random.uniform(1.06, 1.52), 2),
                "winding": random.randint(30, 150),
                "density": random.randint(115, 315)
            }
        }
        for index, name in enumerate(material_names)
    ]
    write_fixture("materials", materials)


def printers_create():
    model_name = model_code(Printer)
    printer_names = [
        "Canon", "Epson", "HP", "Brother", "Ricoh", "Xerox"
    ]
    models = ["XT", "MX", "RL", "MM"]
    printers = []
    count = 0
    workplace_id = 1
    for printer_id in range(1, PRINTERS_COUNT + 1):
        if count == PRINTERS_IN_WORKPLACE:
            workplace_id += 1
            count = 0
        printer = {
            "model": model_name,
            "pk": printer_id,
            "fields": {
                "name": random.choice(printer_names),
                "model": random.choice(models) + "".join(
                    [str(random.randint(0, 9))
                     for _ in range(7)
                     ]),
                "materials": random.sample(range(1, 11), 4),
                "workplace": workplace_id
            }
        }
        count += 1
        printers.append(printer)

    write_fixture("printers", printers)


def workplaces_create():
    model_name = model_code(Workplace)
    workplaces = [
        {
            "model": model_name,
            "pk": index,
            "fields": {
                "name": f"WP {index}",
            }
        }
        for index in range(1, WORKPLACES_COUNT + 1)
    ]
    write_fixture("workplaces", workplaces)



def orders_to_print_create():
   model_name = model_code(Order)
   orders = []
   owners = ["Use", "Meet", "Urus", "Dude"]
   country_posts = [
       "ukr-Nova Post", "ukr-Ukr Post",
       "pl-Dpd", "pl-Poczta Polska",
       "pl-Fedex", "sl-Fedex"
   ]
   image_names = ["flowers", "blocks", "word_map", "painting", "waves"]
   image_format = ".tiff"

   for index in range(1, ORDERS_TO_PRINT_COUNT + 1):
       country_post = random.choice(country_posts)
       material = random.choice(range(1, 11))
       image_name = f"{random.choice(image_names)}_{index}_{image_format}"
       width = range(200, 1000)
       height = range(215, 330)
       order = {
           "model": model_name,
           "pk": index,
           "fields": {
                "code": f"{index}{random.randint(1, 300)}",
               "owner_full_name": random.choice(owners),
               "country_post": country_post,
               "image_name": image_name,
               "width": random.choice(width),
               "height": random.choice(height),
               "material": material,
               "creation_time": str(timezone.now()),
           }
       }
       orders.append(order)
       sleep(0.5)

   write_fixture("orders", orders)

if __name__ == "__main__":
    #pass
    orders_to_print_create()
