# Salain
> Malicious Email Detector

## Prerequisites
- Ensure you have Python 3.10 installed.
- Verify the installation by running:
  ```sh
  python --version
  ```

## Creating a Virtual Environment
1. Open a terminal and navigate to your project directory.
2. Run the following command to create a virtual environment:
   ```sh
   python -m venv venv
   ```

## Activating the Virtual Environment
- **On macOS/Linux:**
  ```sh
  source venv/bin/activate
  ```
- **On Windows (cmd):**
  ```sh
  venv\Scripts\activate
  ```
- **On Windows (PowerShell):**
  ```sh
  venv\Scripts\Activate.ps1
  ```

## Installing Dependencies
After activation, install the required packages using:
```sh
pip install -r requirements.txt
```

## Creating a `.secrets.toml` File
1. In the `.streamlit` directory, create a file named `.secrets.toml`.
2. Add secrets following the format in `.streamlit/secrets.example.toml`.

## Running the Code Locally
To run the application, use:
```sh
python -m app.app
```

## Deactivating the Virtual Environment
To exit the virtual environment, run:
```sh
deactivate
```