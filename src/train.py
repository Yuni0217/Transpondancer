from model import CNN
import datahandler as dh

import torch
import torch.nn as nn
from torch import optim
from torchsummary import summary


# Hyperparameters. We can tune these as we validate the results
epochs = 5
batch_size = 32
learning_rate = 0.001
print_every = 40

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Current device: ", device)



train_loader, test_loader = dh.pre_processor(
                                '../Dataset',
                                batchsize= batch_size)

classes = ('Arabesquae', 'Battement', 'Grand_Plié', 'Pirouette')


model = CNN().to(device)

# print(next(model.parameters()).is_cuda)

# (summary(model, (1, 90, 160))) # prints the summary of the model. 90,160 is image size


optimizer = optim.Adam(model.parameters(), lr=learning_rate)
#scheduler = ReduceLROnPlateau(optimizer, 'max', factor = 0.5, verbose=True)
criterion = nn.CrossEntropyLoss()


#    ******************** Start the training loop here ********************     #

train_loss = []
val_loss = []
n_total_steps = len(train_loader)

for e in range(epochs):
    running_loss = 0
    print(f"Epoch: {e+1}/{epochs}")

    for i, (images, labels) in enumerate(iter(train_loader)):

        # print(type(images))
        # print(type(labels))
        
        images = torch.stack(images).to(device)
        # print(images.is_cuda)
        labels = labels.to(device)
        # print(labels.is_cuda)

        # reset the grdients
        optimizer.zero_grad()
        
        output = model(images)   # 1) Forward pass
        loss = criterion(output, labels) # 2) Compute loss
        # print(loss.is_cuda)

        loss.backward()                  # 3) Backward pass
        optimizer.step()                 # 4) Update model
        
        running_loss += loss.item()
        
        # print(i)
        if i % print_every == 0:
            print (f'Epoch [{e+1}/{epochs}], Step [{i+1}/{n_total_steps}], Loss: {loss.item():.4f}')
            print(f"\tIteration: {i}\t Loss: {running_loss/print_every:.4f}")
            running_loss = 0
            
    train_loss.append(running_loss/images.shape[0])

    correct = 0
    total = 0
    # since we're not training, we don't need to calculate the gradients for our outputs
    with torch.no_grad():
        for i, (images, labels) in enumerate(iter(test_loader)):
            
            images = torch.stack(images).to(device)
            labels = labels.to(device)

            outputs = model(images)
            v_loss = criterion(outputs, labels)
            # the class with the highest energy is what we choose as prediction
            _, predicted = torch.max(outputs.data, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()
        val_loss.append(v_loss/images.shape[0])

    print('Accuracy of the network on the test images: %d %%' % (
        100 * correct / total))

# print('Finished Training')
# PATH = './cnn.pth'
# torch.save(model.state_dict(), PATH)


# with torch.no_grad():
#     correct = 0
#     total = 0
#     n_class_correct = [0 for i in range(4)]
#     n_class_samples = [0 for i in range(4)]

#     for i, (images, labels) in enumerate(iter(test_loader)):

#         images = torch.stack(images).to(device)
#         labels = labels.to(device)

#         outputs = model(images)
#         v_loss = criterion(outputs, labels)
#         # the class with the highest energy is what we choose as prediction
#         _, predicted = torch.max(outputs.data, 1)

#         total += labels.size(0)
#         correct += (predicted == labels).sum().item()

#         for i in range(batch_size):
#             label = labels[i]
#             pred = predicted[i]
#             if (label == pred):
#                 n_class_correct[label] += 1
#             n_class_samples[label] += 1

#     val_loss.append(v_loss/images.shape[0])

# print('Accuracy of the network on test images: %d %%' % (
#     100.0 * correct / total))

# for i in range(4):
#         acc = 100.0 * n_class_correct[i] / n_class_samples[i]
#         print(f'Accuracy of {classes[i]}: {acc} %')