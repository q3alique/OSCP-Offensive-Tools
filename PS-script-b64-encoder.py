import base64
import sys
import re
import os
import getopt

def encode_powershell_script(script_content):
    """
    Encodes a PowerShell script in base64 format, suitable for passing as a parameter
    to PowerShell for execution.

    Args:
        script_content (str): The content of the PowerShell script.

    Returns:
        str: The base64 encoded PowerShell script.
    """
    cleaned_script = ""
    # Remove potential BOM characters that might have been added by ISE
    bom_pattern = re.compile(u'(\xef|\xbb|\xbf)')
    # Insert null byte after each character
    for char in bom_pattern.sub("", script_content):
        cleaned_script += char + "\x00"
    
    # Base64 encode the cleaned PowerShell script
    encoded_script = base64.b64encode(cleaned_script.encode()).decode("utf-8")
    return encoded_script

def print_usage():
    """
    Prints the usage instructions for the script.
    """
    print("Version: 1.0")
    print("Usage: {0} <options>\n".format(sys.argv[0]))
    print("Options:")
    print("   -h, --help                  Show this help message and exit")
    print("   -s, --script      <script>  Path to the PowerShell script file.")
    sys.exit(0)

def main():
    try:
        options, args = getopt.getopt(sys.argv[1:], 'hs:', ['help', 'script='])
    except getopt.GetoptError:
        print("Error: Invalid options provided!")
        print_usage()
    
    if len(sys.argv) == 1:
        print_usage()

    for opt, arg in options:
        if opt in ('-h', '--help'):
            print_usage()
        elif opt in ('-s', '--script'):
            script_file_path = arg
            if not os.path.isfile(script_file_path):
                print("Error: The specified PowerShell script file does not exist.")
                sys.exit(1)
            else:
                with open(script_file_path, 'r') as script_file:
                    script_content = script_file.read()
                    encoded_script = encode_powershell_script(script_content)
                    print("Base64 Encoded Script:\n", encoded_script)
                    print("\nUsage Instructions:")
                    print("1. Open PowerShell with elevated privileges (Run as Administrator).")
                    print("2. Set the execution policy if not already set:")
                    print("   Set-ExecutionPolicy RemoteSigned")
                    print("3. Execute the encoded script:")
                    print("   powershell -EncodedCommand {}".format(encoded_script))

if __name__ == "__main__":
    main()
