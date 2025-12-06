import pandas as pd, json
from pathlib import Path

DATA_PATH = Path("data")/"axonius_identities_sample.csv"
BASELINE_PATH = Path("config")/"baseline_roles.json"
OUTPUT_PATH = Path("data")/"drift_report.csv"
SUMMARY_PATH = Path("data")/"drift_summary.txt"

df = pd.read_csv(DATA_PATH)
baseline = json.load(open(BASELINE_PATH))

def allowed(job): return set(baseline.get(job, {}).get("allowed_ad_groups", []))

rows=[]
for _, r in df.iterrows():
    job = (r.get("job_title") or "UNKNOWN").strip()
    upn = r.get("user_principal_name") or r.get("email") or "unknown"
    groups = set([g.strip() for g in str(r.get("ad_groups","")).split(";") if g.strip()])
    drift = groups - allowed(job)
    if drift:
        rows.append({
            "user": upn, "job_title": job,
            "current_groups": ";".join(sorted(groups)),
            "allowed_groups": ";".join(sorted(allowed(job))),
            "drift_groups": ";".join(sorted(drift))
        })

out = pd.DataFrame(rows)
if not out.empty:
    out.to_csv(OUTPUT_PATH, index=False)
    with open(SUMMARY_PATH,"w") as f:
        f.write(f"Users with drift: {len(out)}\n")
        f.write(out["job_title"].value_counts().to_string())
    print(f"✅ Drift detected for {len(out)} user(s). See {OUTPUT_PATH}")
else:
    print("✅ No privilege drift detected based on baseline.")
