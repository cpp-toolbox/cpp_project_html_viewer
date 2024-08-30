import os
import shutil
import argparse
from collections import defaultdict


def create_html_file(file_path, base_output_dir, base_source_dir):
    """Create an HTML file from a source code file."""
    with open(file_path, 'r') as file:
        content = file.read()

    # Escape HTML special characters
    content = content.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;').replace(
        "'", '&#039;')

    # Determine relative path from the source base directory
    rel_path = os.path.relpath(file_path, base_source_dir)

    # Construct output file path within the output directory
    output_file = os.path.join(base_output_dir, rel_path + '.html')
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    # Write the HTML file
    with open(output_file, 'w') as out_file:
        out_file.write(f'{content}')

    print(f'Processed {file_path} -> {output_file}')


def build_file_structure(base_source_dir):
    """Build a nested dictionary representing the directory structure."""
    file_structure = defaultdict(lambda: {'directories': [], 'files': []})
    for root, dirs, files in os.walk(base_source_dir):
        # Determine the relative path from the base directory
        rel_path = os.path.relpath(root, base_source_dir)
        if rel_path == '.':
            # Set root directory's relative path to empty string
            rel_path = ''

        # Collect files and directories
        file_structure[rel_path]['files'] = [f for f in files if f.endswith(('.cpp', '.hpp', '.h', '.c'))]
        file_structure[rel_path]['directories'] = dirs

    return file_structure


def create_index_page(base_output_dir, file_structure):
    """Create an index HTML page with a directory viewer."""
    index_path = os.path.join(base_output_dir, 'index.html')

    # Write the HTML file
    with open(index_path, 'w') as index_file:
        index_file.write('''
<!DOCTYPE html>
<html>
<head>
    <title>Code Viewer</title>
    <link rel="stylesheet" type="text/css" href="styles.css">
    <script src="scripts.js" defer></script>
</head>
<body>
    <div id="fileList">
        <ul>
''')

        def write_file_structure(structure, path=''):
            """Recursively write the file structure to HTML starting from the given path."""
            if path in structure:
                directories = structure[path].get('directories', [])
                files = structure[path].get('files', [])

                # Write the directory name as an <li> item
                if path or not directories:
                    index_file.write(f'<li>{os.path.basename(path) if path else "Root"}<ul>')

                # Process directories first
                for dir in directories:
                    dir_path = os.path.join(path, dir)
                    write_file_structure(structure, dir_path)

                # Process files
                for file in files:
                    file_url = os.path.join(path, file + '.html')
                    index_file.write(f'<li><a href="#" data-url="{file_url}">{file}</a></li>')

                if path or not directories:
                    index_file.write('</ul></li>')

        # Start writing the file structure
        write_file_structure(file_structure, '')

        index_file.write('''
        </ul>
    </div>
    <div id="resizer"></div>
    <div id="contentArea"></div>
</body>
</html>
''')
    print(f'Index page created at {index_path}')


def copy_static_files(script_root, output_dir):
    """Copy CSS, JS files, and the script itself from the script root to the output directory."""
    files_to_copy = ['styles.css', 'scripts.js', 'generate_html.py']
    for file_name in files_to_copy:
        src_file = os.path.join(script_root, file_name)
        dest_file = os.path.join(output_dir, file_name)
        if os.path.exists(src_file):
            shutil.copy(src_file, dest_file)
            print(f'Copied {src_file} to {dest_file}')
        else:
            print(f'{src_file} does not exist and was not copied.')


def create_zip_archive(output_dir):
    """Create a zip archive of the output directory."""
    shutil.make_archive(output_dir, 'zip', output_dir)
    print(f'Created zip archive {output_dir}.zip')


def main():
    parser = argparse.ArgumentParser(description="Generate HTML files for code browsing.")
    parser.add_argument('source_dir', help="Source directory containing code files.")
    parser.add_argument('output_dir', help="Output directory for HTML files.")
    parser.add_argument('--zip', action='store_true', help="Create a zip archive of the output directory.")
    args = parser.parse_args()

    base_source_dir = args.source_dir
    base_output_dir = args.output_dir
    script_root = os.path.dirname(os.path.abspath(__file__))

    os.makedirs(base_output_dir, exist_ok=True)

    print(f'Starting to process files in {base_source_dir}')

    file_structure = build_file_structure(base_source_dir)

    for dir_path, content in file_structure.items():
        for file in content.get('files', []):
            file_path = os.path.join(base_source_dir, dir_path, file)
            create_html_file(file_path, base_output_dir, base_source_dir)

    create_index_page(base_output_dir, file_structure)

    # Copy static files
    copy_static_files(script_root, base_output_dir)

    if args.zip:
        create_zip_archive(base_output_dir)

    print('Processing complete.')


if __name__ == "__main__":
    main()
