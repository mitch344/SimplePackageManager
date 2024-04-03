# Simple Package Manager

This is a simple package manager template that can be used as a starting point for building your own package management system. It provides basic functionality for managing packages, including installing, uninstalling, updating, and searching for packages.

## Features

- Search for packages in package sources
- Install packages from local files or remote URLs
- Verify package integrity using hash comparison
- Uninstall packages
- Update packages to the latest version
- List installed packages
- Display detailed information about a specific package
- Add package sources

## Getting Started

1. Clone the repository

2. Navigate to the project directory:
```cd simple-package-manager```

3. Run the package manager:

```python package_manager.py```

## Usage

The package manager provides the following commands:

- `search <query>`: Search for packages matching the given query string.
- `install <package_name>`: Install a package by its name.
- `uninstall <package_name>`: Uninstall a package by its name.
- `update <package_name>`: Update a package to the latest version.
- `list`: List all installed packages.
- `info <package_name>`: Display detailed information about a specific package.
- `sources`: View the list of package sources.
- `add-source <source_url_or_path>`: Add a new package source.

## Configuration

The package manager uses the following configuration files:

- `sources.json`: Contains a list of package sources, which can be local file paths or remote URLs.
- `installed_packages.json`: Stores information about installed packages.

## Contributing

Contributions are welcome! If you have any ideas, suggestions, or bug reports, please open an issue or submit a pull request.

## License

This project is open-source and available under the MIT License.

## Acknowledgements

This package manager was created as a simple tool without any specific direction or purpose. It can be used as a starting point for building more advanced package management systems.