import uuid
import csv
from operator import le
import random


class Person:
    def __init__(self, name, team, uid=uuid.uuid4()):
        self._uid = uid
        self._name = name
        self._team = team

    @property
    def uid(self):
        return self._uid

    @property
    def name(self):
        return self._name

    @property
    def team(self):
        return self._team


class PersonRegistry:
    def __init__(self):
        self._uid_to_person = {}
    
    def register_person(self, person):
        assert(person.uid not in self._uid_to_person)
        self._uid_to_person[person.uid] = person


class Relation:
    pass

class Relations:
    pass

class CSVExtractor:
    def extract(file_path) -> tuple[PersonRegistry, Relations]:
        return PersonRegistry(), Relations()

pre_match_users = [

]

tell_topics_to_users = {}
hear_topics_to_users = {}
user_id_to_name = {}
user_name_to_id = {}
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
        assert name not in user_name_to_id.keys()
        user_name_to_id[name] = user_id
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

def norm_topic(t):
    return t.replace("נושאים [", "").replace("]", "")

def generate_match():
    user_ids_in_match = []
    matchs = []

    topics_by_tellers = random_list(topics)

    def make_match(hear_user_id, tell_user_id, topic=None):
        # Find more topics:
        more_topics = []
        for topic_i in topics:
            if topic_i == topic:
                continue

            if (hear_user_id in hear_topics_to_users[topic_i]) and (tell_user_id in tell_topics_to_users[topic_i]):
                more_topics.append(topic_i)
                continue

            if (hear_user_id in tell_topics_to_users[topic_i]) and (tell_user_id in hear_topics_to_users[topic_i]):
                more_topics.append(topic_i)
                continue
        
        if topic == None:
            if len(more_topics) == 0:
                return

            topic = more_topics[0]
            more_topics = more_topics[1:]

        matchs.append((user_id_to_name[hear_user_id], user_id_to_team[hear_user_id], user_id_to_name[tell_user_id], user_id_to_team[tell_user_id], norm_topic(topic), ", ".join([norm_topic(x) for x in more_topics])))
        user_ids_in_match.append(hear_user_id)
        user_ids_in_match.append(tell_user_id)

    pre_match_users_ids = [(user_name_to_id[a], user_name_to_id[b]) for (a, b) in pre_match_users]

    for pre_match in pre_match_users_ids:
        make_match(*pre_match)

    i = 0
    while ((2 * len(matchs)) < len(user_id_to_name)) and (i < 100):
        i += 1

        topic = random.choice(topics_by_tellers)

        tell_users_for_topic = random_list(tell_topics_to_users[topic])

        for tell_user_id in tell_users_for_topic:
            hear_users_for_topic = random_list(hear_topics_to_users[topic])

            for hear_user_id in hear_users_for_topic:
                if user_id_to_team[hear_user_id] == user_id_to_team[tell_user_id]:
                    continue

                if (tell_user_id in user_ids_in_match) or (hear_user_id in user_ids_in_match):
                    continue
                
                make_match(hear_user_id, tell_user_id, topic=topic)
    
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
for i in range(30000):
    match = generate_match()
    if len(max_match) < len(match):
        max_match = match

    if (2 * len(max_match)) == len(user_id_to_name):
        break

iter_to_max = max(i * 2, 5000)
max_len = len(max_match)

max_more_topics = count_more_topics(max_match)
for i in range(iter_to_max):
    match = generate_match()
    if len(match) != max_len:
        continue

    if max_more_topics < count_more_topics(match):
        max_match = match

message = ""
for i in range(len(max_match)):
    match = max_match[i]
    name1, team1, name2, team2, topic, more_topics = match

    message += "*זוג {} - נושא: {}*\n".format(i + 1, topic)
    message += name1 + " ({})\n".format(team1)
    message += name2 + " ({})\n".format(team2)
    if len(more_topics) > 0:
        message += "נושאים נוספים : " + more_topics + "\n"
    message += "\n"

print(message)