import tkinter as tk
from tkinter import ttk, messagebox
import csv
import os
from datetime import datetime, date
from collections import Counter
import matplotlib.pyplot as plt

FILE_NAME = "deadlines.csv"


def load_data():
    if not os.path.exists(FILE_NAME):
        with open(FILE_NAME, "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([
                "ID", "Task", "Category", "Due Date",
                "Priority", "Status", "Description"
            ])

    with open(FILE_NAME, "r", newline="") as file:
        reader = csv.DictReader(file)
        return list(reader)


def save_data():
    with open(FILE_NAME, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([
            "ID", "Task", "Category", "Due Date",
            "Priority", "Status", "Description"
        ])

        for task in tasks:
            writer.writerow([
                task["ID"],
                task["Task"],
                task["Category"],
                task["Due Date"],
                task["Priority"],
                task["Status"],
                task["Description"]
            ])


def get_status(task):
    if task["Status"] == "Completed":
        return "Completed"

    due_date = datetime.strptime(
        task["Due Date"], "%Y-%m-%d"
    ).date()

    if due_date < date.today():
        return "Overdue"

    return "Upcoming"


def update_dashboard():
    total_label.config(text=str(len(tasks)))

    upcoming = 0
    completed = 0
    overdue = 0

    for task in tasks:
        status = get_status(task)

        if status == "Upcoming":
            upcoming += 1
        elif status == "Completed":
            completed += 1
        else:
            overdue += 1

    upcoming_label.config(text=str(upcoming))
    completed_label.config(text=str(completed))
    overdue_label.config(text=str(overdue))


def show_tasks(data=None):
    for item in table.get_children():
        table.delete(item)

    if data is None:
        data = tasks

    for task in data:
        status = get_status(task)

        days_left = (
            datetime.strptime(task["Due Date"], "%Y-%m-%d").date()
            - date.today()
        ).days

        table.insert(
            "",
            "end",
            values=(
                task["ID"],
                task["Task"],
                task["Category"],
                task["Due Date"],
                days_left,
                task["Priority"],
                status,
                task["Description"]
            )
        )

    update_dashboard()


def clear_fields():
    task_entry.delete(0, tk.END)
    date_entry.delete(0, tk.END)
    description_entry.delete(0, tk.END)

    category_box.set("Assignment")
    priority_box.set("Medium")
    status_box.set("Pending")


def add_task():
    task_name = task_entry.get().strip()
    due_date = date_entry.get().strip()

    if task_name == "" or due_date == "":
        messagebox.showerror(
            "Error", "Please enter task name and due date"
        )
        return

    try:
        datetime.strptime(due_date, "%Y-%m-%d")
    except ValueError:
        messagebox.showerror(
            "Error", "Enter date as YYYY-MM-DD"
        )
        return

    task = {
        "ID": str(max([int(t["ID"]) for t in tasks], default=0) + 1),
        "Task": task_name,
        "Category": category_box.get(),
        "Due Date": due_date,
        "Priority": priority_box.get(),
        "Status": status_box.get(),
        "Description": description_entry.get().strip()
    }

    tasks.append(task)
    save_data()
    show_tasks()
    clear_fields()

    messagebox.showinfo("Success", "Deadline added successfully")


def select_task(event):
    selected = table.selection()

    if not selected:
        return

    values = table.item(selected[0], "values")

    clear_fields()

    task_entry.insert(0, values[1])
    category_box.set(values[2])
    date_entry.insert(0, values[3])
    priority_box.set(values[5])

    if values[6] == "Completed":
        status_box.set("Completed")
    else:
        status_box.set("Pending")

    description_entry.insert(0, values[7])


def update_task():
    selected = table.selection()

    if not selected:
        messagebox.showerror("Error", "Select a task first")
        return

    task_name = task_entry.get().strip()
    due_date = date_entry.get().strip()

    if task_name == "" or due_date == "":
        messagebox.showerror(
            "Error", "Please enter task name and due date"
        )
        return

    try:
        datetime.strptime(due_date, "%Y-%m-%d")
    except ValueError:
        messagebox.showerror(
            "Error", "Enter date as YYYY-MM-DD"
        )
        return

    task_id = table.item(selected[0], "values")[0]

    for task in tasks:
        if task["ID"] == task_id:
            task["Task"] = task_name
            task["Category"] = category_box.get()
            task["Due Date"] = due_date
            task["Priority"] = priority_box.get()
            task["Status"] = status_box.get()
            task["Description"] = description_entry.get().strip()

    save_data()
    show_tasks()
    clear_fields()

    messagebox.showinfo("Success", "Deadline updated successfully")


def delete_task():
    selected = table.selection()

    if not selected:
        messagebox.showerror("Error", "Select a task first")
        return

    task_id = table.item(selected[0], "values")[0]

    if messagebox.askyesno("Confirm", "Delete this deadline?"):
        tasks[:] = [
            task for task in tasks if task["ID"] != task_id
        ]

        save_data()
        show_tasks()
        clear_fields()


def complete_task():
    selected = table.selection()

    if not selected:
        messagebox.showerror("Error", "Select a task first")
        return

    task_id = table.item(selected[0], "values")[0]

    for task in tasks:
        if task["ID"] == task_id:
            task["Status"] = "Completed"

    save_data()
    show_tasks()


def search_tasks():
    keyword = search_entry.get().lower()
    category = filter_category.get()
    priority = filter_priority.get()
    status = filter_status.get()

    result = []

    for task in tasks:
        actual_status = get_status(task)

        if keyword not in task["Task"].lower() and keyword not in task["Description"].lower():
            continue

        if category != "All" and task["Category"] != category:
            continue

        if priority != "All" and task["Priority"] != priority:
            continue

        if status != "All" and actual_status != status:
            continue

        result.append(task)

    show_tasks(result)


def show_all():
    search_entry.delete(0, tk.END)
    filter_category.set("All")
    filter_priority.set("All")
    filter_status.set("All")
    show_tasks()


def show_reports():
    if len(tasks) == 0:
        messagebox.showinfo("Reports", "Add some deadlines first")
        return

    categories = Counter(task["Category"] for task in tasks)

    plt.figure(figsize=(7, 5))
    plt.bar(categories.keys(), categories.values())
    plt.title("Category-wise Workload")
    plt.xlabel("Category")
    plt.ylabel("Number of Deadlines")
    plt.tight_layout()
    plt.show()

    statuses = Counter(get_status(task) for task in tasks)

    labels = ["Upcoming", "Completed", "Overdue"]
    values = [statuses.get(label, 0) for label in labels]

    plt.figure(figsize=(7, 5))
    plt.pie(values, labels=labels, autopct="%1.1f%%")
    plt.title("Deadline Status Distribution")
    plt.tight_layout()
    plt.show()

    priorities = Counter(task["Priority"] for task in tasks)

    plt.figure(figsize=(7, 5))
    plt.bar(priorities.keys(), priorities.values())
    plt.title("Priority-wise Workload")
    plt.xlabel("Priority")
    plt.ylabel("Number of Deadlines")
    plt.tight_layout()
    plt.show()


root = tk.Tk()
root.title("Deadline Management System")
root.geometry("1250x750")

tasks = load_data()

title = tk.Label(
    root,
    text="Deadline and Workload Management System",
    font=("Arial", 20, "bold")
)
title.pack(pady=10)

dashboard = tk.Frame(root)
dashboard.pack(pady=5)

tk.Label(dashboard, text="Total", font=("Arial", 12)).grid(row=0, column=0, padx=25)
tk.Label(dashboard, text="Upcoming", font=("Arial", 12)).grid(row=0, column=1, padx=25)
tk.Label(dashboard, text="Completed", font=("Arial", 12)).grid(row=0, column=2, padx=25)
tk.Label(dashboard, text="Overdue", font=("Arial", 12)).grid(row=0, column=3, padx=25)

total_label = tk.Label(dashboard, text="0", font=("Arial", 16, "bold"))
total_label.grid(row=1, column=0)

upcoming_label = tk.Label(dashboard, text="0", font=("Arial", 16, "bold"))
upcoming_label.grid(row=1, column=1)

completed_label = tk.Label(dashboard, text="0", font=("Arial", 16, "bold"))
completed_label.grid(row=1, column=2)

overdue_label = tk.Label(dashboard, text="0", font=("Arial", 16, "bold"))
overdue_label.grid(row=1, column=3)

form = tk.LabelFrame(root, text="Deadline Details", padx=10, pady=10)
form.pack(fill="x", padx=10, pady=10)

tk.Label(form, text="Task Name").grid(row=0, column=0, padx=5, pady=5)
task_entry = tk.Entry(form, width=25)
task_entry.grid(row=0, column=1, padx=5, pady=5)

tk.Label(form, text="Category").grid(row=0, column=2, padx=5, pady=5)
category_box = ttk.Combobox(
    form,
    values=["Assignment", "Bill", "Exam", "Project", "Personal", "Other"],
    state="readonly",
    width=22
)
category_box.set("Assignment")
category_box.grid(row=0, column=3, padx=5, pady=5)

tk.Label(form, text="Due Date").grid(row=0, column=4, padx=5, pady=5)
date_entry = tk.Entry(form, width=18)
date_entry.grid(row=0, column=5, padx=5, pady=5)

tk.Label(form, text="Priority").grid(row=1, column=0, padx=5, pady=5)
priority_box = ttk.Combobox(
    form,
    values=["High", "Medium", "Low"],
    state="readonly",
    width=22
)
priority_box.set("Medium")
priority_box.grid(row=1, column=1, padx=5, pady=5)

tk.Label(form, text="Status").grid(row=1, column=2, padx=5, pady=5)
status_box = ttk.Combobox(
    form,
    values=["Pending", "Completed"],
    state="readonly",
    width=22
)
status_box.set("Pending")
status_box.grid(row=1, column=3, padx=5, pady=5)

tk.Label(form, text="Description").grid(row=1, column=4, padx=5, pady=5)
description_entry = tk.Entry(form, width=25)
description_entry.grid(row=1, column=5, padx=5, pady=5)

buttons = tk.Frame(root)
buttons.pack(pady=5)

tk.Button(buttons, text="Add Deadline", command=add_task).grid(row=0, column=0, padx=5)
tk.Button(buttons, text="Update", command=update_task).grid(row=0, column=1, padx=5)
tk.Button(buttons, text="Delete", command=delete_task).grid(row=0, column=2, padx=5)
tk.Button(buttons, text="Mark Completed", command=complete_task).grid(row=0, column=3, padx=5)
tk.Button(buttons, text="Clear", command=clear_fields).grid(row=0, column=4, padx=5)
tk.Button(buttons, text="Reports", command=show_reports).grid(row=0, column=5, padx=5)

filters = tk.LabelFrame(root, text="Search and Filter", padx=10, pady=10)
filters.pack(fill="x", padx=10, pady=5)

tk.Label(filters, text="Search").grid(row=0, column=0, padx=5)
search_entry = tk.Entry(filters, width=20)
search_entry.grid(row=0, column=1, padx=5)

tk.Label(filters, text="Category").grid(row=0, column=2, padx=5)
filter_category = ttk.Combobox(
    filters,
    values=["All", "Assignment", "Bill", "Exam", "Project", "Personal", "Other"],
    state="readonly",
    width=15
)
filter_category.set("All")
filter_category.grid(row=0, column=3, padx=5)

tk.Label(filters, text="Priority").grid(row=0, column=4, padx=5)
filter_priority = ttk.Combobox(
    filters,
    values=["All", "High", "Medium", "Low"],
    state="readonly",
    width=12
)
filter_priority.set("All")
filter_priority.grid(row=0, column=5, padx=5)

tk.Label(filters, text="Status").grid(row=0, column=6, padx=5)
filter_status = ttk.Combobox(
    filters,
    values=["All", "Upcoming", "Completed", "Overdue"],
    state="readonly",
    width=12
)
filter_status.set("All")
filter_status.grid(row=0, column=7, padx=5)

tk.Button(filters, text="Search", command=search_tasks).grid(row=0, column=8, padx=5)
tk.Button(filters, text="Show All", command=show_all).grid(row=0, column=9, padx=5)

table_frame = tk.Frame(root)
table_frame.pack(fill="both", expand=True, padx=10, pady=10)

columns = (
    "ID", "Task", "Category", "Due Date",
    "Days Left", "Priority", "Status", "Description"
)

table = ttk.Treeview(
    table_frame,
    columns=columns,
    show="headings"
)

for column in columns:
    table.heading(column, text=column)
    table.column(column, width=130, anchor="center")

table.pack(side="left", fill="both", expand=True)

scrollbar = ttk.Scrollbar(
    table_frame,
    orient="vertical",
    command=table.yview
)
scrollbar.pack(side="right", fill="y")
table.configure(yscrollcommand=scrollbar.set)

table.bind("<<TreeviewSelect>>", select_task)

show_tasks()

root.mainloop()