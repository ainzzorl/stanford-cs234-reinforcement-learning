### MDP Value Iteration and Policy Iteration
import argparse
import numpy as np
import gym
import time
from lake_envs import *

np.set_printoptions(precision=3)

parser = argparse.ArgumentParser(description='A program to run assignment 1 implementations.',
								formatter_class=argparse.ArgumentDefaultsHelpFormatter)

parser.add_argument("--env", 
					help="The name of the environment to run your algorithm on.", 
					choices=["Deterministic-4x4-FrozenLake-v0","Stochastic-4x4-FrozenLake-v0"],
					default="Deterministic-4x4-FrozenLake-v0")

"""
For policy_evaluation, policy_improvement, policy_iteration and value_iteration,
the parameters P, nS, nA, gamma are defined as follows:

	P: nested dictionary
		From gym.core.Environment
		For each pair of states in [1, nS] and actions in [1, nA], P[state][action] is a
		tuple of the form (probability, nextstate, reward, terminal) where
			- probability: float
				the probability of transitioning from "state" to "nextstate" with "action"
			- nextstate: int
				denotes the state we transition to (in range [0, nS - 1])
			- reward: int
				either 0 or 1, the reward for transitioning from "state" to
				"nextstate" with "action"
			- terminal: bool
			  True when "nextstate" is a terminal state (hole or goal), False otherwise
	nS: int
		number of states in the environment
	nA: int
		number of actions in the environment
	gamma: float
		Discount factor. Number in range [0, 1)
"""

def policy_evaluation(P, nS, nA, policy, gamma=0.9, tol=1e-3):
	"""Evaluate the value function from a given policy.

	Parameters
	----------
	P, nS, nA, gamma:
		defined at beginning of file
	policy: np.array[nS]
		The policy to evaluate. Maps states to actions.
	tol: float
		Terminate policy evaluation when
			max |value_function(s) - prev_value_function(s)| < tol
	Returns
	-------
	value_function: np.ndarray[nS]
		The value function of the given policy, where value_function[s] is
		the value of state s
	"""

	value_function = np.zeros(nS)

	############################
	# YOUR IMPLEMENTATION HERE #	

	step = 0
	while True:
		step += 1
		# print(f'Policy evaluation step: {step}')
		# print(value_function)
		new_value_function = np.zeros(nS)
		for s in range(nS):
			a = policy[s]
			for prob, next_state, reward, done in P[s][a]:
				new_value_function[s] += prob * reward
				if not done:
					new_value_function[s] += gamma * prob * value_function[next_state]
		should_stop = np.all(np.fabs(value_function - new_value_function) < tol)
		value_function = new_value_function
		if should_stop:
			break

	############################
	return value_function


def policy_improvement(P, nS, nA, value_from_policy, policy, gamma=0.9):
	"""Given the value function from policy improve the policy.

	Parameters
	----------
	P, nS, nA, gamma:
		defined at beginning of file
	value_from_policy: np.ndarray
		The value calculated from the policy
	policy: np.array
		The previous policy.

	Returns
	-------
	new_policy: np.ndarray[nS]
		An array of integers. Each integer is the optimal action to take
		in that state according to the environment dynamics and the
		given value function.
	"""

	new_policy = np.zeros(nS, dtype='int')

	############################
	# YOUR IMPLEMENTATION HERE #

	for s in range(nS):
		best_action = None
		best_action_value = -np.inf
		for a in range(nA):
			action_value = 0
			for prob, next_state, reward, done in P[s][a]:
				action_value += prob * reward
				if not done:
					action_value += prob * gamma * value_from_policy[next_state]
			if action_value > best_action_value:
				best_action = a
				best_action_value = action_value
		new_policy[s] = best_action

	############################
	return new_policy


def policy_iteration(P, nS, nA, gamma=0.9, tol=10e-3):
	"""Runs policy iteration.

	You should call the policy_evaluation() and policy_improvement() methods to
	implement this method.

	Parameters
	----------
	P, nS, nA, gamma:
		defined at beginning of file
	tol: float
		tol parameter used in policy_evaluation()
	Returns:
	----------
	value_function: np.ndarray[nS]
	policy: np.ndarray[nS]
	"""

	value_function = np.zeros(nS)
	policy = np.zeros(nS, dtype=int)

	############################
	# YOUR IMPLEMENTATION HERE #

	step = 0
	while True:
		step += 1
		# print(f'Policy iteration step: {step}')
		policy_old = np.copy(policy)
		value_function = policy_evaluation(P, nS, nA, policy, gamma, tol)
		policy = policy_improvement(P, nS, nA, value_function, policy, gamma)
		# print(policy)
		# print(value_function)
		if np.array_equal(policy, policy_old):
			break

	print('Policy iteration steps:', step)
	print('Final policy:', policy)

	############################
	return value_function, policy

def value_iteration(P, nS, nA, gamma=0.9, tol=1e-3):
	"""
	Learn value function and policy by using value iteration method for a given
	gamma and environment.

	Parameters:
	----------
	P, nS, nA, gamma:
		defined at beginning of file
	tol: float
		Terminate value iteration when
			max |value_function(s) - prev_value_function(s)| < tol
	Returns:
	----------
	value_function: np.ndarray[nS]
	policy: np.ndarray[nS]
	"""

	value_function = np.zeros(nS)
	policy = np.zeros(nS, dtype=int)
	############################
	# YOUR IMPLEMENTATION HERE #

	step = 0
	while True:
		step += 1
		# print(f'Value iteration step: {step}')
		new_value_function = np.zeros(nS)
		for s in range(nS):
			best_action_value = -np.inf
			for a in range(nA):
				action_value = 0
				for prob, next_state, reward, done in P[s][a]:
					action_value += prob * reward
					if not done:
						action_value += prob * gamma * value_function[next_state]
				if action_value > best_action_value:
					best_action_value = action_value
			new_value_function[s] = best_action_value
		should_stop = np.all(np.fabs(value_function - new_value_function) < tol)
		value_function = new_value_function
		if should_stop:
			break

	for s in range(nS):
		best_action_value = -np.inf
		for a in range(nA):
			action_value = 0
			for prob, next_state, reward, done in P[s][a]:
				action_value += prob * reward
				if not done:
					action_value += prob * gamma * value_function[next_state]
			if action_value > best_action_value:
				best_action_value = action_value
				policy[s] = a

	print('Value iteration steps:', step)
	print('Final value function:', value_function)
	print('Final policy:', policy)

	############################
	return value_function, policy

def render_single(env, policy, max_steps=100):
  """
    This function does not need to be modified
    Renders policy once on environment. Watch your agent play!

    Parameters
    ----------
    env: gym.core.Environment
      Environment to play on. Must have nS, nA, and P as
      attributes.
    Policy: np.array of shape [env.nS]
      The action to take at a given state
  """

  episode_reward = 0
  ob = env.reset()
  for t in range(max_steps):
    env.render()
    time.sleep(0.25)
    a = policy[ob]
    ob, rew, done, _ = env.step(a)
    episode_reward += rew
    if done:
      break
  env.render();
  if not done:
    print("The agent didn't reach a terminal state in {} steps.".format(max_steps))
  else:
  	print("Episode reward: %f" % episode_reward)


# Edit below to run policy and value iteration on different environments and
# visualize the resulting policies in action!
# You may change the parameters in the functions below
if __name__ == "__main__":
	# read in script argument
	args = parser.parse_args()
	
	# Make gym environment
	env = gym.make(args.env)

	print("\n" + "-"*25 + "\nBeginning Policy Iteration\n" + "-"*25)

	V_pi, p_pi = policy_iteration(env.P, env.nS, env.nA, gamma=0.9, tol=1e-3)
	render_single(env, p_pi, 100)

	print("\n" + "-"*25 + "\nBeginning Value Iteration\n" + "-"*25)

	V_vi, p_vi = value_iteration(env.P, env.nS, env.nA, gamma=0.9, tol=1e-3)
	render_single(env, p_vi, 100)


