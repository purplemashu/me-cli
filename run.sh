#!/usr/bin/env bash

# Startup script to choose between running the CLI or the bot.

# Ensure the script is run from the project root
cd "$(dirname "$0")"

# Function to display the menu
show_menu() {
    clear
    echo "======================================="
    echo "  MYnyak Engsel - Launcher"
    echo "======================================="
    echo "  Pilih mode untuk dijalankan:"
    echo "  1. CLI (Antarmuka Baris Perintah)"
    echo "  2. Bot (Contoh Titik Masuk Bot)"
    echo "  0. Keluar"
    echo "======================================="
}

# Main loop
while true; do
    show_menu
    read -p "  Masukkan pilihan Anda [1, 2, atau 0]: " choice

    case $choice in
        1)
            echo "Menjalankan CLI..."
            python3 main.py
            echo "CLI ditutup. Tekan Enter untuk kembali ke menu."
            read -n 1 # Wait for a single key press
            ;;
        2)
            echo "Menjalankan contoh Bot..."
            python3 bot.py
            echo "Contoh Bot selesai. Tekan Enter untuk kembali ke menu."
            read -n 1
            ;;
        0)
            echo "Keluar."
            exit 0
            ;;
        *)
            echo "Pilihan tidak valid. Silakan coba lagi."
            sleep 2
            ;;
    esac
done