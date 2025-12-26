import mlflow
import torch

mlflow.set_tracking_uri("http://127.0.0.1:5000")
mlflow.set_experiment("smart-hello")

with mlflow.start_run(run_name="sanity-check"):
    x = torch.tensor([1.0, 2.0, 3.0])
    mlflow.log_param("vector_len", len(x))
    mlflow.log_metric("sum", float(x.sum()))
    print("Logged to MLflow with sum =", x.sum().item())
