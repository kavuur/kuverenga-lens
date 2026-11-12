# Kuverenga Lens

**Snap. Convert. Read.** A phone app that turns the chalkboard into a personal, dyslexia-friendly reader, in English and ChiShona.

It is an installable web app (PWA), so it does **not** need the Google Play Store. After the first open, it works with no internet connection.

## Folder contents

| Folder | What is inside |
|---|---|
| `app/` | The complete app. Copy this folder to a web host to publish it. |
| `testing/` | Test photos, the accuracy test script and its results (`accuracy_results_v1.csv`, `accuracy_results_v2.csv`). |
| `evidence/screenshots/` | Screenshots of every screen. |
| `evidence/video/` | `kuverenga_lens_demo.mp4`, a 48-second demonstration. |
| `report/`, `presentation/`, `poster/`, `charts/` | Project report, slides, poster and charts. |

## What each part of the app does

| File | Job |
|---|---|
| `app/index.html` | The screens: Home, Clean photo, Reader, Fix text, Notes, Help |
| `app/js/app.js` | Camera/photo loading, image clean-up, OCR, reader, read-aloud, notes, two languages |
| `app/js/syllables.js` | Syllable breaker (Shona rule: every syllable ends in a vowel; English rules of thumb) |
| `app/css/style.css` | Look and layout (large buttons, dyslexia-friendly reading area) |
| `app/sw.js` | Service worker: stores the whole app on the phone so it works offline |
| `app/manifest.webmanifest` | Name, icon and colours used when the app is installed on a phone |
| `app/vendor/` | Tesseract.js OCR engine and English language data (runs on the phone) |
| `app/fonts/` | OpenDyslexic font |

## 1. Try it on a computer

```bash
cd app
python -m http.server 8765
```

Open <http://localhost:8765> in Chrome. Use **Choose a photo** with a picture from `testing/photos/`.

## 2. Put it online for free (GitHub Pages)

The phone camera and offline mode need an **https** link. GitHub Pages provides one for free. This project is stored at <https://github.com/kavuur/kuverenga-lens>.

1. Push this whole folder to the repository with git.
2. On GitHub, open the repository and go to **Settings › Pages**. Under *Build and deployment*, choose **Deploy from a branch**, select branch `main` and folder `/ (root)`, then click **Save**.
3. After 1–2 minutes the app is live at <https://kavuur.github.io/kuverenga-lens/app/>. The project's front page (this README) is at <https://kavuur.github.io/kuverenga-lens/>.

## 3. Install it on a phone (no Play Store)

**Android (Chrome):** open the link, then tap **Install on this phone** in the app, or use the menu **⋮ › Add to Home screen / Install app**. The Kuverenga icon appears with your other apps.

**iPhone (Safari):** open the link, then tap **Share › Add to Home Screen**.

Open the app once while online so it can store the reading engine (about 11 MB). After that it works with no data.

To share it, send the link by WhatsApp or SMS, or show a QR code of the link.

## 4. Optional: make an APK file to share by WhatsApp or Bluetooth

1. Go to <https://www.pwabuilder.com> and paste your GitHub Pages link.
2. Choose **Package for stores › Android › Generate**. This is free and does not publish anything.
3. Download the zip. Inside is an `.apk` file.
4. Send the `.apk` to a phone. On the phone, allow **Install unknown apps** for the app you opened it with (Files or WhatsApp), then tap the `.apk`.

## 5. Reading engines: Fast and Handwriting

On the **Clean the photo** screen, the learner chooses a reading engine:

- **Fast** (default): Tesseract OCR, stored inside the app (no extra download). Good for printed or very neat writing.
- **Handwriting**: TrOCR, a model trained on handwriting. It reads chalk handwriting better. It downloads about 75 MB the first time it is used (use Wi-Fi), and after that it works offline. The board is cut into lines (the two sides of a column divider are read separately) and each line is read in turn, which takes a few seconds per line on a phone.

Results on the real classroom photo `Image_to_Test_The_App.png` (22 words): the first app versions read about 5% of the words; the improved chalk cleaning (v3) reads about 45–59% with Fast and about 50% with Handwriting. Handwriting produces whole, readable lines with fewer junk characters. The **Fix text** screen is still needed for real chalk boards.

## 6. Reading aloud in ChiShona

The app uses the phone's own text-to-speech voices. Most phones have no ChiShona voice yet. When one is missing, the app chooses the closest available voice in this order: Shona, then Swahili, then Zulu, then Xhosa, then English (South Africa). For better sound, install a voice under **Settings › Text-to-speech** (Google Speech Services → Install voice data).

## 7. Rerun the tests

```bash
pip install playwright && python -m playwright install chromium
cd app && python -m http.server 8765 &              # keep running
cd ../testing
python make_test_photos.py <handwriting.ttf> <print.ttf>   # optional: rebuild the photos
python run_accuracy_test.py                         # writes accuracy_results.csv
python capture_evidence.py                          # screenshots + demo video
```

## Troubleshooting

**"The photo could not be read" or "The app was opened as a file".** The app was opened by tapping `index.html` in a file manager, WhatsApp or email. A link that starts with `file://` does not work, because browsers block the reading engine on pages opened as files. Open the app from its web link (`https://…github.io/kuverenga-lens/`) or from the installed icon instead.

**Testing on a phone before publishing.** Put the computer and the phone on the same Wi-Fi. Run `python -m http.server 8765 --bind 0.0.0.0` inside the `app` folder, then open `http://<computer's IP address>:8765` on the phone. Reading photos works this way, but installing and offline mode need the https link.

**No sound when tapping Listen.** Turn up the media volume and check that a text-to-speech voice is installed under **Settings › Text-to-speech**.

## Known limitations

- Neat print-style chalk writing works best. Joined (cursive) handwriting is often misread, so the learner uses **Fix text**.
- The OCR engine uses its English model for Shona. Shona uses the same Latin letters, and in testing Shona boards were read as well as English ones.
- Real chalk handwriting is still hard: on the real test photo about half of the words are read correctly, so learners will often need **Fix text**. On the 14 simulated photos, v3 cleaning scores 90.7% (v2 scored 98.9% there, but only about 5% on the real board).

## Credits

- Tesseract.js (Apache-2.0)
- OpenDyslexic font by Abbie Gonzalez (SIL Open Font License)
