import shutil
import tarfile
import tempfile

from collections import defaultdict
from pathlib import Path
from tqdm import tqdm
from upyog.cli import call_parse, P
from upyog.os import get_files, load_json


@call_parse  # Tool to create this func into a CLI program
def extract_and_organize_tarfiles(
    root_dir: P("Path to the root directory with the `.tar` files"), # type: ignore
    output_dir: P("(Optional) Path to the output dir. If not provided, outputs are saved in `root_dir`") = None, # type: ignore
    extract_structure: P("(Optional) Path to a JSON file that captures the output structure. If not provided, we attempt to detect it automatically") = None, # type: ignore
):
    """
    FIXME: Add general description of the program (this will be displayed in the terminal CLI)
    We must provide an example of an `extract_structure` JSON file
    """
    # FIXME: Add docstring, with example of `extract_structure`
    root_dir = Path(root_dir)
    output_dir = Path(output_dir)

    if extract_structure:
        extract_structure = load_json(extract_structure)

    if output_dir is None:
        output_dir = root_dir

    print("Starting extraction and organization process...")

    # Counter for processed files
    tar_files = get_files(root_dir, extensions=[".tar"])
    total_files = len(tar_files)
    processed_files = 0

    print(f"Found {total_files} .tar files to process.")

    # Loop through all .tar files
    progress_bar = tqdm(tar_files, "Extracting .tar files", unit="file")
    for tar_file in progress_bar:
        processed_files += 1
        progress_bar.set_description(f"Extracting {processed_files} / {total_files}: {tar_file.name}")

        # Extract all files to a temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            with tarfile.open(tar_file, "r") as tar:
                tar.extractall(temp_dir)
            temp_path = Path(temp_dir)

            # FIXME: We should run `detect_structure` ONLY ONCE. It's safe to assume
            # that all the tarfiles will have the same output structure. It's wasteful
            # to keep running it in a loop, especially since we may be extracting 1000+ tarfiles
            # Once we detect it, we should print it for the user
            if extract_structure is None:
                extract_structure = detect_structure(temp_path)

            # Create directories based on the extract structure
            for subdir in extract_structure.values():
                output_dir.joinpath(subdir).mkdir(parents=True, exist_ok=True)

            # Move files to appropriate directories
            for file_path in temp_path.iterdir():
                if file_path.is_file():
                    # Ensure we capture '.url.txt' like cases as a single suffix
                    suffix = "".join(file_path.suffixes)

                    if suffix in extract_structure:
                        subdir = extract_structure[suffix]
                        shutil.move(
                            str(file_path),
                            str(output_dir.joinpath(subdir, file_path.name)),
                        )
                    # FIXME: Should we raise a warning here if we find an unexpected suffix? I think so...

    print("Extraction and organization complete.")
    print("-----------------------------------")
    print(f"Total .tar files processed: {processed_files}")
    for subdir in extract_structure.values():
        print(
            f"Total {subdir} files: {len(list(output_dir.joinpath(subdir).glob('*')))}"
        )


def detect_structure(temp_path: Path) -> dict:
    structure = defaultdict(set)
    for file_path in temp_path.iterdir():
        if file_path.is_file():
            suffix = "".join(file_path.suffixes)
            structure[suffix].add(file_path.stem)

    # Create a mapping of suffixes to subdirectories
    extract_structure = {}
    for suffix, stems in structure.items():
        if len(stems) == len(list(temp_path.iterdir())):
            subdir = f"{suffix[1:]}_files"
            extract_structure[suffix] = subdir

    return extract_structure
