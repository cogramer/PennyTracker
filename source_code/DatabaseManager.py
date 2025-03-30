from colorama import Fore, Style
from utility import find_base_directory, date_fetch, selective_id_input, clear_screen, Translator
from tabulate import tabulate
import plotext as plt
import datetime
import sqlite3
import sys
import gc
import os

red = Fore.RED
green = Fore.GREEN
cyan = Fore.CYAN
lmagenta = Fore.LIGHTMAGENTA_EX
lblue = Fore.LIGHTBLUE_EX
lyellow = Fore.LIGHTYELLOW_EX
reset = Style.RESET_ALL


if getattr(sys, 'frozen', False): #If running an executable
    direc = os.path.dirname(sys.executable)
else:
    direc = os.path.dirname(os.path.abspath(__file__))
        
language = "en"
translator = Translator(language, directory=direc)
trans = translator.load_translation()


class DatabaseManager:
    def __init__(self, directory):
        """
        Initializes the DatabaseManager.

        Parameters
        -
            directory : Path
                Base directory where databases are stored.
        """
        self.directory = directory or find_base_directory('Library')

        if self.directory == None:
            raise ValueError(reset + red + trans["The 'Library' directory could not be found in the path hierarchy."] + reset)

    def connect_database(self, database_name):
        """
        Connects to an sqlite3 database.

        Parameters
        -
            database_name : string
        Returns
        - 
            Connection | None
                Returns an sqlite3 Connection object or None in cases of errors.
        """
        database_directory = f"{self.directory}/databases"
        try:
            os.makedirs(database_directory, exist_ok=True)
            database = f"{database_directory}/{database_name}"
            conn = sqlite3.connect(database)
            return conn
        
        except Exception as e:
            error_msg = reset + red + "Error: " + f"{e}" + reset
            print(error_msg)
            return None
        
    def create_table(self, database_name, table_name):
        """
        Creates an expenses table inside of an sqlite database in the format of: \n
            CREATE TABLE {table_name} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            time TEXT,
            value REAL,
            unit TEXT,
            note NULL );

        Parameters
        -
            database_name : string
            table_name : string
            directory : Path
                Base directory to find the database folder.
        """
        conn = self.connect_database(database_name)

        cursor = conn.cursor()

        create_table_query = f'''
        CREATE TABLE {table_name} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            time TEXT,
            value REAL,
            unit TEXT,
            note TEXT
        );
        '''
        try:
            cursor.execute(create_table_query)

        except sqlite3.OperationalError as e:

            if "table {} already exists".format(table_name) in str(e):

                print(trans["Table '"] + table_name + trans["' already exists. Would you like to overwrite it?"])

                print(reset + red + trans["Warning. This will delete everything inside '"] + table_name + "'." + reset)
                
                user_input = input(trans["Overwrite? (y/n): "]).lower()

                if user_input == 'y' or user_input == 'yes':
                    cursor.execute(f"DROP TABLE {table_name}")

                    cursor.execute(create_table_query)

                    print(trans["Table '"] + table_name + trans["' has been overwritten."])
                else:
                    pass

            conn.commit()
            conn.close()

            success_msg = reset + cyan + trans["Table '"] + table_name + trans["' for database '"] + database_name + trans["' created successfully!"] + reset 
            print(success_msg)
        except Exception as e:
            error_msg = reset + red + "Error: " + f"{e}" + reset
            print(error_msg)


    def insert_row_into_table(self, conn, table_name, data):
        cursor = conn.cursor()
        insert_query = f'''
        INSERT INTO {table_name} (date, time, value, unit, note)
        VALUES (?, ?, ?, ?, ?)
        '''
        cursor.execute(insert_query, data)
        conn.commit()


    def remove_rows_from_table(self, conn, table_name, ids_to_delete):
        cursor = conn.cursor()
        delete_query = f'''
        DELETE FROM {table_name} WHERE id IN ({','.join(['?']*len(ids_to_delete))})
        '''
        cursor.execute(delete_query, ids_to_delete)
        conn.commit()

        print(reset + lmagenta + trans["Deleted rows with id(s): "] + f"{', '.join(map(str, ids_to_delete))}" + reset)


    def list_all_tables(self, database_name):
        conn = self.connect_database(database_name)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall() # THIS IS IN TUPLES

        if not tables:
            Error_msg = reset + red + trans["No tables found in '"] + database_name + "'." + reset
            print(Error_msg)
            return []
        
        # EXTRACT NAME FROM TUPLE
        tables_names = [table[0] for table in tables]
        
        print(reset + cyan + trans["Available tables:"] + reset)
        for idx, table in enumerate(tables_names, 0):
            print(f"{idx + 1}: {table}")
        print()

        cursor.close()
        conn.close()

        return tables_names


    def drop_table(self, conn, table_name):
        if table_name == "sqlite_sequence":
            print(reset + red + trans["Table '"] + table_name + trans["' cannot be deleted."] + reset)
            return False

        cursor = conn.cursor() 

        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
        table_exists = cursor.fetchone()

        if table_exists:
            try:
                cursor.execute(f"DROP TABLE {table_name}")
                conn.commit()
                return True
            except Exception as e:
                print(reset + red + "Error: " + f"{e}" + reset)
        else:
            print(reset + red + trans["Table '"] + table_name + trans["' does not exist."] + reset)


    def reset_table_id(self, conn, table_name):
        cursor = conn.cursor()

        create_temp_table_query = f'''
        CREATE TABLE IF NOT EXISTS temp_{table_name} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            time TEXT,
            value REAL,
            unit TEXT,
            note NULL
        );
        '''

        cursor.execute(create_temp_table_query)

        move_data_to_temp = f"INSERT INTO temp_{table_name} (date, time, value, unit, note) SELECT date, time, value, unit, note FROM {table_name} ORDER BY id"
        
        cursor.execute(move_data_to_temp)

        cursor.execute(f"DROP TABLE {table_name}")

        cursor.execute(f"ALTER TABLE temp_{table_name} RENAME TO {table_name}")

        conn.commit()


    def create_plot_table(self, conn, table_name, ids_to_use):
        cursor = conn.cursor()

        creation_query = f'''
        CREATE TEMPORARY TABLE temp_{table_name} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            time TEXT,
            value REAL,
            unit TEXT,
            note TEXT
        );
        '''

        cursor.execute(creation_query)

        if ids_to_use:
            insert_query = f'''
                INSERT INTO temp_{table_name} (id, date, time, value, unit, note)
                SELECT id, date, time, value, unit, note FROM {table_name}
                WHERE id IN ({','.join(['?']*len(ids_to_use))});
            '''
            print(insert_query)
            cursor.execute(insert_query, ids_to_use)
            conn.commit()
        else:
            print(reset + red + trans["No IDs provided, skipping query."] + reset)

    
    def create_bar_plot(self, conn, table_name):
        cursor = conn.cursor()
        
        query = f'''
            SELECT date, value, unit FROM temp_{table_name} ORDER BY date;
        '''
        cursor.execute(query)
        data = cursor.fetchall()

        if not data:
            print(reset + red + trans["No data found."] + reset)
            return

        dates, values = zip(*[(row[0], row[1]) for row in data])
        unit = data[0][2]

        plt.clear_figure()
        plt.clear_terminal()

        plt.bar(dates, values, width=1, orientation="vertical")

        plt.title(trans["Values of '"] + table_name + trans["' from "] + dates[0] + trans[" to "] + dates[-1])
        plt.xlabel(trans["Date"])
        plt.ylabel(trans["Unit: "] + unit)

        plt.show()


    def tabulate_table(self, conn, table_name):
        if table_name == "sqlite_sequence":
            print(reset + red + trans["Table '"] + table_name + trans["' cannot be viewed."] + reset)
        try:
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM {table_name};")
            rows = cursor.fetchall()
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = [col[1] for col in cursor.fetchall()]

            cursor.execute(f"SELECT SUM(value), AVG(value) FROM {table_name};")
            fetch_result_summean = cursor.fetchone()
            sum_value, mean_value = fetch_result_summean if fetch_result_summean is not None else (None, None)

            cursor.execute(f"SELECT * FROM {table_name} ORDER BY value ASC LIMIT 1;")
            fetch_result_smallest = cursor.fetchone()
            smallest_row = fetch_result_smallest if fetch_result_smallest is not None else None

            cursor.execute(f"SELECT * FROM {table_name} ORDER BY value DESC LIMIT 1;")
            fetch_result_largest = cursor.fetchone()
            largest_row = fetch_result_largest if fetch_result_largest is not None else None

            # Print the table
            print(tabulate(rows, headers=columns, tablefmt='fancy_grid', showindex=False, numalign="center", stralign="center"))

            # print summary statistics
            summary_data = [
            [trans["Sum"], sum_value if sum_value is not None else "N/A"],
            [trans["Mean"], mean_value if mean_value is not None else "N/A"],
            [trans["Smallest Value"], smallest_row[3] if smallest_row else "N/A", f"{trans['Row']} ID: {smallest_row[0]}" if smallest_row else "N/A"],
            [trans["Largest Value"], largest_row[3] if largest_row else "N/A", f"{trans['Row']} ID: {largest_row[0]}" if largest_row else "N/A"]
            ]
            print(tabulate(summary_data, tablefmt='fancy_grid', showindex=False, numalign="center", stralign="center"))

        except Exception as e:
                print(reset + red + "Error: " + f"{e}" + reset)


class DatabaseHelper:
    def __init__(self, directory):
        self.DBMan = DatabaseManager(directory)

    def Add_New_Rows(self, conn, table_name):
        while True:
            date = date_fetch()
            if date == -1:
                conn.close()
                print(trans["Data insertion cancelled."])
                break
            
            date = str(date)
            time_of_insert = str(datetime.datetime.now().strftime("%H:%M:%S"))

            cancel_insertion = False

            while True:
                value = input(reset + green + trans["Enter amount (real number or press Enter to quit): "] + reset).strip()
                
                if value == "":
                    print("Data insertion cancelled.")
                    cancel_insertion = True
                    break
                try:
                    value = float(value)
                    break
                except ValueError:
                    print(reset + red + trans["Invalid input! Please enter a valid real number."] + reset)

            if cancel_insertion:
                break

            unit = str(input(reset + green + trans["Enter unit: "] + reset)).strip()
            note = str(input(reset + green + trans["Enter note (optional): "] + reset)).strip()
            row = (date, time_of_insert, value, unit, note)

            self.DBMan.insert_row_into_table(conn, table_name, row)

            print(trans["Data inserted into table '"] + table_name + trans["' successfully."])
            gc.collect()

            confirm = input(reset + lyellow + trans["Add another row? (y/n): "] + reset)
            if confirm.lower() == "y" or confirm.lower() == "yes":
                continue
            else:
                break

    def Remove_Rows(self, conn, table_name):
        while True:
            ids_input = input(trans["Enter the IDs of rows involved (comma-separated, use '->' for ranges): "])
            ids_to_delete = selective_id_input(ids_input)

            if not ids_to_delete:
                confirm = input(reset + lyellow + trans["Continue row removal? (y/n): "] + reset)
                if confirm.lower() in ["n", "no"]:
                    print(trans["Row removal canceled."])
                    conn.close()
                    gc.collect()
                    return
                else:
                    continue
            break

        self.DBMan.remove_rows_from_table(conn, table_name, ids_to_delete)
        self.DBMan.reset_table_id(conn, table_name)
        print(trans["Rows in table '"] + table_name + trans["' removed."])
        gc.collect()

    def Graph_Bar_Plot(self, conn, table_name):
        while True:
            ids_input = input(trans["Enter the IDs of rows involved (comma-separated, use '->' for ranges): "])
            ids_to_graph = selective_id_input(ids_input)

            if not ids_to_graph:
                confirm = input(reset + lyellow + trans["Continue graph plotting? (y/n): "] + reset)
                if confirm.lower() in ["n", "no"]:
                    print(trans["Graph plotting canceled."])
                    conn.close()
                    gc.collect()
                    return
                else:
                    continue
            break
        
        self.DBMan.create_plot_table(conn, table_name, ids_to_graph)
        self.DBMan.create_bar_plot(conn, table_name)
        

    def manage_individual_table(self, database_name, table_name):
        while True:
            conn = self.DBMan.connect_database(database_name)
            self.DBMan.tabulate_table(conn, table_name=table_name)
            conn.close()

            print(reset + lblue + trans["1. Add new row(s)"] + reset)
            print(reset + lblue + trans["2. Remove row(s)"] + reset)
            print(reset + lblue + trans["3. Graph"] + reset)
            print(reset + lblue + trans["4. Clear screen"] + reset)
            print(reset + lblue + trans["5. Return"] + reset)

            choice = input(reset + lyellow + f"{trans['Enter your choice']} (1/2/3/4/5): " + reset)

            try:
                conn = self.DBMan.connect_database(database_name)

                if choice == "1":
                    self.Add_New_Rows(conn, table_name)
                    conn.close()
                    input(f"{trans['Press Enter to continue']}...\n")
                elif choice == "2":
                    self.Remove_Rows(conn, table_name)
                    conn.close()
                    input(f"{trans['Press Enter to continue']}...\n")                   
                elif choice == "3":
                    self.Graph_Bar_Plot(conn, table_name)
                    conn.close()
                    input(f"{trans['Press Enter to continue']}...\n")
                elif choice == "4":
                    conn.close()
                    clear_screen()                   
                elif choice == "5":
                    conn.close()                
                    break
                else:
                    conn.close()
                    print(reset + red + trans["Invalid choice. Please enter only the numbers that are presented."] + reset)
                    
            except Exception as e:
                print(reset + red + "Error: " + f"{e}" + reset)


           