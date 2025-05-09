#%%
import torch
import numpy as np
import time

#Pytorch dataset
from torch.utils.data import Dataset, DataLoader
from torch.utils.data.sampler import SubsetRandomSampler

# PyTorch model
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.optim.lr_scheduler import ReduceLROnPlateau

class PCBDataset(Dataset):
    def __init__(self, inputs_dataset, outputs_dataset, scalar_dataset):

        assert len(inputs_dataset) == len(outputs_dataset) == len(scalar_dataset), "All datasets must be of the same size"
        self.inputs_dataset = inputs_dataset
        self.outputs_dataset = outputs_dataset
        self.scalar_dataset = scalar_dataset

    def __len__(self):

        return len(self.inputs_dataset)

    def __getitem__(self, idx):

        input_data = self.inputs_dataset[idx]
        output_data = self.outputs_dataset[idx]
        scalar_data = self.scalar_dataset[idx]
        return input_data, output_data, scalar_data
    

class StandardScaler3D:
    def __init__(self):
        self.mean = None
        self.std = None

    def fit(self, tensor):
        """
        Calcula la media y la desviación estándar del tensor a lo largo de las dimensiones especificadas
        y las almacena para su uso posterior.
        """
        # Calcula la media y la desviación estándar para el tensor
        # Suponiendo que tensor tiene forma [batch_size, channels, height, width]
        self.mean = tensor.mean(dim=[0, 2, 3], keepdim=True)
        self.std = tensor.std(dim=[0, 2, 3], keepdim=True)

    def transform(self, tensor):
        """
        Estandariza el tensor usando la media y la desviación estándar calculadas en el método fit.
        """
        if self.mean is None or self.std is None:
            raise RuntimeError("StandardScaler3D no ha sido ajustado con datos; por favor, llama a .fit() primero.")
        return (tensor - self.mean) / self.std

    def fit_transform(self, tensor):
        """
        Combina los métodos fit y transform en una sola llamada para conveniencia.
        """
        self.fit(tensor)
        return self.transform(tensor)

class GlobalStandardScaler:
    def __init__(self):
        self.mean = None
        self.std = None

    def fit(self, tensor):
        """
        Calcula la media y la desviación estándar de todo el tensor.
        """
        self.mean = tensor.mean()
        self.std = tensor.std()

    def transform(self, tensor):
        """
        Estandariza el tensor usando la media y la desviación estándar globales calculadas en el método fit.
        """
        if self.mean is None or self.std is None:
            raise RuntimeError("GlobalStandardScaler no ha sido ajustado con datos; por favor, llama a .fit() primero.")
        return (tensor - self.mean) / (self.std + 1e-6)  # Se añade un pequeño valor para evitar la división por cero

    def fit_transform(self, tensor):
        """
        Combina los métodos fit y transform en una sola llamada para conveniencia.
        """
        self.fit(tensor)
        return self.transform(tensor)

    def inverse_transform(self, tensor):
        """
        Desestandariza el tensor usando la media y la desviación estándar globales calculadas en el método fit.
        """
        if self.mean is None or self.std is None:
            raise RuntimeError("GlobalStandardScaler no ha sido ajustado con datos; por favor, llama a .fit() primero.")
        return tensor * self.std + self.mean

#%%
##############################################
############# CARGANDO LOS DATOS #############
##############################################
    
dataset = torch.load('PCB_dataset.pth')

#Estandarizar los datos
scaler_input = StandardScaler3D()
scaler_scalar = GlobalStandardScaler()
scaler_output = GlobalStandardScaler()

scaled_input = scaler_input.fit_transform(dataset.inputs_dataset)
scaled_scalar = scaler_scalar.fit_transform(dataset.scalar_dataset)
scaled_output = scaler_output.fit_transform(dataset.outputs_dataset)


dataset = PCBDataset(scaled_input, scaled_output, scaled_scalar)

# Separando Train and Test
train_cases = 1900
test_cases = 100

batch_size = 64
test_size = 0.0032
num_train = int(len(dataset))
indices = list(range(num_train))
np.random.shuffle(indices)
split = int(np.floor(num_train * test_size))
train_idx, test_idx = indices[split:], indices[:split]

train_sampler = SubsetRandomSampler(train_idx)
test_sampler = SubsetRandomSampler(test_idx)

#Creando los Datalaoders
train_loader = DataLoader(dataset, batch_size=batch_size, sampler=train_sampler)
test_loader = DataLoader(dataset, batch_size=batch_size, sampler=test_sampler)



#%%
###################################################
############# ARQUITECTURA DEL MODELO #############
###################################################

class Net(nn.Module):
    def __init__(self):
        super(Net, self).__init__()

        #Concolutional
        self.conv1 = nn.Conv2d(2, 6, 3, padding=1)
        self.conv1_2 = nn.Conv2d(6, 6, 3, padding=1)
        self.conv1_3 = nn.Conv2d(6, 6, 3, padding=1)

        self.conv2 = nn.Conv2d(6, 12, 3, padding=1)
        self.conv2_2 = nn.Conv2d(12, 12, 3, padding=1)
        self.conv2_3 = nn.Conv2d(12, 12, 3, padding=1)

        self.conv3 = nn.Conv2d(12, 24, 3, padding=1)
        self.conv3_2 = nn.Conv2d(24, 24, 3, padding=1)
        self.conv3_3 = nn.Conv2d(24, 24, 3, padding=1)

        #Pooling
        self.adaptative_pool = nn.AdaptiveMaxPool2d((8,8))
        self.pool = nn.MaxPool2d(2,2)

        #Scalar
        self.fc_scalar = nn.Linear(1, 32)

        #MLP
        self.fc1_1 = nn.Linear(4 * 4 * 24 + 32, 416)
        self.fc1_2 = nn.Linear(416,416)
        self.fc2 = nn.Linear(416,208)
        self.fc3 = nn.Linear(208,160)

        #Decoder
        self.dconv1 = nn.Conv2d(10, 20, 3, padding=1)
        self.dconv1_2 = nn.Conv2d(20, 20, 3, padding=1)
        self.dconv1_3 = nn.Conv2d(20, 20, 3, padding=1)

        self.dconv2 = nn.Conv2d(20, 20, 3, padding=1)
        self.dconv2_2 = nn.Conv2d(20, 20, 3, padding=1)
        self.dconv2_3 = nn.Conv2d(20, 1, 3, padding=1)



        self.dropout = nn.Dropout(p=0)


    def forward(self, x, scalar):

        #Parte Encoder
        x = F.relu(self.conv1(x))
        x = F.relu(self.conv1_2(x))
        x = F.relu(self.conv1_3(x))

        x = self.adaptative_pool(x)

        x = F.relu(self.conv2(x))
        x = F.relu(self.conv2_2(x))
        x = F.relu(self.conv2_3(x))

        x = self.pool(x)

        x = F.relu(self.conv3(x))
        x = F.relu(self.conv3_2(x))
        x = F.relu(self.conv3_3(x))

        x = torch.flatten(x, 1)

        #Parte Tenv
        scalar = F.relu(self.fc_scalar(scalar))

        #Parte MLP conjunto
        x = torch.cat((x,scalar), dim=1)
        x = F.relu(self.fc1_1(x))
        x = self.dropout(x)
        x = F.relu(self.fc1_2(x))
        x = self.dropout(x)
        x = F.relu(self.fc2(x))
        x = self.dropout(x)
        x = F.relu(self.fc3(x))

        #Parte Decoder
        x = x.view(x.size(0), 10, 4, 4)
        x = F.interpolate(x, size=(8,8), mode='bilinear',align_corners=True)
        x = F.relu(self.dconv1(x))
        x = F.relu(self.dconv1_2(x))
        x = F.relu(self.dconv1_3(x))
        x = F.interpolate(x, size=(13,13), mode='bilinear', align_corners=False)
        x = F.relu(self.dconv2(x))
        x = F.relu(self.dconv2_2(x))
        x = self.dconv2_3(x)


        return x
    
model = Net()
model.cuda()
criterion = nn.MSELoss()
optimizer = optim.Adam(model.parameters(), lr=0.0001)
scheduler = ReduceLROnPlateau(optimizer, mode='min', factor=0.1, patience=30)
last_test_loss = np.inf

#%%
######################################
############# TRAIN LOOP #############
######################################

num_epochs = 500

for epoch in range(num_epochs):
    model.train()
    total_loss = 0
    num_batches = len(train_loader)
    for batch, target, scalar in train_loader: 

        
        optimizer.zero_grad()

        scalar = scalar.view(scalar.size(0),1)
        batch, scalar, target = batch.cuda(), scalar.cuda(), target.cuda()

        # Forward pass
        outputs = model.forward(batch, scalar)
        outputs = outputs.view(outputs.size(0),13,13)

        #Añadir criterios de fallo
        T_interfaces = torch.zeros((target.size(0), 2, 2))
        T_interfaces[:,0,0], T_interfaces[:,0,1], T_interfaces[:,1,0], T_interfaces[:,1,1] = target[:,0,0], target[:,0,12], target[:,12,0], target[:,12,12]

        outputs_interfaces = torch.zeros((outputs.size(0),2,2))
        outputs_interfaces[:,0,0], outputs_interfaces[:,0,1], outputs_interfaces[:,1,0], outputs_interfaces[:,1,1] = outputs[:,0,0], outputs[:,0,12], outputs[:,12,0], outputs[:,12,12]

        T_componentes = torch.zeros((target.size(0),2,2))
        T_componentes[:,0,0], T_componentes[:,0,1], T_componentes[:,1,0], T_componentes[:,1,1] = target[:,6,3], target[:,6,9], target[:,3,6], target[:,9,6]

        outputs_componentes = torch.zeros((outputs.size(0),2,2))
        outputs_componentes[:,0,0], outputs_componentes[:,0,1], outputs_componentes[:,1,0], outputs_componentes[:,1,1] = outputs[:,6,3], outputs[:,6,9], outputs[:,3,6], target[:,9,6]

        loss = (2*criterion(outputs, target) + criterion(outputs_interfaces,T_interfaces) + criterion(outputs_componentes,T_componentes))/4.
        #loss = criterion(outputs, target)

        # Backward pass and optimize
        loss.backward()
        optimizer.step()
        total_loss += loss.item()

    avg_loss = total_loss/num_batches


    scheduler.step(avg_loss)


    last_lr = scheduler.optimizer.param_groups[0]['lr']

    total_loss = 0.0
    total_batches = 0

    with torch.no_grad(): 
        for batch, target, scalar in test_loader:

            # Prepare the data and target
            scalar = scalar.view(scalar.size(0), 1)
            batch, scalar, target = batch.cuda(), scalar.cuda(), target.cuda()

            # Forward pass
            outputs = model(batch, scalar)
            outputs = outputs.view(outputs.size(0),13,13)

            loss = criterion(outputs, target)

            # Accumulate the loss
            total_loss += loss.item()
            total_batches += 1

    # Compute the average loss over all batches
    avg_test_loss = total_loss / total_batches

    print(f"Epoch [{epoch+1}/{num_epochs}], Loss: {avg_loss:.8f}, Current LR: {last_lr}")
    if avg_test_loss < last_test_loss:
        print("{:.8f} -----> {:.8f}   Saving...".format(last_test_loss,avg_test_loss))
        torch.save(model.state_dict(), 'modelos\modelo_malo.pth')
        last_test_loss = avg_test_loss

# %%
######################################
############# LOAD MODEL #############
######################################

model.load_state_dict(torch.load('modelos\modelo_bueno.pth'))
model.eval()

# Variables to track losses and the number of batches
total_loss = 0.0
total_batches = 0

with torch.no_grad(): 
    for batch, target, scalar in test_loader:

        # Prepare the data and target
        scalar = scalar.view(scalar.size(0), 1)
        batch, scalar, target = batch.cuda(), scalar.cuda(), target.cuda()

        # Forward pass
        outputs = model(batch, scalar)
        outputs = outputs.view(outputs.size(0),13,13)

        loss = criterion(outputs, target)

        # Accumulate the loss
        total_loss += loss.item()
        total_batches += 1

# Compute the average loss over all batches
avg_test_loss = total_loss / total_batches
print(f'Test Loss: {avg_test_loss:.6f}')
last_test_loss = avg_test_loss
total_params = sum(p.numel() for p in model.parameters())
print(f"Total number of parameters: {total_params}")


#%%
#####################################
############# TEST LOOP #############
#####################################

    # Ensure the model is in evaluation mode
model.eval()

# Variables to track losses and the number of batches
total_loss = 0.0
total_batches = 0

with torch.no_grad(): 
    for batch, target, scalar in test_loader:

        # Prepare the data and target
        scalar = scalar.view(scalar.size(0), 1)
        batch, scalar, target = batch.cuda(), scalar.cuda(), target.cuda()

        # Forward pass
        outputs = model(batch, scalar)
        outputs = outputs.view(outputs.size(0),13,13)

        outputs = scaler_output.inverse_transform(outputs)
        target = scaler_output.inverse_transform(target)

        loss = criterion(outputs, target)

        # Accumulate the loss
        total_loss += loss.item()
        total_batches += 1

# Compute the average loss over all batches
avg_test_loss = total_loss / total_batches
print(f'Test Loss: {avg_test_loss:.6f}')

# %%
##############################################
############# MOSTRAR RESULTADOS #############
##############################################
import matplotlib.pyplot as plt

plt.style.use('default')

plt.rcParams["figure.figsize"] = (6,4)

#plt.rcParams["font.family"] = "Times New Roman"

plt.rcParams["font.family"] = "lmroman10-regular"

plt.rcParams["font.size"] = 12

plt.rcParams["text.usetex"] = True

plt.rcParams["axes.titlesize"] = 11

model.eval()
# Función para visualizar el output de la red y el target
def visualizar_valores_pixeles(output, target):
    # Convertir los tensores a numpy y asegurarse de que están en CPU
    output_np = output.squeeze().cpu().detach().numpy()
    target_np = target.squeeze().cpu().detach().numpy()
    
    fig, axs = plt.subplots(1, 3, figsize=(10, 5), gridspec_kw={'width_ratios': [1, 1, 0.06]})
    
    # Output de la red
    im1 = axs[1].imshow(output_np, cmap='viridis', interpolation='nearest')
    axs[1].title.set_text('Output')
    
    # Target
    im0 = axs[0].imshow(target_np, cmap='viridis', interpolation='nearest')
    axs[0].title.set_text('Target')
    
    # Añadir una sola barra de color para ambas imágenes
    cbar = fig.colorbar(im1, cax=axs[2], orientation='vertical')
    
    # Asegurarse de que las celdas de la grilla sean lo suficientemente grandes para el texto
    fig.tight_layout(pad=3.0)
    
    plt.savefig('completa.png', dpi=300, bbox_inches='tight')
    plt.show()


def visualizar_diferencia_pixeles(output, target):
    # Convertir los tensores a numpy y asegurarse de que están en CPU
    output_np = output.squeeze().cpu().detach().numpy()
    target_np = target.squeeze().cpu().detach().numpy()
    
    # Calcular la diferencia
    diferencia_np =np.abs( output_np - target_np)
    
    fig, ax = plt.subplots(figsize=(5, 5))
    
    # Asegurarse de que las celdas de la grilla sean lo suficientemente grandes para el texto
    fig.tight_layout(pad=3.0)
    
    # Diferencia entre el output de la red y el target
    cax = ax.imshow(diferencia_np, cmap='viridis', interpolation='nearest')
    ax.title.set_text('Absolute Error')
    # for i in range(diferencia_np.shape[0]):
    #     for j in range(diferencia_np.shape[1]):
    #         text = ax.text(j, i, f'{diferencia_np[i, j]:.f}',
    #                        ha="center", va="center", color="w", fontsize=6)
    
    fig.colorbar(cax)
    plt.savefig('completa error.png', dpi=300, bbox_inches='tight')
    plt.show()

count = 0 
with torch.no_grad(): 
    for batch, target, scalar in test_loader:

        # Prepare the data and target
        scalar = scalar.view(scalar.size(0), 1)
        batch, scalar, target = batch.cuda(), scalar.cuda(), target.cuda()

        # Forward pass
        outputs = model(batch, scalar)
        outputs = scaler_output.inverse_transform(outputs)
        target = scaler_output.inverse_transform(target)
        for i in range(1):
            visualizar_valores_pixeles(outputs[i], target[i])
            visualizar_diferencia_pixeles(outputs[i], target[i])
            count += 1
        if count>= 1: break
        



# %%
