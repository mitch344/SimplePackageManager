import json
import os
from zipfile import ZipFile
import tarfile
import datetime
import shutil
import subprocess
import requests
import hashlib

class PackageManager:
    def __init__(self):
        self.installed_packages = self.load_installed_packages()

    def search_package_in_sources(self, package_name):
        for source in self.load_sources():
            packages = self.load_packages(source)
            if package_name in packages:
                return packages[package_name]
        return None

    def generate_hash(self, file_path):
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    def verify_hash(self, file_path, expected_hash):
        calculated_hash = self.generate_hash(file_path)
        return calculated_hash == expected_hash

    def view_sources(self):
        try:
            with open('sources.json', 'r') as f:
                data = json.load(f)
                sources = data.get('sources', [])
                for source in sources:
                    print(source)
        except FileNotFoundError:
            print("Source file not found.")
        except json.JSONDecodeError:
            print("Error decoding JSON from source file.")

    def search_package_strings(self, query):
        found_packages = []

        for source in self.load_sources():
            packages = self.load_packages(source)
            for package in packages.values():
                if query.lower() in package['name'].lower():
                    found_packages.append(package)

        if found_packages:
            for package in found_packages:
                print(f"{package['name']} - {package.get('description', 'No description available')} (Version: {package.get('version', 'N/A')})")
        else:
            print(f"No package found for query: {query}")

    def load_installed_packages(self):
        try:
            with open('installed_packages.json') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def save_installed_packages(self):
        with open('installed_packages.json', 'w') as f:
            json.dump(self.installed_packages, f, indent=4)

    def download_package(self, url, destination_directory):
        if os.path.isfile(url):
            file_name = os.path.basename(url)
            destination_path = os.path.join(destination_directory, file_name)
            shutil.copy(url, destination_path)
            return destination_path
        else:
            file_name = url.split('/')[-1]
            destination_path = os.path.join(destination_directory, file_name)

            response = requests.get(url, stream=True)
            response.raise_for_status()

            with open(destination_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)
            
            return destination_path

    def load_sources(self):
        with open('sources.json') as f:
            return json.load(f)['sources']

    def load_packages(self, source):
        if source.startswith('http'):
            try:
                response = requests.get(source)
                response.raise_for_status()
                data = response.json()
                packages = data.get('packages', [])
                packages_dict = {pkg['name']: pkg for pkg in packages}
                return packages_dict
            except (requests.exceptions.RequestException, json.JSONDecodeError) as e:
                print(f"Failed to fetch packages from {source} due to: {str(e)}")
                return {}
        else:
            try:
                with open(source) as f:
                    data = json.load(f)
                    packages = data.get('packages', [])
                    packages_dict = {pkg['name']: pkg for pkg in packages}
                    return packages_dict
            except json.JSONDecodeError as e:
                print(f"Failed to load package data from source {source} due to: {str(e)}")
                return {}
            
    def download_and_install_package(self, package_info):
        if package_info['name'] in self.installed_packages:
            print(f"The package '{package_info['name']}' is already installed.")
            return

        try:
            package_file_path = self.download_package(package_info['downloadURL'], os.getcwd())

            # Verify hash
            if 'hash' in package_info:
                expected_hash = package_info['hash']
                if not self.verify_hash(package_file_path, expected_hash):
                    print(f"Hash mismatch for package '{package_info['name']}'. Aborting installation.")
                    return
            else:
                print(f"No hash provided for package '{package_info['name']}'. Skipping hash verification.")

        except KeyError:
            print(f"Package '{package_info['name']}' does not have a valid download URL.")
            return
        except Exception as e:
            print(f"An error occurred while downloading package '{package_info['name']}': {e}")
            return

        self.extract_and_install_package(package_info, package_file_path)
        self.cleanup_and_save_package(package_info, package_file_path)

    def extract_and_install_package(self, package, package_file_path):
        filename = os.path.basename(package_file_path)
        file_extension = os.path.splitext(filename)[-1]
        file_name_without_extension = os.path.splitext(filename)[0]

        print(f'Extracting {package["name"]}...')
        if file_extension == ".gz":
            with tarfile.open(package_file_path) as tar:
                tar.extractall()
        elif file_extension == ".zip":
            with ZipFile(package_file_path, 'r') as zipf:
                zipf.extractall()

        self.run_install_script(package, file_name_without_extension)

    def run_install_script(self, package, file_name_without_extension):
        pkg_json_path = os.path.join(file_name_without_extension, "package.json")

        if os.path.isfile(pkg_json_path):
            with open(pkg_json_path, 'r') as pkg_file:
                pkg_meta = json.load(pkg_file)
            install_script_data = pkg_meta.get('install_script', {})
            if install_script_data and 'script' in install_script_data and 'type' in install_script_data:
                install_script_name = install_script_data.get('script')
                install_script_type = install_script_data.get('type')

                install_script_path = os.path.join(file_name_without_extension, install_script_name)
                if os.path.isfile(install_script_path):
                    print(f'Running install script for {package["name"]}...')
                    if install_script_type == 'python':
                        try:
                            subprocess.run(["python3", install_script_path])
                        except subprocess.CalledProcessError:
                            try:
                                subprocess.run(["python", install_script_path])
                            except subprocess.CalledProcessError as e:
                                print(f'Install script failed for {package["name"]}. Error: {e}')
                    elif install_script_type == 'bash':
                        subprocess.run(["bash", install_script_path])
                    elif install_script_type == 'powershell':
                        subprocess.run(["powershell", install_script_path])
                    else:
                        print(f'Unsupported script type for {package["name"]}. Skipping install script.')
                else:
                    print(f'Install script not found for {package["name"]}. Skipping install script.')
            else:
                print(f'No install script found for {package["name"]}.')
        else:
            print(f"'package.json' not found in directory: {file_name_without_extension}. Skipping install script.")

    def cleanup_and_save_package(self, package, package_file_path):
        file_name_without_extension = os.path.splitext(os.path.basename(package_file_path))[0]

        os.remove(package_file_path)
        shutil.rmtree(file_name_without_extension)

        print(f'Installing {package["name"]}...')
        package["install_date"] = datetime.datetime.now().isoformat()
        self.installed_packages[package["name"]] = package
        self.save_installed_packages()
        print(f'Successfully installed {package["name"]}!')

    def list_installed_packages(self):
        if not self.installed_packages:
            print("No packages are currently installed.")
            return

        print("Installed packages:")
        for package_name, package_details in self.installed_packages.items():
            print(f"- {package_name} ({package_details['version']}) installed on {package_details['install_date']}")

    def uninstall_package(self, package_name):
        if package_name in self.installed_packages:
            del self.installed_packages[package_name]
            self.save_installed_packages()
            print(f"Successfully uninstalled {package_name}!")
        else:
            print(f"Package {package_name} is not installed.")

    def update_package(self, package_name):
        if package_name in self.installed_packages:
            package_info = self.search_package_in_sources(package_name)
            if package_info:
                self.uninstall_package(package_name)
                self.download_and_install_package(package_info)
            else:
                print(f"No package found with name: {package_name}")
        else:
            print(f"Package {package_name} is not installed.")

    def display_package_details(self, package_name):
        if package_name in self.installed_packages:
            package_details = self.installed_packages[package_name]
            print(f"Details for package {package_name}:")
            print(f"  Name: {package_details['name']}")
            print(f"  Version: {package_details['version']}")
            print(f"  Install Date: {package_details['install_date']}")
            print(f"  Description: {package_details.get('description', 'No description available')}")
        else:
            print(f"Package {package_name} is not installed.")

    def add_source(self, source_url_or_path):
        sources = self.load_sources()
        if source_url_or_path not in sources:
            sources.append(source_url_or_path)
            with open('sources.json', 'w') as f:
                json.dump({'sources': sources}, f, indent=4)
            print(f"Successfully added source: {source_url_or_path}")
        else:
            print(f"Source {source_url_or_path} already exists.")
