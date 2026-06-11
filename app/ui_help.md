# Local Dashboard Help

Setup

- The app reads `OPENAI_API_KEY` from `openai.env`.
- `openai.env` must live at `C:\Users\Billionaire Mind DT\World_Class_Writing_System\openai.env`.
- Inside that file, add `OPENAI_API_KEY=your_real_key_here`.
- Do not store a real key in tracked repo files.

Launch

```powershell
python app/dashboard.py
```

Dashboard layout

- Left column: `Writing Setup` and `Actions`
- Right column: `Last Run Summary`, `What each field does`, and `How to use this dashboard`
- Lower full-width area: `Governed Output`, `Raw LLM Output`, and `Evaluation Summary`

Quick start

- Start with an idea or paste something you already wrote.
- Then click `Run + Validate`.

Action buttons

- `Run`
  Generate or refine only
- `Run + Validate`
  Full governed execution
- `Reset`
  Clear current form inputs

What this dashboard does

- It sends your topic and settings to the OpenAI API for a raw first draft.
- It saves the raw draft as `raw_llm_output.txt`.
- It runs the repo governance path over that draft.
- It saves the governed result as `final_governed_output.txt`.
- It writes `evaluation_report.json`, `enforcement_report.json`, and `run_summary.json` into `runs/`.

Raw draft vs governed output

- `raw_llm_output.txt` is the direct LLM first draft before repo governance.
- `final_governed_output.txt` is the same draft after voice enforcement, lexical grounding, grit handling, phrase diversity, and validation-aware governance.

What each field does

- `How are you starting this piece?`
  Choose whether you're starting fresh or refining something you already wrote.
- `What are you writing about?`
  This is what your piece is about. It can be rough. The system will help shape it.
- `Paste your writing here`
  Only used in refine mode. Paste your draft and the system will strengthen it without changing your voice.
- `Which system mode do you want?`
  Chooses the logic path.
  `Creative Writing` = imagination-first
  `ACF Lite` = reality-first and claim-disciplined
- `Who should sound like they are speaking?`
  Chooses the voice profile.
  Example: `Tanya Lawson`
- `How sharp should the tone be?`
  Controls how softly or sharply truth is delivered.
  `low` = gentle
  `medium` = balanced
  `high` = direct
  `extreme` = very sharp, use sparingly
- `Where will this be published?`
  Adapts the output for where it will be used.
  Examples: `none`, `twitter`, `linkedin`, `instagram`, `youtube`, `reddit`
- `How long should it be?`
  Controls output size.
  `short`, `medium`, `long`
- `What creative pattern should guide the draft?`
  Creative Writing only. Controls the imaginative framing style.
- `Keep human texture turned on`
  Creative Writing only. Keeps lived detail and human roughness in the writing.
- `What claim or topic are you testing?`
  ACF Lite only. The claim or disciplined topic to examine.
- `What is the defined window?`
  ACF Lite only. The time period in which the claim should be tested.
  Example: `30 days`
- `What outside reality check could prove or disprove this?`
  ACF Lite only. The external collider.
  Example: `actual sales calls`, `mentor review`, `client feedback`, `court filing outcome`
- `What uncertainty should be stated clearly?`
  ACF Lite only. A sentence that admits what is not fully known yet.
  Example: `I may be wrong if the market shifts or if the data changes.`
- `When should results become visible?`
  ACF Lite only. When you expect observable results.
  Example: `within 14 days` or `by the next court date`
- `Which OpenAI model should draft first?`
  Picks the model used for the raw first draft.
- `How much variation should the draft have?`
  Higher = more variation. Lower = tighter drafting.
- `How much draft length can the model use?`
  Caps the raw LLM response size.
- `Show raw LLM output`
  Shows or hides the raw draft panel.
How to use this dashboard

If you are starting fresh, choose `Generate from idea`, enter the topic, pick the mode and controls, then click `Run + Validate`.

If you already wrote something, choose `Refine something I already wrote`, paste the draft, keep `Preserve original structure` on unless you want freer reshaping, then click `Run + Validate`.

Buttons

- `Run`
  Draft generation only.
- `Run + Validate`
  Full governed execution.
- `Reset`
  Clears the form and resets the dashboard.
- `Open raw draft`
  Opens the latest `raw_llm_output.txt`.
- `Open governed output`
  Opens the latest `final_governed_output.txt`.
- `Open evaluation report`
  Opens the latest `evaluation_report.json`.

Notes

- Creative Writing and ACF Lite are separate runtime modes.
- They cannot run at the same time.
- The OpenAI backend is draft generation only.
- Validators and repo governance remain final authority.
- If `openai.env` is missing, if `OPENAI_API_KEY` is missing inside it, or if the API call fails, the dashboard shows a warning and writes a local error report without exposing secrets.
