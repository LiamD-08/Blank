"""Tests for the employee (staffing) system."""

import pytest
from employees.hr import (
    monthly_total_compensation,
    total_monthly_labor_cost,
    give_raise,
    terminate_employee,
    process_monthly_turnover,
    boost_team_morale,
)
from employees.performance import (
    tick_employee,
    aggregate_productivity,
    aggregate_quality,
    check_turnover_risk,
)
from employees.recruiter import (
    generate_applicant,
    get_applicants,
    make_offer,
    hire_employee,
    start_training,
)
from models.employee import Employee, EmployeeRole, EmployeeStatus


def _make_employee(**kwargs) -> Employee:
    defaults = dict(
        id="emp-001",
        name="Test Worker",
        role=EmployeeRole.SKILLED_WORKER,
        annual_salary=50_000,
        skill_level=0.6,
        productivity=0.6,
        morale=0.7,
        quality_contribution=0.6,
        status=EmployeeStatus.ACTIVE,
        days_employed=30,
        onboarding_days_remaining=0,
    )
    defaults.update(kwargs)
    return Employee(**defaults)


class TestCompensation:
    def test_monthly_total_includes_benefits(self):
        emp = _make_employee(annual_salary=60_000)
        total = monthly_total_compensation(emp)
        base_monthly = 60_000 / 12
        assert total > base_monthly
        assert abs(total - base_monthly * 1.15) < 1

    def test_total_labor_cost_sums_active_only(self):
        active = _make_employee(annual_salary=50_000, status=EmployeeStatus.ACTIVE)
        terminated = _make_employee(annual_salary=50_000, status=EmployeeStatus.TERMINATED)
        cost = total_monthly_labor_cost([active, terminated])
        expected = monthly_total_compensation(active)
        assert abs(cost - expected) < 1


class TestGiveRaise:
    def test_salary_increases(self):
        emp = _make_employee(annual_salary=50_000)
        old_sal = emp.annual_salary
        give_raise(emp, 0.10)
        assert emp.annual_salary > old_sal

    def test_morale_improves_after_raise(self):
        emp = _make_employee(morale=0.5)
        give_raise(emp, 0.10)
        assert emp.morale > 0.5

    def test_morale_capped_at_one(self):
        emp = _make_employee(morale=0.99)
        give_raise(emp, 0.50)
        assert emp.morale <= 1.0


class TestTermination:
    def test_status_becomes_terminated(self):
        emp = _make_employee()
        terminate_employee(emp)
        assert emp.status == EmployeeStatus.TERMINATED

    def test_severance_is_positive(self):
        emp = _make_employee(annual_salary=52_000)
        _, severance = terminate_employee(emp)
        assert severance > 0


class TestTurnover:
    def test_low_morale_increases_risk(self):
        risk_low = check_turnover_risk(_make_employee(morale=0.1))
        risk_high = check_turnover_risk(_make_employee(morale=0.9))
        assert risk_low > risk_high

    def test_turnover_risk_bounded(self):
        for morale in [0.0, 0.5, 1.0]:
            risk = check_turnover_risk(_make_employee(morale=morale))
            assert 0.0 <= risk <= 1.0


class TestBoostMorale:
    def test_morale_increases(self):
        emps = [_make_employee(morale=0.5) for _ in range(3)]
        boost_team_morale(emps, 0.1)
        for e in emps:
            assert e.morale > 0.5

    def test_morale_capped_at_one(self):
        emps = [_make_employee(morale=0.99)]
        boost_team_morale(emps, 0.5)
        assert emps[0].morale <= 1.0


class TestTickEmployee:
    def test_onboarding_completes(self):
        emp = _make_employee(
            status=EmployeeStatus.ONBOARDING, onboarding_days_remaining=5
        )
        tick_employee(emp, days=6)
        assert emp.status == EmployeeStatus.ACTIVE

    def test_active_days_increment(self):
        emp = _make_employee()
        before = emp.days_employed
        tick_employee(emp, days=10)
        assert emp.days_employed == before + 10

    def test_productivity_stays_bounded(self):
        emp = _make_employee()
        for _ in range(365):
            tick_employee(emp, days=1)
        assert 0.0 <= emp.productivity <= 1.0
        assert 0.0 <= emp.morale <= 1.0


class TestAggregates:
    def test_aggregate_productivity_returns_zero_with_no_active(self):
        emp = _make_employee(status=EmployeeStatus.ONBOARDING)
        assert aggregate_productivity([emp]) == 0.0

    def test_aggregate_productivity_with_active(self):
        emp = _make_employee(productivity=0.8, morale=1.0)
        result = aggregate_productivity([emp])
        assert result > 0


class TestRecruitment:
    def test_generate_applicant_has_role(self):
        app = generate_applicant(EmployeeRole.MANAGER)
        assert app.role == EmployeeRole.MANAGER

    def test_applicant_salary_in_range(self):
        from config.balancing import EMPLOYEE_SALARY_RANGES
        app = generate_applicant(EmployeeRole.MANAGER)
        lo, hi = EMPLOYEE_SALARY_RANGES["manager"]
        assert lo <= app.annual_salary <= hi

    def test_get_applicants_count(self):
        apps = get_applicants(EmployeeRole.SKILLED_WORKER, count=4)
        assert len(apps) == 4

    def test_start_training_active_employee(self):
        emp = _make_employee()
        msg, cost = start_training(emp)
        assert emp.is_being_trained
        assert cost > 0

    def test_start_training_already_training(self):
        emp = _make_employee(is_being_trained=True, training_weeks_remaining=3)
        msg, cost = start_training(emp)
        assert cost == 0.0

    def test_hire_employee_appends_to_list(self):
        employees = []
        emp, msg = hire_employee(EmployeeRole.UNSKILLED_WORKER, employees)
        # Either hired or declined; list may have one new entry
        if emp is not None:
            assert len(employees) == 1
        else:
            assert len(employees) == 0
