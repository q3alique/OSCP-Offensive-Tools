import argparse
import xml.etree.ElementTree as ET
import xml.dom.minidom
import os

# Usage instructions
USAGE = """
Usage: create_library.py --ip <folder_ip> [--icon <icon_name>] [--folder-type <folder_type_name>] [--pinned <YES/NO>] [-o <output_filename>]

Parameters:
  --ip            IP address of the folder you want to include in the library.
  --icon          Name of the icon to use. Available icons (default: Documents):
                  - Documents
                  - Music
                  - Pictures
                  - Videos
  --folder-type   Type of folder (default: Documents). Available types:
                  - Documents
                  - Music
                  - Pictures
                  - Videos
  --pinned        Specify if the library should be pinned (default: YES). Options:
                  - YES
                  - NO
  -o, --output    Specify the output filename without extension (default: IP-based).

Example:
  python create_library.py --ip "192.168.119.2"
  python create_library.py --ip "192.168.119.2" --icon "Music" --folder-type "Music" --pinned "NO" -o "MyLibrary"
"""

# Common folder types and their GUIDs
FOLDER_TYPES = {
    "Documents": "{7d49d726-3c21-4f05-99aa-fdc2c9474656}",
    "Music": "{94d6ddcc-4a68-4175-a374-bd584a510b78}",
    "Pictures": "{b3690e58-e961-423b-b687-386ebfd83239}",
    "Videos": "{5fa96407-7e77-483c-ac93-691d05850de8}"
}

# Common icons (for simplicity, using sample indices)
ICONS = {
    "Documents": "imageres.dll,-102",
    "Music": "imageres.dll,-108",
    "Pictures": "imageres.dll,-113",
    "Videos": "imageres.dll,-116"
}

def create_library_xml(ip, icon, folder_type, pinned):
    # Ensure IP has the HTTP scheme
    if not ip.startswith("http://") and not ip.startswith("https://"):
        ip = "http://" + ip

    # Create XML structure
    library = ET.Element("libraryDescription", xmlns="http://schemas.microsoft.com/windows/2009/library")
    name = ET.SubElement(library, "name").text = "@windows.storage.dll,-34582"
    version = ET.SubElement(library, "version").text = "6"
    isLibraryPinned = ET.SubElement(library, "isLibraryPinned").text = "true" if pinned.lower() == "yes" else "false"
    iconReference = ET.SubElement(library, "iconReference").text = icon

    templateInfo = ET.SubElement(library, "templateInfo")
    folderType = ET.SubElement(templateInfo, "folderType").text = FOLDER_TYPES[folder_type]

    searchConnectorDescriptionList = ET.SubElement(library, "searchConnectorDescriptionList")
    searchConnectorDescription = ET.SubElement(searchConnectorDescriptionList, "searchConnectorDescription")
    isDefaultSaveLocation = ET.SubElement(searchConnectorDescription, "isDefaultSaveLocation").text = "true"
    isSupported = ET.SubElement(searchConnectorDescription, "isSupported").text = "false"

    simpleLocation = ET.SubElement(searchConnectorDescription, "simpleLocation")
    url = ET.SubElement(simpleLocation, "url").text = ip

    # Convert XML structure to a string
    xml_str = ET.tostring(library, encoding="unicode", method="xml")

    # Parse and pretty-print the XML
    dom = xml.dom.minidom.parseString(xml_str)
    pretty_xml_as_string = dom.toprettyxml(indent="    ")

    return pretty_xml_as_string

def main():
    parser = argparse.ArgumentParser(description="Create a .library-ms file", usage=USAGE)
    parser.add_argument("--ip", required=True, help="IP address of the folder to include in the library")
    parser.add_argument("--icon", choices=ICONS.keys(), default="Documents", help="Choose an icon (default: Documents)")
    parser.add_argument("--folder-type", choices=FOLDER_TYPES.keys(), default="Documents", help="Choose a folder type (default: Documents)")
    parser.add_argument("--pinned", choices=["YES", "NO"], default="YES", help="Set the value of isLibraryPinned (default: YES)")
    parser.add_argument("-o", "--output", default="config",help="Specify the output filename without extension (default: IP-based)")

    args = parser.parse_args()

    library_xml = create_library_xml(args.ip, ICONS[args.icon], args.folder_type, args.pinned)

    # Determine output filename
    if args.output:
        library_filename = args.output + ".library-ms"
    else:
        # Sanitize IP for default filename (remove scheme, replace ':' and '/' with '_')
        base_name = args.ip.replace("http://", "").replace("https://", "").replace(":", "_").replace("/", "_")
        library_filename = base_name + ".library-ms"

    # Save XML to a .library-ms file
    with open(library_filename, "w", encoding="utf-8") as f:
        f.write(library_xml)
    
    print(f".library-ms file created: {library_filename}")

if __name__ == "__main__":
    main()
