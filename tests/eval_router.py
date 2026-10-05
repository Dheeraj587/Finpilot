import json
from app.state import financestate
from app.nodes.router import router_node

with open('tests/eval_set.json')as f:
    cases =json.load(f)

correct =0
for case in cases:
    result =router_node(financestate(user_message=case['message']))
    ok =result['route']==case['expected_route']
    correct+= ok
    print(f"{'PASS' if ok else 'FAIL'} | expected={case['expected_route']:6} got ={result['route']:6}| {case['message']}")
    if not ok:
        print(f"   reason: {result['route_reason']}")
print(f"\nRouting accuracy: {correct}/{len(cases)}={correct/len(cases):.0%}")
