import os
import investor8_sdk
from jinja2 import Template

API_KEY = os.getenv("I8_CORE_API_KEY")

def main():
    investor8_sdk.ApiClient().configuration.api_key["apiKey"] = API_KEY
    all_metrics = investor8_sdk.MetricsApi().get_list_metrics_metadata(page_size=1000)
    all_metrics = sorted(all_metrics, key=lambda m: m.type, reverse=True)

    with open("docs/metrics/index.md.j2", "r") as reader:
        index_template = Template(reader.read())

    with open("docs/metrics/index.md", "w") as writer:
        writer.write(index_template.render({"metrics": all_metrics}))

    with open("docs/metrics/metric.md.j2", "r") as reader:
        metric_template = Template(reader.read())

    for m in all_metrics:
        with open(f"docs/metrics/{m.metric_name}.md", "w") as writer:
            writer.write(metric_template.render({"m": m, "description": m.description.replace("’", "'")}))

    print("Metric docs are generated successfully!")

if __name__ == '__main__':
    main()
