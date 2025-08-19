# Hi there, I'm Chinmaya Padhi 👋

🎓 MTech in VLSI & Embedded Systems | Data Analyst | ML Enthusiast  

## 🌱 About Me  
- 🔭 I’m currently working on VLSI, Machine Learning, and AI.  
- 🎯 Interests: Data Science, Embedded Systems, and Semiconductor Design.  
- 📚 Learning new tools like Silvaco TCAD , verilog , LTspice, and Logisim.  
- ✍️ Passionate about **AI in VLSI** and industry-level research.  

## 🔗 Connect with Me  
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-blue?style=for-the-badge&logo=linkedin)](https://www.linkedin.com/in/chinmaya-padhi1234)  
[![GitHub](https://img.shields.io/badge/GitHub-Follow-black?style=for-the-badge&logo=github)](https://github.com/chinmaya-padhi)  
[![YouTube](https://img.shields.io/badge/YouTube-Subscribe-red?style=for-the-badge&logo=youtube)](https://www.youtube.com/@ChinmayaTechDive)  


## 📊 GitHub Stats  
![GitHub Stats](https://github-readme-stats-sigma-five.vercel.app/api?username=chinmaya-padhi&show_icons=true&theme=radical)


## Languages I've used (across my public GitHub repos)

![Languages I've used](./languages_pie.png)


## ⚡ Fun Fact  
💡 I love working on **real-world industry projects** and collaborating on open-source work!  

name: Update languages pie

on:
  schedule:
    - cron: '0 0 * * 1'   # every Monday at 00:00 UTC (adjust if wanted)
  workflow_dispatch:
  push:
    branches:
      - main

jobs:
  generate:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4
        with:
          persist-credentials: true

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Install deps
        run: |
          python -m pip install --upgrade pip
          pip install requests matplotlib

      - name: Generate languages pie
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          python .github/scripts/generate_lang_pie.py --user YOUR_GITHUB_USERNAME --out languages_pie.png

      - name: Commit and push image if changed
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
          git add languages_pie.png || true
          if ! git diff --staged --quiet; then
            git commit -m "chore: update languages_pie.png"
            git push
          else
            echo "No changes to commit"
          fi
