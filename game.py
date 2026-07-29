"""Business Turnaround Simulation – main entry point."""

from __future__ import annotations

import sys
from typing import Optional

from businesses.marketplace import Marketplace, compute_lease_cost
from core.clock import GameClock
from core.simulation import Simulation
from economy.finance import compute_valuation
from models.business import AcquisitionMode
from services.player import Player
from ui.business_view import show_business_detail, business_action_menu
from ui.dashboard import show_player_summary, show_portfolio, show_marketplace
from ui.employee_view import show_employee_roster
from ui.reports import print_monthly_pnl, print_transaction_history


def _input(prompt: str) -> str:
    try:
        return input(prompt).strip()
    except (EOFError, KeyboardInterrupt):
        print("\nGoodbye!")
        sys.exit(0)


def main() -> None:
    print("\n  Welcome to Business Turnaround Simulation!")
    print("  You are a turnaround specialist. Acquire failing businesses,")
    print("  improve them, and build a profitable portfolio.\n")

    player = Player()
    clock = GameClock()
    marketplace = Marketplace()
    sim = Simulation(player, clock)

    while True:
        show_player_summary(player, clock.date_str)
        print("\n  MAIN MENU")
        print("  1. View portfolio")
        print("  2. Browse marketplace")
        print("  3. Manage a business")
        print("  4. View reports")
        print("  5. Advance 1 day")
        print("  6. Advance 1 month")
        print("  7. Sell a business")
        print("  0. Quit")

        choice = _input("\n  Choose: ")

        if choice == "1":
            show_portfolio(player)

        elif choice == "2":
            _marketplace_menu(player, marketplace, clock)

        elif choice == "3":
            _manage_business_menu(player, sim)

        elif choice == "4":
            _reports_menu(player)

        elif choice == "5":
            notifications = sim.advance_days(1)
            print(f"\n  Advanced to {clock.date_str}")
            for n in notifications:
                print(f"  ⚡ {n}")
            # Refresh marketplace monthly
            if clock.is_first_day_of_month():
                marketplace.refresh()
                print("  📋 Marketplace refreshed with new listings.")

        elif choice == "6":
            print(f"\n  Advancing to end of {clock.month_name} {clock.year}...")
            result = sim.advance_month()
            print(f"\n  ── Month End: {clock.date_str} ──")
            for n in result["notifications"]:
                print(f"  ⚡ {n}")
            # Print monthly summaries
            for biz_id, data in result["summary"].items():
                print_monthly_pnl(data["summary"], data["name"])
            marketplace.refresh()
            print("\n  📋 Marketplace refreshed.")
            marketplace.age_listings(30)

        elif choice == "7":
            _sell_business_menu(player, sim)

        elif choice == "0":
            print("\n  Thanks for playing! Goodbye.\n")
            sys.exit(0)

        else:
            print("  Invalid choice.")


def _marketplace_menu(player: Player, marketplace: Marketplace, clock: GameClock) -> None:
    """Handle marketplace browsing and acquisition."""
    show_marketplace(marketplace.listings)
    if not marketplace.listings:
        return

    choice = _input("\n  Enter listing # to acquire (or 0 to back): ")
    if choice == "0" or not choice:
        return
    try:
        idx = int(choice) - 1
        listing = marketplace.listings[idx]
    except (ValueError, IndexError):
        print("  Invalid selection.")
        return

    biz = listing.business
    show_business_detail(biz)

    print(f"\n  Acquisition options for {biz.name}:")
    print(f"  A. Buyout  – ${listing.effective_price:,.0f} upfront + ${biz.outstanding_debt:,.0f} debt")
    lease_cost = compute_lease_cost(biz)
    print(f"  B. Lease   – ${lease_cost:,.0f}/month (no upfront)")
    print("  0. Back")

    acq_choice = _input("  Choose (A/B/0): ").upper()
    if acq_choice == "0":
        return

    if acq_choice == "A":
        mode = AcquisitionMode.BUYOUT
        price = listing.effective_price
        lease = 0.0
    elif acq_choice == "B":
        mode = AcquisitionMode.RENT
        price = 0.0
        lease = lease_cost
    else:
        print("  Invalid choice.")
        return

    success = player.acquire_business(
        biz, mode, price, lease_monthly=lease, current_day=clock.total_days
    )
    if success:
        marketplace.remove_listing(biz.id)
        print(f"\n  ✅ Acquired {biz.name} via {mode.value}!")
    else:
        print(f"\n  ❌ Insufficient funds! Need ${price:,.0f}, have ${player.cash:,.0f}.")


def _manage_business_menu(player: Player, sim: Simulation) -> None:
    """Select and manage an owned business."""
    businesses = player.owned_businesses
    if not businesses:
        print("\n  No businesses in portfolio.")
        return

    print("\n  Select a business:")
    for i, b in enumerate(businesses, 1):
        print(f"  {i}. {b.name} ({b.sector}) – EBITDA/mo: ${b.ebitda_monthly:,.0f}")

    choice = _input("  Choose (0 to back): ")
    if choice == "0":
        return
    try:
        idx = int(choice) - 1
        business = businesses[idx]
    except (ValueError, IndexError):
        print("  Invalid selection.")
        return

    while True:
        show_business_detail(business)
        print("\n  1. Turnaround actions")
        print("  2. View staff")
        print("  0. Back")
        sub = _input("  Choose: ")
        if sub == "1":
            msg = business_action_menu(business, player.cash)
            if msg:
                print(f"\n  → {msg}")
        elif sub == "2":
            show_employee_roster(business.employees, business.name)
        elif sub == "0":
            break


def _reports_menu(player: Player) -> None:
    """Show financial reports."""
    print("\n  REPORTS")
    print("  1. Transaction history")
    print("  2. Portfolio summary")
    print("  0. Back")
    choice = _input("  Choose: ")
    if choice == "1":
        print_transaction_history(player.transaction_ledger)
    elif choice == "2":
        show_portfolio(player)


def _sell_business_menu(player: Player, sim: Simulation) -> None:
    """Sell an owned business."""
    businesses = player.owned_businesses
    if not businesses:
        print("\n  No businesses to sell.")
        return

    print("\n  Select business to sell:")
    for i, b in enumerate(businesses, 1):
        val = compute_valuation(b)
        print(f"  {i}. {b.name} – Est. value: ${val:,.0f}")

    choice = _input("  Choose (0 to back): ")
    if choice == "0":
        return
    try:
        idx = int(choice) - 1
        business = businesses[idx]
    except (ValueError, IndexError):
        print("  Invalid selection.")
        return

    suggested_price = compute_valuation(business)
    print(f"\n  Suggested sale price: ${suggested_price:,.0f}")
    price_str = _input(f"  Enter sale price (or press Enter to use suggested): ")
    try:
        sale_price = float(price_str) if price_str else suggested_price
    except ValueError:
        print("  Invalid price.")
        return

    from businesses.manager import BusinessManager
    from models.financial import Transaction, TransactionType

    rec = player.acquisition_records.get(business.id)
    acq_cost = rec.acquisition_cost if rec else 0.0

    mgr = BusinessManager(business)
    proceeds = mgr.sell_business(sale_price, acq_cost)

    player.portfolio.remove(business)
    if business.id in player.acquisition_records:
        del player.acquisition_records[business.id]

    # Credit net proceeds
    txn = Transaction(
        day=sim.clock.total_days,
        amount=proceeds["net_proceeds"],
        type=TransactionType.SALE_PROCEEDS,
        description=f"Sale of {business.name}",
        business_id=business.id,
    )
    player.record_transaction(txn)

    print(f"\n  ✅ {business.name} sold!")
    print(f"     Sale price:        ${proceeds['sale_price']:,.0f}")
    print(f"     Transaction cost:  ${proceeds['transaction_cost']:,.0f}")
    print(f"     Capital gains tax: ${proceeds['tax']:,.0f}")
    print(f"     Net proceeds:      ${proceeds['net_proceeds']:,.0f}")


if __name__ == "__main__":
    main()
