from pathlib import Path
import pandas as pd

from constants import ALL_METHODS, DATA_DIR

project_dict = {"scrimage":1, "mltk":2, "mallet":3, "openaudible":4, "freecol":5}

if __name__ == "__main__":
    import glob

    for p in list(range(3, 13)) + list(range(21, 33)):
        path = DATA_DIR
        pid =''

        files = [f for f in glob.glob(path + f"/P{p}-Dats/*/P*.csv")]

        if p< 20:
            with open(path + '/summaries_study1.csv', 'r') as s:
                summaries = pd.read_csv(s)
        else:
            with open(path + '/summaries_study2.csv', 'r') as s:
                summaries = pd.read_csv(s)

        for fname in files:
            with open(fname, 'r') as file:
                project_dir = fname.rsplit(".", 2)[0].split("/")[-1].replace("_", "-")
                project_txt = [f for f in \
                                glob.glob(f"{path}/P{p}-Dats/{project_dir}/*.txt") \
                                if f.split("/")[-1].split(".")[0] in project_dict.keys() or \
                                f.split("/")[-1].split(".")[0] == "srcimage"][0]
                participant = int(fname.split(f"{path}/P")[1].split("-Dats")[0])
                project = project_txt.split("/")[-1].split(".")[0]
                if project == 'srcimage':
                    project = 'scrimage'
                method_num = int(fname.split(".")[-2])
                txt_file = open(project_txt, 'r')
                txt_body = txt_file.read()
                method_name = txt_body.split(f"Method {method_num}:")[1].lstrip().split('\n')[0].split()[1]
                method_name = method_name.replace("SetColors", "setColors")
                def truncate_method(m):
                    return m.split()[1].replace("SetColors", "setColors")
                summaries['method_trunc'] = summaries.apply(lambda x: truncate_method(x.path), axis=1)
                try:
                    row = summaries[(summaries.participant == participant) & (summaries.project == project) \
                                            & (summaries.method_trunc == method_name)]
                    try:
                        task_name = row.path.values[0].split()[-3].replace("SetColors", "setColors")
                        accuracy = float(row.Accuracy.values[0])
                        completeness = float(row.Completeness.values[0])
                        conciseness = float(row.Conciseness.values[0])
                        clarity = float(row.Clarity.values[0])
                    except:
                        task_name = method_name
                        accuracy = None
                        completeness = None
                        conciseness = None
                        clarity = None
                    try:
                        confidence = float(txt_body.split(f"Method {method_num}:")[1].split("scale of 1-5:")[1].lstrip().split()[0])
                    except:
                        try: 
                            confidence = float(txt_body.split(f"Method {method_num}:")[1].split("onfident:")[1].lstrip().split()[0])
                        except:
                            confidence = None
                    if len(row) == 0:
                        print("No summary found P", participant, project)
                        row = summaries[(summaries.participant == participant) & (summaries.project == project)]
                except Exception  as e:
                    print(f"No summary found, {participant} {project} {method_num}")
                    break

                if task_name in ALL_METHODS:
                    pid = f'P{participant}_T{project_dict[project]}_{task_name}'
                    df = pd.read_csv(open(fname, "r"))
                    df['accuracy'] = accuracy
                    df['completeness'] = completeness
                    df['conciseness'] = conciseness
                    df['clarity'] = clarity
                    df['confidence'] = confidence

                    Path(f"Processed Data/T{project_dict[project]}/P{p}/").mkdir(parents=True, exist_ok=True)
                    df.to_csv(f"Processed Data/T{project_dict[project]}/P{p}/"+pid+".csv")   