from upyog.imports import *
from upyog.os.read_files import *
from upyog.utils import *
from upyog.cli import Param as P, call_parse


__all__ = ["move_files", "cleanup_duplicates"]


@call_parse
def move_files(
    i: P("Input folders to move the files from", str, nargs="+", metavar="INP") = None,
    o: P("Path to the output folders", str) = None,
    move: P("Move files (desctructively)", action="store_true") = False,
):
    """
            --------- FILE MOVER ---------

    Move files from an arbitrary number of input folders to a _single_ output folder.

    The input folders are scanned recursively.
    If the output folder doesn't exist, it is created
    """
    recurse = True
    files = flatten([get_files(p, recurse=recurse) for p in i])
    out_dir = Path(o)
    if not out_dir.exists():
        rich.print(f"Creating output folder: {out_dir}")
        out_dir.mkdir(exist_ok=True, parents=True)

    mover = shutil.move if move else shutil.copy

    for file in track(files, "Moving Files..."):
        mover(str(file), str(out_dir))


@call_parse
def remove_duplicates_from_folder(
    i: P("Single input folder that is to be cleaned up", str) = None,
    t: P(
        "An arbitrary number of target folders that contain duplicate files that are to be removed from the input folder `--i`",
        str,
        nargs="+",
    ) = None,
):
    """
            --------- DUPLICATE REMOVER ---------

    This program scans the _names_ of the files in the input and target folders
    recursively, and removes all the files from the `input` folder that exist in
    `target` folders

    If input folder has the following files:
    ├── input-folder
    │   ├── file1.jpg
    │   ├── file2.jpg
    │   └── file3.jpg

    And the target folder(s) have the following files:
    ├── target-folder-1
    │   ├── file1.jpg
    │   ├── other-random-file-1.jpg

    ├── target-folder-2
    │   ├── file2.jpg
    │   ├── other-random-file-2.jpg

    Using this program would remove `file1.jpg` and `file2.jpg` from the input folders

    Usage:
    ------

    remove-duplicates-from-folder
        --i input-folder
        --t target-folder-1   target-folder-2   ...
    """
    cleanup_path = Path(i)
    target_paths = [Path(p) for p in t]

    target_fnames = flatten([get_files(path, recurse=True) for path in target_paths])
    target_fnames = [f.stem for f in target_fnames]

    cleanup_files = get_files(cleanup_path, recurse=True)
    cleanup_fnames = [f.stem for f in cleanup_files]

    fnames_to_delete = set.intersection(set(cleanup_fnames), set(target_fnames))

    counter = 0
    for f in track(cleanup_files, "Scanning Files..."):
        if f.stem in fnames_to_delete:
            print(f"Deleting {f.name}")
            counter += 1
            f.unlink()

    print(f"Deleted {counter} files")


@call_parse
def add_parent_folder_name(
    # i: P("Input folder(s) and files", str, nargs="+"),
    i: P("Input folder", str),
    sep: P("Separator", str) = "_",
):
    files = get_files(i, recurse=True)
    for file in tqdm(files):
        if file.is_file():
            new_name = file.with_name(f"{file.parent.name}{sep}{file.name}")
            print(f"Renamed: {file.name} => {new_name}")
            file.rename(new_name)


@call_parse
def find_common_files_between_folders(
    i: P("Input folders", str, nargs="+"),
    include_parent: P("Include name of parent folder?", bool) = False,
):
    """
            --------- COMMON FILES DETECTOR ---------

    This program scans an arbitray number of input folders and prints the
    number of common elements between these folders.

    Say we have the following input folders:
    ├── input-folder-1
    │   ├── file1.jpg
    │   ├── file2.jpg
    │   └── file3.jpg
    ├
    ├── input-folder-2
    │   ├── file3.jpg
    │   ├── file4.jpg

    Where there's one common file between input-folder-1 and 2, the result
    is as follows:

        {
            "input-folder-1 (3)": {
                "input-folder-2 (2)": 1
            },
            "input-folder-2 (2)": {
                "input-folder-1 (3)": 1
            }
        }

    Note that the number of files in each folder is added in brackets.

    Usage:
    ------

    find-common-files-between-folders  input-folder-1 input-folder-2

    """
    assert i
    input_folders = i

    def folder_with_parent(f, files=None):
        f = Path(f)
        result = f"{f.parent.name} / {f.name}" if include_parent else f.name
        return f"{result} ({len(files)})" if files is not None else result

    folder2files = {folder: get_image_files(folder) for folder in input_folders}
    folder2files = {
        folder: [f.name for f in files] for folder, files in folder2files.items()
    }
    folder2files = {folder_with_parent(k, v): v for k, v in folder2files.items()}

    # folder_names = [folder_with_parent(f) for f in folder2files.keys()]
    # results = dict.fromkeys(folder_names)
    results = dict.fromkeys(folder2files)
    for f1 in folder2files.keys():
        f1_common = {}
        for f2, files in folder2files.items():
            if f2 == f1:
                continue

            common = set(folder2files[f1]).intersection(files)
            f1_common[f2] = len(common)

        results[f1] = f1_common

    rich.print_json(data=results)
    return results


@call_parse
def print_folder_distribution(
    parent_folders: P("Parent folders", str, nargs="+")
) -> Dict[str, pd.DataFrame]:
    """
    Prints the number of files inside each given `parent_folders`.
    """
    results = {}

    for folder in parent_folders:
        freq = {}
        folder = Path(folder)
        for subdir in sorted(folder.list_dirs()):
            freq[subdir.name] = len(get_files(subdir, recurse=True))

        # rich.print(f"----- {folder} -----\n")
        # rich.print_json(data=freq)
        # breakpoint()

        freq = pd.DataFrame([freq]).T.reset_index()
        freq.columns = ["Sub Folders", "Frequency"]
        freq = print_df(freq, title = folder.name)

        results[folder.name] = freq

    return results
