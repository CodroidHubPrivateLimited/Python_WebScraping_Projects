#!/usr/bin/env python3
"""
Main entry point for Face Recognition Attendance System.
Run: python main.py
Choose Register / CLI / GUI / Web.
"""
import os
import subprocess
import sys
import webbrowser
import time

def check_prereqs():
    if not os.path.exists("./Images"):
        print("Note: ./Images/ empty. Use Register to add faces.")
    print("Ready! Use my_env\\Scripts\\activate first.")

def run_register():
    print("Register new employee: name input → capture 5 photos.")
    subprocess.run([sys.executable, "register_face.py"])

def run_cli():
    print("CLI mode: Press q to exit cam.")
    subprocess.run([sys.executable, "deepface_attendance.py"])

def run_gui():
    print("GUI mode: Press Start button.")
    subprocess.run([sys.executable, "attendance_gui.py"])

def run_web():
    print("Web mode: http://127.0.0.1:5000")
    server = subprocess.Popen([sys.executable, "Flask Backend.py"])
    webbrowser.open("http://127.0.0.1:5000")
    input("Press Enter to stop...")
    server.terminate()

if __name__ == '__main__':
    check_prereqs()
    print("\n0. Register new employee")
    print("1. CLI Attendance")
    print("2. GUI Attendance")
    print("3. Web Attendance")
    print("q. Quit")
    choice = input("Choose: ").strip().lower()
    if choice == '0':
        run_register()
    elif choice == '1':
        run_cli()
    elif choice == '2':
        run_gui()
    elif choice == '3':
        run_web()
    else:
        print("Bye!")
