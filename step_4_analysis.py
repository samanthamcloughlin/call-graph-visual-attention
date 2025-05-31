import glob
from statistics import mean
import scipy
import seaborn as sns
from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

from statsmodels.stats.multitest import fdrcorrection 

from step_2_annotate_methods import is_method_header, method_dict
from call_graph_builder import build_call_tree, read_call_graph
from constants import VALID_CALLEE_METHODS, VALID_CALLER_METHODS, PROJECTS_DIR

project_dict = {1: "scrimage", 2: "mltk", 3: "mallet", 4: "openaudible", 5: "freecol"}

x_cols = ["node_coverage", "weighted_node_coverage", "edge_coverage", "weighted_edge_coverage"]

y_cols = ["confidence", "conf_abs_perc_diff", "total_score",
          "accuracy", "conciseness", "completeness", "clarity"]

def get_dfs(mode="all"):
    target_methods = VALID_CALLEE_METHODS + VALID_CALLER_METHODS
    dfs = []
    fnames = glob.glob("Processed Data/T*/P*/processed_*.csv")
    if mode == 1:
        fnames = [f for f in fnames if int(f.split("/P")[1].split("/")[0]) < 20]
    elif mode == 2:
        fnames = [f for f in fnames if int(f.split("/P")[1].split("/")[0]) > 20]
    for f in fnames:
        try:
            df = pd.read_csv(f)
            df = df[df['fixation_target'].str.contains(".java")]
            target_method = f.split("_")[-1].replace(".csv", "")
            target_method = [t for t in target_methods if t.split(":")[1].split("(")[0] == target_method][0]
            method_cache = {}
            caller_graph = read_call_graph(target_method, up=True)
            callee_graph = read_call_graph(target_method, up=False)
            def get_method_category(method, fixation_target):
                if method in method_cache.keys():
                    return method_cache[method]
                class_name = fixation_target.split(".")[0]
                if not isinstance(method, str) or len(method) == 0:
                    method_cache[method] = "no_method"
                    return "no_method"
                method = class_name + ":" + method
                if method == target_method:
                    method_cache[method] = "target"
                    return "target"
                call_graph_methods = set(list([c[0] for c in caller_graph] + [c[1] for c in caller_graph]))
                if method in call_graph_methods:
                    method_cache[method] = "call_graph_up"
                    return "call_graph_up"
                call_graph_methods = set(list([c[0] for c in callee_graph] + [c[1] for c in callee_graph]))
                if method in call_graph_methods:
                    method_cache[method] = "call_graph_down"
                    return "call_graph_down"
                method_cache[method] = "non_call_graph"
                return "non_call_graph"
            df['method_category'] = df.apply(lambda x: get_method_category(x['method_name'], x['fixation_target']), axis=1)
            df['study'] = '2' if int(f.split("/P")[1].split("/")[0]) > 20 else '1'
            dfs.append(df)
        except Exception as e:
            pass
    return dfs

def get_fixation_positions(dfs, plot=False):
    avg_fixation_placement = {k: list([]) for k in ["target", "callgraph", "caller", "callee", "noncall"]}
    study1_avg_fixation_placement = {k: list([]) for k in ["target", "callgraph", "caller", "callee", "noncall"]}
    study2_avg_fixation_placement = {k: list([]) for k in ["target", "callgraph", "caller", "callee", "noncall"]}
    for d in dfs:
        total_fixation = d['duration'].sum()
        fixation_dict = {k: list([]) for k in ["target", "callgraph", "caller", "callee", "noncall"]}
        acc_fixation = 0
        for index, row in d.iterrows():
            if row['method_category'] == 'call_graph_up':
                fixation_dict['caller'].append(acc_fixation/total_fixation)
            elif row['method_category'] == 'call_graph_down':
                fixation_dict['callee'].append(acc_fixation/total_fixation)
            elif row['method_category'] == 'target':
                fixation_dict['target'].append(acc_fixation/total_fixation)
            elif row['method_category'] == 'non_call_graph':
                fixation_dict['noncall'].append(acc_fixation/total_fixation)
            acc_fixation += row['duration']
        fixation_dict["callgraph"] = fixation_dict["callee"] + fixation_dict["caller"]
        for k,v in fixation_dict.items():
            if len(v) > 0:
                avg_fixation_placement[k].append(mean(v))
                if row['study'] == 2:
                    study2_avg_fixation_placement[k].append(mean(v))
                else:
                    study1_avg_fixation_placement[k].append(mean(v))
    print("---Average Fixation Positions---")
    for k, v in avg_fixation_placement.items():
        print(k, ": ", mean(v))
    if plot==True:
        df = pd.concat(dfs)
        df_dict = {'fixations':[], 'segment':[], 'study':[]}
        for k,v in avg_fixation_placement.items():
            if k!='target':
                df_dict['fixations'].extend(v)
                df_dict['segment'].extend([k for x in range(0, len(v))])
                df_dict['study'].extend(['combined' for x in range(0, len(v))])
        for k,v in study1_avg_fixation_placement.items():
            if k!='target':
                df_dict['fixations'].extend(v)
                df_dict['segment'].extend([k for x in range(0, len(v))])
                df_dict['study'].extend(['1' for x in range(0, len(v))])
        for k,v in study2_avg_fixation_placement.items():
            if k!='target':
                df_dict['fixations'].extend(v)
                df_dict['segment'].extend([k for x in range(0, len(v))])
                df_dict['study'].extend(['2' for x in range(0, len(v))])
        color_dict = {'2': "#cc0000", '1': "#1155cc", 'combined':'#9900ff'}
        sns.violinplot(data = pd.DataFrame.from_dict(df_dict), x='fixations', y ='segment', 
                    hue='study', palette=color_dict, cut=0, legend=False, inner='point')
        plt.show()

def get_summary_stats(dfs, plot=False):
    df = pd.concat(dfs)
    print("---Summary Statistics---")
    print ("Average fixation duration: ", df['duration'].mean())
    print ("Average num fixations: ", df['duration'].count()/len(dfs))
    print ("Total fixation time: ", df['duration'].sum())

    print("---")
    tot_dur_fixations = df['duration'].sum()
    print ("Total fixation time on root method ", \
           df[df.method_category == 'target']['duration'].sum(), ' ', \
           df[df.method_category == 'target']['duration'].sum()/tot_dur_fixations)
    print ("Total fixation time on nonroot call graph methods ", \
           df[df.method_category.isin(['call_graph_up', 'call_graph_down'])]['duration'].sum(), ' ', \
           df[df.method_category.isin(['call_graph_up', 'call_graph_down'])]['duration'].sum()/tot_dur_fixations)
    print ("    Total fixation time on upward nonroot call graph methods ", \
           df[df.method_category == 'call_graph_up']['duration'].sum(), ' ', \
           df[df.method_category == 'call_graph_up']['duration'].sum()/tot_dur_fixations)
    print ("    Total fixation time on downward nonroot call graph methods ", \
           df[df.method_category == 'call_graph_down']['duration'].sum(), ' ', \
           df[df.method_category == 'call_graph_down']['duration'].sum()/tot_dur_fixations)
    print ("Total fixation time on non call graph methods ", \
           df[df.method_category == 'non_call_graph']['duration'].sum(), ' ', \
           df[df.method_category == 'non_call_graph']['duration'].sum()/tot_dur_fixations)
    print ("Total fixation time on non methods ", \
           df[df.method_category == 'no_method']['duration'].sum(), ' ', \
           df[df.method_category == 'no_method']['duration'].sum()/tot_dur_fixations)
    
    if plot == True:
        x = ['Proportion of Total Fixation Time']
        y1 = df[df.method_category == 'target']['duration'].sum()/tot_dur_fixations
        y2 = df[df.method_category == 'call_graph_up']['duration'].sum()/tot_dur_fixations
        y3 = df[df.method_category == 'call_graph_down']['duration'].sum()/tot_dur_fixations
        y4 = df[df.method_category == 'non_call_graph']['duration'].sum()/tot_dur_fixations
        y5 = df[df.method_category == 'no_method']['duration'].sum()/tot_dur_fixations
        
        plt.figure(figsize=(1, 5))
        plt.bar(x, y1, color='#c0241c')
        plt.bar(x, y2, bottom=y1, color='#2854c5')
        plt.bar(x, y3, bottom=y1+y2, color='#98ade3')
        plt.bar(x, y4, bottom=y1+y2+y3, color='gray')
        plt.bar(x, y5, bottom=y1+y2+y3+y4, color='darkgray')
        plt.show()
    return df

def load_data():
    callees_dfs = []
    callers_dfs = []
    for i in range (1, 6):
        task = project_dict[i]
        callers_fnames = glob.glob(f"output/T{i}/callers_*.csv")
        callees_fnames = glob.glob(f"output/T{i}/callees_*.csv")

        def process_file(f):
            df = pd.read_csv(f)
            if "callers_" in f:
                f = f.replace("callers_", "")
            if "callees_" in f:
                f = f.replace("callees_", "")
            method = f.split(".csv")[0].split("/")[-1]
            df["total_score"] = df["conciseness"] + df["accuracy"] + df["completeness"] + df["clarity"]
            def get_percentile(pop, x):
                pop = [p for p in pop if isinstance(p, float)]
                if isinstance(x, float):
                    return stats.percentileofscore(pop, x, kind="mean")
                return None
            df["score_percentile"] = df.apply(lambda x: get_percentile(df['total_score'], x['total_score']), axis=1)
            df["conf_percentile"] = df.apply(lambda x: get_percentile(df['confidence'], x['confidence']), axis=1)
            df["conf_perc_diff"] = df["conf_percentile"] - df['score_percentile']
            df["conf_abs_perc_diff"] = abs(df["conf_perc_diff"])
            df["total_fixation_time"] = df['avg_fixation_duration']*df['num_fixations']
            df["task"] = task
            df["method"] = method
            df["participant"] = df.apply(lambda x: int(x['trial'].split("_")[0]), axis=1)
            df['study'] = df.apply(lambda x: '2' if x['participant'] > 20 else '1', axis=1)
            return df
        for f in callees_fnames:
            callees_dfs.append(process_file(f))
        for f in callers_fnames:
            callers_dfs.append(process_file(f))
    return pd.concat(callees_dfs), pd.concat(callers_dfs)

def get_depth_stats(callee_data, caller_data):
    print("---Depth Statistics---")
    for i in range(0, 6):
        print(f"Callee % reached depth {i}: ", len(callee_data[callee_data.max_depth >= i]['max_depth'])/
          len(callee_data['max_depth']))
        print(f"Caller % reached depth {i}: ", len(caller_data[caller_data.max_depth >= i]['max_depth'])/
          len(caller_data['max_depth']))
    print('Callee mean max depth', callee_data['max_depth'].mean())
    print("Callee max depth 90%: ", np.percentile(callee_data['max_depth'], 90))
    print('Caller mean max depth', caller_data['max_depth'].mean())
    print("Caller max depth 90%: ",np.percentile(caller_data['max_depth'], 90))
    def cohend(d1, d2):
        n1, n2 = len(d1), len(d2)
        s1, s2 = np.var(d1, ddof=1), np.var(d2, ddof=1)
        s = np.sqrt(((n1 - 1) * s1 + (n2 - 1) * s2) / (n1 + n2 - 2))
        u1, u2 = mean(d1), mean(d2)
        return (u1 - u2) / s
    print("T-test max depth")
    print(scipy.stats.ttest_ind(callee_data['max_depth'], caller_data['max_depth']), cohend(callee_data['max_depth'], caller_data['max_depth']))
    print("T-test average depth")
    print(scipy.stats.ttest_ind(callee_data['average_depth'], caller_data['average_depth']), cohend(callee_data['average_depth'], caller_data['average_depth']))
    pvalues = []
    for x in ['node_coverage', 'weighted_node_coverage', 'edge_coverage', 'weighted_edge_coverage']:
        print(f"Callee mean {x}: ", callee_data[x].mean())
        print(f"Caller mean {x}: ", caller_data[x].mean())
        ttest = scipy.stats.ttest_ind(callee_data[x], caller_data[x]), cohend(callee_data[x], caller_data[x])
        print(ttest)
        pvalues.append(ttest[0].pvalue)
    print("FDR: ", fdrcorrection(pvalues))
    

def run_analysis(mode="all", prefix = None, plot=False):
    print(f"---{mode}---")
    dfs = get_dfs(mode)
    get_fixation_positions(dfs, plot)
    get_summary_stats(dfs, plot)

    callee_data, caller_data = load_data()
    prefix = mode if prefix is None else prefix
    if mode == 2 or mode == 1:
        callee_data = callee_data[callee_data.participant > 20] if mode==2 else callee_data[callee_data.participant < 20]
        caller_data = caller_data[caller_data.participant > 20] if mode==2 else caller_data[caller_data.participant < 20]
    for m in ["scale", "points", "ensureCapacity", "computeGradient", "urlGetArgs", "drawRenderingTimeStrings",
              "accept", "draw"]:
        callee_data = callee_data[callee_data.method != m]
    
    # Exclude participants who never even looked at the method they're summarizing
    callee_data = callee_data[callee_data.node_coverage > 0]
    caller_data = caller_data[caller_data.node_coverage > 0]
    
    get_depth_stats(callee_data, caller_data)

    # Save data to analyze with R
    callee_data['average_total_score'] = callee_data['total_score']/4
    callee_data.to_csv(f"{prefix}_callee_plot_data.csv")

    caller_data['average_total_score'] = caller_data['total_score']/4
    caller_data.to_csv(f"{prefix}_caller_plot_data.csv")

def calc_method_prop():
    project_method_counts = {}
    for task in ["scrimage", "mltk", "mallet", "openaudible", "freecol"]:
        methods = 0
        files = glob.glob(f"{PROJECTS_DIR}/{task}/**/*.java", recursive=True)
        for f in files:
            lines = open(f, 'r').readlines()
            for i, l in enumerate(lines):
                if (is_method_header(lines, i)):
                    methods+=1
        project_method_counts[task] = methods
    num = 0
    denom = 0
    def tree_to_list(root):
        l = [root.method.split("_")[0]]
        for c in root.children:
            l = l + tree_to_list(c)
        return l
    
    reverse_method_dict = {}
    for k, v in method_dict.items():
        for m in v:
            reverse_method_dict[m] = project_dict[k]
    for m in VALID_CALLEE_METHODS:
        call_graph = read_call_graph(m)
        call_tree_root = build_call_tree(call_graph, m)
        prop = len(list(set(tree_to_list(call_tree_root))))/project_method_counts[reverse_method_dict[m.split(":")[1].split("(")[0]]]
        num += prop
        denom+=1
    for m in VALID_CALLER_METHODS:
        call_graph = read_call_graph(m, up=True)
        call_tree_root = build_call_tree(call_graph, m)
        prop = len(list(set(tree_to_list(call_tree_root))))/project_method_counts[reverse_method_dict[m.split(":")[1].split("(")[0]]]
        num += prop
        denom+=1
    print("% methods in call graph: ", num/denom)
                    
if __name__ == "__main__":
    calc_method_prop()
    run_analysis(2, "study2_me")
    run_analysis(1, "study1_me")
    run_analysis("all", "all_me")
