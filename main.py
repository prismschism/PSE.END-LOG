# ==================================================
# END::LOG — Terminal-Based Mission Log System
# Author: Sahit Felix - PSE
# ==================================================

from textual.app import App, ComposeResult
from textual.events import Key
from textual.widgets import Header, Footer, Input, Static
from textual.containers import Vertical, VerticalScroll
from datetime import datetime, timezone
import asyncio
import os
import json
import uuid


# ==================================================
# Global Variables and Methods
# ==================================================


# Folder where log files will be stored
LOG_FOLDER = "logs"


##### ======Get Timestamp Method======#####

def get_timestamp() -> str:
    # Get current time in UTC zone.
    now = datetime.now(timezone.utc)
    # Return formatted timestamp
    return now.strftime("%Y-%m-%dT%H:%M:%S.") + f"{int(now.microsecond / 1000):03d}" + "Z"


# ==================================================
# Custom Log Viewer
# ==================================================

class LogViewer(VerticalScroll):
    """
    Scrollable widget for displaying log entries.
    """

    ##### ======Append Log Method======#####
    # Appends a newly submitted log entry to the log display.
    def append_log(self, text: str) -> None:

        log_entry = Static(
            text, classes="log-entry", markup=False)  # Create a new line of text
        # Add it to the scrollable view
        log_entry.styles.display = "block"  # Add style display to entry.

        self.mount(log_entry)
        return log_entry  # Important so the App can scroll after mounting


# ==================================================
# Main Application Class
# ==================================================


class EnduranceLogApp(App):
    """
    The main application class for END::LOG.
    Creates the interface and handles user input, display, and storage.
    """

    CSS_PATH = "themes/endlog.tcss"  # CSS styling

    # Bool initialized for later shutdown prompt use.
    awaiting_shutdown_confirmation = False

    def __init__(self):
        super().__init__()
        self.username = "usernamePlaceHolder"
        self.session = str(uuid.uuid4().hex[:6])
        self.log_counter = -2

    ##### ======Compose Method======#####
    def compose(self) -> ComposeResult:
        """
        UI layout:
        Header, Log Display (ScrollView), Input field, Footer.
        """
        yield Header()

        # Vertical layout holds the viewer and input together
        with Vertical():
            self.viewer = LogViewer(id="log-viewer")  # Log display area
            yield self.viewer

            self.input = Input(
                placeholder="Type log entry and press Enter...")  # Input field
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

        self.awaiting_shutdown_confirmation = False

        # Mount spacer so ScrollView has a child (Ensures initial view is blank)
        self.viewer.mount(spacer)

        # System startup log
        # Source and Level keys
        source = "system"
        level = "sys_message"
        self.system_log("SYSTEM LAUNCH", source, level)
        self.system_log("ENDURANCE LOG SYSTEM ONLINE", source, level)

        ##### =======Fromat Log Method======#####

    def format_log(self, entry_type: str, log_message: str, source: str, level: str) -> dict:
        self.log_counter += 1

        return {
            "session_id": f"username_{self.session}",
            "instance_count": self.log_counter,
            "type": entry_type,
            "source": source,
            "level": level,
            "message": log_message,
            "message_id": uuid.uuid4().hex[:6],
            "timestamp": get_timestamp()
        }

    ##### ======On Input Submitted Method======#####

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """
        Handles log entry submission when user presses Enter.
        Adds the entry to both the display and the log file.
        """
        log_entry = event.value.strip()  # Remove any surrounding spaces

        if log_entry:
            # Get timestamp

            timestamp = get_timestamp()

            # Set type, source, level for format_log
            entry_type = "LOG"
            source = "user"
            level = "input"

            # Combine timestamp and message for log entries.
            display_entry = f"[{timestamp}] [{entry_type}]    :: {log_entry}"

            # Display in the terminal UI
            self.viewer.append_log(display_entry)
            self.set_timer(0.02, lambda: self.viewer.scroll_end(animate=True))

            # Format user's input for log
            save_user_entry = self.format_log(
                entry_type, log_entry, source, level)

            # Save to file
            self.save_log(save_user_entry)

        # Clear input field for next entry
        self.input.value = ""

    ##### ======On Key Method======#####
    async def on_key(self, event: Key) -> None:
        # DEBUG
        # self.debug_log(f"Key pressed: {event.key}")

        # Source and Level keys
        source = "system"
        # sys_message for messages to user or prompt for prompts.
        level = ""

        # If already awaiting shutdown confirmation
        if self.awaiting_shutdown_confirmation:
            if event.key in ("1", "2"):
                level = "sys_message"  # Appropriate level for message.
                if event.key == "1":
                    self.system_log(
                        "Shutdown confirmed. Exiting END::LOG...", source, level)
                    # Sleeper to allow user to see the exit was recognized.
                    await asyncio.sleep(3)

                    self.exit()
                elif event.key == "2":
                    self.system_log("Shutdown aborted.", source, level)
                    self.awaiting_shutdown_confirmation = False

            # If key options 1 or 2 not pressed, abort
            else:
                level = "sys_message"  # Appropriate level for message
                self.system_log(
                    "Unrecognized input. Shutdown aborted.", source, level)
                self.awaiting_shutdown_confirmation = False  # Cancel confirmation state
            return  # Stop propagation here

        # If ESC pressed to exit, prompt confirmation and switch awaiting shutdown to true
        if event.key == "escape":
            level = "prompt"  # Appropriate level of message.
            self.awaiting_shutdown_confirmation = True
            self.set_focus(None)
            self.system_log(
                "TERMINATE PROGRAM? 1. Confirm    2. Abort", source, level)

    ##### ======Save Log Method======#####

    def save_log(self, entry: str) -> None:

        # Saves the given log entry to a file named by date
        timestamp = get_timestamp()
        date_str = timestamp[:10]  # Extracting date from ISO 8601 date
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
    def system_log(self, message: str, source: str, level: str) -> None:

        # Generate precise timestamp
        timestamp = get_timestamp()

        # Entry type
        entry_type = "SYSTEM"

        # Combine timestamp and message for displaying System entries.
        display_system_entry = f"[{timestamp}] [SYSTEM] :: {message}"

        # Display in the terminal UI
        self.viewer.append_log(display_system_entry)
        self.set_timer(0.02, lambda: self.viewer.scroll_end(animate=True))

        # Format_log for JSON.
        save_system_entry = self.format_log(
            entry_type, message, source, level)
        # Save to JSON
        self.save_log(save_system_entry)

    def debug_log(self, message: str, source: str, level: str) -> None:

        # Get precise timestamp
        timestamp = get_timestamp()
        # DEBUG message entry stamp
        debug_entry = f"[{timestamp}] [DEBUG]  :: {message}"
        # Display in terminal UI
        self.viewer.append_log(debug_entry)

        # Format log for JSON
        save_debug_log = self.format_log("DEBUG", message, source, level)
        # Save to JSON
        self.save_log(save_debug_log)


# ==================================================
# Launch the App
# ==================================================
if __name__ == "__main__":
    EnduranceLogApp().run()
