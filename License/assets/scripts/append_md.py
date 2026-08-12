import os
import sys

# python append_md.py /path/to/folder

def append_markdown_files(folder_path, output_name="APPENDED_FILES.md"):
    md_files = sorted(
        f for f in os.listdir(folder_path) if f.lower().endswith(".md")
    )

    total = len(md_files)
    print(f"Found {total} markdown files.")

    output_path = os.path.join(folder_path, output_name)

    with open(output_path, "w", encoding="utf-8") as out:
        for idx, filename in enumerate(md_files, start=1):
            file_path = os.path.join(folder_path, filename)
            print(f"[{idx}/{total}] Processing: {filename}")

            out.write(f"\n\n---\n\n# FILE: {filename}\n\n")

            with open(file_path, "r", encoding="utf-8") as f:
                out.write(f.read())

    print(f"\nDone. Output written to: {output_path}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python append_md.py <folder_path>")
        sys.exit(1)

    append_markdown_files(sys.argv[1])
