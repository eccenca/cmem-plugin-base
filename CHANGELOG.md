<!-- markdownlint-disable MD012 MD013 MD024 MD033 -->
# Change Log

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/) and this project adheres to [Semantic Versioning](https://semver.org/)

## [Unreleased]

TODO: add at least one Added, Changed, Deprecated, Removed, Fixed or Security section


## [4.12.1] 2025-06-24 - shipped with DI v25.2.0

### Fixed

- Re-add missing entryPath attribute in FileEntitySchema


## [4.12.0] 2025-06-24

### Added

- RDF Quad entity type (CMEM-6243).


## [4.11.0] 2025-06-19

### Added

- `File` entities: add `entry_path` attribute and `read_stream` method

### Changed

- dependency cmem-cmempy >=25.2.0
- dependency python-ulid ^3.0.0


## [4.10.2] 2025-05-15 - shipped with DI v25.1.1

### Fixed

- Resolved an issue in `FileEntitySchema` for empty MIME types (CMEM-6623).


## [4.10.1] 2025-05-08

### Fixed

- Adapted FileEntitySchema so it can be used with datasets (CMEM-6615).


## [4.10.0] 2025-03-31 - shipped with DI v25.1.0

### Added

- Custom actions for Workflow plugins (CMEM-5576)
- Added explicit_schema parameter to FlexibleOutputSchema (CMEM-6444)

### Fixed

- Check if passwords can be decrypted, i.e., if the key is valid (CMEM-5932)


## [4.9.0] 2025-02-20

### Added

- TypedEntitySchema - A custom entity schema that holds entities of a specific type (e.g. files)
- FileEntitySchema - Entity schema that holds a collection of files
- testing module with different context classes for tests:
  - TestUserContext
  - TestPluginContext
  - TestTaskContext
  - TestExecutionContext
  - TestSystemContext


## [4.8.0] 2024-09-12 - shipped with DI v24.3.0

### Added

- The execution report also contains sample entities now (CMEM-3664):
  - For plugins that don't update the execution report by themselves, DataIntegration will automatically add sample entities.
  - Plugins that update the execution report can add sample entities to `ExecutionReport.sample_entities`.


## [4.7.0] 2024-06-13 - shipped with DI v24.2.0

### Added

- Added workflow status to execution context. This can be used to check if the workflow task has been cancelled by the user: `context.workflow.status() != "Canceling"`
- Added workflow identifier to execution context: `context.workflow.workflow_id()`
- Added package_name to PluginDescription. This is read by DataIntegration and part of the plugin JSON.


## [4.6.0] 2024-06-07

### Fixed

- discover_plugins function to make sure all package modules are re-imported freshly


## [4.5.0] 2024-01-10 - shipped with DI v24.1.0

### Added

- util method to generate entities from python dict | list object
- parameter sub_schemata in EntitySchema to capture nested entity schemata

### Changed

- renamed EntityPath parameter is_uri to is_relation
- renamed EntitySchema parameter sub_path to path_to_root


## [4.4.0] 2023-11-24

### Added

- capabilities for hierarchical entities as input and output of workflow tasks


## [4.3.0] 2023-10-20 - shipped with DI v23.3.0

### Added

- Workflow plugins can specify their input and output ports now. 
- `ResourceParameterType` - for selecting DI dataset resources
- `CodeParameterType` - which supports various different code languages

### Changed

- dependency to cmempy >= 23.3.0


## [4.2.0] 2023-09-04

### Added

- Optional `plugin_icon` parameter in a plugin description to specify a custom plugin icon as data URL.


## [4.1.0] 2023-07-12 - shipped with DI v23.2.0

### Changed

- use `post_resource` api in `write_to_dataset` function to update dataset file resource
- use cmempy 23.2


## [4.0.0] 2023-07-03

### Changed

- upgrade dependencies
- enforce Python 3.11


## [3.0.0] 2023-02-20 - shipped with DI v23.1

### Added

- Autocompleted parameter types may declare dependent parameters.
    For instance, a parameter 'city' may declare that its completed values depend on another parameter 'country':
    ```
    class CityParameterType(StringParameterType):
        autocompletion_depends_on_parameters: list[str] = ["country"]

        def autocomplete(self,
                         query_terms: list[str],
                         depend_on_parameter_values: list[Any],
                         context: PluginContext) -> list[Autocompletion]:
           # 'depend_on_parameter_values' contains the value of the country parameter
           return ...
    ```

- Password plugin parameter type.
    Passwords will be encrypted in the backend and not shown to users:
    ```
    @Plugin(label="My Plugin")
    class MyTestPlugin(TransformPlugin):

    def __init__(self, password: Password):
        self.password = password
  
    # The decrypted password can be accessed using:
    self.password.decrypt()
    ```

- Custom parameter types can be registered. See implementation of PasswordParameterType for an example.

### Migration Notes

The signature of the autocomplete function has been changed.
All autocomplete implementations need to be updated to the following signature:

`def autocomplete(self, query_terms: list[str], depend_on_parameter_values: list[Any], context: PluginContext) -> list[Autocompletion]`

Parameters using the old signature will continue to work for one release, but a warning will be printed in the log.

The same applies to the label function that has been updated to the following signature:

`def label(self, value: str, depend_on_parameter_values: list[Any], context: PluginContext) -> Optional[str]`


## [2.1.0] 2022-07-19 - shipped with DI v22.2

### Changed

- DatasetParameterType: to use user context


## [2.0.1] 2022-07-12

### Fixed

- ChoiceParameterType: to_string and from_string need to be the inverse of each other.


## [2.0.0] 2022-07-12

### Added

- Added ChoiceParameterType
- Added context classes to various functions (CMEM-4173).

### Migration Notes

Due to the added context classes, the signature of a number of functions has been changed.
The following changes need to be made to implementation of these classes:

### WorkflowPlugin

- The execute function has a new parameter `context`:
  - `def execute(self, inputs: Sequence[Entities], context: ExecutionContext)`

### ParameterType

- The `project_id` parameters of the label and the autocompletion functions have been replaced by the PluginContext:
  - `def autocomplete(self, query_terms: list[str], context: PluginContext) -> list[Autocompletion]`
  - `def label(self, value: str, context: PluginContext) -> Optional[str]`
  - The project identifier can still be accessed via `context.project_id`
- The `fromString` function has a new parameter `context`:
  - `def from_string(self, value: str, context: PluginContext) -> T`


## [1.2.0] 2022-06-15

### Added

- `write_to_dataset` function to utils module to write to a dataset
- Added MultilineStringParameterType


## [1.1.1] 2022-05-16 - shipped with DI v22.1

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

