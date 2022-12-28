import csv
from operator import le
import random

tell_topics_to_users = {}
hear_topics_to_users = {}
user_id_to_name = {}
user_id_to_team = {}
user_id_to_tell_count = {}
user_id_to_hear_count = {}

def random_list(l):
    return random.choices(l, k=len(l))

with open("/Users/roiamiel/Downloads/kks_match_w1.csv", newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    
    name_field_name = reader.fieldnames[-5]
    team_field_name = reader.fieldnames[-4]

    topics = reader.fieldnames[1:-5]

    for topic in topics:
        tell_topics_to_users[topic] = []
        hear_topics_to_users[topic] = []

    for row in reader:
        name = row[name_field_name]
        team = row[team_field_name]

        user_id = len(user_id_to_name)
        user_id_to_name[user_id] = name
        user_id_to_team[user_id] = team
        user_id_to_tell_count[user_id] = 0
        user_id_to_hear_count[user_id] = 0

        for topic in topics:
            if row[topic] == "רוצה להקשיב":
                hear_topics_to_users[topic].append(user_id)
                user_id_to_hear_count[user_id] += 1
            if row[topic] == "רוצה לספר":
                tell_topics_to_users[topic].append(user_id)
                user_id_to_tell_count[user_id] += 1

def generate_match():
    user_ids_in_match = []
    matchs = []

    topics_by_tellers = random_list(topics)
    # topics_by_tellers.sort(key=lambda topic: len(tell_topics_to_users[topic]))

    for topic in topics_by_tellers:
        tell_users_for_topic = random_list(tell_topics_to_users[topic])
        tell_users_for_topic.sort(key=lambda id: user_id_to_tell_count[id])

        for tell_user_id in tell_users_for_topic:
            hear_users_for_topic = random_list(hear_topics_to_users[topic])
            hear_users_for_topic.sort(key=lambda id: user_id_to_hear_count[id])

            for hear_user_id in hear_users_for_topic:
                if user_id_to_team[hear_user_id] == user_id_to_team[tell_user_id]:
                    continue

                if (tell_user_id in user_ids_in_match) or (hear_user_id in user_ids_in_match):
                    continue

                matchs.append((user_id_to_name[hear_user_id], user_id_to_team[hear_user_id], user_id_to_name[tell_user_id], user_id_to_team[tell_user_id], topic))
                user_ids_in_match.append(hear_user_id)
                user_ids_in_match.append(tell_user_id)
    
    return matchs


max_match = generate_match()
for i in range(10000):
    match = generate_match()
    if len(max_match) < len(match):
        max_match = match

for match in max_match:
    print(" - ".join(match))
print(len(max_match))