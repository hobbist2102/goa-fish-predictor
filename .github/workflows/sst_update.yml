name: Run SST fetch

on:
  schedule:
    - cron: "0 4 * * *"  # Daily at 9:30 AM IST
  workflow_dispatch:

jobs:
  fetch-sst:
    runs-on: ubuntu-latest

    env:
      CMEMS_USER: ${{ secrets.CMEMS_USER }}
      CMEMS_PASS: ${{ secrets.CMEMS_PASS }}

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt

      - name: Configure CMEMS credentials
        run: |
          mkdir -p ~/.config/copernicusmarine
          echo "machine copernicusmarine.auth.ecmwf.int login $CMEMS_USER password $CMEMS_PASS" > ~/.netrc
          chmod 600 ~/.netrc

      - name: Run SST fetch script
        run: |
          echo "Fetching SST from CMEMS..."
          python cmems_sst.py || echo "SST fetch failed"

      - name: Commit SST data if available
        run: |
          git config user.name 'GitHub Actions'
          git config user.email 'actions@github.com'
          if ls sst_*.nc 1> /dev/null 2>&1; then
            git add sst_*.nc
            git commit -m "⬇️ Daily SST data update: $(date -u +'%Y-%m-%d')" || echo "Nothing to commit"
            git push
          else
            echo "No SST data file found to commit."
