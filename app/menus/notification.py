from app.menus.util import clear_screen
from app.client.engsel import get_notifications, get_notification_detail
from app.service.auth import AuthInstance

WIDTH = 55

def show_notification_menu():
    in_notification_menu = True
    while in_notification_menu:
        print("Fetching notifications...")
        clear_screen()
        
        api_key = AuthInstance.api_key
        tokens = AuthInstance.get_active_tokens()
        
        notifications_res = get_notifications(api_key, tokens)
        if not notifications_res:
            print("No notifications found.")
            return
        
        notifications = notifications_res.get("data", {}).get("inbox", [])
        
        if not notifications:
            print("No notifications available.")
            return
        
        print("=" * WIDTH)
        print("Notifications:")
        print("=" * WIDTH)
        unread_count = 0
        for idx, notification in enumerate(notifications):
            is_read = notification.get("is_read", False)
            full_message = notification.get("full_message", "")
            brief_message = notification.get("brief_message", "")
            time = notification.get("timestamp", "")
            
            status = ""
            if is_read:
                status = "READ"
            else:
                status = "UNREAD"
                unread_count += 1

            print(f"{idx + 1}. [{status}] {brief_message}")
            print(f"- Time: {time}")
            print(f"- {full_message}")
            print("-" * WIDTH)
        print(f"Total notifications: {len(notifications)} | Unread: {unread_count}")
        print("=" * WIDTH)
        print("1. Read All Unread Notifications")
        print("00. Back to Main Menu")
        print("=" * WIDTH)
        choice = input("Enter your choice: ")
        if choice == "1":
            for notification in notifications:
                if notification.get("is_read", False):
                    continue
                notification_id = notification.get("notification_id")
                detail = get_notification_detail(api_key, tokens, notification_id)
                if detail:
                    print(f"Mark as READ notification ID: {notification_id}")
            input("Press Enter to return to the notification menu...")
        elif choice == "00":
            in_notification_menu = False
        else:
            print("Invalid choice. Please try again.")

