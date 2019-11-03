from datetime import datetime, timezone
from typing import Generator

from .record import Record
from .shared_queries import (
    GET_ACTIVE_COUNTS_QUERY,
    GET_ORG_NUMBER_TREE_QUERY,
    GET_PROPERTY_BY_ORG_ID_QUERY,
    GET_PROPERTY_ORG_VALUES_QUERY,
    GET_PROVIDER_QUERY,
    GET_SERVICE_AREA_DEVICES_QUERY,
    GET_SERVICE_AREA_SERVICE_PLANS_QUERY,
    GET_SERVICE_AREAS_QUERY,
)


class PropertiesMixin:
    def update_time_zones(
        self, record: Record, org_number: str, dates_to_localize: tuple
    ):
        # Get some properties from PropertyMapping
        _action = self.get_site_values(org_number)
        if "TimeZone" in _action:
            for pfik, pfiv in dates_to_localize:
                _action[pfiv] = self.convert_utc_to_local_time(
                    record.raw[pfik], _action["TimeZone"]
                )

        record.raw.update(_action)

    def get_site_values(self, org_number: str):
        """
        Grab the site level org values and information given a organization number
        """
        _action = {}
        prop = self.get_and_cache_property_by_org_number(org_number)
        if prop:
            for pfik, pfiv in self.property_fields_include:
                _action[pfik] = prop.get(pfiv or pfik, "")

        return _action

    def get_and_cache_property_by_org_number(self, org_number):
        if self.cache_client.exists(org_number):
            self.debug(f"Fetching record from cache for Org Number: {org_number}.")
            return self.cache_client.get(org_number)
        else:
            self.info(f"Fetching record from DB for Org Number: {org_number}.")
            record = self._get_property_by_org_number(org_number)

            if record is None:
                msg = f"Property not found for Org Number: {org_number}. Updating cache with a null object"
                self.warning(msg)

            # Set the property in the cache. If the object is null, then this will create a key
            # for this org number and this will be how we know not to continually go back to ES
            # for data that doesn't exist. The ESImport process for properties will overwrite
            # this cache entry with the correct object.
            self.cache_client.set(org_number, record)
            return record

    def _get_property_by_org_number(self, org_number: str):
        try:
            rec = next(
                self.fetch_rows_as_dict(GET_PROPERTY_BY_ORG_ID_QUERY, org_number)
            )
        except StopIteration:
            return None

        self._set_additonal_property_info(rec)
        return rec

    def _set_additonal_property_info(self, property_record: dict):
        self._set_provider(property_record)
        self._set_org_values(property_record)
        self._set_service_areas(property_record)
        self._set_org_number_tree(property_record)
        self._set_active_counts(property_record)
        self._embed_address(property_record)
        self._ensure_dates_are_in_UTC(property_record)
        property_record["UpdateTime"] = datetime.now(tz=timezone.utc)

    def _set_service_areas(self, property_record: dict):
        # All site-level service plans are stored with their org ID as key
        site_level_sps = {}
        record_id = property_record["ID"]

        for service_plan in self.fetch_rows(
            GET_SERVICE_AREA_SERVICE_PLANS_QUERY, record_id
        ):
            sp_dic = {
                "Number": service_plan.Number,
                "Name": service_plan.Name,
                "Description": service_plan.Description,
                "Price": service_plan.Price,
                "UpKbs": service_plan.UpKbs,
                "DownKbs": service_plan.DownKbs,
                "IdleTimeout": service_plan.IdleTimeout,
                "ConnectionLimit": service_plan.ConnectionLimit,
                "RadiusClass": service_plan.RadiusClass,
                "GroupBandwidthLimit": service_plan.GroupBandwidthLimit,
                "Type": service_plan.Type,
                "PlanTime": service_plan.PlanTime,
                "PlanUnit": service_plan.PlanUnit,
                "LifespanTime": service_plan.LifespanTime,
                "LifespanUnit": service_plan.LifespanUnit,
                "CurrencyCode": service_plan.CurrencyCode,
                "Status": service_plan.Status,
                "OrgCode": service_plan.OrgCode,
                "DateCreatedUTC": self.set_utc_timezone(service_plan.DateCreatedUTC),
            }

            if not service_plan.Owner_Org_ID in site_level_sps:
                site_level_sps[service_plan.Owner_Org_ID] = [sp_dic]
            else:
                site_level_sps[service_plan.Owner_Org_ID].append(sp_dic)

        sa_list = []

        for service_area in self.fetch_rows(GET_SERVICE_AREAS_QUERY, record_id):
            id_ = service_area.ID
            # Get service plans:
            s_plans = site_level_sps[id_] if id_ in site_level_sps else []
            sa_list.append(
                {
                    "Number": service_area.Number,
                    "Name": service_area.Name,
                    "ZoneType": service_area.ZoneType,
                    "ActiveMembers": service_area.ActiveMembers,
                    "ActiveDevices": service_area.ActiveDevices,
                    "Hosts": [
                        device for device in self.__get_devices_for_service_area(id_)
                    ],
                    "ServicePlans": s_plans,
                }
            )

        property_record["ServiceAreaObjects"] = sa_list

    def _set_provider(self, property_record: dict):
        property_record["Provider"] = self.execute_query(
            GET_PROVIDER_QUERY, property_record["ID"]
        ).fetchval()

    def _set_org_values(self, property_record: dict):
        record_id = property_record["ID"]
        for org_v in self.execute_query(GET_PROPERTY_ORG_VALUES_QUERY, record_id):
            val = org_v.Value
            property_record[org_v.Name] = float(val) if org_v.Name == "TaxRate" else val

    def _set_org_number_tree(self, property_record: dict):
        org_number_tree_list = []
        record_id = property_record["ID"]

        for row in self.fetch_rows(GET_ORG_NUMBER_TREE_QUERY, record_id, record_id):
            org_number_tree_list.append(row[0])  # row[0] is the orgNumber itself.

        property_record["OrgNumberTree"] = org_number_tree_list

    def _set_active_counts(self, property_record: dict):
        row = self.execute_query(
            GET_ACTIVE_COUNTS_QUERY, property_record["ID"]
        ).fetchone()

        property_record["ActiveMembers"] = row.ActiveMembers if row else 0
        property_record["ActiveDevices"] = row.ActiveDevices if row else 0

    def _embed_address(self, property_record: dict):
        property_record["Address"] = {
            "AddressLine1": property_record.pop("AddressLine1"),
            "AddressLine2": property_record.pop("AddressLine2"),
            "City": property_record.pop("City"),
            "Area": property_record.pop("Area"),
            "PostalCode": property_record.pop("PostalCode"),
            "CountryName": property_record.pop("CountryName"),
        }

    def _ensure_dates_are_in_UTC(self, property_record: dict):
        for key, value in property_record.items():
            if isinstance(value, datetime):
                property_record[key] = self.set_utc_timezone(value)

    def __get_devices_for_service_area(self, service_area_id: int) -> Generator[dict]:
        for device in self.fetch_rows(GET_SERVICE_AREA_DEVICES_QUERY, service_area_id):
            yield {
                "NASID": device.NASID,
                "RadiusNASID": device.RadiusNASID,
                "HostType": device.HostType,
                "VLANRangeStart": device.VLANRangeStart,
                "VLANRangeEnd": device.VLANRangeEnd,
                "NetIP": device.NetIP,
            }
