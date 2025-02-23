# Personal Local Private FinApp

A personal, local, private financial application written in 10 minutes using **Grok 3**. This lightweight app is designed to run locally within your secure environment.

## Setup Instructions

Follow these steps to set up and run the application:

1. **Create a Python Virtual Environment**  
   Run the following command to create an isolated virtual environment:
   ```bash
   python3 -m venv .venv
   ```

2. **Activate the Virtual Environment**  
   Activate the virtual environment based on your operating system:

   - **Linux/macOS:**
     ```bash
     source ./.venv/bin/activate
     ```
   - **Windows:**
     ```bash
     .\.venv\Scripts\activate
     ```

3. **Install Required Dependencies**  
   Install all project dependencies listed in the `requirements.txt` file:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Application**  
   Start the application by running:
   ```bash
   python main.py
   ```

---

## Additional Instructions for macOS

If you're on macOS, follow these additional tips to ensure smooth setup:

- Use `python3` in all commands since macOS may link `python` to the older Python 2.x version. For example:
  ```bash
  python3 -m venv .venv
  source ./.venv/bin/activate
  pip install -r requirements.txt
  python3 main.py
  ```

- If you encounter a **"Permission Denied"** error or issues installing dependencies, it may help to install `pip` dependencies in user mode:
  ```bash
  pip install --user -r requirements.txt
  ```

- To ensure `python3` points to the correct version, check your Python version:
  ```bash
  python3 --version
  ```
  It must be **Python 3.7+**.

- Ensure Developer Tools are installed. If not, install them using:
  ```bash
  xcode-select --install
  ```