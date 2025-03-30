# PennyTracker
PennyTracker is a lightweight SQLite database manager designed to help users track daily expenses with ease. It allows users to create, manage, and modify tables in a pre-existing .db file, making it a simple yet efficient tool for personal finance tracking.

Features
-
- User-friendly interface for managing expense records
- SQLite-powered—no external database setup required
- Can create multiple tables for different records
- Supports data insertion, deletion, and visualization
- Compact & fast, ideal for quick financial logging
- Available in multiple languages

How PennyTracker differs
-
`Lightweight & Simple`: Unlike full-fledged finance apps, PennyTracker is minimalistic and only focuses on expense tracking.

`SQLite-based`: PennyTracker directly manages tables in a .db file, making it structured and modifiable outside the app.

`Command-Line Interface`: Most alternatives have a GUI, while PennyTracker is CLI-driven, appealing to more technical users.

Installation
-
- Python 3.11+
- SQLite installed (optional but recommended) https://www.sqlite.org/index.html

Usage
-
- There are executable files for each available language, switching between them will only change the language interface as they all manage the same database file.
- Current supported languages: English, Vietnamese.

#Functionality
-
In the main menu
-
- `1. View table`: Display stored expense records (tables) 
- `2. Create new table`: Add a new table to track finances
- `3. Remove table(s)`: Delete an existing table
- `4. Clear screen`: Refresh the display
- `5. Exit program`: Close PennyTracker
- NOTE: You may see a table named `sqlite_sequence` after you create your first table. This table is automatically generated by SQLite and is used to manage the row ID numbers of every other table that you have created.

For managing individual tables
-
- `1. Add new row(s)`: Update your table with new records
- `2. Remove row(s)`: Remove records from your table
- `3. Graph`: Graph a bar plot based on which records you chose to have displayed
- `4. Clear screen`: Refresh the display
- `5. Return`: Returns back to the main menu
- NOTES:
  - Date Format: When entering a record’s date, follow the format YYYY MM DD (e.g., 2025 3 12).
  - Selecting Rows for Update/Deletion:
      - You will be prompted with `Enter the IDs of rows involved (comma-separated, use '->' for ranges): `.
      - Example input: 1, 2, 3, 5->9, 12, 13
      - This is equivalent to selecting: 1, 2, 3, 5, 6, 7, 8, 9, 12, 13

License
-
PennyTracker is open-source and licensed under the Apache 2.0 License.

Author's note
-
I hope you find this small app to be useful. Feel free to submit pull requests or report issues on the repository. Contributions are always welcome!
