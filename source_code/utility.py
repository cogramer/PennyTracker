from colorama import Fore, Style
from pathlib import Path
import json
import datetime
import sys
import os

red = Fore.RED
reset = Style.RESET_ALL

class Translator:
    def __init__(self, language, directory):
        self.language = language
        self.directory = directory or find_base_directory('Library')

        if self.directory == None:
            raise ValueError(reset + red + "The 'Library' directory could not be found in the path hierarchy." + reset)

    def load_translation(self):
        languages_directory = f"{self.directory}/languages"
        try:
            os.makedirs(languages_directory, exist_ok=True)
            with open(f"{languages_directory}/{self.language}.json", "r", encoding="utf-8") as t:
                return json.load(t)
        
        except Exception as e:
            error_msg = reset + red + "Error: " + f"{e}" + reset
            print(error_msg)
            return None


if getattr(sys, 'frozen', False): #If running an executable
    direc = os.path.dirname(sys.executable)
else:
    direc = os.path.dirname(os.path.abspath(__file__))
        
language = "en"
translator = Translator(language, directory=direc)
trans = translator.load_translation()
        

def find_base_directory(target_folder_name):
    """
    Travels backwards from the current folder to find a matching parent folder.

    Parameters
    ----------
        target_folder_name : Path
            Path of the desired parent folder.
    Returns
    -------
        parent : Path | None
            Returns None if the desired parent folder does not exist.

    """
    current_path = Path(__file__).resolve()
    for parent in current_path.parents:
        if parent.name == target_folder_name:
            return parent
    return None

def selective_id_input(ids_input):
    """
    Parses the user input for IDs (comma-separated or range) and returns a sorted list of unique IDs. Example: "1,2,4,6->9,11".

    Parameters
    -
        ids_input : list

    Returns
    -
        ids_to_use : list 
    """
    try:
        ids_to_use = []
        for part in ids_input.split(','):
            part = part.strip()
            if '->' in part:
                # Handles range inputs like 1->5
                start, end = map(int, part.split('->'))
                ids_to_use.extend(range(start, end + 1))
            else:
                # handles individual inputs
                ids_to_use.append(int(part))
        
        # Remove dupes and sort
        return sorted(set(ids_to_use))

    except ValueError:
        print(reset + red + trans["Invalid input! Please enter integers or ranges in the correct format."] + reset)
        return []
    

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def date_fetch():
    date_input = input(Style.RESET_ALL + Fore.GREEN + trans["Enter date (YYYY MM DD): "] + Style.RESET_ALL).strip()
    year, month, day = map(int, date_input.split())
    try:
        specific_date = datetime.date(year, month, day)
        return specific_date
    except ValueError as e:
        print(f"{trans['This date does not exist: ']} {e} {trans['. Please try again.']}")
        confirm = input(reset + red + trans["Continue? (y/n): "] + reset)
        confirm = confirm.lower()
        if 'y' or 'yes' in confirm:
            date_fetch()
        else:
            return -1
