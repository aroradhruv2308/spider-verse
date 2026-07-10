# 🕸️ The Spider-Verse

My personal digital garden — one website spun from my Obsidian notes, across every
universe I'm learning in: AI/ML, software engineering, system design, fitness,
psychology, and English.

**Live site:** https://aroradhruv2308.github.io/spider-verse/

Built with [Quartz v5](https://quartz.jzhao.xyz/) · themed after
*Spider-Man: Into the Spider-Verse* · personal, non-commercial fan tribute.

---

## 🗺️ The map

Everything I write lives in the `content/` folder — that's the Obsidian vault.
Everything else in this repo is the site engine; I don't touch it day-to-day.

```
content/
├── index.md                  ← homepage (Miles)
├── AI-and-ML/                ← Peni Parker & SP//dr
├── Software-Engineering/     ← Margo "Spider-Byte"
├── System-Design-and-LLD/    ← Miguel O'Hara (2099)
├── Fitness/                  ← Peter B. Parker
├── General-Concepts/         ← Spider-Ham
├── Mind-and-Life/            ← Gwen Stacy / Ghost-Spider
└── English/                  ← Spider-Man Noir
```

**House rule:** never create new top-level folders. New folders always go *inside*
one of the 7 dimensions. (The homepage links to exactly these 7 — a stray
top-level folder would float around unlinked.)

---

## ✍️ Writing a new article

1. Open Obsidian (vault = the `content/` folder).
2. Create a note inside the right dimension, e.g.
   `AI-and-ML/Transformers.md`. Spaces in names are fine — they become
   dashes in the URL.
3. Just write. Wikilinks (`[[Transformers]]`), tags, callouts, images pasted
   from clipboard — everything renders on the site.
4. Frontmatter is optional. Useful bits:

   ```yaml
   ---
   title: Custom Title        # otherwise the filename is used
   tags: [ml, attention]
   draft: true                # keeps the note OFF the public site
   ---
   ```

## 📁 Creating a new folder (inside a dimension)

1. In Obsidian, create the folder inside a dimension, e.g.
   `AI-and-ML/Deep-Learning/`, and add notes to it.
2. That's it — the sidebar explorer picks it up automatically, and the site
   generates a listing page for the folder.
3. Optional polish: add an `index.md` inside the new folder with a short
   heading + description, and it becomes the folder's landing page.

## 🚀 Publishing (the only command that matters)

```powershell
cd C:\Users\dhruv\spider-verse
npx quartz sync
```

This commits my changes, pulls anything remote, and pushes to GitHub —
which triggers the deploy workflow. **~2 minutes later the site is live.**

Optional commit message: `npx quartz sync -m "add transformers note"`

## 👀 Preview locally before publishing

```powershell
cd C:\Users\dhruv\spider-verse
npx quartz build --serve
```

Then open http://localhost:8080. It live-reloads as I edit. `Ctrl+C` to stop.

---

## 🧰 Rare operations

| Task | Command / where |
|---|---|
| Upgrade Quartz itself | `npx quartz update` (pulls from the original project) |
| Change colors / fonts | `quartz.config.yaml` → `theme:` block |
| Change comic effects | `quartz/styles/custom.scss` |
| Deploy logs / failures | GitHub repo → Actions tab |
| Fresh setup on a new machine | `git clone https://github.com/aroradhruv2308/spider-verse.git` → `npm i` → `npx quartz plugin install` |

## ⚠️ Remember

- This repo is **public** — never put passwords, keys, or private info in notes.
  Use `draft: true` for anything not ready for the world.
- The website never shows this README; only `content/` is published.

> *"Anyone can wear the mask."* — so go write something.
