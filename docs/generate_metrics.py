import json
import os

import investor8_sdk
import pandas as pd
from jinja2 import Template

API_KEY = os.getenv("I8_CORE_API_KEY")

def main():
    investor8_sdk.ApiClient().configuration.api_key["apiKey"] = API_KEY
    all_metrics = investor8_sdk.MetricsApi().get_list_metrics_metadata(page_size=1000)
    all_metrics_df = pd.DataFrame([d.to_dict() for d in all_metrics])
    all_metrics_desc = investor8_sdk.MetricsApi().get_list_metrics_description(page_size=1000)
    all_metrics_desc_df = pd.DataFrame([d.to_dict() for d in all_metrics_desc])[["metric_name", "description"]]
    all_metrics_df = all_metrics_df.merge(all_metrics_desc_df, on="metric_name")
    all_metrics_df = all_metrics_df.sort_values("type", ascending=False)
    metrics_list = json.loads(all_metrics_df.to_json(orient="records"))
    with open("docs/metrics/index.md.j2", "r") as reader:
        index_template = Template(reader.read())

    with open("docs/metrics/index.md", "w") as writer:
        writer.write(index_template.render({"metrics": metrics_list}))

    with open("docs/metrics/metric.md.j2", "r") as reader:
        metric_template = Template(reader.read())

    for m in metrics_list:
        with open(f"docs/metrics/{m['metric_name']}.md", "w") as writer:
            writer.write(metric_template.render({"m": m, "description": m["description"].replace("’", "'")}))

    print("Metric docs are generated successfully!")

if __name__ == '__main__':
    main()
