import re
import json


text = """
% of pepole exit partys without telling people they're leaving - 25%
% of people have purchased condoms from gas station bathroom dispensers - 17%
When seeing their neighbors in passing, what % of people normally do NOT greet them using their first names? - 63%
% of people only go to the Dentist when something is wrong? - 53%
% of people have attended an Ugly Sweater Party? - 35%
When a Mariachi band suddely appears, what % of people are more annoyed than anything else? - 40%
% of people have ever had usernames (email, Twitter, etc) with the number 69 in them? - 9%
% of people keep diaries or journals that they update pretty much daily? - 4%
% of people have purchased car washes at gas astations in the past year? - 43%
% of people have parachuted out of an aircraft? - 5%
% of people own more mittens than they do gloves? - 5%
% of people have visitied cemeteries where nobody they knew was buried? - 73%
% of people have vaped? - 32%
% of people said they would keep working at their jobs if they won $900 million in the lottery? - 37%
% of people have left scathing notes on strangers' cars because of poor parking jobs or other vehicular offenses? - 24%
% of people regularly talk out loud to themselves when alone? - 76%
% of epople reguarly cut off, or avoid eating, the crusts on their sandwiches? - 13%
% of people prefer brownies with nuts over nutless brownies? - 30%
% of people have donated to crowdfunding projects? - 70%
% of people have photobombed total strangers? - 53%
% of people woudl rather come up with different usernames than different passwords? - 30%
% of people like their orange juice with pulp rather than pulp-free? - 44%
% of people own movies starring Gerard Depardieu? - 8%
% of people prefer The Rolling Stones to The Beatles? - 23%
% of people have used a search engine to get information about someone before a first date? - 39%
% of people have functioning VCRs in their homes? - 42%
% of people regularly pay for things costing less than a dollar with credit cards? - 3%
% of people would generally rather clean the toilet than wash the dishes? - 32%
% of people wash their bed sheets at least once a week? - 12%
% of people, at this very moment, have more than five magnets on their refridgerator? - 77%
% of people have bought "As Seen on TV" or informercial products? - 66%
% of people take their Oreos apart before eating them? - 46%
% of people have ever put potato chips IN a sandwich? - 70%
% of people generally ignore restaurant straws and drink straightfrom the glass? - 14%
% of people would, if offered by a sexy vampire, seize the chance to become vampires themselves? - 45%
% of people have accidentally walked in on their parents having sex? - 22%
"""



pattern = r"% of (.*?) - (\d+)%"
matches = re.findall(pattern, text)

result = [
    {"question": f"What percentage of {statement}?", "answer": int(percent)}
    for statement, percent in matches
]

print(json.dumps(result, indent=2))



