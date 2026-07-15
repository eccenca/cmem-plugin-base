## Overview of Changes

### Goal
Convert the four entity classes in `entity.py` from plain Python classes to Pydantic `BaseModel` subclasses, removing handwritten boilerplate while preserving full backward compatibility.

---

### `cmem_plugin_base/dataintegration/entity.py`

**`EntityPath` → `BaseModel, frozen=True`**

Before: manual `__init__`, `__eq__`, `__hash__`, `__repr__` (41 lines).  
After: 4 field declarations (8 lines).

`frozen=True` makes the model immutable and auto-generates `__hash__` and `__eq__`. This is correct because `EntityPath` is a value object — there's no reason to mutate a path after construction, and immutability enables safe use as dict keys or in sets.

**`EntitySchema` → `BaseModel` (non-frozen)**

Before: manual `__init__`, `__eq__`, `__hash__`, `__repr__` (50 lines) with a `None`→`EntityPath("")` conversion in `__init__`.  
After: 4 field declarations (5 lines); the `path_to_root` default replaces the `None` sentinel logic.

`frozen=True` was considered but dropped because `TypedEntitySchema` (in `typed_entities/typed_entities.py`) subclasses `EntitySchema` using a singleton pattern that sets `self._initialized` — which requires mutability. A frozen Pydantic model disallows `__setattr__` calls entirely, so the subclass would break.

`paths` and `sub_schemata` are typed as `tuple[EntityPath, ...]` / `tuple["EntitySchema", ...] | None`. Pydantic v2 coerces list inputs to tuples automatically at runtime, which is why call sites can still pass lists — Pydantic normalises them. The stored value is always a tuple, ensuring consistent equality comparisons.

**`Entity` → `BaseModel`**

Before: manual `__init__` (2 lines of field assignment).  
After: 2 field declarations + `arbitrary_types_allowed=True` config.

`arbitrary_types_allowed=True` is required because `values: Sequence[Sequence[str]]` uses an abstract type that Pydantic cannot validate with its default type system.

**`Entities` — kept as plain Python class**

Two incompatibilities prevented the Pydantic conversion:
1. `TypedEntities` subclasses `Entities` with a completely different `__init__` signature (`values: Iterator[T], schema: TypedEntitySchema[T]`), which clashes with Pydantic's model init mechanics.
2. The field name `schema` shadows Pydantic `BaseModel`'s deprecated `.schema()` classmethod, causing a `UserWarning` (no functional issue, but noisy).

Since `Entities` had no `__eq__`/`__hash__`/`__repr__` boilerplate to begin with, there was nothing to gain by converting it.

---

### Call-site fixes (required due to Pydantic not accepting positional args)

Pydantic `BaseModel.__init__` requires keyword arguments. All positional constructor calls were updated:

| File | Change |
|---|---|
| `tests/test_utils_build_entities_from_data.py` | `EntityPath("name", False, ...)` → `EntityPath(path="name", ...)` and `paths=[...]` → `paths=(...)` |
| `typed_entities/quads.py` | `EntityPath(path_uri(...))` → `EntityPath(path=path_uri(...))` |
| `typed_entities/file.py` | Same as quads |
| `typed_entities/typed_entities.py` | `super().__init__(type_uri, paths)` → `super().__init__(type_uri=type_uri, paths=tuple(paths))` |
| `utils/entity_builder.py` | `paths=schema_paths` → `paths=tuple(schema_paths)` |

The `tuple()` wraps in the last two are also necessary for mypy: the field is typed `tuple[EntityPath, ...]`, so passing a `list` is a type error even though Pydantic would coerce it at runtime. Making the coercion explicit satisfies both mypy and the type contract.

---

### Net result

- `entity.py` reduced from 129 lines to 68 lines
- Zero handwritten `__init__`, `__eq__`, `__hash__`, or `__repr__` methods remain in the converted classes
- All 30 tests pass, mypy reports no errors, ruff reports no issues