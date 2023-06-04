import os
import shutil
import py7zr
import tempfile

def generate_modpack(name, version, mods_dir, output_dir):
    # Create a new directory for the modpack
    modpack_dir = os.path.join(tempfile.gettempdir(), name)
    if not os.path.exists(modpack_dir):
        os.mkdir(modpack_dir)

    # Copy all files and directories from the mods directory to the modpack directory
    for item in os.listdir(mods_dir):
        item_path = os.path.join(mods_dir, item)
        if os.path.isfile(item_path):
            shutil.copy2(item_path, modpack_dir)
        elif os.path.isdir(item_path):
            shutil.copytree(item_path, os.path.join(modpack_dir, item))

    # Compress the modpack directory into a 7z file
    zip_file = os.path.join(output_dir, f'{name}-{version}.7z')
    with py7zr.SevenZipFile(zip_file, 'w') as archive:
        archive.writeall(modpack_dir, os.path.basename(modpack_dir))

    # Remove the modpack directory
    shutil.rmtree(modpack_dir)

    return zip_file
