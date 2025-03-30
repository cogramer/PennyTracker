from utility import clear_screen, Translator
from DatabaseManager import DatabaseManager, DatabaseHelper
from colorama import Fore, Style
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

databaseManager = DatabaseManager(directory=direc)
db_name = "database.db"

if __name__ == "__main__":
    try:
        while True:
            print(reset + lyellow + "-----Main-Menu-----")
            print(reset + lblue + trans["1. View table"] + reset)
            print(reset + lblue + trans["2. Create new table"] + reset)
            print(reset + lblue + trans["3. Remove table(s)"] + reset)
            print(reset + lblue + trans["4. Clear screen"] + reset)
            print(reset + lblue + trans["5. Exit program"] + reset)

            choice = input(reset + lyellow + f"{trans['Enter your choice']} (1/2/3/4/5): " + reset)

            if choice == "1":
                tables_list = databaseManager.list_all_tables(database_name=db_name)

                if not tables_list:
                    continue
                table_choice = int(input(trans["Enter the ID number of the table you want to view: "]))

                if 1 <= table_choice <= len(tables_list):
                    table_to_use = tables_list[table_choice - 1]
                else:
                    print(reset + red + trans["Table ID "] + f"{table_choice}" + trans[" invalid."] + reset)
                    continue
                databaseHelper = DatabaseHelper(directory=direc)   
                databaseHelper.manage_individual_table(database_name=db_name, table_name=table_to_use)
            
            elif choice == "2":
                new_table = input(reset + lyellow + trans["Name of new table: "] + reset).strip()
                databaseManager.create_table(database_name=db_name, table_name=new_table)
                print(trans["Table '"] + new_table + trans["' created successfully."])
            
            elif choice == "3":
                tables_list = databaseManager.list_all_tables(database_name=db_name)
                if not tables_list:
                    continue
                table_choice = int(input(trans["Enter the ID number of the table you want to remove: "]))

                if 1 <= table_choice <= len(tables_list):
                    table_to_use = tables_list[table_choice - 1]
                else:
                    print(reset + red + trans["Table ID "] + f"{table_choice}" + trans[" invalid."] + reset)
                    continue
                conn = databaseManager.connect_database(database_name=db_name)
                dropped = databaseManager.drop_table(conn, table_name=table_to_use)
                conn.close()
                if dropped:
                    print(trans["Table '"] + table_to_use + trans["' Removed successfully."])

            elif choice == "4":
                clear_screen()
            
            elif choice == "5":
                break
            else:
                    print(reset + red + trans["Invalid choice. Please enter only the numbers that are presented."] + reset)

    except Exception as e:
        print(reset + red + "Error: " + f"{e}" + reset)
    
