import tkinter as tk
from tkinter import messagebox
import sqlite3
import math
import simpleaudio as sa

# Constants
PINK = "#e2979c"
RED = "#e7305b"
GREEN = "#9bdeac"
YELLOW = "#f7f5dd"
FONT_NAME = "Courier"
WORK_MIN = 25
SHORT_BREAK_MIN = 5
LONG_BREAK_MIN = 15

# Global variables
reps = 0
timer = None
task_entry = None
task_label = None
add_task_button = None
change_task_button = None
mark_completed_button = None
db_connection = None
cursor = None
tick_marks = 0

# Database initialization
def init_db():
    global db_connection, cursor
    db_connection = sqlite3.connect('tasks.db')
    cursor = db_connection.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS tasks
                      (task_name TEXT, pomodoro_sessions INT, time_taken INT, completed BOOLEAN)''')
    db_connection.commit()

# Function to reset the timer
def reset_timer():
    global reps, tick_marks,mark_completed_button,change_task_button
    reps = 0
    tick_marks = 0
    window.after_cancel(timer)
    change_task_button.grid_forget() 
    mark_completed_button.grid_forget()
    canvas.itemconfig(timer_text, text="00:00")
    title_label.config(text="Timer")
    check_marks.config(text="")
    task_label.config(text="")
    task_entry.delete(0, tk.END)
    task_entry.grid(row=1, column=0, padx=5, pady=5)  # Adjusted row value here
    add_task_button.grid(row=1, column=3, padx=5, pady=5)

# Function to start the timer
def start_timer():
    global reps
    reps += 1

    work_sec = WORK_MIN * 60
    short_break_sec = SHORT_BREAK_MIN * 60
    long_break_sec = LONG_BREAK_MIN * 60

    if reps % 8 == 0:
        play_sound("long_break_bell.wav")
        messagebox.showinfo("Break Time", "Take a long break!")
        count_down(long_break_sec)
        title_label.config(text="Break", fg=RED)
    elif reps % 2 == 0:
        play_sound("short_break_bell.wav")
        messagebox.showinfo("Break Time", "Take a short break!")
        count_down(short_break_sec)
        title_label.config(text="Break", fg=PINK)
    else:
        play_sound("work_bell.wav")
        messagebox.showinfo("Work Time", "Time to work!")
        count_down(work_sec)
        title_label.config(text="Work", fg=GREEN)

# Function to count down
def count_down(count):
    global tick_marks
    count_min = math.floor(count / 60)
    count_sec = count % 60
    if count_sec < 10:
        count_sec = f"0{count_sec}"
    canvas.itemconfig(timer_text, text=f"{count_min}:{count_sec}")
    if count > 0:
        global timer
        timer = window.after(1000, count_down, count - 1)
    else:
        add_tick_mark()
        if reps % 8 != 0:
            start_timer()

# Function to add a tick mark
def add_tick_mark():
    global tick_marks
    tick_marks += 1
    check_marks.config(text="✔" * (tick_marks // 2))

# Function to add a task
def add_task():
    global task_entry, task_label, add_task_button, change_task_button, mark_completed_button
    task_name = task_entry.get()
    if task_name:
        task_entry.grid_forget()
        add_task_button.grid_forget()
        task_label = tk.Label(window, text=task_name, font=(FONT_NAME, 16), bg=YELLOW)
        task_label.grid(row=1, column=1, padx=5, pady=5)  # Adjusted row value here
        change_task_button = tk.Button(window, text="Change Task", command=change_task)
        change_task_button.grid(row=2, column=0, padx=5, pady=5)
        mark_completed_button = tk.Button(window, text="Mark Task Completed", command=mark_completed)
        mark_completed_button.grid(row=2, column=3, padx=5, pady=5)
    else:
        messagebox.showerror("Error", "Please enter the name of the task.")

# Function to change the task
def change_task():
    global task_entry, task_label, add_task_button, change_task_button, mark_completed_button
    task_label.grid_forget()
    change_task_button.grid_forget()
    mark_completed_button.grid_forget()
    task_entry.delete(0, tk.END)
    task_entry.grid(row=1, column=0, padx=5, pady=5)
    add_task_button.grid(row=1, column=3, padx=5, pady=5)

# Function to mark the task as completed
def mark_completed():
    global task_entry, task_label, add_task_button, change_task_button, mark_completed_button
    change_task_button.grid_forget() 
    mark_completed_button.grid_forget()
    task_name = task_label.cget("text")
    cursor.execute("INSERT INTO tasks (task_name, pomodoro_sessions, time_taken, completed) VALUES (?, ?, ?, ?)",
                   (task_name, reps // 2, WORK_MIN * reps // 2 * 60, 1))
    db_connection.commit()
    play_sound("achievement_bell.wav")
    messagebox.showinfo("Task Completed", f"Congratulations! Task '{task_name}' has been completed.")
    reset_timer()

# Function to view tasks
def view_tasks():
    cursor.execute("SELECT * FROM tasks")
    tasks = cursor.fetchall()
    task_info = ""
    for task in tasks:
        task_info += f"Task: {task[0]}, Pomodoro Sessions: {task[1]}, Time Taken: {task[2]} seconds, Completed: {task[3]}\n"
    messagebox.showinfo("Tasks Information", task_info)

# Function to save the task details to the database
def save_task():
    global task_label
    task_name = task_label.cget("text")
    cursor.execute("INSERT INTO tasks (task_name, pomodoro_sessions, time_taken, completed) VALUES (?, ?, ?, ?)",
                   (task_name, reps // 2, WORK_MIN * reps // 2 * 60, 0))
    db_connection.commit()

# Function to play a sound
def play_sound(sound_file):
    wave_obj = sa.WaveObject.from_wave_file(sound_file)
    play_obj = wave_obj.play()
    play_obj.wait_done()  # Wait until sound has finished playing

# UI Setup
window = tk.Tk()
window.title("Pomodoro Timer")
window.config(padx=20, pady=20, bg=YELLOW)

init_db()

title_label = tk.Label(window, text="Timer", fg=GREEN, bg=YELLOW, font=(FONT_NAME, 50))
title_label.grid(column=1, row=0)

canvas = tk.Canvas(window, width=200, height=224, bg=YELLOW, highlightthickness=0)
tomato_img = tk.PhotoImage(file="redtomato.png")
canvas_image=canvas.create_image(100, 112, image=tomato_img)
timer_text = canvas.create_text(100, 130, text="00:00", fill="white", font=(FONT_NAME, 35, "bold"))
canvas.grid(column=1, row=3)

start_button = tk.Button(window, text="Start Pomodoro Work Session", highlightthickness=0, command=start_timer)
start_button.grid(column=0, row=4)

reset_button = tk.Button(window, text="Reset Timer", highlightthickness=0, command=reset_timer)
reset_button.grid(column=3, row=4)

check_marks = tk.Label(window, fg=GREEN, bg=YELLOW)
check_marks.grid(column=1, row=4)

task_entry = tk.Entry(window, font=(FONT_NAME, 12), bg=YELLOW)
task_entry.grid(row=1, column=0, padx=5, pady=5)
task_entry.insert(0, "Enter task: ")

add_task_button = tk.Button(window, text="Add Task", highlightthickness=0, command=add_task)
add_task_button.grid(row=1, column=3, padx=5, pady=5)

show_tasks_button = tk.Button(window, text="Show Tasks", highlightthickness=0, command=view_tasks)
show_tasks_button.grid(column=1, row=5)

window.mainloop()
