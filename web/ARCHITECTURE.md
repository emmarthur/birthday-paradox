# Architecture

```
index.html + app.js
    POST /api/sample          → run_sample()     → one group + match
    GET  /stream/monte-carlo  → monte_carlo_stream() → SSE progress + done

birthday_core.py  ← same rules as reference/birthdayparadox.py (getBirthdays / getMatch)
```

Monte Carlo runs in the SSE generator thread (blocking). Expect several seconds for 100,000 trials.
