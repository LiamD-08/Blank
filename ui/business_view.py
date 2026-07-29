"""Business detail view – display and interactive turnaround actions."""

from __future__ import annotations

from typing import Optional

from businesses.manager import BusinessManager
from economy.finance import compute_valuation
from employees.hr import give_raise, terminate_employee, boost_team_morale
from employees.recruiter import hire_employee, start_training
from models.business import Business, AcquisitionMode
from models.employee import EmployeeRole
from ui.reports import print_monthly_pnl, print_kpi_table


def show_business_detail(business: Business) -> None:
    """Display overview of a single owned business."""
    mgr = BusinessManager(business)
    mode = business.acquisition_mode.value if business.acquisition_mode else "N/A"
    print(f"\n{'='*55}")
    print(f"  {business.name}")
    print(f"  Sector: {business.sector.title()}  |  Size: {business.size.title()}  |  Mode: {mode.upper()}")
    print(f"  Purchase Price: ${business.purchase_price:,.0f}  |  Debt: ${business.outstanding_debt:,.0f}")
    if business.acquisition_mode == AcquisitionMode.RENT:
        print(f"  Monthly Lease: ${business.lease_monthly:,.0f}")
    print(f"  Valuation: ${compute_valuation(business):,.0f}")
    print(f"{'='*55}")
    print_kpi_table(business)
    print_monthly_pnl(
        {
            "revenue": business.monthly_revenue,
            "cogs": business.monthly_cogs,
            "gross_profit": business.monthly_gross_profit,
            "labor": business.monthly_labor_cost,
            "overhead": business.overhead_monthly,
            "maintenance": business.maintenance_monthly,
            "marketing": business.marketing_spend_monthly,
            "debt_service": 0,
            "ebitda": business.ebitda_monthly,
            "gross_margin": business.monthly_gross_profit / business.monthly_revenue if business.monthly_revenue else 0,
            "operating_margin": business.ebitda_monthly / business.monthly_revenue if business.monthly_revenue else 0,
        },
        business.name,
    )


def business_action_menu(business: Business, player_cash: float) -> Optional[str]:
    """
    Interactive menu for turnaround actions on a business.
    Returns a message describing what happened, or None if cancelled.
    """
    mgr = BusinessManager(business)
    print(f"\n  Actions for: {business.name}")
    print("  1. Adjust pricing")
    print("  2. Set marketing spend")
    print("  3. Invest in maintenance")
    print("  4. Improve processes  ($5,000)")
    print(f"  5. Upgrade equipment  (${business.purchase_price*0.10:,.0f})")
    print("  6. Negotiate/restructure debt")
    print("  7. Hire employee")
    print("  8. Train employee")
    print("  9. Give raise")
    print("  10. Terminate employee")
    print("  11. Boost team morale  ($2,000)")
    print("  0. Back")

    choice = input("  Choose action: ").strip()

    if choice == "1":
        try:
            pct = float(input("  Price change % (e.g. 10 for +10%, -5 for -5%): ")) / 100
        except ValueError:
            return "Invalid input."
        return mgr.adjust_pricing(pct)

    elif choice == "2":
        try:
            spend = float(input("  Monthly marketing spend ($): "))
        except ValueError:
            return "Invalid input."
        return mgr.set_marketing_spend(spend)

    elif choice == "3":
        try:
            amount = float(input("  Amount to invest in maintenance ($): "))
        except ValueError:
            return "Invalid input."
        if amount > player_cash:
            return "Insufficient funds."
        return mgr.invest_maintenance(amount)

    elif choice == "4":
        msg, cost = mgr.improve_processes()
        if cost > 0 and cost > player_cash:
            return "Insufficient funds."
        return f"{msg}  Cost: ${cost:,.0f}"

    elif choice == "5":
        msg, cost = mgr.upgrade_equipment()
        if cost > 0 and cost > player_cash:
            return "Insufficient funds."
        return f"{msg}  Cost: ${cost:,.0f}"

    elif choice == "6":
        try:
            months = int(input("  Extend term by how many months? "))
        except ValueError:
            return "Invalid input."
        msg, fee = mgr.negotiate_debt(months)
        return msg

    elif choice == "7":
        print("  Roles: manager, skilled_worker, unskilled_worker, salesperson, technician")
        role_str = input("  Role to hire: ").strip()
        try:
            role = EmployeeRole(role_str)
        except ValueError:
            return "Unknown role."
        emp, msg = hire_employee(role, business.employees)
        return msg

    elif choice == "8":
        if not business.employees:
            return "No employees to train."
        for i, e in enumerate(business.employees):
            if e.is_active:
                print(f"  {i+1}. {e.name} ({e.role.value})")
        try:
            idx = int(input("  Select employee #: ")) - 1
            emp = [e for e in business.employees if e.is_active][idx]
        except (ValueError, IndexError):
            return "Invalid selection."
        msg, cost = start_training(emp)
        return f"{msg}"

    elif choice == "9":
        if not business.employees:
            return "No employees."
        active = [e for e in business.employees if e.is_active]
        for i, e in enumerate(active):
            print(f"  {i+1}. {e.name} – ${e.annual_salary:,.0f}/yr")
        try:
            idx = int(input("  Select employee #: ")) - 1
            emp = active[idx]
            pct = float(input("  Raise % (e.g. 5 for 5%): ")) / 100
        except (ValueError, IndexError):
            return "Invalid input."
        msg, _ = give_raise(emp, pct)
        return msg

    elif choice == "10":
        if not business.employees:
            return "No employees."
        active = [e for e in business.employees if e.is_active]
        for i, e in enumerate(active):
            print(f"  {i+1}. {e.name} – {e.role.value}")
        try:
            idx = int(input("  Select employee to terminate #: ")) - 1
            emp = active[idx]
        except (ValueError, IndexError):
            return "Invalid selection."
        msg, cost = terminate_employee(emp)
        return f"{msg}  Severance: ${cost:,.0f}"

    elif choice == "11":
        cost = 2_000
        if cost > player_cash:
            return "Insufficient funds."
        msg = boost_team_morale(business.employees, 0.10)
        return f"{msg}  Cost: ${cost:,.0f}"

    return None
