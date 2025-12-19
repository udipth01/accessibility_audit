import json

def issue_key(issue):
    return json.dumps(issue, sort_keys=True)

def diff_issues(prev, curr):
    diff = {}
    for key in ["MissingAlt","LinksNoName","ButtonsNoLabel","InputsNoLabel","HeadingOrderIssues"]:
        prev_set = set(issue_key(i) for i in prev.get(key, []))
        curr_set = set(issue_key(i) for i in curr.get(key, []))
        diff[key] = {
            "FIXED": list(prev_set - curr_set),
            "NEW": list(curr_set - prev_set)
        }
    return diff
