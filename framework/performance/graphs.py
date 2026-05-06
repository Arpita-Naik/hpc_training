import matplotlib.pyplot as plt


def plot_local_iterations(values):

    runs = list(range(1, len(values)+1))
    avg = sum(values) / len(values)

    plt.figure()

    plt.bar(runs, values)
    plt.xticks(runs)
    plt.axhline(avg, linestyle='--')

    plt.title("STREAM Iteration Performance")
    plt.xlabel("Iteration")
    plt.ylabel("TRIAD")

    plt.grid(axis='y', linestyle='', alpha=0.6)
    plt.show()

def plot_last_iterations():

    import json
    import matplotlib.pyplot as plt

    file = "performance/data/stream_iterations.json"

    with open(file) as f:
        data = json.load(f)

    last = data[-1]["values"]

    runs = list(range(1, len(last)+1))
    avg = sum(last) / len(last)

    plt.figure()
    plt.bar(runs, last)
    plt.xticks(runs)
    plt.axhline(avg, linestyle='--')

    plt.show()

def plot_avg_history():

    import json
    import os
    import matplotlib.pyplot as plt

    file = "performance/data/stream_avg.json"

    if not os.path.exists(file):
        print("No average history found")
        return

    with open(file) as f:
        data = json.load(f)

    if len(data) == 0:
        print("No data to plot")
        return

    values = [d["avg"] for d in data]
    runs = list(range(1, len(values) + 1))

    plt.figure()

    plt.bar(runs, values)
    plt.xticks(runs)
    plt.title("STREAM Average Performance per Run")
    plt.xlabel("Run Number")
    plt.ylabel("Average TRIAD")

    plt.grid(axis='y', linestyle='', alpha=0.6)
    plt.show()

def plot_hpl_avg():

    import json
    import matplotlib.pyplot as plt

    file = "performance/data/hpl_avg.json"

    with open(file) as f:
        data = json.load(f)

    values = [d["avg"] for d in data]
    runs = list(range(1, len(values)+1))

    plt.figure()
    plt.bar(runs, values)
    plt.xticks(runs)
    plt.title("HPL Average Performance")
    plt.xlabel("Run Number")
    plt.ylabel("GFLOPS")

    plt.grid(axis='y', linestyle='', alpha=0.6)
    plt.show()
    
def plot_hpl_last_iterations():

    import json
    import os
    import matplotlib.pyplot as plt

    file = "performance/data/hpl_iterations.json"

    if not os.path.exists(file):
        print("No HPL iteration data found")
        return

    with open(file) as f:
        data = json.load(f)

    if len(data) == 0:
        print("No data to plot")
        return

    last = data[-1]["values"]

    runs = list(range(1, len(last)+1))
    avg = sum(last) / len(last)

    plt.figure()
    plt.bar(runs, last)
    plt.xticks(runs)
    plt.axhline(avg, linestyle='--')

    plt.title("HPL Iteration Performance")
    plt.xlabel("Iteration")
    plt.ylabel("GFLOPS")

    plt.grid(axis='y', linestyle='', alpha=0.6)
    plt.show()