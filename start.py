import os
import subprocess
import sys

def run_command(command):
    print(f"Running: {command}")
    try:
        subprocess.check_call(command, shell=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {e}")
        return False
    return True

def main():
    print("========================================")
    print("   Quranic Chatbot - Master Starter   ")
    print("========================================\n")

    # 1. Check for virtual environment
    if not hasattr(sys, 'real_prefix') and not (sys.base_prefix != sys.prefix):
        print("Tip: It is recommended to run this in a virtual environment.")
        print("Run 'setup_venv.bat' first if you haven't already.\n")

    # 2. Ensure data directory exists
    if not os.path.exists('data'):
        print("Creating data directory...")
        os.makedirs('data')

    # 3. Check for main data file
    if not os.path.exists('data/main_df.csv'):
        print("Main data file missing. Attempting to download...")
        if os.path.exists('download_data.py'):
            run_command("python download_data.py")
        else:
            print("Error: download_data.py not found!")

    # 4. Check for embeddings
    if not os.path.exists('data/quran_embeddings.npy'):
        print("Embeddings missing. Generating now (this may take a few minutes)...")
        if os.path.exists('generate_full_embeddings.py'):
            run_command("python generate_full_embeddings.py")
        else:
            print("Error: generate_full_embeddings.py not found!")

    # 5. Start the application
    print("\nStarting the Flask application...")
    if os.path.exists('app.py'):
        run_command("python app.py")
    else:
        print("Error: app.py not found!")

if __name__ == '__main__':
    main()
