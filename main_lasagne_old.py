# -*- coding: utf-8 -*-
"""
Spyder Editor
 
main script for training/classifying
"""
if not '__file__' in vars(): __file__= u'C:/Users/Simon/dropbox/Uni/Masterthesis/AutoSleepScorer/main.py'
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))+'/ANN')
import numpy as np
import lasagne
from theano import tensor as T
import theano
#from custom_analysis import Analysis
import matplotlib.pyplot as plt
if not 'sleeploader' in vars() : import sleeploader  # prevent reloading module
import tools
import time
import sklearn
from sklearn import metrics
from sklearn.preprocessing import scale
import matplotlib
matplotlib.rcParams['figure.figsize'] = (10, 3)
import scipy
try:
    with open('count') as f:
        counter = int(f.read())
except IOError:
    print('No previous experiment?')
    counter = 0
     
with open('count', 'w') as f:
  f.write(str(counter+1))        
#%%
#def main():
batch_size = 64
neurons = 25
layers = 3
epochs= 200
chunk_size = 3000
clipping = 25
decay = 1e-5
cutoff = None
future = 0
comment = 'Lasagna test'
#link = L.LSTM
gpu=-1
 
#result  = [str(neurons) + ': '+ str(runRNN(neurons, layers, epochs, clipping, decay, cutoff, link, gpu, batch_size, comment)) for neurons in nneurons]
 
#%%
print(comment)
if os.name == 'posix':
    datadir  = '/home/simon/sleep/'
#    datadir  = '/home/simon/vinc/'
    datadir = '/media/simon/Windows/sleep/corrupted'

else:
    datadir = 'c:\\sleep\\data\\'
#    datadir = 'C:\\sleep\\vinc\\brainvision\\correct\\'
    datadir = 'C:\\sleep\\corrupted\\'

 
 
sleep = sleeploader.SleepDataset(datadir)

#sleep.load(selection, force_reload=False, shuffle=True, chunk_len=chunk_size)

#sleep.load_object('adults.dat')
sleep.load_object()

sleep.shuffle_data()
train_data, train_target = sleep.get_train()
test_data, test_target   = sleep.get_test()
train_data = train_data[:,:,1]
test_data = test_data[:,:,1]

test_data    = scipy.stats.mstats.zmap(test_data, train_data , axis = None)
train_data   = scipy.stats.mstats.zmap(train_data, train_data, axis = None)


#child_data, child_target = sleep.load(children_sel, force_reload=False, shuffle=True, flat=True, chunk_len=chunk_size)
#train_data, train_target, test_data, test_target = sleep.get_intrasub()
 
#test_data  = tools.normalize(test_data)
#train_data = tools.normalize(train_data)
 


 

print('Extracting features')
#train_data = np.hstack( (tools.feat_eeg(train_data[:,:,0]), tools.feat_eog(train_data[:,:,1]),tools.feat_emg(train_data[:,:,2])))
#test_data  = np.hstack( (tools.feat_eeg(test_data[:,:,0]), tools.feat_eog(test_data[:,:,1]), tools.feat_emg(test_data[:,:,2])))
#child_data = np.hstack( (tools.feat_eeg(child_data[:,:,0]), tools.feat_eog(child_data[:,:,1]), tools.feat_emg(child_data[:,:,2])))
#train_data =  tools.feat_eeg(train_data[:,:,0])
#test_data  =  tools.feat_eeg(test_data[:,:,0])
 
#train_data =   np.hstack([tools.get_freqs(train_data[:,:,0],50),tools.feat_eog(train_data[:,:,1])])
#test_data  =   np.hstack([tools.get_freqs(test_data[:,:,0], 50),tools.feat_eog(test_data[:,:,1])])
 
 
 
#train_target[train_target==4] = 3
train_target[train_target==5] = 4
#train_target[train_target==8] = 5
#test_target [test_target==4] = 3
test_target [test_target==5] = 4
#test_target [test_target==8] = 5

train_data   = np.delete(train_data, np.where(train_target==8) ,axis=0)     
train_target = np.delete(train_target, np.where(train_target==8) ,axis=0)     
test_data    = np.delete(test_data, np.where(test_target==8) ,axis=0)     
test_target  = np.delete(test_target, np.where(test_target==8) ,axis=0) 


#train_data =  tools.future(train_data, 4)
#test_data  =  tools.future(test_data, 4)

#training_data   = custom_datasets.DynamicData(train_data, train_target, batch_size=batch_size)
#validation_data = custom_datasets.DynamicData(test_data, test_target, batch_size=batch_size)             
#train_data = np.expand_dims(train_data,1)
#test_data = np.expand_dims(test_data,1)
train_data = np.expand_dims(train_data,1)
test_data = np.expand_dims(test_data,1)
# 
if np.sum(np.isnan(train_data)) or np.sum(np.isnan(test_data)):print('Warning! NaNs detected')
#%% training routine
#train_target = tools.label_to_one_hot(train_target)
#test_target  = tools.label_to_one_hot(test_target)

starttime = time.time()
#training_data   = datasets.DynamicData(train_data, train_target, batch_size=batch_size)
#validation_data = datasets.DynamicData(test_data, test_target, batch_size=batch_size)
 
data_size = train_data.shape
n_classes = len(np.unique(train_target))
input_var  = T.tensor3('inputs')
target_var = T.ivector('targets')

#def LSTM(data_size, n_classes):
#    network = L.InputLayer(shape=(None, None, data_size[2]))
#    network = L.LSTMLayer(network,  25)
#    network = L.LSTMLayer(network,  25)
#    network = L.LSTMLayer(network,  25)
#    network = L.DenseLayer( network, num_units=n_classes, W=lasagne.init.GlorotNormal(), nonlinearity=lasagne.nonlinearities.softmax)
#    return network
from lasagne import layers as L
def tsinalis(data_size, n_classes):
    network = L.InputLayer(shape=(None, 1, 1, data_size[3]), input_var=input_var)
    print network.output_shape
    network = L.Conv2DLayer( network, num_filters=20, filter_size = (1,500),stride= (1,1),  nonlinearity=lasagne.nonlinearities.elu, W=lasagne.init.HeNormal()) 
    network = L.batch_norm(network)
    print network.output_shape
    network = L.MaxPool2DLayer(network, pool_size = (1,20), stride = (1,10))
    print network.output_shape
    network = L.reshape(network, ([0],[2],[1],-1))
    print network.output_shape
    network = L.Conv2DLayer( network, num_filters = 400, filter_size = (20,30), stride = (1,1),  nonlinearity=lasagne.nonlinearities.elu, W=lasagne.init.HeNormal()) 
    network = L.batch_norm(network)
    print network.output_shape
    network = L.MaxPool2DLayer(network, pool_size = (1,10), stride = (1,2))
    print network.output_shape
    network = L.DenseLayer( network, num_units=500, W=lasagne.init.HeNormal(),      nonlinearity=lasagne.nonlinearities.elu)
    network = L.batch_norm(network)
    network = L.DenseLayer( network, num_units=500, W=lasagne.init.HeNormal(),      nonlinearity=lasagne.nonlinearities.elu)
    network = L.batch_norm(network)
    network = L.DropoutLayer(network, p=0.3)
    network = L.DenseLayer( network, num_units=n_classes,W=lasagne.init.GlorotNormal(),      nonlinearity=lasagne.nonlinearities.softmax)
    return network

def CNN(data_size, n_classes):
    network = L.InputLayer(shape=(None, data_size[1], data_size[2]), input_var=input_var)
    print network.output_shape
    network = L.Conv1DLayer( network, num_filters=50, filter_size = 50, stride = 10, W=lasagne.init.HeNormal())
    network = L.batch_norm(network)
    network = L.DropoutLayer(network, p=0.2)

    network = L.Conv1DLayer( network, num_filters=100, filter_size = 5, stride = 1, W=lasagne.init.HeNormal())
    network = L.DropoutLayer(network, p=0.2)

    network = L.batch_norm(network)
    network = L.MaxPool1DLayer(network, pool_size = (5), stride = (2))
    network = L.DimshuffleLayer(network, (0, 2, 1))
    print network.output_shape
    network = L.LSTMLayer(network, 250)
    network = L.DenseLayer( network, num_units=500, W=lasagne.init.HeNormal())
    network = L.batch_norm(network)
    network = L.DropoutLayer(network, p=0.5)
    print network.output_shape

    network = L.DenseLayer( network, num_units=n_classes,W=lasagne.init.GlorotNormal(),      nonlinearity=lasagne.nonlinearities.softmax)
    return network

def RNN2(data_size, n_classes):
    network = L.InputLayer(shape=(None, data_size[1], data_size[2]), input_var=input_var)
    print network.output_shape
    network = L.Conv1DLayer( network, num_filters=32, filter_size = 5,  nonlinearity=lasagne.nonlinearities.elu, W=lasagne.init.HeNormal()) 
    print network.output_shape
    network = L.DimshuffleLayer(network, (0, 2, 1))
    print network.output_shape
    network = L.LSTMLayer(network, 200)
    print network.output_shape
    network = L.DenseLayer( network,num_leading_axes=2, num_units=n_classes,W=lasagne.init.GlorotNormal(),      nonlinearity=lasagne.nonlinearities.softmax)
    print network.output_shape 
    return network


from lasagne.regularization import regularize_layer_params_weighted, l2
network = CNN(data_size, n_classes)

#%%
# get the prediction during training
network_output = L.get_output(network)
loss = lasagne.objectives.categorical_crossentropy(network_output, target_var).mean()
params = L.get_all_params(network, trainable=True)
updates = lasagne.updates.adam(loss,params)
accuracy = T.mean(T.eq(T.argmax(network_output, axis=1), target_var), dtype=theano.config.floatX)

train_fn = theano.function([input_var, target_var], [loss, accuracy], updates=updates)

prediction = L.get_output(network, deterministic = True)
layers = {network.input_layer.input_layer: 0.5, network.input_layer.input_layer: 0.5}
l2_penalty = regularize_layer_params_weighted(layers, l2)

val_loss = lasagne.objectives.categorical_crossentropy(prediction, target_var).mean() # + l2_penalty
accuracy = T.mean(T.eq(T.argmax(prediction, axis=1), target_var), dtype=theano.config.floatX)
val_fn = theano.function([input_var, target_var], [val_loss, accuracy, T.argmax(prediction, axis=1)],allow_input_downcast=True)
#pred_fn = theano.function([input_var], network_output)
 
n_mini_batch_training = data_size[0]/batch_size # number of training mini-batches given the batch_size
 
# lists where we will be storing values during training, for visualization purposes
tra_losses = []
val_losses = []
val_accs   = []
     
    # we want to save the parameters that give the best performance on the validation set
    # therefore, we store the best validation accuracy, and save the parameters to disk
#best_val_acc = 0
#fig = plt.figure(figsize=(10, 5))
#plt.ion()
best_val_acc = 0
# loop over the number of epochs
plt.close('all')
from sklearn.metrics import f1_score
def train_convnet(network,
                  train_x,
                  train_y,
                  validation_x,
                  validation_y,
                  n_epochs,
                  network_name,
                  training_fn,
                  validation_fn,
                  training_batch_size,
                  validation_batch_size,
                  plot_curves=True):
    """
    Train the given network.
    
    Args:
        network (L.Layer): Output layer.
        train_x (numpy.ndarray): Training images.
        train_y (numpy.ndarray): Training labels.
        validation_x (numpy.ndarray): Validation images.
        validation_y (numpy.ndarray): Validation labels.
        n_epochs (int): Number of epochs.
        network_name (str): Name used to identify experiment.
        traing_fn (function): Training function.
        validation_fn (function): Validation function.
        training_batch_size (int): Training batch size.
        validation_batch_size (int): Validation batch size.
        plot_curves (bool): Plot curves flag.
    """

    n_batch_train = len(train_y)/training_batch_size # number of training mini-batches given the batch_size
    n_batch_val   = len(validation_y)/validation_batch_size 
    # lists where we will be storing values during training, for visualization purposes
    tra_losses = []
    tra_accs   = []
    val_losses = []
    val_accs   = []
    
    # we want to save the parameters that give the best performance on the validation set
    # therefore, we store the best validation accuracy, and save the parameters to disk
    best_val_acc = 0
    # loop over the number of epochs
    plt.close('all')
    fig = plt.figure(figsize=(10, 5))
    for epoch in xrange(n_epochs):
        # training
        print epoch
        train_x, train_y = sklearn.utils.shuffle(train_x,train_y)
        cum_tra_loss = 0.0 # cumulative training loss
        cum_tra_acc = 0.0
        start = time.time()
        for b in range(n_batch_train-1):
            x_batch = train_x[b*training_batch_size:(b+1)*training_batch_size,:].astype(np.float32) # extract a mini-batch from x_train
            y_batch = train_y[b*training_batch_size:(b+1)*training_batch_size] # extract labels for the mini-batch
            mini_batch_loss, mini_batch_acc = training_fn(x_batch, y_batch)
            cum_tra_loss += mini_batch_loss
            cum_tra_acc += mini_batch_acc
        cum_tra_loss /= float(n_batch_train)
        cum_tra_acc /= float(n_batch_train)
        
#        # validation
        cum_val_loss = 0.0
        cum_val_acc = 0.0
        preds = []
        for b in range(n_batch_val+1):
            x_batch = validation_x[b*validation_batch_size:(b+1)*validation_batch_size,:].astype(np.float32) # extract a mini-batch from x_train
            y_batch = validation_y[b*validation_batch_size:(b+1)*validation_batch_size] # extract labels for the mini-batch
            val_loss, val_acc, pred = validation_fn(x_batch, y_batch)
            preds.extend(pred)
            
            cum_val_loss += val_loss
            cum_val_acc  += val_acc
        preds = np.array(preds)
        print preds.shape
        cum_val_acc  /= float(n_batch_val)
        cum_val_loss /= float(n_batch_val)
        print 'Took {:.1f} min. Done validating'.format((time.time()-start)/60)
        print('F1-Score {}'.format(f1_score(validation_y, preds, average='macro')))
#        cum_val_loss, cum_val_acc = validation_fn(validation_x.astype(np.float32), validation_y.astype(np.float32))
        # if the accuracy improves, save the network parameters
        
        params = L.get_all_param_values(network)
        p=np.hstack([x.flatten() for x in params])
        print np.max(p)
        print np.min(p)
        print np.sum(np.isfinite(p))
        if cum_val_acc > best_val_acc:
            best_val_acc = cum_val_acc
            # save network
            
            with open('./'+ network_name +'.npz', 'w') as f:
                print 'saving params'
                np.savez(f, params=params)
                print 'done'

        # add to lists
        tra_losses.append(cum_tra_loss)
        tra_accs.append(cum_tra_acc)
        val_losses.append(cum_val_loss)
        val_accs.append(cum_val_acc)
        print('Train: {:.1f}  Val: {:.1f}, Best-Val:{:.1f} '.format( cum_tra_acc*100, cum_val_acc*100, best_val_acc*100))
        plt.subplot(1,2,1)
        tra_loss_plt = plt.plot(range(len(tra_losses)), tra_losses, 'b')
        val_loss_plt = plt.plot(range(len(val_losses)), val_losses, 'g')
        plt.legend([tra_loss_plt[0],val_loss_plt [0]], ['Training loss', 'Validation loss'], loc='center right', bbox_to_anchor=(1, 0.5))
        plt.ylabel('loss')
        plt.xlabel('epoch')
        plt.title('Losses')
        plt.subplot(1,2,2)
        tra_acc_plt  = plt.plot(range(len(tra_accs)), tra_accs, 'b')
        val_acc_plt  = plt.plot(range(len(val_accs)), val_accs, 'g')
        plt.legend([tra_acc_plt[0],val_acc_plt [0]], ['Training acc', 'Validation acc'], loc='center right', bbox_to_anchor=(1, 0.5))
        plt.xlabel('epoch')
       
                  
        plt.title('Accuracy (Best-Val {:.2f}%)'.format(100. * best_val_acc))
        plt.pause(0.001)


        # Your code. Hint: you can copy your solution from the last assignment.
        pass
    
print('start training')
train_convnet(network, train_data,train_target,test_data,test_target,50,'jonet',train_fn, val_fn, 128,128)
#%%  Reporting and analysis.
 
stop
 
# plot loss and throughput
ann.report('results/{} {}-{}-{}-{}-{}-{}-{}'.format(counter,layers,neurons,epochs,clipping,decay,batch_size, comment))
# create analysis object
#ann.model.to_cpu()
ana = Analysis(ann.model,gpu=gpu, fname='results/{} {}-{}-{}-{}-{}-{}-{}'.format(counter,layers,neurons,epochs,clipping,decay,batch_size, comment))
start = time.time()
 
Y, T = ana.predict(training_data)
#Y = tools.epoch_voting(Y,30)
train_acc   = metrics.accuracy_score(Y,T)
train_f1    = metrics.f1_score(Y,T,average='macro')
train_conf   = ana.confusion_matrix(Y,T,plot=False)
 
Y, T = ana.predict(validation_data)
#Y = tools.epoch_voting(Y,30)
test_acc    = metrics.accuracy_score(Y,T)
test_f1     = metrics.f1_score(Y,T,average='macro')
classreport = metrics.classification_report(Y,T)
test_conf   = ana.confusion_matrix(Y,T,plot=True)
  
print("\nAccuracy: Test: {}%, Train: {}%".format("%.3f" % test_acc,"%.3f" % train_acc))
print("F1: \t  Test: {}%, Train: {}%".format("%.3f" % test_f1,"%.3f" % train_f1))
print(classreport)
print(test_conf)
print((time.time()-start) / 60.0)
#%%
# save results
train_loss = ann.log[('training','loss')][-1]
test_loss  = ann.log[('validation','loss')][-1]
np.set_printoptions(precision=2,threshold=np.nan)
 
save_dict = {'1 Time':time.strftime("%c"),
            'Dataset':datadir,
            'Runtime': "%.2f" % (runtime/60),
            '5 Layers':layers,
            '10 Neurons':neurons,
            '15 Epochs':epochs,
            'Clipping':clipping,
            'Weightdecay':decay,
            'Batch-Size':batch_size,
            'Cutoff':cutoff,
            '20 Train-Acc':"%.3f" % train_acc,
            '21 Val-Acc':"%.3f" % test_acc,
            'Train-Loss':"%.5f" %train_loss,
            'Val-Loss':"%.5f" %test_loss,
            '30 Comment':comment,
            'Selection':str(len(selection)) + ' in ' + str(selection) ,
            'Shape':str(train_data.shape) ,
            'Link':str(link),
            'Report':classreport,
            '22 Train-F1':"%.3f" %  train_f1,
            '27 Val-F1':"%.3f" %  test_f1,
            'Train-Confusion': str(train_conf),
            'Val-Confusion':  str(test_conf),
            'NLabels' : str(np.unique(T)),
            '29 Chunksize': str(chunk_size),
            '2 Number': counter,
            'Future': future
                      }
 
np.set_printoptions(precision=2,threshold=1000)
tools.append_json('experiments.json', save_dict)
tools.jsondict2csv('experiments.json', 'experiments.csv')
#return train_acc, test_acc
#if __name__ == "__main__":
#    main()
    