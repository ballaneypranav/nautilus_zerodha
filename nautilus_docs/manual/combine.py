import os

def combine_files_in_directory(output_filename="combined.md"):
    """
    Recursively finds all .md and .txt files in the current directory
    and its subdirectories, and combines them into a single file.

    The format for each included file is:
    file path:
    [file contents]
    ---
    """
    # A list to hold the paths of all the files to be combined.
    files_to_combine = []

    # Recursively walk through the directory structure starting from the current directory.
    for dirpath, _, filenames in os.walk('.'):
        for filename in filenames:
            # Check if the file has a .md or .txt extension.
            if filename.endswith('.md') or filename.endswith('.txt'):
                # Construct the full, normalized path of the file.
                full_path = os.path.join(dirpath, filename)
                
                # IMPORTANT: Exclude the output file itself to prevent it from
                # being included in subsequent runs of the script.
                if os.path.normpath(full_path) != os.path.normpath(output_filename):
                    files_to_combine.append(full_path)

    # Open the output file in write mode with UTF-8 encoding.
    try:
        with open(output_filename, 'w', encoding='utf-8') as outfile:
            print(f"Creating output file: {output_filename}")
            
            # Process each file found.
            for i, filepath in enumerate(files_to_combine):
                print(f"Processing: {filepath}")
                
                # Write the header with the file path.
                outfile.write(f"file path: {filepath}\n")
                
                try:
                    # Open the source file in read mode.
                    with open(filepath, 'r', encoding='utf-8', errors='ignore') as infile:
                        # Write the contents of the source file to the output file.
                        outfile.write(infile.read())
                except Exception as e:
                    # If a file can't be read, write an error message instead.
                    outfile.write(f"\n[Error reading file: {e}]\n")

                # Add a separator between files for clarity, but not after the last file.
                if i < len(files_to_combine) - 1:
                    outfile.write("\n\n---\n\n")

        print("\nOperation complete.")
        print(f"Successfully combined {len(files_to_combine)} files into '{output_filename}'.")

    except IOError as e:
        print(f"\nError: Could not write to output file '{output_filename}'.")
        print(f"Reason: {e}")

if __name__ == '__main__':
    combine_files_in_directory()
