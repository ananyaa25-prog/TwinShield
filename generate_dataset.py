"""
Generate a diverse telemetry dataset for TWINSHIELD.
"""

from simulation.config import create_simulation_config
from simulation.dataset import (
    generate_dataset_rows,
    save_rows_to_csv,
)


def main():
    config_variants = [
        create_simulation_config(
            flow_rates_mbps={
                "f1": 10.0,
                "f2": 15.0,
                "f3": 8.0,
            },
            shared_bottleneck_background_load_mbps=2.0,
            background_surge_load_mbps=10.0,
        ),
        create_simulation_config(
            flow_rates_mbps={
                "f1": 15.0,
                "f2": 20.0,
                "f3": 10.0,
            },
            shared_bottleneck_background_load_mbps=5.0,
            background_surge_load_mbps=25.0,
        ),
        create_simulation_config(
            flow_rates_mbps={
                "f1": 18.0,
                "f2": 25.0,
                "f3": 12.0,
            },
            shared_bottleneck_background_load_mbps=8.0,
            background_surge_load_mbps=40.0,
        ),
    ]

    rows = generate_dataset_rows(
        scenarios=[
            "normal",
            "shared_bottleneck",
            "background_surge",
        ],
        num_steps=5,
        episodes_per_scenario=10,
        config_variants=config_variants,
    )

    output_path = save_rows_to_csv(
        rows,
        "data/twinshield_telemetry_diverse.csv",
    )

    print("Saved to:", output_path)
    print("Rows saved:", len(rows))


if __name__ == "__main__":
    main()