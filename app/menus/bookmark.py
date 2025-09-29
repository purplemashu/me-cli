"""
Handles the user interface for bookmarks.
"""
from app.core.bookmark import get_all_bookmarks, remove_bookmark_by_index, get_package_details_for_bookmark
from app.menus.util import clear_screen, pause
from app.menus.package import show_package_details
from app.service.auth import AuthInstance

def show_bookmark_menu():
    """Displays the bookmark management menu."""
    in_bookmark_menu = True
    while in_bookmark_menu:
        clear_screen()
        print("-------------------------------------------------------")
        print("Bookmark Paket")
        print("-------------------------------------------------------")
        bookmarks = get_all_bookmarks()
        if not bookmarks or len(bookmarks) == 0:
            print("Tidak ada bookmark tersimpan.")
            pause()
            return

        for idx, bm in enumerate(bookmarks):
            print(f"{idx + 1}. {bm['family_name']} - {bm['variant_name']} - {bm['option_name']}")

        print("-------------------------------------------------------")
        print("00. Kembali ke menu utama")
        print("99. Hapus Bookmark")
        print("-------------------------------------------------------")
        choice = input("Pilih bookmark (nomor): ")

        if choice == "00":
            in_bookmark_menu = False
            return
        elif choice == "99":
            del_choice = input("Masukan nomor bookmark yang ingin dihapus: ")
            if del_choice.isdigit() and 1 <= int(del_choice) <= len(bookmarks):
                remove_bookmark_by_index(int(del_choice) - 1)
                print("Bookmark dihapus.")
                pause()
            else:
                print("Input tidak valid.")
                pause()
            continue
        elif choice.isdigit() and 1 <= int(choice) <= len(bookmarks):
            selected_bm_index = int(choice) - 1
            api_key = AuthInstance.api_key
            tokens = AuthInstance.get_active_tokens()
            
            package_details = get_package_details_for_bookmark(selected_bm_index)
            
            if package_details:
                show_package_details(api_key, tokens, package_details["option_code"], package_details["is_enterprise"])
            else:
                print("Gagal mengambil detail paket.")
                pause()
        else:
            print("Input tidak valid.")
            pause()
            continue