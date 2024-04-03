from PackageManager import PackageManager
import argparse

class PackageManagerCLI:
    def __init__(self):
        self.manager = PackageManager()
        self.parser = argparse.ArgumentParser(
            description='PackageManagerCLI'
        )
        self._add_arguments()
        
    def _add_arguments(self):
        self.parser.add_argument('-i', '--install', metavar='PACKAGE', help='Install a package by name')
        self.parser.add_argument('-u', '--uninstall', metavar='PACKAGE', help='Uninstall a package by name')
        self.parser.add_argument('-up', '--update', metavar='PACKAGE', help='Update a package by name')
        self.parser.add_argument('-l', '--list', action='store_true', help='List installed packages')
        self.parser.add_argument('-v', '--view-sources', action='store_true', help='View available sources')
        self.parser.add_argument('-s', '--search', metavar='QUERY', help='Search for a package by name')
        self.parser.add_argument('-d', '--details', metavar='PACKAGE', help='Display details of a package by name')
        self.parser.add_argument('-a', '--add-source', metavar='SOURCE', help='Add a new source URL or file path')

    def run(self):
        args = self.parser.parse_args()

        if args.install:
            package_name = args.install
            package_info = self.manager.search_package_in_sources(package_name)
            if package_info:
                self.manager.download_and_install_package(package_info)
            else:
                print(f"No package found with name: {package_name}")
        elif args.uninstall:
            package_name = args.uninstall
            self.manager.uninstall_package(package_name)
        elif args.update:
            package_name = args.update
            self.manager.update_package(package_name)
        elif args.list:
            self.manager.list_installed_packages()
        elif args.view_sources:
            self.manager.view_sources()
        elif args.search:
            self.manager.search_package_strings(args.search)
        elif args.details:
            package_name = args.details
            self.manager.display_package_details(package_name)
        elif args.add_source:
            source_url_or_path = args.add_source
            self.manager.add_source(source_url_or_path)
        else:
            self.parser.print_help()

if __name__ == "__main__":
    cli = PackageManagerCLI()
    cli.run()