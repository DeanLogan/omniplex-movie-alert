import os
import shutil
import subprocess

def create_package_folder():
    # Create package folder
    os.makedirs("package", exist_ok=True)

def install_requirements():
    # Install requirements into package folder
    subprocess.run(["pip", "install", "-r", "requirements.txt", "-t", "package"])

def copy_files():
    # Copy movie_alerts.py.py and aws_storage.py into package folder
    shutil.copy("movie_alerts.py", "package")
    shutil.copy("aws_storage.py", "package")

    # Copy .env into package folder
    shutil.copy(".env", "package")
    
    # Copy geckodriver into package folder
    shutil.copy("geckodriver", "package")
    
    # Make geckodriver executable
    os.chmod("package/geckodriver", 0o755)

def copy_files_test():
    shutil.copy("main.py", "package")

    # Copy .env into package folder
    shutil.copy(".env", "package")
    
    # Copy geckodriver into package folder
    shutil.copy("geckodriver", "package")
    
    # Make geckodriver executable
    os.chmod("package/geckodriver", 0o755)

def create_zip():
    # Save current directory
    original_dir = os.getcwd()

    # Change directory to 'package'
    os.chdir('package')

    # Create functions.zip with contents of package folder
    shutil.make_archive("function", "zip", ".")

    # Move the zip file to the original directory
    shutil.move("function.zip", original_dir)

    # Change back to original directory
    os.chdir(original_dir)

if __name__ == "__main__":
    create_package_folder()
    install_requirements()
    copy_files()
    create_zip()
