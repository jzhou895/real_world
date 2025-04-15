import os
import sys
import json
import statistics
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def get_actor_logs(logdir):
    logdir = os.path.join("/proj/VerifiedMLSys/rohitd99/model_checkpoints_256_actors/", logdir, "train_log")
    actor_logfiles = list(filter(lambda x: "Eval" not in x and "OUTPUT" not in x and "tar.gz" not in x, os.listdir(logdir)))

    MAX_STEPS = -1 
    all_dfs = []
    steps_run = []

    for logfile in actor_logfiles:
        with open(os.path.join(logdir, logfile), 'r') as f:
            df = pd.DataFrame(list(map(lambda x: json.loads(x), filter(lambda x: x.startswith("{"), f.readlines()))))
        MAX_STEPS = max(df['Epoch'].max(), MAX_STEPS)
        all_dfs.append(df)
    
    for i in range(len(all_dfs)):
        all_dfs[i]['e2e_epoch'] = ((all_dfs[i]['Session'] - 1) * MAX_STEPS) + all_dfs[i]['Epoch']
    assert len(all_dfs) == 256
    mean_df = pd.concat(all_dfs).groupby('e2e_epoch').mean().reset_index()
    std_df  = pd.concat(all_dfs).groupby('e2e_epoch').std().reset_index()
    return mean_df, std_df


def load_all_actors_rewards(model_name, file_prefix, actor_nums):
    actors_rewards = {
        'raw_rewards': {},
        'certified_rewards': {},
        'overall_rewards': {}
    }
    training_dir = os.path.join("/proj/VerifiedMLSys/rohitd99/model_checkpoints_256_actors/", model_name, "train_log")
    for actor_id in range(actor_nums):
        file_name = f'{training_dir}/{file_prefix}-actor{actor_id}.txt'
        line_count = 0
        for line in open(file_name, 'r').readlines():
            if line_count <= 2:
                line_count += 1
                continue
            line_count += 1
            data = line[:-1].split('; ')
            # Epoch: 10, Eval/Return/RawReward: 33.63373060842887; Eval/Return/EmpiricalConstraintReward: 7.86; Eval/Return/SymbolicConstraintReward: 29.933223481393355; Eval/Return/OverallReward: 33.63373060842887
            # I want to get the RawReward value, Symbolic Constraint Reward value, and Overall Reward value.
            raw_reward = float(data[0].split(', ')[1].split(": ")[1])
            symbolic_constraint_reward = float(data[2].split(': ')[1])
            overall_reward = float(data[3].split(': ')[1])
            actors_rewards['raw_rewards'].setdefault(actor_id, []).append(raw_reward)
            actors_rewards['certified_rewards'].setdefault(actor_id, []).append(symbolic_constraint_reward)
            actors_rewards['overall_rewards'].setdefault(actor_id, []).append(overall_reward)

    raw_rewards = actors_rewards['raw_rewards']
    certified_rewards = actors_rewards['certified_rewards']
    overall_rewards = actors_rewards['overall_rewards']

    print(len(raw_rewards[0]))

    raw_rewards_mean = []
    raw_rewards_std = []
    for i in range(len(raw_rewards[0])):
        actor_rawrewards = []
        for actor_id in raw_rewards.keys():
            if len(raw_rewards[actor_id]) > i:
                actor_rawrewards.append(raw_rewards[actor_id][i])
        raw_rewards_mean.append(sum(actor_rawrewards)/len(actor_rawrewards))
        raw_rewards_std.append(statistics.stdev(actor_rawrewards))

    certified_rewards_mean = []
    certified_rewards_std = []
    for i in range(len(certified_rewards[0])):
        actor_certified_rewards = []
        for actor_id in certified_rewards.keys():
            if len(certified_rewards[actor_id]) > i:
                actor_certified_rewards.append(certified_rewards[actor_id][i])
        certified_rewards_mean.append(sum(actor_certified_rewards)/len(actor_certified_rewards))
        certified_rewards_std.append(statistics.stdev(actor_certified_rewards))

    overall_rewards_mean = []
    overall_rewards_std = []
    for i in range(len(overall_rewards[0])):
        actor_overall_rewards = []
        for actor_id in overall_rewards.keys():
            if len(overall_rewards[actor_id]) > i:
                actor_overall_rewards.append(overall_rewards[actor_id][i])
        overall_rewards_mean.append(sum(actor_overall_rewards)/len(actor_overall_rewards))
        overall_rewards_std.append(statistics.stdev(actor_overall_rewards))

    raw_rewards_mean = np.array(raw_rewards_mean)
    raw_rewards_std = np.array(raw_rewards_std)
    certified_rewards_mean = np.array(certified_rewards_mean)
    certified_rewards_std = np.array(certified_rewards_std)
    overall_rewards_mean = np.array(overall_rewards_mean)
    overall_rewards_std = np.array(overall_rewards_std)
    
    # Construct a dataframe with the mean of the rewards.
    mean_df = pd.DataFrame({
        'e2e_epoch': np.arange(len(raw_rewards_mean)) * 1000,
        'RawReward': raw_rewards_mean,
        'SymbolicConstraintReward': certified_rewards_mean,
        'OverallReward': overall_rewards_mean
    })
    std_df = pd.DataFrame({
        'e2e_epoch': np.arange(len(raw_rewards_std)) * 1000,
        'RawReward': raw_rewards_std,
        'SymbolicConstraintReward': certified_rewards_std,
        'OverallReward': overall_rewards_std
    })
    print(len(mean_df))
    return mean_df, std_df

def make_plots(mean_std_dfs, names, num_steps = 50000):
    len(mean_std_dfs) == len(names)
    
    # Plot formatting
    plt.rcParams["font.size"] = 14
    fig, axs = plt.subplots(3, 1, figsize=(8, 6), sharex=True)
    
    # COLORS = ['red', 'blue', 'green', 'yellow', 'purple']
    COLORS = ["#82B366", "#D79B00", "#9673A6", "#6C8EBF", "#D6B656", "B85450", "#BF5700"]
    styles = ["-", "--", "-.", ":", (0, (3, 1, 1, 1)), (0, (5, 1))]

    ylabels = ['Raw', 'Symbolic', 'Overall']
            
    for i in range(len(mean_std_dfs)):
        mean_df = mean_std_dfs[i][0]
        std_df = mean_std_dfs[i][1]
        name = "Orca" if "baseline" in names[i].lower() else "C3"
        style_id = -1 if name is "C3" else i

        # Plot each reward type with mean and shaded area for ± std
        axs[0].plot(mean_df['e2e_epoch'], mean_df['RawReward'], label=name, color=COLORS[style_id], linestyle=styles[style_id])
        axs[0].fill_between(mean_df['e2e_epoch'], mean_df['RawReward'] - std_df['RawReward'], 
                            mean_df['RawReward'] + std_df['RawReward'], color=COLORS[style_id], alpha=0.2)

        axs[1].plot(mean_df['e2e_epoch'], mean_df['SymbolicConstraintReward'], label=name, color=COLORS[style_id], linestyle=styles[style_id])
        axs[1].fill_between(mean_df['e2e_epoch'], mean_df['SymbolicConstraintReward'] - std_df['SymbolicConstraintReward'], 
                            mean_df['SymbolicConstraintReward'] + std_df['SymbolicConstraintReward'], color=COLORS[style_id], alpha=0.2)

        axs[2].plot(mean_df['e2e_epoch'], mean_df['OverallReward'], label=name, color=COLORS[style_id], linestyle=styles[style_id])
        axs[2].fill_between(mean_df['e2e_epoch'], mean_df['OverallReward'] - std_df['OverallReward'], 
                            mean_df['OverallReward'] + std_df['OverallReward'], color=COLORS[style_id], alpha=0.2)

        

        axs[-1].set_xlabel('Epochs')
        
    # Set titles and labels
    for i, ax in enumerate(axs):
        ax.legend()
        ax.set_ylabel(ylabels[i])
        
    plt.legend()
    
    plt.xlim(0, num_steps)
    # Show the plot
    plt.tight_layout()
    plt.savefig("train_loss.png")

if __name__ == "__main__":
    # Model conf is of the form: {model_name}@{train_type}
    model_confs = sys.argv[1:]

    data = []
    model_names = []
    for conf in model_confs:
        # Extract the model name and the training type.
        model_name, train_type = conf.split('@')
        model_names.append(model_name)

        if train_type == "old":
            mean_df, std_df = load_all_actors_rewards(model_name, "v9_actorNum256_multi_lambda0.25_ksymbolic5_k1_raw-sym_threshold25_seed0", 256)
        else:
            mean_df, std_df = get_actor_logs(model_name)
        data.append((mean_df, std_df))

    make_plots(data, model_names, num_steps=50_000)
