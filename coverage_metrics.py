import pandas as pd

from call_graph_builder import build_call_tree, read_call_graph

def calculate_coverage_metrics(f_list, func_name, up = False):
    full_call_graph = read_call_graph(func_name, up)
    call_tree_root = build_call_tree(full_call_graph, func_name)
    keys = ["trial", "weighted_node_coverage", "node_coverage", "weighted_edge_coverage", "edge_coverage", 
            "avg_fixation_duration", "num_fixations", "accuracy", "completeness", "conciseness", 
            "clarity", "confidence"]
    output_df = {k:[] for k in keys}
    root_search_dict = dict({})
    for f in f_list:
        project = f.split("/")[1]
        df = pd.read_csv(f)
        try:
            output_df["trial"].append(f.split("processed_P")[-1].split(".")[0])
            results, root_search_dict = calculate_depth(df, call_tree_root, root_search_dict)
            for k,v in results.items():
                if k not in output_df:
                    output_df[k] = [v]
                else:
                    output_df[k].append(v)
            
            call_path = list(results["path"])
            node_coverage = calculate_node_coverage(call_tree_root, call_path)
            output_df["weighted_node_coverage"].append(node_coverage[0])
            output_df["node_coverage"].append(node_coverage[1])
            edge_coverage = calculate_edge_coverage(call_tree_root, call_path)
            output_df["weighted_edge_coverage"].append(edge_coverage[0])
            output_df["edge_coverage"].append(edge_coverage[1])
            avg_fixation_duration, num_fixations = get_summary_stats(f)
            output_df["avg_fixation_duration"].append(avg_fixation_duration)
            output_df["num_fixations"].append(num_fixations)
            for c in ['accuracy', 'completeness', 'conciseness', 'clarity', 'confidence']:
                output_df[c].append(df[c][0])
        except Exception as e:
            print(e)
            print('Error in: ', f, f.split("processed_P")[-1].split(".")[0])
            num_valid = min([len(v) for k,v in output_df.items()])
            output_df = {k:v[:num_valid] for k,v in output_df.items()}

    method_name = call_tree_root.method.split(":")[-1].split("(")[0]
    df = pd.DataFrame.from_dict(output_df)
    if up:
        df.to_csv(f"output/{project}/callers_{method_name}.csv")
        print(f"Wrote results to 'output/{project}/callers_{method_name}.csv'")
    else:
        df.to_csv(f"output/{project}/callees_{method_name}.csv")
        print(f"Wrote results to 'output/{project}/callees_{method_name}.csv'")

def calculate_depth(df, call_tree_root, root_search_dict, v = False):
    call_tree_root.parents = []
    def root_search(method_name):
        if len(method_name) == 0:
            return None
        if method_name in root_search_dict.keys():
            return root_search_dict[method_name]
        q = [call_tree_root]
        while len(q) > 0:
            cur = q.pop(0)
            if cur.method.split("_")[0] == method_name:
                root_search_dict[method_name] = cur
                return cur
            else:
                for n in cur.children:
                    q.append(n)
        root_search_dict[method_name] = None
        return None
 
    def update_dur(depth, dur):
        fixation_per_depth[depth]=fixation_per_depth[depth]+dur if depth in fixation_per_depth else dur
    
    max_depth = 0
    fixation_per_depth = {}
    edge_count = 0
    nonedge_count = 0
    path = []

    cur_node = None
    for index, row in df.iterrows():
        file = row['fixation_target'].split(".")[0]
        # file = row['gaze_target'].split(".")[0]
        method_name = row['method_name']
        row_method = file + ":" + method_name if isinstance(method_name, str) > 0 else ''
        if cur_node is not None:
            if cur_node.method.split("_")[0] != row_method:
                # If the next node is a child
                if row_method in [c.method.split("_")[0] for c in cur_node.children]:
                    cur_node = [c for c in cur_node.children if c.method.split("_")[0] == row_method][0]
                    path.append(cur_node.method)
                    edge_count+=1
                # If the next node is a parent
                elif row_method in [c.method.split("_")[0] for c in cur_node.parents]:
                    cur_node = [c for c in cur_node.parents if c.method.split("_")[0] == row_method][0]
                    path.append(cur_node.method)
                    edge_count+=1
                # If the next node doesn't share an edge
                else:
                    new_node = root_search(row_method)
                    if new_node is not None:
                        cur_node = new_node
                        path.append(cur_node.method)
                        nonedge_count +=1

            update_dur(cur_node.depth, row['duration'])
            max_depth = cur_node.depth if cur_node.depth > max_depth else max_depth
        elif row_method == call_tree_root.method.split("_")[0]:
            cur_node = call_tree_root
            path.append(cur_node.method)
            update_dur(0, row['duration'])
    
    e = edge_count/(nonedge_count + edge_count) if nonedge_count + edge_count > 0 else 0

    results = dict({"max_depth": max_depth,
                    "edges_proportion": e,
                    "path": path})
        
    weighted_duration = 0
    tot_duration = 0
    for n in range(0, 6):
        if n in fixation_per_depth:
            weighted_duration+= n * fixation_per_depth[n]
            tot_duration+= fixation_per_depth[n]
    results["average_depth"] = weighted_duration/tot_duration if tot_duration != 0 else 0
    return results, root_search_dict

def calculate_node_coverage(call_tree_root, call_path):
    def tree_to_list(root):
        l = [root.method.split("_")[0]]
        for c in root.children:
            l = l + tree_to_list(c)
        return l
    unlevelled_call_path = [c.split("_")[0] for c in call_path]
    coverage = len(set(unlevelled_call_path))
    def calc_weighted(root):
        num = 1 if root.method.split("_")[0] in unlevelled_call_path else 0
        denom = 1
        for c in root.children:
            results = calc_weighted(c)
            num += 1/len(root.children)*results[0]
            denom += 1/len(root.children)*results[1]
        return num, denom
    weighted_coverage = calc_weighted(call_tree_root)

    return weighted_coverage[0]/weighted_coverage[1], coverage

def calculate_edge_coverage(call_tree_root, call_path):
    def get_all_edges(node):
        e = []
        for c in node.children:
            e.append(f"{node.method}->{c.method}")
            e = e + get_all_edges(c)
        return e

    call_path_edges = [f"{call_path[i]}->{call_path[i+1]}" for i in range(0, len(call_path)-1)]
    all_edges = get_all_edges(call_tree_root)

    def calc_weighted(root):
        denom = len(root.children)
        num = 0
        for c in root.children:
            edge = f"{root.method}->{c.method}"
            if edge in call_path_edges:
                num +=1
            result = calc_weighted(c)
            num+= 1/len(root.children) * result[0]
            denom+= 1/len(root.children) * result[1]
        return num, denom

    weighted_coverage = calc_weighted(call_tree_root)

    coverage = len(set([e for e in call_path_edges if e in all_edges]))
    total = len(all_edges)
    if weighted_coverage[1] == 0:
        return 0, coverage
    return weighted_coverage[0]/weighted_coverage[1], coverage

def get_summary_stats(f):
    df = pd.read_csv(f)
    
    avg_fixation_duration = 0
    num_fixations = 0
    
    prev_node = ''
    prev_duration = 0

    for index, row in df.iterrows():
        file = row['fixation_target'].split(".")[0]
        method_name = row['method_name']
        node = file + ":" + method_name if isinstance(method_name, str) > 0 else ''
        
        if node == prev_node:
            prev_duration += row['duration']
        elif prev_node != '':
            avg_fixation_duration = (avg_fixation_duration*num_fixations + prev_duration)/(num_fixations+1)
            num_fixations+=1

        prev_node = node
        prev_duration = row['duration']
    
    return avg_fixation_duration, num_fixations
