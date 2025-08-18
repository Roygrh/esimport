import os
from datetime import datetime, timezone

from esimport.core import Record, SyncBase
from .ddb_syncer import DeviceDdbSyncer


class DeviceSyncer(SyncBase):
    """
    Synchronize devices exclusively from DynamoDB,
    delegating data retrieval to DeviceDdbSyncer.
    """

    def __init__(
        self,
        *,
        region: str | None = None,
        table_name: str | None = None,
        query_limit: int | None = None,
        ddb_helper: DeviceDdbSyncer | None = None,
    ):
        # Llama a SyncBase para conservar el comportamiento de la app (logger, buffers, etc.)
        super().__init__()

        # Fallbacks a variables de entorno ONLY si no llegan por DI
        eff_region = (
            region
            or os.getenv("AWS_REGION")
            or os.getenv("AWS_DEFAULT_REGION")
            or "us-east-1"
        )
        eff_table = table_name or os.getenv("DYNAMODB_TABLE_NAME") or "client-tracking-data"
        eff_limit = int(query_limit if query_limit is not None else os.getenv("DDB_QUERY_LIMIT", "1000"))

        # Permite inyectar un helper ya configurado (tests); si no, se crea aquí
        self.ddb_helper = ddb_helper or DeviceDdbSyncer(
            region=eff_region,
            table_name=eff_table,
            query_limit=eff_limit,
        )

    def sync(self, start_date: datetime):
        start_dt = start_date.astimezone(timezone.utc)
        end_dt = datetime.now(timezone.utc)

        for item in self.ddb_helper.fetch_from_ddb(start_dt, end_dt):
            record = Record(
                index=self.get_target_elasticsearch_index(item["DateUTC"]),
                id=None,  # ES genera _id
                body=item,
            )
            self.add_record(record)
