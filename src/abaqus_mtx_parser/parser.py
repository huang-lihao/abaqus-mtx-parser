import numpy as np
import re


class MtxFile:
    def __init__(self) -> None:
        self.stiffness: np.array = None
        self.mass: np.array = None
        self.nodes: list = None
        self.dof: dict[int, list[int]] = {}
        self.data: list = None


def parse_mtx(file_name: str):
    result = MtxFile()
    with open(file_name, "r") as mtx:
        lines = mtx.readlines()

    data = []
    frame = None
    for line in lines:
        if re.match('^\*{1}([A-Za-z0-9,=\s]{1,})\n$', line):
            variable = line.lstrip('*').rstrip().split(',')
            data.append((
                variable[0], {}
            ))
            keyword = variable[0]
            frame = data[-1][1]
            frame["parameter"] = {}
            for v in variable[1:]:
                t = v.split("=")
                if len(t) == 1:
                    frame["parameter"][t[0].strip()] = True
                elif len(t) == 2:
                    frame["parameter"][t[0].strip()] = t[1].strip()
            frame["data"] = []
            continue
        if frame:
            if re.match('^\*{2}([A-Za-z0-9,=\s]{1,})\n$', line):
                text = line.lstrip("*").strip()
                if "comments" in frame:
                    frame["comments"].append(text)
                else:
                    frame["comments"] = [text]
            else:
                if re.match(
                    "^(\s*-?\d*(\.\d*)?([Ee][+-]\d*)?[,]*[\s]*)+\n$",
                    line,
                ):
                    variable = line.strip().rstrip(",").split(",")
                    if keyword == "USER ELEMENT":
                        frame["data"].append(variable)
                    else:
                        frame["data"].extend(variable)

    for d in data:
        if d[0] == "USER ELEMENT":
            if "UNSYM" in d[1]["parameter"]:
                symmetric = False
            else:
                symmetric = True

            dof_raw = d[1]["data"]
            dof_raw = [[int(vv) for vv in v] for v in dof_raw]
            dof_raw[0].insert(0, 1)
            dof_raw = {v[0] - 1: v[1:] for v in dof_raw}
            node_keys = sorted(list(dof_raw.keys()))

            nodes = [
                int(n)
                for n in "".join(d[1]["comments"][1:]).split(",")
            ]
            num_nodes = int(d[1]["parameter"]["NODES"])
            assert num_nodes == len(nodes)
            result.nodes = nodes

            j = 0
            for i, node in enumerate(nodes):
                if len(node_keys) == 1:
                    result.dof[node] = dof_raw[node_keys[0]]
                    continue

                if (j + 1) < len(node_keys) and i == node_keys[j + 1]: j += 1
                result.dof[node] = dof_raw[node_keys[j]]

    for d in data:
        if d[0] == "MATRIX":
            d[1]["data"] = np.array([
                float(v)
                for v in d[1]["data"]
            ])

            array = d[1]["data"]
            if not symmetric and d[1]["parameter"]["TYPE"] == "STIFFNESS":
                n = int(np.sqrt(len(array)))
                assert n * n == len(array)
                d[1]["data"] = array.reshape((n, n))
            else:
                n = int(np.floor(np.sqrt(2 * len(array))))
                assert n * (n + 1) / 2 == len(array)
                d[1]["data"] = np.zeros((n, n))
                d[1]["data"][np.tril_indices(n)] = array
                d[1]["data"].T[np.tril_indices(n)] = array
            
            if d[1]["parameter"]["TYPE"] == "STIFFNESS":
                result.stiffness = d[1]["data"]
            elif d[1]["parameter"]["TYPE"] == "MASS":
                result.mass = d[1]["data"]
    result.data = data

    return result
