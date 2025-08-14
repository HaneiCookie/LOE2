import LOEView

if __name__ == "__main__":
    app = LOEView.LOEView()
    app.mainloop()

## pyinstaller --hidden-import=PIL -w -F LOEMain.py test