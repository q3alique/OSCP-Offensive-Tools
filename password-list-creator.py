import argparse

def generate_password_list(users_file):
    # Predefined common passwords
    common_passwords = [
        "Password1", "Welcome1", "Letmein1",
        "Password123", "Welcome123", "Letmein123"
    ]
    
    # Open the file and read usernames
    try:
        with open(users_file, 'r') as file:
            usernames = [line.strip() for line in file if line.strip()]
    except FileNotFoundError:
        print(f"Error: The file '{users_file}' was not found.")
        return
    
    password_list = set(common_passwords)  # Start with common passwords in the list
    
    for username in usernames:
        # Add username without modification
        password_list.add(username)
        
        # Add mutations of the username
        password_list.add(username + "1")
        password_list.add(username + "@")
        password_list.add(username.capitalize())  # Capitalize first character
        password_list.add(username.lower())
        password_list.add(username.upper())
        
        # Combinations of username with common numbers and symbols
        password_list.add(username.capitalize() + "1")
        password_list.add(username.capitalize() + "@")
    
    # Save to file
    with open("password_list.txt", 'w') as outfile:
        for password in sorted(password_list):
            outfile.write(password + "\n")
    
    print("Password list generated and saved to 'password_list.txt'.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Password list generator for password spraying.")
    parser.add_argument("--users", required=True, help="File containing a list of valid usernames")
    args = parser.parse_args()
    
    generate_password_list(args.users)
