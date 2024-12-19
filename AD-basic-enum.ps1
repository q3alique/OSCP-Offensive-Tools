param (
    [Parameter(Position=0)]
    [string]$AdObj,  # The type of Active Directory object to search for
    
    [Parameter(Position=1)]
    [string]$Name    # Optional argument for a specific user, group, or computer name
)

# Function to display help and available search types
function Show-Help {
    Write-Host "Usage: .\enum.ps1 <ad_obj_type> [name]"
    Write-Host ""
    Write-Host "Positional Parameters:"
    Write-Host "  <ad_obj_type>    The type of Active Directory object to search for."
    Write-Host "                   Valid values:"
    Write-Host "                     users                 - Find user accounts"
    Write-Host "                     users-basic           - Find user accounts with basic information"
    Write-Host "                     computers             - Find computer accounts"
    Write-Host "                     computers-basic       - Find computer accounts with basic information"
    Write-Host "                     groups                - Find security groups"
    Write-Host "                     groups-basic          - Find security groups with basic information"
    Write-Host "                     domaincontrollers     - Find domain controllers"
    Write-Host "                     serviceaccounts       - Find service accounts"
    Write-Host "                     trusteddomains        - Find trusted domains"
    Write-Host "                     ou                    - Find organizational units"
    Write-Host "                     printers              - Find printers"
    Write-Host "                     sites                 - Find AD sites"
    Write-Host "                     contacts              - Find contacts"
    Write-Host "                     foreignsecurity       - Find foreign security principals"
    Write-Host "                     managedserviceaccounts- Find managed service accounts"
    Write-Host "                     gpos                  - Find Group Policy Objects"
    Write-Host "                     containers            - Find containers"
    Write-Host "                     dynamicdistribution   - Find dynamic distribution groups"
    Write-Host "                     subnets               - Find AD subnets"
    Write-Host "                     sitelinks             - Find AD site links"
    Write-Host "                     hosts                 - Find host accounts"
    Write-Host ""
    Write-Host "  [name]           (Optional) The name of a specific object to search for."
    Write-Host "                   Examples:"
    Write-Host "                     .\enum.ps1 users jeff"
    Write-Host "                     .\enum.ps1 groups-basic 'Domain Admins'"
}

# If no arguments are provided, show the help message and exit
if (-not $AdObj) {
    Show-Help
    exit
}

# Dictionary of search filters
$searchFilters = @{
    "users"                 = "samAccountType=805306368"
    "computers"             = "samAccountType=805306369"
    "groups"                = "samAccountType=268435456"
    "domaincontrollers"     = "userAccountControl:1.2.840.113556.1.4.803:=8192"
    "serviceaccounts"       = "userAccountControl:1.2.840.113556.1.4.803:=512"
    "trusteddomains"        = "objectClass=trustedDomain"
    "ou"                    = "objectCategory=organizationalUnit"
    "printers"              = "objectCategory=printQueue"
    "sites"                 = "objectClass=site"
    "contacts"              = "objectCategory=contact"
    "foreignsecurity"       = "objectCategory=foreignSecurityPrincipal"
    "managedserviceaccounts"= "objectCategory=msDS-GroupManagedServiceAccount"
    "gpos"                  = "objectCategory=groupPolicyContainer"
    "containers"            = "objectCategory=container"
    "dynamicdistribution"   = "objectCategory=group"
    "subnets"               = "objectClass=subnet"
    "sitelinks"             = "objectClass=siteLink"
    "hosts"                 = "objectCategory=computer"
}

# Convert to lowercase for case-insensitive comparison
$AdObjLower = $AdObj.ToLower()

# Separate the object type from the mode (basic/full) if specified
$splitAdObj = $AdObjLower -split "-"
$objectType = $splitAdObj[0]
$mode = if ($splitAdObj.Length -eq 2) { $splitAdObj[1] } else { "full" }

# Validate the AD object type
if (-not $searchFilters.ContainsKey($objectType)) {
    Write-Host "Invalid search type '$objectType'! Use the script without arguments to see available search types."
    exit
}

# Debug: Output the valid AdObj and mode
Write-Host "Valid AdObj: $objectType"
Write-Host "Output Mode: $mode"

# Get domain information
$domainObj = [System.DirectoryServices.ActiveDirectory.Domain]::GetCurrentDomain()
$PDC = $domainObj.PdcRoleOwner.Name
$DN = ([adsi]'').distinguishedName 
$LDAP = "LDAP://$PDC/$DN"

# Set up directory entry and searcher
$direntry = New-Object System.DirectoryServices.DirectoryEntry($LDAP)
$dirsearcher = New-Object System.DirectoryServices.DirectorySearcher($direntry)

# Apply the base filter
$filter = $searchFilters[$objectType]

# Add specific user, group, or host filter if provided
if ($Name) {
    if ($objectType -eq "users" -or $objectType -eq "serviceaccounts") {
        $filter = "(&($filter)(samAccountName=$Name))"
    } elseif ($objectType -eq "groups") {
        $filter = "(&($filter)(cn=$Name))"
    } elseif ($objectType -eq "computers" -or $objectType -eq "hosts") {
        $filter = "(&($filter)(name=$Name))"
    }
}

# Debug: Output the LDAP filter for clarity
Write-Host "LDAP Filter: $filter"

# Apply the filter to the searcher
$dirsearcher.filter = $filter

# Perform the search and display the results
$result = $dirsearcher.FindAll()

# Function to resolve DNS and get the IP address (for computers-basic only)
function Resolve-IP {
    param (
        [string]$ComputerName
    )
    try {
        $dnsEntry = Resolve-DnsName -Name $ComputerName -ErrorAction Stop
        $ipAddress = $dnsEntry | Where-Object { $_.QueryType -eq "A" } | Select-Object -ExpandProperty IPAddress
        return $ipAddress
    } catch {
        return "Unable to resolve IP"
    }
}

# Function to get group members (for groups-basic only)
function Get-GroupMembers {
    param (
        [string]$GroupDN
    )
    try {
        $groupSearcher = New-Object System.DirectoryServices.DirectorySearcher
        $groupSearcher.Filter = "(&(objectClass=user)(memberOf=$GroupDN))"
        $groupSearcher.PropertiesToLoad.Add("samaccountname") | Out-Null
        $groupResult = $groupSearcher.FindAll()
        return $groupResult
    } catch {
        return @()
    }
}

# Full output mode (original functionality)
if ($mode -eq "full") {
    Foreach ($obj in $result) {
        Foreach ($prop in $obj.Properties) {
            $prop
        }
        Write-Host "-------------------------------"
    }
}
# Basic output mode for users-basic, groups-basic, computers-basic
else {
    Write-Host "`n### $objectType Results`n"
    
    if ($objectType -eq "users") {
        foreach ($obj in $result) {
            $samAccountName = $obj.Properties["samaccountname"]
            $memberOf = $obj.Properties["memberof"]
            Write-Host "- **samAccountName**: $samAccountName"
            if ($memberOf) {
                Write-Host "  - **MemberOf**:"
                foreach ($group in $memberOf) {
                    Write-Host "    - $group"
                }
            }
        }
    }
    elseif ($objectType -eq "computers") {
        foreach ($obj in $result) {
            $name = $obj.Properties["name"]
            $os = $obj.Properties["operatingsystem"]
            $ip = Resolve-IP -ComputerName $name
            Write-Host "- **Computer Name**: $name"
            Write-Host "  - **Operating System**: $os"
            Write-Host "  - **IP Address**: $ip"
        }
    }
    elseif ($objectType -eq "groups") {
        foreach ($obj in $result) {
            $cn = $obj.Properties["cn"]
            $description = $obj.Properties["description"]
            $distinguishedName = $obj.Properties["distinguishedname"]
            Write-Host "- **Group Name**: $cn"
            if ($description) {
                Write-Host "  - **Description**: $description"
            }
            # Get and display group members
            $members = Get-GroupMembers -GroupDN $distinguishedName
            if ($members.Count -gt 0) {
                Write-Host "  - **Members**:"
                foreach ($member in $members) {
                    Write-Host "    - $($member.Properties['samaccountname'])"
                }
            } else {
                Write-Host "  - **Members**: No members found"
            }
        }
    }
}
