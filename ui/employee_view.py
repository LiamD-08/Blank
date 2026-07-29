"""Employee management view."""

from __future__ import annotations

from typing import List

from models.employee import Employee, EmployeeStatus

try:
    from tabulate import tabulate
    _HAS_TABULATE = True
except ImportError:
    _HAS_TABULATE = False


def show_employee_roster(employees: List[Employee], business_name: str) -> None:
    """Display the employee roster for a business."""
    print(f"\n  ── Staff: {business_name} ──")
    if not employees:
        print("  No employees.")
        return

    rows = []
    for e in employees:
        status = e.status.name
        training = "In Training" if e.is_being_trained else ""
        rows.append([
            e.name,
            e.role.value,
            f"${e.annual_salary:,.0f}",
            f"{e.skill_level:.2f}",
            f"{e.effective_productivity:.2f}",
            f"{e.morale:.2f}",
            status,
            training,
        ])

    headers = ["Name", "Role", "Salary", "Skill", "Productivity", "Morale", "Status", "Training"]
    if _HAS_TABULATE:
        print(tabulate(rows, headers=headers, tablefmt="simple"))
    else:
        header_line = "  " + "  ".join(f"{h:<15}" for h in headers)
        print(header_line)
        for row in rows:
            print("  " + "  ".join(f"{str(v):<15}" for v in row))
