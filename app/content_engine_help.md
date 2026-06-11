# Content Engine Help

Launch from the project folder:

```powershell
python app/content_engine_page.py
```

What it does:

- accepts one or more topics
- generates a long-form base piece for each topic
- generates platform variants for the selected platforms
- preserves raw and governed outputs
- runs validation and ranking
- supports review, approval, rejection, and approved-bundle export

Batch inputs:

- topics, one per line
- mode
- grit
- voice profile
- selected platforms
- desired output count per topic
- model
- temperature
- max tokens

Approval states:

- `generated`
- `needs_review`
- `approved`
- `rejected`

Export behavior:

- approved items are copied into a clean export folder under the batch run directory
- export manifests are recorded locally
- no auto-posting is performed
