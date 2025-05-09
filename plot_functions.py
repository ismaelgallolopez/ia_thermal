import torch
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.patches import Rectangle
from matplotlib.animation import PillowWriter
import os

#%%

def plot_sample(output,target):

    plt.style.use('default')

    plt.rcParams["figure.figsize"] = (6,4)

    plt.rcParams["font.family"] = "Times New Roman"

    plt.rcParams["font.size"] = 12

    plt.rcParams["text.usetex"] = False

    plt.rcParams["axes.titlesize"] = 11

    # Convertir los tensores a numpy y asegurarse de que están en CPU
    try:
        output_np = output.squeeze().cpu().detach().numpy()
        target_np = target.squeeze().cpu().detach().numpy()
    except:
        output_np=output
        target_np=target
    
    fig, axs = plt.subplots(1, 2, figsize=(10, 5))
    
    # Asegurarse de que las celdas de la grilla sean lo suficientemente grandes para el texto
    fig.tight_layout(pad=3.0)
    
    # Output de la red
    axs[1].imshow(output_np, cmap='viridis', interpolation='nearest')
    axs[1].title.set_text('Output')
    for i in range(output_np.shape[0]):
        for j in range(output_np.shape[1]):
            text = axs[1].text(j, i, f'{output_np[i, j]:.0f}',
                            ha="center", va="center", color="w", fontsize=6)

    # Target
    axs[0].imshow(target_np, cmap='viridis', interpolation='nearest')
    axs[0].title.set_text('Target')
    for i in range(target_np.shape[0]):
        for j in range(target_np.shape[1]):
            text = axs[0].text(j, i, f'{target_np[i, j]:.0f}',
                            ha="center", va="center", color="w", fontsize=6)

    # Calcular la diferencia
    diferencia_np =np.abs( output_np - target_np)
    
    fig2, ax2 = plt.subplots(figsize=(5, 5))
    
    # Asegurarse de que las celdas de la grilla sean lo suficientemente grandes para el texto
    fig2.tight_layout(pad=3.0)
    
    # Diferencia entre el output de la red y el target
    cax2 = ax2.imshow(diferencia_np, cmap='viridis', interpolation='nearest')
    ax2.title.set_text('Absolute Error')

    fig.colorbar(cax2)
    plt.show()


#%%
def visualizar_valores_vectoreslatentes(output, target):

    plt.style.use('default')

    plt.rcParams["figure.figsize"] = (6,4)

    plt.rcParams["font.family"] = "Times New Roman"

    plt.rcParams["font.size"] = 12

    plt.rcParams["text.usetex"] = False

    plt.rcParams["axes.titlesize"] = 11
    
    # Convert tensors to numpy and make sure they're on CPU
    if type(output) == torch.Tensor:
        output_np = output.cpu().detach().numpy()
    else:
        output_np = output
    if type(target) == torch.Tensor:
        target_np = target.cpu().detach().numpy()
    else: 
        target_np = target
    
    # Create a plot with 2 subplots: one for the output and one for the target
    fig, axs = plt.subplots(1, 2, figsize=(15, 5))
    
    # Plot the output vector
    axs[1].plot(list(range(1,10)),output_np.flatten(), marker='.', linestyle='--', color='darkcyan')
    axs[1].title.set_text('Output')
    axs[1].grid(False)
    
    # Plot the target vector
    axs[0].plot(list(range(1,10)),target_np.flatten(), marker='.', linestyle='-', color='crimson')
    axs[0].title.set_text('Target')
    axs[0].grid(False)

    # Show the plot
    plt.show()

    # Create a plot with 2 subplots: one for the output and one for the target
    fig, axs = plt.subplots(1, 1, figsize=(5, 5))
    
    # Plot the output vector
    axs.plot(list(range(1,10)),output_np.flatten(), marker='.', linestyle='--', color='darkcyan')
    axs.plot(list(range(1,10)),target_np.flatten(), marker='.', linestyle='--', color='crimson')
    axs.grid(False)

    
    # Plot the target vector
    plt.show()
    
#%%

def plot_loss_evolution(train_loss, test_loss):
    
    """
    Plot the training and validation loss
    
    Args:
    train_loss (list): list with the training loss
    test_loss (list): list with the test loss
    
    """
    
    epochs = np.arange(1, len(train_loss)+1)
    
    
    plt.plot(epochs, train_loss, label='Train', color='black')
    plt.plot(epochs, test_loss, label='Test', color='red')
    plt.xlabel('Epochs')
    plt.ylabel('Loss')
    plt.yscale('log')
    plt.legend()
    
    # Ajustar los ticks del eje x dinámicamente
    max_ticks = 10  # Número máximo de ticks que deseas mostrar
    if len(epochs) > max_ticks:
        tick_positions = np.linspace(1, len(epochs), num=max_ticks, dtype=int)
        plt.xticks(tick_positions)  # Mostrar solo los ticks seleccionados
    else:
        plt.xticks(epochs)  # Mostrar todos los ticks si hay pocos
        
    # Ajustar los límites del eje x al rango de valores de las épocas
    plt.xlim(epochs[0], epochs[-1])
    
    plt.show()
    

#%%
def plot_error_map(y_pred, y_true, i=0, t=0):
    """
    Muestra el mapa de temperaturas reales, predichas y el error (por pixel) en un instante concreto.
    Parámetros:
        y_pred: tensor con shape (B, T, 1, H, W)
        y_true: tensor con shape (B, T, 1, H, W)
        i: índice de la muestra
        t: timestep dentro de la secuencia
    """
    real = y_true[i, t].squeeze().detach().cpu().numpy()
    pred = y_pred[i, t].squeeze().detach().cpu().numpy()
    error = pred - real
    abs_error = abs(error)

    fig, axs = plt.subplots(1, 3, figsize=(14, 4))
    
    im0 = axs[0].imshow(real, cmap='hot')
    axs[0].set_title("Temperatura real")
    plt.colorbar(im0, ax=axs[0])

    im1 = axs[1].imshow(pred, cmap='hot')
    axs[1].set_title("Temperatura predicha")
    plt.colorbar(im1, ax=axs[1])

    im2 = axs[2].imshow(abs_error, cmap='viridis')
    axs[2].set_title("Absolute error")  
    plt.colorbar(im2, ax=axs[2])

    plt.tight_layout()
    plt.show()
    
#%%
def plot_se_map(y_pred, y_true, time=0, dt=1, show_pred=True, return_mse=False):
    """
    Muestra el mapa de temperaturas reales, predichas y el Squared Error (por pixel) en un instante concreto.
    
    Parámetros:
        y_pred: array con shape (T, H, W)
        y_true: tensor con shape (T, H, W)
        time: instante de tiempo real (en segundos)
        dt: intervalo de tiempo entre pasos
        show_pred: si es True, muestra el mapa de temperaturas predichas también
        return_mse: si es True, devuelve el valor del MSE
    """
    t = time // dt

    real = y_true[t, :, :]
    pred = y_pred[t, :, :]
    sq_diff = (pred - real) ** 2
    mse = np.mean(sq_diff)

    if show_pred:
        # Rango común de temperatura
        vmin = min(real.min(), pred.min())
        vmax = max(real.max(), pred.max())

        fig, axs = plt.subplots(1, 3, figsize=(14, 4))
        
        im0 = axs[0].imshow(real, cmap='hot', vmin=vmin, vmax=vmax)
        axs[0].set_title("Real temperature [K]")
        plt.colorbar(im0, ax=axs[0])

        im1 = axs[1].imshow(pred, cmap='hot', vmin=vmin, vmax=vmax)
        axs[1].set_title("Predicted temperature [K]")
        plt.colorbar(im1, ax=axs[1])

        im2 = axs[2].imshow(sq_diff, cmap='viridis')
        axs[2].set_title("Squared error [K²]")
        plt.colorbar(im2, ax=axs[2])
        
    else:
        fig, ax = plt.subplots(1, 1, figsize=(5, 4))
        
        im = ax.imshow(sq_diff, cmap='viridis')
        ax.set_title("Squared error [K²]")
        plt.colorbar(im, ax=ax)

    fig.suptitle(f'Temperature map at t = {time:.2f} s', fontsize=14)
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    plt.show()

    print(f"MSE: {mse:.8f} K^2")

    if return_mse:
        return mse
        
#%% 
def plot_nodes_evolution(y_pred, y_true, nodes_idx, dt=1, together=True, save_as_pdf=False, filename='nodes_evolution'):
    """
    Muestra la evolución temporal de las temperaturas reales y predichas en una serie de nodos.
    
    Parámetros:
        y_pred: array con shape (T, H, W)
        y_true: array con shape (T, H, W)
        nodes_idx: lista de índices de los nodos a mostrar [(idx1, idy1), (idx2, idy2), ...]
        dt: intervalo de tiempo entre cada paso de tiempo
        together: si es True, muestra todas las evoluciones en un solo gráfico
        save_as_pdf: si es True, guarda la figura como PDF en la carpeta 'figures'
        filename: nombre base del archivo (sin extensión)
    """
    time = np.arange(y_pred.shape[0]) * dt

    if together:
        plt.figure(figsize=(12, 6))
        
        for i, node_idx in enumerate(nodes_idx):
            color = plt.cm.tab10(i % 10)
            label = f'Node ({node_idx[0]}, {node_idx[1]})'

            y_true_node = y_true[:, node_idx[0], node_idx[1]]
            y_pred_node = y_pred[:, node_idx[0], node_idx[1]]

            plt.plot(time, y_true_node, label=f'{label} - Ground Truth', color=color)
            plt.plot(time, y_pred_node, 'x', label=f'{label} - Prediction', color=color)
        
        plt.xlabel('Time [s]')
        plt.ylabel('Temperature [K]')
        plt.title('Time evolution of temperature in selected nodes')
        plt.xlim(time[0], time[-1])
        plt.legend()
        plt.grid(True)
        plt.tight_layout()

        if save_as_pdf:
            os.makedirs('figures', exist_ok=True)
            plt.savefig(f'figures/{filename}.pdf', format='pdf')
        plt.show()

    else:
        fig, axs = plt.subplots(len(nodes_idx), 1, figsize=(12, 3 * len(nodes_idx)), sharex=True)
        if len(nodes_idx) == 1:
            axs = [axs]

        for i, node_idx in enumerate(nodes_idx):
            axs[i].plot(time, y_true[:, node_idx[0], node_idx[1]], label='Ground truth', color='blue')
            axs[i].plot(time, y_pred[:, node_idx[0], node_idx[1]], 'x', label='Prediction', color='orange')
            axs[i].set_title(f"Node ({node_idx[0]}, {node_idx[1]})")

            axs[i].set_ylabel('Temperature [K]')
            axs[i].set_xlim(time[0], time[-1])

            if i == len(nodes_idx) - 1:
                axs[i].set_xlabel('Time [s]')
            if i == 0:
                axs[i].legend(loc='upper right')

        fig.suptitle('Time evolution of temperature in selected nodes', fontsize=16)
        fig.align_ylabels()
        plt.tight_layout(rect=[0, 0, 1, 0.96])

        if save_as_pdf:
            os.makedirs('figures', exist_ok=True)
            fig.savefig(f'figures/{filename}.pdf', format='pdf')
        plt.show()
        
        
#%%

def compare_error_maps_2d(err1_map, err2_map, 
                          titles=("Error Map 1", "Error Map 2"),
                          return_mse=False,
                          save_as_pdf=False,
                          filename='compare_error_maps'):
    """
    Compara visualmente dos mapas de error 2D (por ejemplo, error cuadrático por píxel).

    Parámetros:
        err1_map: array (H, W) – primer mapa de error
        err2_map: array (H, W) – segundo mapa de error
        titles: tupla de strings – títulos personalizados para los mapas
        return_mse: bool – si es True, devuelve el MSE global de cada mapa
        save_as_pdf: bool – si es True, guarda la figura como PDF en 'figures'
        filename: string – nombre base del archivo (sin extensión)

    Devuelve:
        mse1, mse2: MSE global para cada mapa (si return_mse == True)
    """
    mse1 = np.mean(err1_map**2)
    mse2 = np.mean(err2_map**2)

    vmax = max(err1_map.max(), err2_map.max())

    fig, axs = plt.subplots(1, 2, figsize=(12, 4))

    im1 = axs[0].imshow(err1_map, cmap='viridis', vmin=0, vmax=vmax)
    axs[0].set_title(f"{titles[0]}\nMSE = {mse1:.6f} K²")
    plt.colorbar(im1, ax=axs[0])

    im2 = axs[1].imshow(err2_map, cmap='viridis', vmin=0, vmax=vmax)
    axs[1].set_title(f"{titles[1]}\nMSE = {mse2:.6f} K²")
    plt.colorbar(im2, ax=axs[1])

    plt.tight_layout()

    if save_as_pdf:
        os.makedirs('figures', exist_ok=True)
        plt.savefig(f'figures/{filename}.pdf', format='pdf')

    plt.show()

    if return_mse:
        return mse1, mse2
    

#%%

def plot_prediction_and_error(y_pred, y_true, t=0, cmap='hot', save_as_pdf=False, filename='prediction_and_error'):
    """
    Representa la predicción de un modelo junto con el error absoluto en cada punto.
    
    Parámetros:
        y_pred: array o tensor con shape (T, H, W) – predicciones del modelo
        y_true: array o tensor con shape (T, H, W) – valores reales del solver
        t: int – índice del tiempo que se desea visualizar
        cmap: str – esquema de colores para los mapas de temperatura
        save_as_pdf: bool – si es True, guarda la figura como PDF en 'figures'
        filename: str – nombre base del archivo (sin extensión)
    """
    # Asegurarse de que los datos estén en formato NumPy
    if isinstance(y_pred, torch.Tensor):
        y_pred = y_pred.detach().cpu().numpy()
    if isinstance(y_true, torch.Tensor):
        y_true = y_true.detach().cpu().numpy()

    # Extraer los datos en el tiempo t
    pred = y_pred[t, :, :]
    real = y_true[t, :, :]
    abs_error = np.abs(pred - real)

    # Rango común de temperatura para predicción y valores reales
    vmin = min(real.min(), pred.min())
    vmax = max(real.max(), pred.max())

    # Crear la figura con dos subplots
    fig, axs = plt.subplots(1, 2, figsize=(12, 5))

    # Mapa de predicción
    im0 = axs[0].imshow(pred, cmap=cmap, vmin=vmin, vmax=vmax)
    axs[0].set_title("Predicted Temperature [K]")
    plt.colorbar(im0, ax=axs[0])

    # Mapa de error absoluto
    im1 = axs[1].imshow(abs_error, cmap='viridis')
    axs[1].set_title("Absolute Error [K]")
    plt.colorbar(im1, ax=axs[1])

    # Ajustar diseño
    plt.tight_layout()

    # Guardar como PDF si es necesario
    if save_as_pdf:
        os.makedirs('figures', exist_ok=True)
        plt.savefig(f'figures/{filename}.pdf', format='pdf')

    # Mostrar la figura
    plt.show()
    
#%%


def generar_gif_pcb_comparacion(model_preds, solver_data, dt=1, nombre_archivo="comparison_evolution",
                                 guardar_en_figures=False, duracion_total=10.0):
    """
    Genera un GIF o animación comparando las predicciones del modelo y los datos del solver.
    Fondo blanco, texto de tiempo grande y barra de progreso con fondo.

    Args:
        model_preds (np.ndarray): Array (T, H, W) de predicciones del modelo.
        solver_data (np.ndarray): Array (T, H, W) de datos del solver (ground truth).
        dt (float): Paso temporal entre frames (en segundos).
        nombre_archivo (str or None): Nombre base del archivo (sin extensión). Si None, no se guarda.
        guardar_en_figures (bool): Si True, guarda el gif en la carpeta 'figures/' junto al notebook.
        duracion_total (float): Duración total del gif en segundos.

    Returns:
        ani (matplotlib.animation.FuncAnimation): Objeto de animación para uso en Jupyter.
    """

    assert model_preds.shape == solver_data.shape, "Las formas de model_preds y solver_data deben coincidir."
    total_frames = model_preds.shape[0]

    # Calcular fps e intervalo para mantener la duración total deseada
    fps = total_frames / duracion_total
    interval_ms = int(1000 / fps)

    # Crear figura
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 5))

    # Fondo blanco
    fig.patch.set_facecolor('white')
    ax1.set_facecolor('white')
    ax2.set_facecolor('white')

    vmin = min(model_preds.min(), solver_data.min())
    vmax = max(model_preds.max(), solver_data.max())
    im1 = ax1.imshow(model_preds[0], vmin=vmin, vmax=vmax, cmap='jet')
    im2 = ax2.imshow(solver_data[0], vmin=vmin, vmax=vmax, cmap='jet')

    ax1.set_title("Modelo", fontsize=14, color='black')
    ax2.set_title("Solver", fontsize=14, color='black')
    for ax in [ax1, ax2]:
        ax.axis('off')

    # Barra de color común
    cbar_ax = fig.add_axes([0.92, 0.2, 0.02, 0.6])
    cbar = plt.colorbar(im1, cax=cbar_ax)
    cbar.ax.yaxis.set_tick_params(color='black')
    plt.setp(cbar.ax.yaxis.get_ticklabels(), color='black', fontsize=10)


    # Barra de progreso con fondo
    progress_ax = fig.add_axes([0.25, 0.01, 0.5, 0.02])
    progress_ax.set_xlim(0, 1)
    progress_ax.set_ylim(0, 1)
    progress_ax.axis('off')
    background_bar = Rectangle((0, 0), 1, 1, color='lightgray')
    progress_bar = Rectangle((0, 0), 0, 1, color='blue')
    progress_ax.add_patch(background_bar)
    progress_ax.add_patch(progress_bar)

    # Texto del tiempo fuera de la barra
    tiempo_num = fig.text(0.5, 0.045, "0.00 s", ha='center', va='bottom', fontsize=18, color='black')

    # Función de actualización
    def update(frame):
        im1.set_data(model_preds[frame])
        im2.set_data(solver_data[frame])
        tiempo_actual = frame * dt
        progress_bar.set_width((frame + 1) / total_frames)
        tiempo_num.set_text(f"{tiempo_actual:.2f} s")
        return im1, im2, progress_bar, tiempo_num

    # Crear animación (¡sin blit!)
    ani = animation.FuncAnimation(fig, update, frames=total_frames, interval=interval_ms, blit=False)

    if nombre_archivo and guardar_en_figures:
        base_path = os.getcwd()
        carpeta = os.path.join(base_path, "figures")
        os.makedirs(carpeta, exist_ok=True)
        ruta_salida = os.path.join(carpeta, f"{nombre_archivo}.gif")
        print(f"Guardando gif en: {ruta_salida}")
        ani.save(ruta_salida, writer='pillow', fps=fps, savefig_kwargs={'facecolor': 'white'})
        print("Gif guardado.")
    plt.close()
    
    return ani


#%%


def generar_gif_error_evolucion(model_preds, solver_data, dt=1, nombre_archivo="error_evolution",
                                 guardar_en_figures=False, duracion_total=10.0):
    """
    Genera un GIF o animación mostrando la evolución del error absoluto entre las predicciones del modelo y los datos del solver.
    Fondo blanco, texto de tiempo grande y barra de progreso con fondo.

    Args:
        model_preds (np.ndarray): Array (T, H, W) de predicciones del modelo.
        solver_data (np.ndarray): Array (T, H, W) de datos del solver (ground truth).
        dt (float): Paso temporal entre frames (en segundos).
        nombre_archivo (str or None): Nombre base del archivo (sin extensión). Si None, no se guarda.
        guardar_en_figures (bool): Si True, guarda el gif en la carpeta 'figures/' junto al notebook.
        duracion_total (float): Duración total del gif en segundos.

    Returns:
        ani (matplotlib.animation.FuncAnimation): Objeto de animación para uso en Jupyter.
    """
    assert model_preds.shape == solver_data.shape, "Las formas de model_preds y solver_data deben coincidir."
    total_frames = model_preds.shape[0]

    error_abs = np.abs(model_preds - solver_data)

    # Calcular fps e intervalo para mantener la duración total deseada
    fps = total_frames / duracion_total
    interval_ms = int(1000 / fps)

    # Crear figura
    fig, ax = plt.subplots(figsize=(5, 5))
    fig.patch.set_facecolor('white')
    ax.set_facecolor('white')

    vmin = 0.0
    vmax = error_abs.max()
    im = ax.imshow(error_abs[0], vmin=vmin, vmax=vmax, cmap='hot')
    ax.set_title("Error absoluto", fontsize=14, color='black')
    ax.axis('off')

    # Barra de color
    cbar_ax = fig.add_axes([0.88, 0.2, 0.03, 0.6])
    cbar = plt.colorbar(im, cax=cbar_ax)
    cbar.ax.yaxis.set_tick_params(color='black')
    plt.setp(cbar.ax.yaxis.get_ticklabels(), color='black', fontsize=10)

    # Barra de progreso con fondo
    progress_ax = fig.add_axes([0.25, 0.01, 0.5, 0.02])
    progress_ax.set_xlim(0, 1)
    progress_ax.set_ylim(0, 1)
    progress_ax.axis('off')
    background_bar = Rectangle((0, 0), 1, 1, color='lightgray')
    progress_bar = Rectangle((0, 0), 0, 1, color='blue')
    progress_ax.add_patch(background_bar)
    progress_ax.add_patch(progress_bar)

    # Texto del tiempo
    tiempo_num = fig.text(0.5, 0.045, "0.00 s", ha='center', va='bottom', fontsize=18, color='black')

    # Función de actualización
    def update(frame):
        im.set_data(error_abs[frame])
        tiempo_actual = frame * dt
        progress_bar.set_width((frame + 1) / total_frames)
        tiempo_num.set_text(f"{tiempo_actual:.2f} s")
        return im, progress_bar, tiempo_num

    ani = animation.FuncAnimation(fig, update, frames=total_frames, interval=interval_ms, blit=False)

    if nombre_archivo:
        base_path = os.getcwd()
        carpeta = os.path.join(base_path, "figures") if guardar_en_figures else base_path
        os.makedirs(carpeta, exist_ok=True)
        ruta_salida = os.path.join(carpeta, f"{nombre_archivo}.gif")
        ani.save(ruta_salida, writer='pillow', fps=fps, savefig_kwargs={'facecolor': 'white'})
        plt.close()
    else:
        plt.close()

    return ani

#%%
def generar_gif_temperatura(temperaturas, dt=1.0, nombre_archivo="temperatura_evolucion",
                        guardar_en_figures=False, duracion_total=10.0):
    """
    Genera un GIF mostrando la evolución de la temperatura en el tiempo.

    Args:
        temperaturas (np.ndarray): Array (T, H, W) con la evolución temporal de la temperatura.
        dt (float): Paso temporal entre frames (en segundos).
        nombre_archivo (str or None): Nombre base del archivo (sin extensión). Si None, no se guarda.
        guardar_en_figures (bool): Si True, guarda el gif en la carpeta 'figures/' junto al notebook.
        duracion_total (float): Duración total del gif en segundos.

    Returns:
        ani (matplotlib.animation.FuncAnimation): Objeto de animación para uso en Jupyter.
    """
    assert temperaturas.ndim == 3, "temperaturas debe tener forma (T, H, W)"
    total_frames = temperaturas.shape[0]

    # Calcular fps e intervalo para lograr la duración deseada
    fps = total_frames / duracion_total
    interval_ms = 1000 / fps # Cambio importante aquí

    # Crear figura
    fig, ax = plt.subplots(figsize=(5, 5))
    fig.patch.set_facecolor('white')
    ax.set_facecolor('white')

    vmin = temperaturas.min()
    vmax = temperaturas.max()
    im = ax.imshow(temperaturas[0], vmin=vmin, vmax=vmax, cmap='hot')
    ax.set_title("Temperatura", fontsize=14, color='black')
    ax.axis('off')

    # Barra de color
    cbar_ax = fig.add_axes([0.88, 0.2, 0.03, 0.6])
    cbar = plt.colorbar(im, cax=cbar_ax)
    cbar.ax.yaxis.set_tick_params(color='black')
    plt.setp(cbar.ax.yaxis.get_ticklabels(), color='black', fontsize=10)

    # Barra de progreso
    progress_ax = fig.add_axes([0.25, 0.01, 0.5, 0.02])
    progress_ax.set_xlim(0, 1)
    progress_ax.set_ylim(0, 1)
    progress_ax.axis('off')
    background_bar = Rectangle((0, 0), 1, 1, color='lightgray')
    progress_bar = Rectangle((0, 0), 0, 1, color='red')
    progress_ax.add_patch(background_bar)
    progress_ax.add_patch(progress_bar)

    # Texto del tiempo
    tiempo_num = fig.text(0.5, 0.045, "0.00 s", ha='center', va='bottom', fontsize=18, color='black')

    # Función de actualización
    def update(frame):
        im.set_data(temperaturas[frame])
        tiempo_actual = frame * dt
        progress_bar.set_width((frame + 1) / total_frames)
        tiempo_num.set_text(f"{tiempo_actual:.2f} s")
        return im, progress_bar, tiempo_num

    ani = animation.FuncAnimation(fig, update, frames=total_frames, interval=interval_ms, blit=False)

    if nombre_archivo:
        base_path = os.getcwd()
        carpeta = os.path.join(base_path, "figures") if guardar_en_figures else base_path
        os.makedirs(carpeta, exist_ok=True)
        ruta_salida = os.path.join(carpeta, f"{nombre_archivo}.gif")
        writer = PillowWriter(fps=fps)
        ani.save(ruta_salida, writer=writer, savefig_kwargs={'facecolor': 'white'})
        plt.close()
    else:
        plt.close()

    return ani


#%%
def plot_mae_per_pixel(model, dataloader, dataset, device, sample_idx=0):
    """
    Calcula y grafica el error absoluto medio (MAE) por píxel acumulado en el tiempo para una muestra del dataloader.
    Compatible con modelos que usan (x, y) o (x, t, y).
    """
    model.eval()
    model.to(device)
    with torch.no_grad():
        for batch in dataloader:
            if len(batch) == 3:
                x, t, y = batch
                x, t, y = x.to(device), t.to(device), y.to(device)
                y_pred = model(x, t)
            else:
                x, y = batch
                x, y = x.to(device), y.to(device)
                y_pred = model(x)
            break  # solo un batch

    y_true = y[sample_idx].squeeze(1).cpu()       # (T, 13, 13)
    y_pred = y_pred[sample_idx].squeeze(1).cpu()  # (T, 13, 13)

    error_map = torch.mean(torch.abs(y_true - y_pred), dim=0)  # (13, 13)
    error_map_real = error_map * dataset.T_outputs_std.cpu()  # (13, 13)

    plt.figure(figsize=(5, 5))
    plt.imshow(error_map_real, cmap='hot')
    plt.colorbar(label="MAE acumulado[K]")
    plt.title("Mapa de error absoluto medio por píxel")
    plt.axis('off')
    plt.tight_layout()
    plt.show()



    
    
#%%
def plot_mae_per_frame(model, dataloader, dataset, device, sample_idx=0):
    """
    Calcula y grafica el error absoluto medio (MAE) por paso temporal en escala original (desnormalizada)
    para una muestra del dataloader. Compatible con modelos que usan (x, y) o (x, t, y).
    """
    model.eval()
    model.to(device)
    with torch.no_grad():
        for batch in dataloader:
            if len(batch) == 3:
                x, t, y = batch
                x, t, y = x.to(device), t.to(device), y.to(device)
                y_pred = model(x, t)
            else:
                x, y = batch
                x, y = x.to(device), y.to(device)
                y_pred = model(x)
            break  # solo un batch

    y_true = y[sample_idx].squeeze(1).cpu()       # (T, 13, 13)
    y_pred = y_pred[sample_idx].squeeze(1).cpu()  # (T, 13, 13)

    # Desnormalizar salidas
    std = dataset.T_outputs_std.cpu()
    y_true_denorm = y_true * std
    y_pred_denorm = y_pred * std

    # MAE por paso temporal
    mae_per_t = torch.mean(torch.abs(y_true_denorm - y_pred_denorm), dim=(1, 2))  # (T,)

    plt.figure(figsize=(8, 4))
    plt.plot(mae_per_t, marker='o')
    plt.title("Error absoluto medio por paso temporal (desnormalizado)")
    plt.xlabel("Paso temporal t")
    plt.ylabel("MAE [K]")
    plt.grid(True)
    plt.tight_layout()
    plt.show()

    # return mae_per_t

