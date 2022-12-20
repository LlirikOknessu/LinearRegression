import tensorflow as tf
from tensorflow import keras
from keras.layers import Dense
from keras.models import Model
from pathlib import Path
import pandas as pd
import datetime
import shutil
import argparse
import yaml
import numpy as np
from joblib import load
from sklearn.metrics import mean_squared_error

def parser_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_dir', '-id', type=str, default='data/prepared', help="path to input directory")
    parser.add_argument('--output_dir', '-od', type=str, default='data/models', help="path to output directory")
    parser.add_argument('--logs_dir', '-ld', type=str, default='data/logs', help="path to logs directory")
    parser.add_argument('--baseline_model', '-bm', type=str, default='data/models/LinearRegression_prod.joblib', help='path to linear regression prod version')
    parser.add_argument('--params', '-p', type=str, default='params.yaml', help='file with dvc stage params')
    return parser.parse_args()

class NeuNet(Model):
    def __init__(self, neurons=128):
        super(NeuNet, self).__init__()        
        self.in_layer = Dense(10, activation='relu')
        self.hidden_1 = Dense(neurons, activation='relu')
        self.hidden_2 = Dense(neurons, activation='relu')
        self.hidden_3 = Dense(neurons, activation='relu')
        self.hidden_4 = Dense(neurons, activation='relu')
        self.hidden_5 = Dense(neurons, activation='relu')
        self.hidden_6 = Dense(neurons, activation='relu')
        self.hidden_7 = Dense(neurons, activation='relu')
        self.hidden_8 = Dense(neurons, activation='relu')
        self.hidden_9 = Dense(neurons, activation='relu')
        self.hidden_10 = Dense(neurons, activation='relu')
        self.out_layer = Dense(1, activation='relu')

    def call(self, inputs):
        x = self.in_layer(inputs)
        x = self.hidden_1(x)
        x = self.hidden_2(x)
        x = self.hidden_3(x)
        x = self.hidden_4(x)
        x = self.hidden_5(x)
        x = self.hidden_6(x)
        x = self.hidden_7(x)
        x = self.hidden_8(x)
        x = self.hidden_9(x)
        x = self.hidden_10(x)
        outputs = self.out_layer(x)
        return outputs

def train_net(data: pd.DataFrame, labels: pd.DataFrame, net: NeuNet, loss: tf.keras.losses, optimizer: tf.keras.optimizers, train_loss, train_accuracy):
    with tf.GradientTape() as tape:
        predictions = net(data)
        loss = loss(labels, predictions)
    gradients = tape.gradient(loss, net.trainable_variables)
    optimizer.apply_gradients(zip(gradients, net.trainable_variables))
    train_loss(loss)
    train_accuracy(labels, predictions)


def val_net(data: pd.DataFrame, labels: pd.DataFrame, net: NeuNet, loss: tf.keras.losses, val_loss, val_accuracy):
    predictions = net(data)
    loss = loss(labels, predictions)
    val_loss(loss)
    val_accuracy(labels, predictions)


if __name__ == '__main__':
    args = parser_args()
    with open(args.params, 'r') as f:
        params_all = yaml.safe_load(f)
    params = params_all['neural_network']

    BATCH_SIZE = params.get('batch_size')
    BUFFER_SIZE = params.get('buffer_size')
    NEURONS = params.get('neurons')
    LEARNING_RATE = params.get('learning_rate')
    EPOCHS = 50
    
    in_dir = Path(args.input_dir)
    out_dir = Path(args.output_dir)
    logs_path = Path(args.logs_dir)
    baseline_model_path = Path(args.baseline_model)

    if logs_path.exists():
        shutil.rmtree(logs_path)
    out_dir.mkdir(exist_ok=True, parents=True)

    X_train_name = in_dir / 'X_train.csv'
    y_train_name = in_dir / 'y_train.csv'
    X_train = pd.read_csv(X_train_name)
    y_train = pd.read_csv(y_train_name)
    X_val_name = in_dir / 'X_val.csv'
    y_val_name = in_dir / 'y_val.csv'
    X_val = pd.read_csv(X_val_name)
    y_val = pd.read_csv(y_val_name)

    bestLoss = 1000
    bestParameters = []
    
    for _batch_size in BATCH_SIZE:
        for _buffer_size in BUFFER_SIZE:
            for _neurons in NEURONS:
                for _learning_rate in LEARNING_RATE:
                    tf.summary.trace_on(graph=True, profiler=True)
                    template1 = 'Batch Size {}, Buffer Size: {}, Neurons: {}, Learning Rate: {}'
                    print(template1.format(_batch_size,
                                            _buffer_size,
                                            _neurons,
                                            _learning_rate))

                    train_ds = tf.data.Dataset.from_tensor_slices(
                    (X_train, y_train)).shuffle(_buffer_size).batch(_batch_size)
                    val_ds = tf.data.Dataset.from_tensor_slices((X_val, y_val)).batch(_batch_size)

                    net = NeuNet(neurons=_neurons)
                    net.compile()
                    loss = tf.keras.losses.MeanSquaredError()
                    optimizer = tf.keras.optimizers.SGD(learning_rate=_learning_rate)
                    train_loss = tf.keras.metrics.Mean(name='train_loss')
                    train_accuracy = tf.keras.metrics.MeanSquaredError(name='train_mse')
                    val_loss = tf.keras.metrics.Mean(name='val_loss')
                    val_accuracy = tf.keras.metrics.MeanSquaredError(name='val_mse')

                    current_time = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
                    train_log_dir = logs_path / 'gradient_tape' / current_time / 'train'
                    val_log_dir = logs_path / 'gradient_tape' / current_time / 'val'
                    train_log_dir.mkdir(exist_ok=True, parents=True)
                    val_log_dir.mkdir(exist_ok=True, parents=True)
                    train_summary_writer = tf.summary.create_file_writer(str(train_log_dir))
                    val_summary_writer = tf.summary.create_file_writer(str(val_log_dir))

                    logdir = logs_path / "fit" / datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
                    logdir.mkdir(exist_ok=True, parents=True)
                    fit_summary_writer = tf.summary.create_file_writer(str(logdir))
                            
                    for epoch in range(EPOCHS):
                        for (X_train, y_train) in train_ds:
                            with fit_summary_writer.as_default():
                                train_net(X_train, y_train, net, loss, optimizer, train_loss, train_accuracy)
                        with train_summary_writer.as_default():
                            tf.summary.scalar('loss', train_loss.result(), step=epoch)
                            tf.summary.scalar('accuracy', train_accuracy.result(), step=epoch)
                        for (X_val, y_val) in val_ds:
                            val_net(X_val, y_val, net, loss, val_loss, val_accuracy)
                        with train_summary_writer.as_default():
                            tf.summary.scalar('loss', train_loss.result(), step=epoch)
                            tf.summary.scalar('mse', train_accuracy.result(), step=epoch)

                        template = 'Epoch {}, Loss: {}, Accuracy: {}, val Loss: {}, val MSE: {}'
                        print (template.format(epoch+1,
                                                train_loss.result(),
                                                train_accuracy.result(),
                                                val_loss.result(),
                                                val_accuracy.result()))
                            
                        if epoch == EPOCHS - 1:
                            if val_loss.result().numpy() < bestLoss:
                                bestLoss = val_loss.result().numpy()
                                bestParameters = [_batch_size, _buffer_size, _neurons, _learning_rate]
                                net.save('./data/models/NeuNet', overwrite=True)
                                    
                        # Reset metrics every epoch
                        train_loss.reset_states()
                        val_loss.reset_states()
                        train_accuracy.reset_states()
                        val_accuracy.reset_states()

                    with fit_summary_writer.as_default():
                        tf.summary.trace_export(
                            name="my_func_trace",
                            step=0,
                            profiler_outdir=logdir
                        )
    template1 = 'Best parameters: Batch Size {}, Buffer Size: {}, Neurons: {}, Learning Rate: {}'
    print(template1.format(*[str(x) for x in bestParameters]))
    print("bessLoss: ", bestLoss)    

    baseline_model = load(baseline_model_path)
    y_pred_baseline = np.squeeze(baseline_model.predict(X_val))
    print("Baseline RMSE: ", mean_squared_error(y_val, y_pred_baseline))





                
    
    




