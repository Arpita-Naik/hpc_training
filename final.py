from google.cloud import compute_v1, billing_v1
import google.auth
import h5py
import numpy as np

credentials, PROJECT_ID = google.auth.default()

if PROJECT_ID is None:
    raise Exception("Project ID not found")

def get_all_machine_data():
    client = compute_v1.MachineTypesClient()
    request = compute_v1.AggregatedListMachineTypesRequest(project=PROJECT_ID)
    agg_list = client.aggregated_list(request=request)

    region_data = {}

    for zone_path, response in agg_list:
        if not response.machine_types:
            continue

        region = "-".join(zone_path.split("/")[-1].split("-")[:-1])

        if region not in region_data:
            region_data[region] = {}

        for mt in response.machine_types:
            if mt.name not in region_data[region]:
                region_data[region][mt.name] = {
                    "instance": mt.name,
                    "vcpu": mt.guest_cpus,
                    "memory_gb": mt.memory_mb / 1024
                }

    return {reg: list(m.values()) for reg, m in region_data.items()}

def get_pricing():
    client = billing_v1.CloudCatalogClient()
    services = client.list_services()
    compute_service = next(
        s.name for s in services if "Compute Engine" in s.display_name
    )

    pricing_map = {}

    for sku in client.list_skus(parent=compute_service):
        desc = sku.description.lower()

        if sku.category.usage_type != "OnDemand":
            continue

        if any(x in desc for x in [
            "preemptible",
            "commitment",
            "spot",
            "gpu",
            "premium"
        ]):
            continue

        try:
            rate = sku.pricing_info[0].pricing_expression.tiered_rates[0]
            price = rate.unit_price.units + rate.unit_price.nanos / 1e9

            for region in sku.service_regions:
                r = region.lower()

                if r not in pricing_map:
                    pricing_map[r] = []

                pricing_map[r].append({
                    "desc": desc,
                    "price": price
                })

        except:
            continue

    return pricing_map

def merge_data(machine_data, pricing_map):
    final_data = {}

    for region, machines in machine_data.items():
        r_low = region.lower()
        skus = pricing_map.get(r_low, []) + pricing_map.get("global", [])

        final_data[region] = []

        for m in machines:
            instance = m["instance"].lower()
            family = instance.split("-")[0]

            cpu_price = 0.0
            ram_price = 0.0

            for sku in skus:
                d = sku["desc"]

                if family in d:
                    if "core" in d or "cpu" in d:
                        cpu_price = sku["price"]
                    elif "ram" in d or "memory" in d:
                        ram_price = sku["price"]

            if cpu_price == 0:
                for sku in skus:
                    d = sku["desc"]

                    if "core" in d or "cpu" in d:
                        cpu_price = sku["price"]
                        break

            if ram_price == 0:
                for sku in skus:
                    d = sku["desc"]

                    if "ram" in d or "memory" in d:
                        ram_price = sku["price"]
                        break

            total_price = (
                m["vcpu"] * cpu_price
            ) + (
                m["memory_gb"] * ram_price
            )

            for sku in skus:
                if instance in sku["desc"]:
                    total_price = sku["price"]
                    break

            final_data[region].append({
                "instance": m["instance"],
                "price": round(total_price, 6) if total_price > 0 else 0.0,
                "vcpu": m["vcpu"],
                "memory_gb": m["memory_gb"]
            })

    return final_data

def save_to_hdf5(data):
    filename = "gcp_pricing_v15.h5"

    with h5py.File(filename, "w") as f:
        gcp_group = f.create_group("GCP")

        for region, items in data.items():
            grp = gcp_group.create_group(region)

            grp.create_dataset(
                "Instance",
                data=np.array(
                    [i["instance"] for i in items],
                    dtype="S"
                )
            )

            grp.create_dataset(
                "Instance_Pricing",
                data=np.array(
                    [i["price"] for i in items],
                    dtype="f4"
                )
            )

            grp.create_dataset(
                "Memory",
                data=np.array(
                    [i["memory_gb"] for i in items],
                    dtype="f4"
                )
            )

            grp.create_dataset(
                "vCPU",
                data=np.array(
                    [i["vcpu"] for i in items],
                    dtype="i4"
                )
            )

def main():
    machine_data = get_all_machine_data()
    pricing_data = get_pricing()
    merged_data = merge_data(machine_data, pricing_data)
    save_to_hdf5(merged_data)

if __name__ == "__main__":
    main()
