# ==================================================
# END::LOG — Terminal-Based Mission Log System
# Author: Sahit Felix - PSE
# ==================================================

from textual.app import App, ComposeResult
from textual.events import Key
from textual.widgets import Header, Footer, Input, Static
from textual.scroll_view import ScrollView
from textual.containers import Vertical
from datetime import datetime
import asyncio
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

    CSS_PATH = None  # Will add custom styling here in Phase 3

    awaiting_shutdown_confirmation = False

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

        #
        self.awaiting_shutdown_confirmation = False

        # Mount spacer so ScrollView has a child (Ensures initial view is blank)
        self.viewer.mount(spacer)

        # Then append system startup log
        self.system_log("SYSTEM LAUNCH")
        self.system_log("ENDURANCE LOG SYSTEM ONLINE")

    ##### ======On Input Submitted Method======#####
    def on_input_submitted(self, event: Input.Submitted) -> None:
        """
        Handles log entry submission when user presses Enter.
        Adds the entry to both the display and the log file.
        """
        log_entry = event.value.strip()  # Remove any surrounding spaces

        if log_entry:
            # Generate a precise timestamp: [YYYY-MM-DD HH:MM:SS.mmm]

            timestamp = get_timestamp()

            # Combine timestamp and message for log entries.
            full_entry = f"[{timestamp}] [LOG]    :: {log_entry}"

            # Display in the terminal UI
            self.viewer.append_log(full_entry)

            # Save to file
            self.save_log(full_entry)

        # Clear input field for next entry
        self.input.value = ""

    ##### ======On Key Method======#####
    async def on_key(self, event: Key) -> None:
        # DEBUG
        # self.debug_log(f"Key pressed: {event.key}")

        # If already awaiting shutdown confirmation
        if self.awaiting_shutdown_confirmation:
            if event.key in ("1", "2"):
                if event.key == "1":
                    self.system_log("Shutdown confirmed. Exiting END::LOG...")
                    # Sleeper to allow user to see the exit was recognized.
                    await asyncio.sleep(3)

                    self.exit()
                elif event.key == "2":
                    self.system_log("Shutdown aborted.")
                    self.awaiting_shutdown_confirmation = False

            # If key options 1 or 2 not pressed, abort
            else:
                self.system_log("Unrecognized input. Shutdown aborted.")
                self.awaiting_shutdown_confirmation = False  # 💥 Cancel confirmation state
            return  # Stop propagation here

        # If ESC pressed to exit, prompt confirmation and switch awaiting shutdown to true
        if event.key == "escape":
            self.awaiting_shutdown_confirmation = True
            self.set_focus(None)
            self.system_log("TERMINATE PROGRAM? 1. Confirm    2. Abort")

    ##### ======Save Log Method======#####

    def save_log(self, entry: str) -> None:

        # Saves the given log entry to a file named by date.
        date_str = datetime.now().strftime("%Y-%m-%d")  # File name based on date
        log_path = os.path.join(
            LOG_FOLDER, f"END_LOG_{date_str}.json")  # Full path to file

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

    ##### ======System Log Method======#####
    def system_log(self, message: str) -> None:

        # Generate precise timestamp

        timestamp = get_timestamp()

        # Combine timestamp and message for log entries.
        system_entry = f"[{timestamp}] [SYSTEM] :: {message}"

        # Display in the terminal UI
        self.viewer.append_log(system_entry)

        # Save to file
        self.save_log(system_entry)

    def debug_log(self, message: str) -> None:

        # Get precise timestamp
        timestamp = get_timestamp()
        # DEBUG message entry stamp
        debug_entry = f"[{timestamp}] [DEBUG]  :: {message}"
        # Display in terminal UI
        self.viewer.append_log(debug_entry)
        # Save to file
        self.save_log(debug_entry)


# ==================================================
# Global Methods
# ==================================================

##### ======Get Timestamp Method======#####
def get_timestamp() -> str:
    # Get current time
    now = datetime.now()
    # Return formatted timestamp
    return now.strftime("%Y-%m-%d %H:%M:%S.") + f"{int(now.microsecond / 1000):03d}"


# ==================================================
# Launch the App
# ==================================================


if __name__ == "__main__":
    EnduranceLogApp().run()
