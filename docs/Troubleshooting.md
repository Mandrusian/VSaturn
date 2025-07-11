---
layout: default
title: Troubleshooting
---
# Troubleshooting Common Errors

This page provides solutions to common issues you might encounter while using VSaturn.

## 1. "ModuleNotFoundError: No module named 'yt_dlp'"
* **Cause:** This usually means the `yt-dlp` library (or its components) was not correctly bundled with the application.
* **Solution:**
    1.  Ensure you have `yt-dlp` installed in your Python environment (`pip install yt-dlp`).
    2.  Perform a clean rebuild of the application using PyInstaller. Navigate to your project directory (where `vsaturn.spec` is) in Terminal and run:
        ```bash
        rm -rf build dist
        pyinstaller "vsaturn.spec"
        ```
    3.  Verify that your `vsaturn.spec` file explicitly lists `yt_dlp` and its submodules in the `hiddenimports` section.

## 2. "Download Failed: [Specific yt-dlp Error]"
* **Cause:** `yt-dlp` might encounter issues with specific URLs (e.g., age-restricted content, private videos, geo-restrictions, or changes in the platform's website structure).
* **Solution:**
    1.  **Check the URL:** Double-check that the URL is correct and publicly accessible.
    2.  **Try a different video:** See if the issue is specific to that one video or a broader problem.
    3.  **Update yt-dlp:** The underlying `yt-dlp` tool is constantly updated. While the bundled app won't auto-update, if you're building it yourself, try updating `yt-dlp` in your environment and rebuilding the app:
        ```bash
        pip install --upgrade yt-dlp
        ```
    4.  **Check the in-app log:** The "Download Log" within the VSaturn application window will often provide more specific error messages from `yt-dlp`.

## 3. "Application Crashes on Launch" (No specific error message)
* **Cause:** This can be due to various reasons, including missing system dependencies, corrupted app bundle, or fundamental Python/Qt issues.
* **Solution:**
    1.  **Run from Terminal:** Open your Mac's Terminal, navigate to the executable inside the app bundle (e.g., `dist/VSaturn.app/Contents/MacOS/`) and run `./VSaturn`. Copy any error messages that appear.
    2.  **Check Console.app:** Open `Applications/Utilities/Console.app` on your Mac, clear existing logs, try launching the app, and look for new error messages related to "VSaturn" or "Python".
    3.  **Perform a Clean Rebuild:** This is often the solution for bundling issues. Navigate to your project directory and run:
        ```bash
        rm -rf build dist
        pyinstaller "vsaturn.spec"
        ```

---

## Reporting New Issues

If you encounter an issue not listed here, please help us by reporting it! Provide as much detail as possible:

1.  The exact URL(s) you were trying to download.
2.  The full "Download Log" output from the VSaturn application.
3.  A clear description of the steps to reproduce the issue.
4.  (Optional) If the app crashes, include any relevant crash reports or messages from `Console.app`.

---
_Last Updated: July 11, 2025_
