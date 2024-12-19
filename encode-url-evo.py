import urllib.parse
import sys

def url_encode_spaces(input_string):
    """
    Encode only spaces in the input string.
    
    Args:
        input_string (str): The string to encode.
    
    Returns:
        str: The string with spaces URL encoded.
    """
    return input_string.replace(' ', '%20')

def url_encode_all(input_string):
    """
    Encode all characters in the input string.
    
    Args:
        input_string (str): The string to encode.
    
    Returns:
        str: The URL encoded string.
    """
    return urllib.parse.quote(input_string, safe='')

def double_url_encode(input_string):
    """
    Perform double URL encoding on the input string.
    
    Args:
        input_string (str): The string to double encode.
    
    Returns:
        str: The double URL encoded string.
    """
    first_encoded = url_encode_all(input_string)
    return url_encode_all(first_encoded) if first_encoded else None

def url_encode_component(input_string):
    """
    Encode the input string similar to JavaScript's encodeURIComponent function,
    leaving the scheme (e.g., "http") unencoded if present.
    
    Args:
        input_string (str): The string to encode.
    
    Returns:
        str: The component-encoded string with scheme unencoded.
    """
    # Split scheme if present (e.g., http:// or https://)
    scheme_split = input_string.split("://", 1)
    if len(scheme_split) > 1:
        # Encode only the part after the scheme
        encoded_body = urllib.parse.quote(scheme_split[1], safe='~-._')
        return f"{scheme_split[0]}://{encoded_body}"
    else:
        # No scheme found, encode the entire input
        return urllib.parse.quote(input_string, safe='~-._')

def display_encoded_versions(user_input):
    """
    Display the encoded versions of the user input.
    
    Args:
        user_input (str): The original input string.
    """
    # Simplest encoding (spaces only)
    spaces_encoded = url_encode_spaces(user_input)
    
    # URL Component encoding (new encoding type)
    component_encoded = url_encode_component(user_input)
    
    # All characters encoded
    all_encoded = url_encode_all(user_input)
    
    # Double encoding
    double_encoded = double_url_encode(user_input)
    
    print(f"\033[92mSimplest encoding (spaces only):\033[0m\n{spaces_encoded}\n")  # Green color
    print(f"\033[93mURL Component encoding:\033[0m\n{component_encoded}\n")       # Yellow color
    print(f"\033[94mAll characters encoded:\033[0m\n{all_encoded}\n")             # Blue color
    print(f"\033[96mDouble encoding:\033[0m\n{double_encoded}\n")                 # Cyan color

def main():
    # Check if user input is provided via command-line argument
    if len(sys.argv) > 1:
        user_input = ' '.join(sys.argv[1:])
    else:
        # Get user input from standard input
        user_input = input("Enter the text to be URL encoded: ")
    
    # Display the encoded versions of the user input
    display_encoded_versions(user_input)

if __name__ == "__main__":
    main()
