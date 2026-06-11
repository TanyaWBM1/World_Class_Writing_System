# Local CLI Help

Use the system with one command from the repo root:

```powershell
python run_writer.py --topic "Why discipline isn't the problem"
```

Narrative piece:

```powershell
python run_writer.py --topic "Why discipline isn't the problem" --mode narrative --grit medium
```

Authority piece:

```powershell
python run_writer.py --topic "Most people do not need more strategy, they need honesty" --mode authority --grit medium
```

Low grit reflection:

```powershell
python run_writer.py --topic "You are tired, not lazy" --mode narrative --grit low
```

High grit correction:

```powershell
python run_writer.py --topic "Why your confusion is really avoidance" --mode authority --grit high
```

Platform-targeted run:

```powershell
python run_writer.py --topic "What people call burnout is often prolonged self-betrayal" --mode narrative --platform linkedin --length long
```
