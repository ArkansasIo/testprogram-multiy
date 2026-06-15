"""
IDE Compiler Manager - Main Entry Point
Multi-project executable compiler and bundler
"""
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from ide_gui import main as gui_main

if __name__ == "__main__":
    print("="*60)
    print("IDE Compiler Manager")
    print("Multi-Project EXE Builder")
    print("="*60)
    print("\nStarting GUI...")
    
    try:
        gui_main()
    except Exception as e:
        print(f"Error starting GUI: {e}")
        import traceback
        traceback.print_exc()
        input("\nPress Enter to exit...")

# Made with Bob
