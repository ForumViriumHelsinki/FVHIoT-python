# FVHIoT Python

Forum Virium Helsinki's experimental Python utils
to manage IoT related messaging.  

# Installation

## pyproject.toml

Add fvhiot to your dependencies in `pyproject.toml`.

Don't forget to add necessary extras and correct tag.
E.g. FastAPI based endpoint service needs `starlette` and `kafka` extras.
See [setup.cfg](setup.cfg) for all extras.

Examples (add just one line):

```toml
dependencies = [
  "fvhiot@https://github.com/ForumViriumHelsinki/FVHIoT-python/archive/refs/tags/v0.4.0.zip",
  "fvhiot[kafka,starlette] @ https://github.com/ForumViriumHelsinki/FVHIoT-python/archive/refs/tags/v0.4.0.zip",
]
```
