import torch
import torch.nn.functional as F
import random
import numpy as np
import os
import matplotlib.pyplot as plt
from torch_geometric.utils import to_dense_batch



def train(model, loader, optimizer, device):
    model.train()
    total_loss = 0.0
    criterion = torch.nn.MSELoss()

    for batch in loader:
        batch = batch.to(device)
        optimizer.zero_grad()
        out = model(batch.x, batch.edge_index).view(-1)
        true_vals = batch.y.view(-1)

        loss = criterion(out, true_vals)
        loss.backward()
        optimizer.step()
        total_loss += loss.item() * batch.num_graphs

    return total_loss / len(loader.dataset)


def evaluate(model, loader, device, error_threshold, percentage_threshold=None, plot_results=False):
    model.eval()

    all_mse, all_mae, all_r2, all_accuracy = [], [], [], []
    all_true_vals, all_pred_vals = [], []

    # Leer info de normalización solo si se va a graficar
    norm_info = torch.load(os.path.join("Datasets", "normalization_info.pth"))
    max_temp_output = norm_info["max_T_outputs"].item() # Esta es la real, con la que queremos comparar nuestra predicción (Utilizar esta escala)

    with torch.no_grad():
        for data in loader:
            data = data.to(device)
            out = model(data.x, data.edge_index).view(-1)
            true_vals = data.y.view(-1)

            pred_vals = out

            total_nodos = true_vals.shape[0]
            nodos_por_grafico = data.num_nodes  # Asume nodos fijos por gráfico

            if total_nodos % nodos_por_grafico != 0:
                raise ValueError(f"El número total de nodos ({total_nodos}) no es divisible por nodos_por_grafico ({nodos_por_grafico}).")

            true_split = torch.split(true_vals, nodos_por_grafico)
            pred_split = torch.split(pred_vals, nodos_por_grafico)

            for true_graph, pred_graph in zip(true_split, pred_split):
                eps = 1e-8
                mse = F.mse_loss(pred_graph, true_graph).item()
                mae = F.l1_loss(pred_graph, true_graph).item()

                ss_res = torch.sum((true_graph - pred_graph) ** 2)
                ss_tot = torch.sum((true_graph - true_graph.mean()) ** 2) + eps
                r2 = 1 - ss_res / ss_tot

                if percentage_threshold is not None:
                    relative_error = torch.abs((true_graph - pred_graph) / (true_graph + eps)) * 100
                    within = relative_error <= percentage_threshold
                else:
                    error_threshold_norm = error_threshold / max_temp_output  # Escala normalizada
                    within = torch.abs(true_graph - pred_graph) <= error_threshold_norm

                acc = torch.sum(within).item() / len(true_graph) * 100

                all_mse.append(mse)
                all_mae.append(mae)
                all_r2.append(r2.item())
                all_accuracy.append(acc)

                all_true_vals.append(true_graph.cpu())
                all_pred_vals.append(pred_graph.cpu())
        if plot_results:
            # Tomamos una sola muestra del primer batch
            true_vals_batch = data.y.view(-1, 1)
            pred_vals_batch = out.view(-1, 1)
            batch = data.batch  # Indica qué nodo pertenece a qué grafo

            # Convierte a [batch_size, num_nodes, 1]
            true_dense, mask = to_dense_batch(true_vals_batch, batch)
            pred_dense, _ = to_dense_batch(pred_vals_batch, batch)

            for i in range(true_dense.size(0)):  # Recorremos cada gráfico
                true_graph = true_dense[i][mask[i]].squeeze().cpu()
                pred_graph = pred_dense[i][mask[i]].squeeze().cpu()

                n = true_graph.shape[0]
                lado = int(np.sqrt(n))
                if lado * lado == n:
                    plot_temperature_maps(true_graph * max_temp_output, pred_graph * max_temp_output)
                break
            else:
                print("No se encontró ninguna muestra con número de nodos cuadrado perfecto para graficar.")
    return (
    float(torch.tensor(all_mse).mean()),
    float(torch.tensor(all_mae).mean()),
    float(torch.tensor(all_r2).mean()),
    float(torch.tensor(all_accuracy).mean())
    )


def predict(model, loader, device):
    model.eval()
    all_pred_vals = []

    with torch.no_grad():
        for data in loader:
            data = data.to(device)
            out = model(data.x, data.edge_index).view(-1)

            nodos_por_grafico = data.num_nodes
            if out.shape[0] % nodos_por_grafico != 0:
                raise ValueError(f"El número total de nodos ({out.shape[0]}) no es divisible por nodos_por_grafico ({nodos_por_grafico}).")

            pred_vals_div = torch.split(out, nodos_por_grafico)
            all_pred_vals.extend([pred.cpu() for pred in pred_vals_div])

    return all_pred_vals


def plot_temperature_maps(true_vals, pred_vals):
    true_vals = true_vals.numpy()
    pred_vals = pred_vals.numpy()
    total_nodos = true_vals.shape[0]
    nodos_lado = int(np.sqrt(total_nodos))
    if nodos_lado ** 2 != total_nodos:
        raise ValueError("El número de nodos no forma cuadrado perfecto.")

    true_vals = true_vals.reshape(nodos_lado, nodos_lado)
    pred_vals = pred_vals.reshape(nodos_lado, nodos_lado)
    error_abs = np.abs(true_vals - pred_vals)

    vmin_temp = min(true_vals.min(), pred_vals.min())
    vmax_temp = max(true_vals.max(), pred_vals.max())

    fig, axes = plt.subplots(1, 3, figsize=(18, 6))

    im1 = axes[0].imshow(true_vals, cmap='jet', vmin=vmin_temp, vmax=vmax_temp)
    axes[0].set_title("Temperaturas Reales (K)")
    fig.colorbar(im1, ax=axes[0])

    im2 = axes[1].imshow(pred_vals, cmap='jet', vmin=vmin_temp, vmax=vmax_temp)
    axes[1].set_title("Temperaturas Predichas (K)")
    fig.colorbar(im2, ax=axes[1])

    im3 = axes[2].imshow(error_abs, cmap='jet')
    axes[2].set_title("Error Absoluto (K)")
    fig.colorbar(im3, ax=axes[2])

    plt.tight_layout()
    plt.show()

