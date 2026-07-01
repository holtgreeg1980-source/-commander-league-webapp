# Deploy so it works on iPhone

This is a Streamlit web app. Your iPhone does not install Python; it opens the deployed app link in Safari.

## Easiest free deployment: Streamlit Community Cloud

1. Create or sign in to a GitHub account.
2. Create a new GitHub repository named `commander-league-simulator`.
3. Upload every file from this folder to the repository. Keep `app.py` and `requirements.txt` at the top level.
4. Go to Streamlit Community Cloud: https://share.streamlit.io/
5. Click **New app**.
6. Pick your GitHub repo.
7. Set **Main file path** to `app.py`.
8. Click **Deploy**.
9. Open the deployed app link on your iPhone in Safari.
10. Optional: tap Share → Add to Home Screen.

## Card pictures

Card pictures load from Scryfall while the app is online. If images fail, the tracker still works with text logs.

## Save files

Use the **Download Saved Game JSON** button after a game session. On the next session, use **Load saved game JSON** in the sidebar.
