# dcm-mini-viewer

A small PySide6 application for viewing DICOM files, developed as a discovery project for the OnkoDICOM project.

## Features

- Preference management using SQLite database
- Loading and validation of DICOM files
- Display of DICOM images
- Display of DICOM metadata
- Cross-platform support (Windows, macOS, Linux)
- Comprehensive logging
- High test coverage

## Project Structure

```
src/
├── main.py                    # Main application entry point
├── config/
│   ├── __init__.py
│   ├── preferences_manager.py # Manages reading/writing preferences
├── dicom/
│   ├── __init__.py
│   ├── dicom_handler.py       # DICOM file handling logic
├── ui/
│   ├── __init__.py
│   ├── main_window.py         # Main application window
│   ├── dialogs/
│       ├── __init__.py
│       ├── element_dialog.py  # Dialog for missing DICOM elements
├── utils/
│   ├── __init__.py
│   ├── logger.py              # Logging configuration

test/
├── __init__.py
├── test_preferences_manager.py
├── test_dicom_handler.py
```

## Requirements

This project uses Poetry for dependency management. All dependencies are specified in the `pyproject.toml` file.

## Setup

1. Clone the repository
2. Set up a virtual environment using Poetry:

```bash
poetry shell
```

3. Install pre-commit hooks (for development):

```bash
poetry run pre-commit install
```

4. Run the application:

```bash
python -m src.main
```

## Testing

Run the tests using pytest:

```bash
python -m pytest test/
```

Run tests with coverage reporting:

```bash
python -m pytest --cov=src test/
```

## Development Guidelines

- All code must follow Black formatting with a 127 character line length
- Use pre-commit hooks to ensure consistent code style
- All new functionality must have corresponding unit tests
- Maintain at least 80% test coverage
- Use the Model-View-Controller (MVC) pattern for UI development

## License

GPL 3
