import orjson
from pydantic import BaseModel


# We are going to use orjson (see below), this function is a small wrapper
# to match the standard json.dumps behavior.
def orjson_dumps(v, *, default):
    # orjson.dumps returns bytes, to match standard json.dumps we need to call `.decode()`
    return orjson.dumps(v, default=default).decode()


class BaseSchema(BaseModel):
    """
    A base class for anything schema (config, records, ..)
    By 'schema' we mean:
    - How the data *should* look like ?
    - Do we need to check if the data indeed looks like we expected? if so, proceed with data 
      validation *against* its schema. Then choose whether to "fail" or send alerts/warnings
      in case the validation failed.
    - This is achieved using native Python type hinting and dataclasses, thanks to Pydantic:
      https://pydantic-docs.helpmanual.io
    """

    # Use orjson, a faster json serializere/deserializer that also handles
    # datetime objects and dataclasses very well.
    # More info at: https://github.com/ijl/orjson
    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps
