import os
import pandas as pd
from datetime import datetime


def saveReportAll(models, model_totals):
    # Create Reports folder if it doesn't exist
    os.makedirs("Reports", exist_ok=True)

    # Timestamped filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"AllModels_{timestamp}.csv"
    filepath = os.path.join("Reports", filename)

    # Collect data
    rows = []
    for model in models:
        totals = model_totals[model]
        avg_clarity = round(totals["clarity"] / max(totals["turns"], 1), 2)

        rows.append({
            "Model": model,
            "Tokens": totals["tokens"],
            "Words": totals["words"],
            "Estimated Cost ($)": round(totals["cost"], 4),
            "ML Keywords Used": totals["key_terms"],
            "Avg. Clarity Score": avg_clarity,
            "Turns": totals["turns"]
        })

    # Create DataFrame and save to CSV
    df = pd.DataFrame(rows)
    df.to_csv(filepath, index=False)

    return filepath  # Optional: return for display

