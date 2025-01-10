#!/usr/bin/env python3
import subprocess
import sys
import os
import time
import argparse
import threading
import atexit

class SimulationManager:
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.processes = {}
        self.log_file = os.path.join(self.base_dir, 'logs', 'simulation.log')
        atexit.register(self.cleanup)
        
        # Create logs directory if it doesn't exist
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
        
        # Delete existing log file
        if os.path.exists(self.log_file):
            try:
                os.remove(self.log_file)
                print(f"Deleted previous log file: {self.log_file}")
            except Exception as e:
                print(f"Warning: Could not delete log file: {e}")

    def get_script_path(self, script_name):
        return os.path.join(self.base_dir, 'code', script_name)

    def start_backend(self):
        backend_path = self.get_script_path('backend/backend.py')
        # Run the backend in the current terminal
        try:
            subprocess.run([sys.executable, backend_path], check=True)
        except KeyboardInterrupt:
            print("\nBackend stopped.")

    def start_game_engine(self):
        engine_path = self.get_script_path('gameengine/gameengine.py')
        # Start game engine in a new terminal window based on OS
        if sys.platform == 'win32':
            self.processes['engine'] = subprocess.Popen(
                ['start', 'cmd', '/c', sys.executable, engine_path],
                shell=True
            )
        elif sys.platform == 'darwin':  # macOS
            self.processes['engine'] = subprocess.Popen(
                ['osascript', '-e', 
                f'tell app "Terminal" to do script "{sys.executable} {engine_path}"']
            )
        else:  # Linux and other Unix-like
            terminals = ['gnome-terminal', 'xterm', 'konsole']
            for term in terminals:
                try:
                    self.processes['engine'] = subprocess.Popen(
                        [term, '--', sys.executable, engine_path]
                    )
                    break
                except FileNotFoundError:
                    continue

    def start_test(self):
        test_path = self.get_script_path('test-script.py')
        # Run test script in a new terminal
        if sys.platform == 'win32':
            subprocess.Popen(
                ['start', 'cmd', '/c', 
                 f'{sys.executable} {test_path} && pause'],
                shell=True
            )
        elif sys.platform == 'darwin':
            subprocess.Popen(
                ['osascript', '-e', 
                f'tell app "Terminal" to do script "{sys.executable} {test_path}"']
            )
        else:
            terminals = ['gnome-terminal', 'xterm', 'konsole']
            for term in terminals:
                try:
                    subprocess.Popen([term, '--', sys.executable, test_path])
                    break
                except FileNotFoundError:
                    continue

    def cleanup(self):
        for process in self.processes.values():
            try:
                process.terminate()
            except:
                pass

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Start simulation components')
    parser.add_argument('--test', action='store_true', 
                       help='Run test script after starting servers')
    args = parser.parse_args()

    manager = SimulationManager()
    
    print("Starting game engine simulator in new terminal...")
    manager.start_game_engine()
    time.sleep(2)  # Wait for game engine to initialize
    
    if args.test:
        print("Starting test script in new terminal...")
        manager.start_test()
        time.sleep(1)

    print("Starting backend server with interactive interface...")
    print("Note: Other components are running in separate terminal windows")
    time.sleep(1)
    manager.start_backend()
