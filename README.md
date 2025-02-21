# Wallis - Print Queue Management System



## 📌 Project Description
**Wallis** is a Django-based project designed to automate and streamline the creation of print queues, order selection, and related operations. 

## 🎯 Why This Project?
During my previous work, I encountered a lot of manual paperwork related to order calculations, material matching, and print queue building. To simplify these processes, I developed **Wallis**, which serves as both a practical Django project and an automation tool.

## 📂 Project Structure
Wallis follows an **MVC (Model-View-Controller) pattern**, with the following core models:

### 📌 Models Overview:
- **Worker** – Represents employees handling orders.
- **Printer** – Stores information about available printing devices.
- **Order** – Manages customer orders, including dimensions and material.
- **Material** – Defines available printing materials.
- **PrintQueue** – Organizes orders into print queues.
- **Workplace** – Represents different working stations with assigned printers.

### 📊 Database Schema:
![Wallis Models Structure](docs/structure.png)

---

## ⚡ Features
Wallis aims to replicate real-world printing workflow as closely as possible.


### 📈 Real time statistic:
- **Track leaderboard** for daily closed orders.
- **Track productivity for week**.
  ![Index](docs/index.png)

### ✔️ CRUD Operations:
- **Create, Update, Delete** print queues and orders.
- **Real-time calculations** and **order filtering** in forms.
- **Dynamic backend-driven UI** for an improved user experience.

### 📌 Print Queue Management:
- **Creating a print queue**:
  ![Print Queue Creation](docs/print-queue-create.gif)
  
- **Updating an existing queue**:
  ![Print Queue Update](docs/print-queue-update.gif)


### 🛠️ Tech Stack
- **Django 4.x – Backend framework**
- **SQLite3 – Database**
- **Bootstrap 5 – Frontend styling**
- **Chartist.js – Data visualization**
- **Django Filters – Advanced filtering**
---

## 🚀 Installation Guide

### 1️⃣ Setup & Migrations
Clone the repository and run the following commands:

`git clone https://github.com/vsafian/wallis.git`
`cd wallis`
`python -m venv venv`
`source venv/bin/activate`  # On Windows use: `venv\Scripts\activate`
`pip install -r requirements.txt`
`python manage.py makemigrations`
`python manage.py migrate`

### 2️⃣ Load Sample Data
The project provides fixtures to pre-load test data.

`python manage.py loaddata fixtures/<fixture name>.json`
Available fixtures:

materials.json
orders.json
printers.json
workers.json
workplaces.json
superuser.json

(!) Important: Load superuser.json first if you want to use pre-configured admin credentials and correct load workers fixture.

The recommended order of fixture loading:
1. workplaces.json
2. materials.json
3. printers.json
4. orders.json
5. superuser.json
6. workers.json

🔑 Superuser Credentials:
Username: `admin.user`
Password: `1qazcde3`
