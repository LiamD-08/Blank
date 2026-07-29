"""Tunable game balance constants."""

# Player starting state
INITIAL_CAPITAL = 500_000

# Marketplace
MARKET_BUSINESS_COUNT_MIN = 3
MARKET_BUSINESS_COUNT_MAX = 5
MARKET_REFRESH_DAYS = 30

# Acquisition costs
RENT_MARKUP_MIN = 0.08   # 8% of purchase price per year
RENT_MARKUP_MAX = 0.12   # 12% of purchase price per year
BUYOUT_TRANSACTION_FEE = 0.02  # 2% of purchase price

# Valuation / exit
SECTOR_EBITDA_MULTIPLES = {
    "restaurant": 4.0,
    "retail": 5.0,
    "manufacturing": 6.0,
    "service": 7.0,
    "technology": 10.0,
    "healthcare": 8.0,
    "hospitality": 4.5,
    "logistics": 5.5,
}
DEFAULT_EBITDA_MULTIPLE = 5.0
SALE_TRANSACTION_COST = 0.03   # 3% of sale price
CAPITAL_GAINS_TAX = 0.20       # 20% on profit

# Debt
ANNUAL_INTEREST_RATE_MIN = 0.06   # 6% pa
ANNUAL_INTEREST_RATE_MAX = 0.15   # 15% pa
DEBT_RESTRUCTURE_FEE = 0.01       # 1% of outstanding debt

# Employee settings
EMPLOYEE_SALARY_RANGES = {
    "manager": (60_000, 150_000),
    "skilled_worker": (40_000, 80_000),
    "unskilled_worker": (28_000, 50_000),
    "salesperson": (35_000, 70_000),
    "technician": (45_000, 90_000),
}
BENEFITS_COST_RATE = 0.15          # 15% of salary
HIRING_SUCCESS_RATE_MIN = 0.60
HIRING_SUCCESS_RATE_MAX = 0.80
ONBOARDING_WEEKS = 4               # ramp-up period
TRAINING_PAYOFF_WEEKS_MIN = 4
TRAINING_PAYOFF_WEEKS_MAX = 8
TRAINING_COST_PER_WEEK = 500
LAYOFF_COST_WEEKS = 4              # weeks of salary as severance
TURNOVER_BASE_RATE = 0.02          # 2% per month at neutral morale

# KPI ranges
CUSTOMER_SATISFACTION_MAX = 100
UTILIZATION_MIN = 0.0
UTILIZATION_MAX = 1.0
QUALITY_SCORE_MAX = 100

# Uncertainty / noise
UNCERTAINTY_FACTOR_MIN = 0.05
UNCERTAINTY_FACTOR_MAX = 0.10

# Seasonal demand variation amplitudes (fraction of base demand)
SEASONAL_AMPLITUDE = {
    "restaurant": 0.15,
    "retail": 0.25,
    "hospitality": 0.30,
    "logistics": 0.10,
    "manufacturing": 0.05,
    "service": 0.05,
    "technology": 0.05,
    "healthcare": 0.08,
}

# Simulation tick
DAYS_PER_TICK = 1
TICKS_PER_MONTH = 30
