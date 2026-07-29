"""Business type (archetype) definitions."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Tuple


@dataclass
class BusinessArchetype:
    sector: str
    size_label: str          # small / medium / large
    price_range: Tuple[float, float]
    annual_revenue_range: Tuple[float, float]
    cogs_rate_range: Tuple[float, float]
    overhead_monthly_range: Tuple[float, float]
    maintenance_monthly_range: Tuple[float, float]
    debt_ratio_range: Tuple[float, float]  # debt as fraction of price
    typical_headcount: Tuple[int, int]


ARCHETYPES: Dict[str, Dict[str, BusinessArchetype]] = {
    "restaurant": {
        "small": BusinessArchetype(
            sector="restaurant", size_label="small",
            price_range=(80_000, 200_000),
            annual_revenue_range=(200_000, 500_000),
            cogs_rate_range=(0.28, 0.38),
            overhead_monthly_range=(5_000, 12_000),
            maintenance_monthly_range=(500, 1_500),
            debt_ratio_range=(0.3, 0.7),
            typical_headcount=(4, 10),
        ),
        "medium": BusinessArchetype(
            sector="restaurant", size_label="medium",
            price_range=(200_000, 600_000),
            annual_revenue_range=(500_000, 1_500_000),
            cogs_rate_range=(0.28, 0.36),
            overhead_monthly_range=(12_000, 30_000),
            maintenance_monthly_range=(1_500, 4_000),
            debt_ratio_range=(0.3, 0.65),
            typical_headcount=(10, 25),
        ),
    },
    "retail": {
        "small": BusinessArchetype(
            sector="retail", size_label="small",
            price_range=(50_000, 150_000),
            annual_revenue_range=(150_000, 400_000),
            cogs_rate_range=(0.45, 0.60),
            overhead_monthly_range=(3_000, 8_000),
            maintenance_monthly_range=(200, 800),
            debt_ratio_range=(0.2, 0.5),
            typical_headcount=(2, 6),
        ),
        "medium": BusinessArchetype(
            sector="retail", size_label="medium",
            price_range=(150_000, 500_000),
            annual_revenue_range=(400_000, 1_200_000),
            cogs_rate_range=(0.45, 0.58),
            overhead_monthly_range=(8_000, 20_000),
            maintenance_monthly_range=(800, 2_500),
            debt_ratio_range=(0.2, 0.5),
            typical_headcount=(6, 20),
        ),
    },
    "manufacturing": {
        "small": BusinessArchetype(
            sector="manufacturing", size_label="small",
            price_range=(200_000, 600_000),
            annual_revenue_range=(300_000, 900_000),
            cogs_rate_range=(0.50, 0.65),
            overhead_monthly_range=(8_000, 20_000),
            maintenance_monthly_range=(2_000, 6_000),
            debt_ratio_range=(0.3, 0.7),
            typical_headcount=(5, 15),
        ),
        "medium": BusinessArchetype(
            sector="manufacturing", size_label="medium",
            price_range=(600_000, 2_000_000),
            annual_revenue_range=(900_000, 3_000_000),
            cogs_rate_range=(0.48, 0.62),
            overhead_monthly_range=(20_000, 60_000),
            maintenance_monthly_range=(6_000, 18_000),
            debt_ratio_range=(0.3, 0.65),
            typical_headcount=(15, 50),
        ),
    },
    "service": {
        "small": BusinessArchetype(
            sector="service", size_label="small",
            price_range=(60_000, 180_000),
            annual_revenue_range=(100_000, 350_000),
            cogs_rate_range=(0.20, 0.35),
            overhead_monthly_range=(3_000, 9_000),
            maintenance_monthly_range=(300, 1_000),
            debt_ratio_range=(0.1, 0.4),
            typical_headcount=(2, 8),
        ),
        "medium": BusinessArchetype(
            sector="service", size_label="medium",
            price_range=(180_000, 600_000),
            annual_revenue_range=(350_000, 1_000_000),
            cogs_rate_range=(0.18, 0.30),
            overhead_monthly_range=(9_000, 25_000),
            maintenance_monthly_range=(1_000, 3_000),
            debt_ratio_range=(0.1, 0.4),
            typical_headcount=(8, 25),
        ),
    },
    "technology": {
        "small": BusinessArchetype(
            sector="technology", size_label="small",
            price_range=(150_000, 500_000),
            annual_revenue_range=(200_000, 600_000),
            cogs_rate_range=(0.15, 0.30),
            overhead_monthly_range=(8_000, 20_000),
            maintenance_monthly_range=(500, 2_000),
            debt_ratio_range=(0.1, 0.4),
            typical_headcount=(3, 10),
        ),
    },
    "healthcare": {
        "small": BusinessArchetype(
            sector="healthcare", size_label="small",
            price_range=(120_000, 400_000),
            annual_revenue_range=(250_000, 700_000),
            cogs_rate_range=(0.25, 0.40),
            overhead_monthly_range=(10_000, 25_000),
            maintenance_monthly_range=(1_000, 3_000),
            debt_ratio_range=(0.2, 0.5),
            typical_headcount=(4, 12),
        ),
    },
    "hospitality": {
        "small": BusinessArchetype(
            sector="hospitality", size_label="small",
            price_range=(100_000, 350_000),
            annual_revenue_range=(180_000, 600_000),
            cogs_rate_range=(0.30, 0.45),
            overhead_monthly_range=(6_000, 15_000),
            maintenance_monthly_range=(1_500, 4_000),
            debt_ratio_range=(0.3, 0.65),
            typical_headcount=(4, 12),
        ),
    },
    "logistics": {
        "small": BusinessArchetype(
            sector="logistics", size_label="small",
            price_range=(100_000, 300_000),
            annual_revenue_range=(200_000, 700_000),
            cogs_rate_range=(0.55, 0.70),
            overhead_monthly_range=(5_000, 15_000),
            maintenance_monthly_range=(2_000, 6_000),
            debt_ratio_range=(0.3, 0.6),
            typical_headcount=(4, 15),
        ),
    },
}

ALL_SECTORS = list(ARCHETYPES.keys())
