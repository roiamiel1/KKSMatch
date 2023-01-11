import csv
from operator import le
import random
import tqdm

pre_match_users = [
    
]

tell_topics_to_users = {}
hear_topics_to_users = {}
talk_topics_to_users = {}
user_id_to_name = {}
user_name_to_id = {}
user_id_to_team = {}
user_id_to_tell_count = {}
user_id_to_hear_count = {}
user_id_to_talk_count = {}

def random_list(l):
    return random.choices(l, k=len(l))

with open("/Users/roiamiel/Downloads/kss_match_w2.csv", newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    
    name_field_name = reader.fieldnames[-4]
    team_field_name = reader.fieldnames[-3]

    topics = reader.fieldnames[1:-4]

    for topic in topics:
        tell_topics_to_users[topic] = []
        hear_topics_to_users[topic] = []
        talk_topics_to_users[topic] = []

    for row in reader:
        name = row[name_field_name]
        team = row[team_field_name]

        user_id = len(user_id_to_name)
        user_id_to_name[user_id] = name
        assert name not in user_name_to_id.keys()
        user_name_to_id[name] = user_id
        user_id_to_team[user_id] = team
        user_id_to_tell_count[user_id] = 0
        user_id_to_hear_count[user_id] = 0
        user_id_to_talk_count[user_id] = 0

        for topic in topics:
            if row[topic] == "רוצה להקשיב":
                hear_topics_to_users[topic].append(user_id)
                user_id_to_hear_count[user_id] += 1
            if row[topic] == "רוצה לספר":
                tell_topics_to_users[topic].append(user_id)
                user_id_to_tell_count[user_id] += 1
            if row[topic] == "רוצה לדבר":
                talk_topics_to_users[topic].append(user_id)
                user_id_to_talk_count[user_id] += 1

def norm_topic(t):
    return t.replace("נושאים [", "").replace("]", "")

def generate_match():
    user_ids_in_match = []
    matchs = []

    topics_by_tellers = random_list(topics)

    def make_match(hear_user_id, tell_user_id, topic=None, force=False):
        if (hear_user_id in user_ids_in_match) or (tell_user_id in user_ids_in_match):
            return

        if hear_user_id == tell_user_id:
            return

        if (not force) and (user_id_to_team[hear_user_id] == user_id_to_team[tell_user_id]):
            return

        # Find more topics:
        more_topics = []
        for topic_i in topics:
            if topic_i == topic:
                continue
            
            total_users = tell_topics_to_users[topic_i] + hear_topics_to_users[topic_i] + talk_topics_to_users[topic_i]
            if (hear_user_id in total_users) and (tell_user_id in total_users):
                more_topics.append(topic_i)
                continue
        
        more_topics = list(set(more_topics))

        if topic == None:
            if len(more_topics) == 0:
                return

            topic = more_topics[0]
            more_topics = more_topics[1:]

        more_topics = random_list(more_topics)[:min(3, len(more_topics) - 1)]

        matchs.append((user_id_to_name[hear_user_id], user_id_to_team[hear_user_id], user_id_to_name[tell_user_id], user_id_to_team[tell_user_id], norm_topic(topic), ", ".join([norm_topic(x) for x in more_topics])))
        user_ids_in_match.append(hear_user_id)
        user_ids_in_match.append(tell_user_id)

    for (user_1_name, user_2_name, topic) in pre_match_users:
        make_match(user_name_to_id[user_1_name], user_name_to_id[user_2_name], topic=topic, force=True)

    i = 0
    while ((2 * len(matchs)) < len(user_id_to_name)) and (i < 100):
        i += 1

        # topic = random.choice(topics_by_tellers)
        for topic in topics_by_tellers:
            for tell_user_id in random_list(tell_topics_to_users[topic]):
                for hear_user_id in random_list(hear_topics_to_users[topic]):
                    make_match(hear_user_id, tell_user_id, topic=topic)

            for talk_user_id in random_list(talk_topics_to_users[topic]):
                for talk_user_id_2 in random_list(talk_topics_to_users[topic]):                
                    make_match(talk_user_id, talk_user_id_2, topic=topic)

                for tell_user_id in random_list(tell_topics_to_users[topic]):
                    make_match(talk_user_id, tell_user_id, topic=topic)
            
    return matchs

def count_more_topics(matchs):
    count = 0
    for match in matchs:
        _, _, _, _, _, more_topics = match
        if len(more_topics) > 0:
            count += 1
        if len(more_topics) >= 2:
            count += 2
    return count

max_match = generate_match()
for i in tqdm.tqdm(range(1000)):
    match = generate_match()
    if len(max_match) < len(match):
        max_match = match

    if (2 * len(max_match)) == len(user_id_to_name):
        break

iter_to_max = max(i * 2, 1000)
max_len = len(max_match)

max_more_topics = count_more_topics(max_match)
for i in tqdm.tqdm(range(iter_to_max)):
    match = generate_match()
    if len(match) != max_len:
        continue

    if max_more_topics < count_more_topics(match):
        max_match = match

message = ""
for i in tqdm.tqdm(range(len(max_match))):
    match = max_match[i]
    name1, team1, name2, team2, topic, more_topics = match

    message += "*זוג {} - נושא: {}*\n".format(i + 1, topic)
    message += name1 + " ({})\n".format(team1)
    message += name2 + " ({})\n".format(team2)
    if len(more_topics) > 0:
        message += "נושאים נוספים : " + more_topics + "\n"
    message += "\n"

print(message)