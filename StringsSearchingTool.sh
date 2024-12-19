#!/bin/bash

# Define default terms
DEFAULT_TERMS=("password" "pass" "credentials" "config" "creds")

# Function to get search terms
get_search_terms() {
    echo -e "\nDefault list of terms:"
    for term in "${DEFAULT_TERMS[@]}"; do
        echo -e " - $term"
    done
    read -p "Do you want to use the default list of terms? (yes/no): " choice
    choice=$(echo "$choice" | tr '[:upper:]' '[:lower:]')
    if [ "$choice" == "yes" ]; then
        SEARCH_TERMS=("${DEFAULT_TERMS[@]}")
    else
        read -p "Enter your own list of terms separated by spaces: " -a SEARCH_TERMS
    fi
}

# Function to search for terms within files
search_in_files() {
    FOLDER="$1"
    SEARCH_RECURSIVE="$2"
    declare -A matched_strings_map

    # Clear or create output file
    > matched_strings.txt

    if [ "$FOLDER" == "current" ]; then
        ROOT_FOLDER=$(pwd)
    elif [ "$FOLDER" == "all" ]; then
        ROOT_FOLDER="/"
    else
        ROOT_FOLDER="$FOLDER"
    fi

    # Set search depth based on recursive choice
    if [ "$SEARCH_RECURSIVE" == "yes" ]; then
        FIND_CMD="find \"$ROOT_FOLDER\" -type f"
    else
        FIND_CMD="find \"$ROOT_FOLDER\" -maxdepth 1 -type f"
    fi

    # Iterate over each file and search for terms
    while IFS= read -r -d '' file; do
        while IFS= read -r line; do
            for term in "${SEARCH_TERMS[@]}"; do
                if [[ "$line" == *"$term"* ]]; then
                    matched_strings_map["$file:$line"]=1
                fi
            done
        done < "$file"
    done < <(eval "$FIND_CMD -print0")

    # Save results or show no match message
    if [ ${#matched_strings_map[@]} -eq 0 ]; then
        echo -e "\e[1;31mNo matching strings found in the files.\e[0m"
    else
        for entry in "${!matched_strings_map[@]}"; do
            echo "$entry" >> matched_strings.txt
        done
        echo -e "\e[1;32m\nMatching strings have been saved to 'matched_strings.txt'.\e[0m"
    fi
}

# Function to print logo
print_logo() {
    echo -e "
   / \\__
  (    @\\___
  /         O
 /   (_____/
 /_____/   U"
    echo -e "\e[1;36mstring sEaRchIng tool 1.0.1 by q3alique\e[0m"
}

# Function for loading animation
loading_animation() {
    animation="|/-\\"
    for ((i=0; i<10; i++)); do
        for char in {1..4}; do
            echo -ne "\rProcessing... ${animation:$char:1}"
            sleep 0.1
        done
    done
}

main() {
    # Print logo
    print_logo

    # Get folder choice
    echo -e "\e[1;33m\nOptions:\e[0m"
    echo -e "\e[1;33m1. Examine current folder\e[0m"
    echo -e "\e[1;33m2. Examine all folders\e[0m"
    echo -e "\e[1;33m3. Specify a folder to examine\e[0m"
    read -p $'\e[1;33m\nEnter your choice (1, 2, or 3): \e[0m' choice

    # Get folder choice
    case "$choice" in
        1) FOLDER="current";;
        2) FOLDER="all";;
        3) read -p $'\e[1;33mEnter the folder path to examine: \e[0m' FOLDER;;
        *) echo "Invalid choice"; exit 1;;
    esac

    # Get search terms
    get_search_terms

    # Get search options
    read -p $'\e[1;33m\nDo you want to examine recursively? (yes/no): \e[0m' SEARCH_RECURSIVE
    SEARCH_RECURSIVE=$(echo "$SEARCH_RECURSIVE" | tr '[:upper:]' '[:lower:]')

    # Search in files
    search_in_files "$FOLDER" "$SEARCH_RECURSIVE"
}

# Run main function
main
