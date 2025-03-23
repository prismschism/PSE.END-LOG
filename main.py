# ==================================================
# END::LOG — Terminal-Based Mission Log System
# Compatible with Textual v2.1.2
# Author: Sahit
# ==================================================

from textual.app import App, ComposeResult
from textual.events import Key
from textual.widgets import Header, Footer, Input, Static
from textual.scroll_view import ScrollView
from textual.containers import Vertical
from datetime import datetime
import os
import json


# Folder where log files will be stored
LOG_FOLDER = "logs"


# ==================================================
# Custom Log Viewer
# ==================================================

class LogViewer(ScrollView):
    """
    Scrollable widget for displaying log entries.
    """

    def append_log(self, text: str) -> None:
        """
        Appends a new entry to the log display.

        Parameters:
        - text (str): The full log entry including timestamp.
        """
        log_entry = Static(
            text, classes="log-entry", markup=False)  # Create a new line of text
        # Add it to the scrollable view
        log_entry.styles.display = "block"  # Add style display to entry.

        self.mount(log_entry)
        # Auto-scroll to newest entry
        self.scroll_end(animate=False)


# ==================================================
# Main Application Class
# ==================================================

class EnduranceLogApp(App):
    """
    The main application class for END::LOG.
    Creates the interface and handles user input, display, and storage.
    """

    CSS_PATH = None  # We'll add custom styling here in Phase 3

    ##### ======Compose Method======#####
    def compose(self) -> ComposeResult:
        """
        Defines the UI layout:
        Header, Log Display (ScrollView), Input field, Footer.
        """
        yield Header()

        # Vertical layout holds the viewer and input together
        with Vertical():
            self.viewer = LogViewer()  # Log display area
            yield self.viewer

            self.input = Input(
                placeholder="Type mission log entry and press Enter...")  # Input field
            yield self.input

        yield Footer()

    ##### ======On Mount Method======#####
    def on_mount(self) -> None:
        """
        Runs on app start. Ensures the log storage folder exists.
        """
        os.makedirs(
            LOG_FOLDER, exist_ok=True)  # Create /logs if it doesn't exist
        # Create a spacer widget with no text
        spacer = Static("", classes="spacer", markup=False)
        spacer.styles.display = "block"

        # Mount spacer so ScrollView has a child
        self.viewer.mount(spacer)

        # Then append your startup log
        self.viewer.append_log(
            "[END::LOG SYSTEM ONLINE] :: Awaiting input...")

    ##### ======On Input Submitted Method======#####
    def on_input_submitted(self, event: Input.Submitted) -> None:
        """
        Handles log entry submission when user presses Enter.
        Adds the entry to both the display and the log file.
        """
        log_entry = event.value.strip()  # Remove any surrounding spaces

        if log_entry:
            # Generate a precise timestamp: [YYYY-MM-DD HH:MM:SS.mmm]
            now = datetime.now()
            timestamp = now.strftime(
                "%Y-%m-%d %H:%M:%S.") + f"{int(now.microsecond / 1000):03d}"

            # Combine timestamp and message
            full_entry = f"[{timestamp}] :: {log_entry}"

            # Display in the terminal UI
            self.viewer.append_log(full_entry)

            # Save to file
            self.save_log(full_entry)

        # Clear input field for next entry
        self.input.value = ""

    ##### ======On Key Method======#####
    def on_key(self, event: Key) -> None:
        # Exit app if ESC is pressed.
        if event.key == "escape":
            self.exit()

    ##### ======Save Log Method======#####
    def save_log(self, entry: str) -> None:
        """
        Saves the given log entry to a file named by date (e.g., 2025-03-21.json).

        Parameters:
        - entry (str): The full formatted log string to store.
        """
        date_str = datetime.now().strftime("%Y-%m-%d")  # File name based on date
        log_path = os.path.join(
            LOG_FOLDER, f"{date_str}.json")  # Full path to file

        # Load existing log entries if file exists, otherwise start fresh
        if os.path.exists(log_path):
            with open(log_path, "r") as f:
                logs = json.load(f)
        else:
            logs = []

        # Append the new log entry
        logs.append(entry)

        # Write all entries back to the file
        with open(log_path, "w") as f:
            json.dump(logs, f, indent=2)

# ==================================================
# Launch the App
# ==================================================


if __name__ == "__main__":
    EnduranceLogApp().run()
