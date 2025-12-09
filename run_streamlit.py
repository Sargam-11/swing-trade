"""
Direct Streamlit launcher to ensure correct Python environment
"""
import sys
import subprocess

if __name__ == "__main__":
    # Print Python info
    print(f"Python version: {sys.version}")
    print(f"Python executable: {sys.executable}")
    print()

    # Run streamlit with the current Python interpreter
    result = subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"])
    sys.exit(result.returncode)
