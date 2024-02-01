import argparse
import re

def extract_env_variables(file_path):
    pattern = re.compile(r'\$\{([^}:]+)(?::-([^}]*))?\}')
    env_vars = {}
    with open(file_path, 'r') as file:
        content = file.read()
        matches = pattern.findall(content)
        for match in matches:
            env_vars[match[0]] = match[1]
    return env_vars

def interactive_mode(env_vars):
    user_values = {}
    for var, default in env_vars.items():
        user_input = input(f"{var} [{default}]: ") or default
        user_values[var] = user_input
    return user_values

def write_to_env_file(user_values, output_file):
    with open(output_file, 'w') as file:
        for var, value in user_values.items():
            file.write(f"{var}={value}\n")

def main():
    parser = argparse.ArgumentParser(description="Extract environment variables from a Docker Compose file.")
    parser.add_argument('-f', '--inputfile', type=str, help='Path to the Docker Compose file', required=True)
    parser.add_argument('-i', '--interactive', action='store_true', help='Interactive mode')
    args = parser.parse_args()

    env_vars = extract_env_variables(args.inputfile)

    if args.interactive:
        user_values = interactive_mode(env_vars)
        write_to_env_file(user_values, 'output.env')
    else:
        for var, default in env_vars.items():
            print(f"{var}={default}")

if __name__ == "__main__":
    main()
