import sys
sys.path.append('../')

from Utils import *
import numpy as np
import random
from keras.models import Sequential
from keras.layers import Dense, Dropout
from tensorflow.keras.optimizers import Adam
from collections import deque

class DQN:
    def __init__(self, choices):
        self.memory = deque(maxlen=200)
        self.choices = choices
        self.gamma = 0.85
        self.epsilon = 1
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.99
        self.learning_rate = 0.005
        self.tau = .125

        self.model = self.create_model()
        self.target_model = self.create_model()

    def create_model(self):
        model = Sequential()
        state_shape = 1
        model.add(Dense(2, input_dim=1, activation="relu", use_bias=False))
        model.add(Dense(2, use_bias=False))
        model.compile(loss="mean_squared_error",
                      optimizer=Adam(lr=self.learning_rate))
        return model

    def act(self):
        self.epsilon *= self.epsilon_decay
        self.epsilon = max(self.epsilon_min, self.epsilon)
        if np.random.random() < self.epsilon:
            return np.random.random() < 0.5 * 0 + np.random.random() > 0.5 * 1
        print((self.model.predict([1])))
        return np.argmax(self.model.predict([1])[0])

    def remember(self, action, reward):
        self.memory.append([action, reward])

    def replay(self):
        batch_size = 4
        if len(self.memory) < batch_size:
            return
        print('hi')
        samples = random.sample(self.memory, batch_size)
        for sample in samples:
            action, reward = sample
            target = self.target_model.predict([1])
            target[0][action] = reward
            self.model.fit(np.array([1]), target, epochs=1, verbose=0)

    def target_train(self):
        weights = self.model.get_weights()
        target_weights = self.target_model.get_weights()
        for i in range(len(target_weights)):
            target_weights[i] = weights[i] * self.tau + target_weights[i] * (1 - self.tau)
        self.target_model.set_weights(target_weights)

    def save_model(self, fn):
        self.model.save(fn)


if __name__ == "__main__":
    choices= retreaveinfo()

    gamma = 0.9
    epsilon = .9

    trials = 1
    trial_len = 500

    # updateTargetNetwork = 1000
    dqn_agent = DQN(choices)
    steps = []
    for trial in range(trials):
        for step in range(trial_len):
            action = dqn_agent.act()
            f = open('RL.txt', 'a')
            selected_choice = action
            f.write(f'{selected_choice}\n')
            f.close()

            reward = play_game(choices[action])

            # reward = reward if not done else -20
            dqn_agent.remember(action, reward)

            dqn_agent.replay()  # internally iterates default (prediction) model
            dqn_agent.target_train()  # iterates target model

            print("Completed in {} trials".format(trial))
    dqn_agent.save_model("success.model")



