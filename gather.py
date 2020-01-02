#!/usr/bin/env python3
#
#
"""
gather
- retrieve all competitions with their participants

result is:
- stored copy of the competion.json  (WetId__GrpId.json)
- a list of all participants, with the list of all WetId__GrpId in json format

This will allow to query for a list of participants and their shared
competitions resulting in a list of competitions, where at least two
participants participated.

This will then generate a matrix on all participants in the list vs.
the competitions

"""

import json
from os import listdir
import os
import re

from pyquery import PyQuery
import requests

Directory = os.path.join(os.path.dirname(__name__), 'competitions')

Participants = {}

base_url = "https://www.digitalrock.de/"
json_url = "https://www.digitalrock.de/egroupware/ranking/json.php?"


def get_links_from_html(content):
    """
    helper - to parse a html page for <a href='link'>
    and return the list of links

    :return: generator to return the links
    """

    pq = PyQuery(content)

    for tag in pq("a"):
        yield tag.attrib.get('href')


def gather_competition_data(comp_url, target_directory=None):
    """
    gather all competition data from the url:
        "https://www.digitalrock.de/dav_calendar.php?no_dav=1&year=2019"

    :return: - nothing - but side efect are the competition
             files in target directory
    """

    print("Fetching competition data from %r" % comp_url)

    response = requests.get(comp_url)
    html_content = response.text

    # try to create the target directory if it did not exist

    if not target_directory:
        target_directory = Directory

        if not os.path.exists(target_directory):
            raise Exception('directory does not exist: %r' % target_directory)

    for href in get_links_from_html(html_content):

        if not href or not href.startswith('/egroupware'):
            continue

        _, _, params = href.partition('!')

        if not params:
            continue

        competition = params.replace("&", "::") + '.json'
        filename = os.path.join(target_directory, competition)

        if os.path.exists(filename):
            print("File already exists: %r" % filename)
            continue

        print("fetching competition %r" % params)
        response = requests.get(json_url + params)

        if not response.ok:
            print("Error while fetchin data")
            continue

        jresp = json.loads(response.text)

        with open(filename, "w") as f:
            f.write(json.dumps(jresp, indent=4))


def add_participant(participant, gender, competition, discipline, participants):
    """
    helper
     to add a participant to the directory of all participants (last argument)

    :param participant: the raw participant input from the competition (dict)
    :param gender: one of 'Maenner' oder 'Frauen'
    :param competition: the name of the competition
    :param discipline: one of 'Bouldern', 'Lead', 'Speed', 'Combined'

    :param participants: the directory of all participants

    """

    firstname = participant.get("firstname")
    lastname = participant.get("lastname")
    rank = participant.get('result_rank', '')

    comp = {
        'name': competition,
        'rank': rank,
        'discipline': discipline
    }

    PerId = participant.get("PerId")
    if PerId not in participants:

        participants[PerId] = {
            'firstname': firstname,
            'lastname': lastname,
            'gender': gender,
            'PerId': PerId,
            'Competitions': [comp],
        }
    else:
        participants[PerId]['Competitions'].append(comp)


def is_standard_competition(json_data):
    """ helper - to check if this is a standard competition """

    if 'participants' in json_data:
        return True
    return False


def get_fallback_gender(json_data):

    fallback_gender = None
    categorie_name = None

    categories = json_data.get('categories', json_data.get('categorys', ''))

    if "GrpId" in json_data and categories:
        grp_id = json_data["GrpId"]
        for categorie in categories:
            if categorie.get("GrpId", '') == grp_id:
                categorie_name = categorie.get('name')

    if not categorie_name and 'route_name' in json_data:
        categorie_name = json_data['route_name']

    damen_exps = ['weiblich', 'D A M E N', 'W O M E N']
    for damen_exp in damen_exps:
        if damen_exp in categorie_name:
            return 'Damen'

    men_exps = ['männlich', 'H E R R E N', 'M E N', 'Junioren']
    for men_exp in men_exps:
        if men_exp in categorie_name:
            return 'Maenner'

    return fallback_gender


def gather_std_participants(json_data, competition, participants):
    """
    gather the participants from all competitions

    :param json_data: the competition structure where the partitions reside
    :param competition: the name of the competition
    :param participants: the result dict with all participants
    """

    discipline = get_discipline(json_data.get('discipline', ''))

    fallback_gender = get_fallback_gender(json_data)

    for participant in json_data.get('participants', []):
        gender = get_gender(participant, fallback_gender)
        add_participant(
            participant, gender, competition, discipline, participants)


def is_compound_competition(json_data):
    """ helper - to check if this is a compunt competition """

    if json_data.get('categorys', []):
        return True
    return False


def get_gender(data, fallback_gender=None):
    """ helper to guess the gender from the competition describing rkey"""

    rkey = data.get("rkey", "")

    if not rkey:

        if not fallback_gender:
            print('unknown gender')

        return fallback_gender

    damen_regs = [r'.*F.$', r'.*F..$', r'.*F$', r'.*_F_.$', r'.*_F_..$']

    for damen_reg in damen_regs:
        if re.match(damen_reg, rkey):
            return 'Damen'

    herren_regs = [r'.*M.$', r'.*M..$', r'.*M$', r'.*_M_.$', r'.*_M_..$']

    for herren_reg in herren_regs:
        if re.match(herren_reg, rkey):
            return 'Maenner'

    if not fallback_gender:
        print('unknown gender')

    return fallback_gender


def get_discipline(discipline):
    """
    helper
        guess the discipline from the competition name / description
    """

    if 'boulder' in discipline.lower():
        return 'Bouldern'

    elif 'lead' in discipline.lower():
        return 'Lead'

    elif 'speed' in discipline.lower():
        return 'Speed'

    elif 'combined' in discipline.lower():
        return 'Combined'

    else:
        print("unknown categorie")
        return 'Lead'


def gather_compound_participants(json_data, competition, participants):
    """

    """

    for categorie in json_data.get('categorys'):

        discipline = get_discipline(categorie.get('name', ''))

        gender = get_gender(categorie)

        for participant in categorie.get("results"):
            add_participant(
                participant, gender, competition, discipline, participants)


def gather_participants(target_directory=None):

    if not target_directory:
        target_directory = Directory

    if not os.path.exists(target_directory):
        raise Exception('directory does not exist: %r' % target_directory)

    # ---------------------------------------------------------------------- --

    Participants = {}

    for competition in listdir(target_directory):

        competition_file = os.path.join(target_directory, competition)

        if not os.path.isfile(competition_file):
            print('no such file %r' % competition_file)
            continue

        competition = os.path.basename(competition_file)

        print('competition %r' % competition)

        if not competition.startswith('comp='):
            continue

        if not competition.endswith('.json'):
            continue

        print("reading %s " % competition_file)

        with open(competition_file, "r") as f:
            data = f.read()

            try:
                json_data = json.loads(data)
            except Exception as _exx:
                print('unable to load json data: %r' % competition)

            if is_standard_competition(json_data):
                gather_std_participants(
                    json_data, competition, Participants)

            elif is_compound_competition(json_data):
                gather_compound_participants(
                    json_data, competition, Participants)

            else:
                print('unknown competition')

    filename = os.path.join(target_directory, "participants.json")

    with open(filename, "w") as p:
        p.write(json.dumps(Participants, indent=4))


def load_participants(target_directory=None):

    if not target_directory:
        target_directory = Directory

    if not os.path.exists(target_directory):
        raise Exception('directory does not exist: %r' % target_directory)

    # ---------------------------------------------------------------------- --

    filename = os.path.join(target_directory, "participants.json")

    with open(filename, "r") as p:
        data = p.read()

    participants = json.loads(data)

    participant_index = {}

    for PerId, participant in participants.items():

        firstname = participant['firstname']
        lastname = participant['lastname']
        name = firstname + ':' + lastname

        if name not in participant_index:
            participant_index[name] = []

        partids = participant_index[name]
        partids.append(PerId)
        participant_index[name] = partids

    return participant_index, participants


def get_ranking(users):

    boulder = set()
    lead = set()
    speed = set()
    combined = set()

    participant_index, participants = load_participants()

    boulder_users = {}
    speed_users = {}
    lead_users = {}
    combined_users = {}

    for user in users:

        if user not in participant_index:
            continue

        for PerId in participant_index[user]:
            participant = participants[PerId]
            competitions = participant.get('Competitions', [])

            for comp in competitions:

                if comp['discipline'] == 'Bouldern':
                    boulder.add(comp['name'])
                    boulder_users[PerId] = participant

                elif comp['discipline'] == 'Speed':
                    speed.add(comp['name'])
                    speed_users[PerId] = participant

                elif comp['discipline'] == 'Lead':
                    lead.add(comp['name'])
                    lead_users[PerId] = participant

                elif comp['discipline'] == 'Combined':
                    combined.add(comp['name'])
                    combined_users[PerId] = participant

        yield 'bouldern', boulder_users, boulder
        yield 'speed', speed_users, speed
        yield'lead', lead_users, lead
        yield 'combined', combined_users, combined


def write_csv(discipline, query_users, competitions, target_directory=None):

    if not target_directory:
        target_directory = Directory

    if not os.path.exists(target_directory):
        raise Exception('directory does not exist: %r' % target_directory)

    # ---------------------------------------------------------------------- --

    filename = os.path.join(target_directory, discipline + '.csv')

    head = []

    with open(filename, "w") as f:

        for per_id, query_user in query_users.items():

            line = []

            if not head:
                head.append('ProbandenID')
                head.append('Name')
                head.append('Geschlecht')
                for comp in competitions:
                    head.append(comp)
                f.write(','.join(head))
                f.write('\n')

            name = query_user['firstname'] + ' ' + query_user['lastname']
            line.append(name)
            line.append(per_id)
            line.append(query_user['gender'])

            user_competitions = query_user['Competitions']
            for comp in competitions:
                rank = ''
                for user_competition in user_competitions:
                    if comp == user_competition['name']:
                        rank = user_competition['rank']
                        break

                line.append("%s" % rank)

            f.write(','.join(line))
            f.write('\n')

    return

# -------------------------------------------------------------------------- --


def read_users():
    """
    read the users by 'Nachname' and 'Vorname' from commandline

    :return: a list of usenames, with 'firstname::lastname'
    """
    users = []

    while True:

        lastname = input("Nachname: ")
        firstname = input("Vorname: ")

        if 'done' in lastname or 'done' in firstname:
            break

        name = firstname.strip() + ':' + lastname.strip()
        users.append(name)

    return users


def read_users_from_file(filename):
    """
    read the users by 'Nachname' and 'Vorname' from commandline

    :return: a list of usenames, with 'firstname:lastname'
    """
    with open(filename, 'r') as f:
        lines = f.read_lines()

    users = []

    for line in lines:
        vorname, _, nachname = line.partition(' ')

        users.append(vorname.strip() + ':' + nachname.strip())

    return users


def main():

    fetch_competitions = True
    build_participants_index = True
    build_participants_table = True

    if fetch_competitions:
        comp_url = "https://www.digitalrock.de/dav_calendar.php?no_dav=1&year=2019"
        gather_competition_data(comp_url)

    if build_participants_index:
        gather_participants()

    if build_participants_table:

        users = []

        users.append("Anna-Lena:Wolf")
        users.append("Emilia:Merz")
        users.append("Julanda:Peter")

        # users = read_users()

        for disciplin, users, competition in get_ranking(users):
            write_csv(disciplin, users, competition)

    print('completed')


if __name__ == "__main__":
    main()
