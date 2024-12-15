import subprocess, time

def run_app():
    # Usar subprocess para ejecutar streamlit
    subprocess.run(["streamlit", "run", "src/modules/ui.py"])

if __name__ == "__main__":    
    run_app()

