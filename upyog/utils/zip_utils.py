from upyog.imports import *

def zip_folder(path: PathLike):
    path = Path(path)
    assert path.is_dir()
    assert path.exists()

    return shutil.make_archive(path, "zip", path)

def compose_files_into_zip_archive(
    files: List[PathLike],
    out_dir: PathLike,
    zip_name: str = "Archive",
):
    import tempfile

    out_dir = Path(out_dir)
    out_dir.mkdir(exist_ok=True)

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        for file in files:
            shutil.copy(file, tmp_path)

        archive_path = shutil.make_archive(str(out_dir / zip_name), "zip", tmp_path)

    return archive_path
