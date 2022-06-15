# Change Log

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/) and this project adheres to [Semantic Versioning](https://semver.org/)

## [1.2.0] 2022-06-15

### Added

- `write_to_dataset` function to utils module to write to a dataset
- Added MultilineStringParameterType

## [1.1.1] 2022-05-16

### Fixed

- DatasetParameterType provides labels now
- DatasetParameterType returns combined dataset ID now

## [1.1.0] 2022-05-04

### Added

- DatasetParameterType - for selecting DI datasets
- GraphParameterType - for selecting DP Knowledge Graphs

### Fixed

- Plugin discovery had an issue that plugins that are in the root module of a package have not been re-discovered on the second call. 
- Boolean values are formatted lower case in order to conform to xsd:bool.

## [1.0.0] 2022-04-01

### Changed

- release 1.0.0

## [0.0.13] 2022-03-21

### Changed

- python >= 3.7 dependency
- examples dev-dependency
- update dependencies

## [0.0.12] 2022-03-21

### Added

- `autocompletion_enabled` method to ParameterType class to signal whether autocompletion should be enabled.

### Changed

- downgrade needed python version to 3.7+

## [0.0.11] 2022-03-16

### Fixed

- Fixed `discover_plugins_in_module`: Need to reload modules that have been imported already.

## [0.0.10] 2022-03-16

### Added

- Support for custom plugin parameter types
- Enumeration parameter type

## [0.0.9] 2022-03-09

### Fixed

- Only return parameters for user-defined init methods

## [0.0.8] 2022-03-04

### Added

- Added constants for common categories.
- Added plugin APIs for logging and retrieving configuration.

## [0.0.7] 2022-03-02

### Added

- parameter type validation and matching to internal types

## [0.0.6] 2022-02-28

### Added

- optional plugin identifier

### Changed

- plugin discovery no for multiple base moduls of a prefix

## [0.0.2] 2022-02-25

### Added

- parameter and description annotation of plugins
- discovery methods of plugins

## [0.0.1] 2022-02-23

### Added

- WorkflowPlugin v1
- initial project with Taskfile.yml and pre-commit hooks

