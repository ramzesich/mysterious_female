# The books' pages (2026-11-21)

Each of the fourteen books shows its first page when she reads it (the Library's red chair; book 5 on her bed):
the opening of the real book, readable, in its own language and script, set by `tools/draw_pages.py` into
`assets/ship/pages/page-<n>.png`. The user, 2026-11-21: "Text only for all the books"; the ten drawn hint pages
of step 2 are gone. Whole sentences from the start, as many as fit ("Don't break sentences"), covering the page.

- `Pixelzone.ttf`: the lettering, by GGBotNet, **CC0** (https://github.com/ggbotnet/fonts-cc0). Chosen from the
  three CC0 pixel fonts there with Latin and the Polish letters, Ukrainian and Russian Cyrillic, and Hebrew
  (Liber Struct's 6 px "z" read as "e"; Public Pixel, an 8 x 8 monospace, held half as much). No vowel points.
  **Mended here (2026-11-22, the user's choice of three):** Й and й are И and и with a 2 px line one empty row above
  them, in place of the font's breve (two dots over a bar, which read as dots). Always drawn by `tools/pixelzone.py`
  (eight times larger, read back pixel by pixel): FreeType's hinting at 16 px moves the font's small parts.
- `<nn>.txt`: each book's opening, one paragraph a line, as printed (italics dropped, the font has none).
  `04.txt` is missing: its page is a title page until the text comes.

| # | Book | Where the text is from | State |
|---|---|---|---|
| 1 | Atomic Habits | The UK ebook's sample (OverDrive, ISBN 9781473537804): two sentences | **Placeholder**: the user gives her copy's opening |
| 2 | Harry Potter and the Chamber of Secrets | The Pottermore en-gb ebook's sample (OverDrive, ISBN 9781781100226): two sentences | **Placeholder** |
| 3 | Танґо смерті | readli.net (edition not named), the untitled passage before chapter 1 | Set |
| 4 | Unexpected Lessons in Love | Not found online (Transworld 2019/2020) | **Title page** until the user gives it |
| 5 | Її війна | Vivat 2024, the publisher's own excerpt (a scan of p. 5), the first story (Валерія Зеленська) | Set |
| 6 | Harry Potter and the Philosopher's Stone | The Pottermore en-gb ebook's sample (OverDrive, ISBN 9781781100219): two sentences | **Placeholder** |
| 7 | Понаїхали | royallib.com (Нора-Друк 2015), «Частина перша», 1; its Latin i put back to Cyrillic і | Set |
| 8 | Niebieskie nitki | The publisher's free ebook fragment (ebookpoint, Virtualo 2022/2023), chapter "sobota" | Set |
| 9 | Двор | readli.net, «Книга первая», I | Set |
| 10 | Боря, выйди с моря | The user's text (as the scan on homeread.net), «Тс-с…» set for the scan's «Тс— с…» (the user) | Set |
| 11 | נערה במעיל כחול | The user's text (פן, chapter 1, «יום שלישי»); a footnote mark after «ירוקים.» left out | Set |
| 12 | Poczwarka | The novel's start as quoted on zpe.gov.pl (Kraków 2004, p. 8) | Set |
| 13 | Daughters of Warsaw | The user's text (chapter 1, "Seattle, Present Day") | Set |
| 14 | Pachinko | PBS NewsHour's annotated first page: two sentences | **Placeholder** |

Each is to be checked against her copy (the user).
