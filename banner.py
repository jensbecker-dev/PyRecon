# Banner module for the PyRecon tool
# Displays a colorful ASCII art banner when the tool starts
from colorama import Fore, Style

def show():
    print(f"""{Fore.CYAN}
   ▄███████▄ ▄██   ▄      ▄████████    ▄████████  ▄████████  ▄██████▄  ███▄▄▄▄   
  ███    ███ ███   ██▄   ███    ███   ███    ███ ███    ███ ███    ███ ███▀▀▀██▄ 
  ███    ███ ███▄▄▄███   ███    ███   ███    █▀  ███    █▀  ███    ███ ███   ███ 
  ███    ███ ▀▀▀▀▀▀███  ▄███▄▄▄▄██▀  ▄███▄▄▄     ███        ███    ███ ███   ███ 
▀█████████▀  ▄██   ███ ▀▀███▀▀▀▀▀   ▀▀███▀▀▀     ███        ███    ███ ███   ███ 
  ███        ███   ███ ▀███████████   ███    █▄  ███    █▄  ███    ███ ███   ███ 
  ███        ███   ███   ███    ███   ███    ███ ███    ███ ███    ███ ███   ███ 
 ▄████▀       ▀█████▀    ███    ███   ██████████ ████████▀   ▀██████▀   ▀█   █▀  
                         ███    ███                                              
{Style.RESET_ALL}""")
    print(f"{Fore.GREEN}  [!]  Recon Tool v1.0{Style.RESET_ALL}")
    print(f"{Fore.GREEN}  [!]  Developed by jensbecker-dev{Style.RESET_ALL}")
    print("" + "-" * 80 + "\n")

if __name__ == "__main__":

    show()
    