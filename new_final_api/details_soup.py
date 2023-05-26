import json
import re
import grequests
import requests
import os
import html5lib


from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains

from util import get_safe_nested_key


class UsernameError(Exception):
    pass


class PlatformError(Exception):
    pass


class BrokenChangesError(Exception):
    pass


class UserData:
    def __init__(self, username=None):
        self.__username = username

    def update_username(self, username):
        self.__username = username

    def __codechef(self):
        url = 'https://www.codechef.com/users/{}'.format(self.__username)

        page = requests.get(url)

        soup = BeautifulSoup(page.text, 'html.parser')

        try:
            rating = soup.find('div', class_='rating-number').text
        except AttributeError:
            raise UsernameError('User not Found')

        stars = soup.find('span', class_='rating')
        if stars:
            stars = stars.text

        highest_rating_container = soup.find('div', class_='rating-header')
        highest_rating = highest_rating_container.find_next('small').text.split()[-1].rstrip(')')

        rating_ranks_container = soup.find('div', class_='rating-ranks')
        rating_ranks = rating_ranks_container.find_all('a')

        global_rank = rating_ranks[0].strong.text
        country_rank = rating_ranks[1].strong.text

        if global_rank != 'NA' and global_rank != 'Inactive':
            global_rank = int(global_rank)
            country_rank = int(country_rank)



        def user_details_get():
            user_details_attribute_exclusion_list = {'username', 'link', 'teams list', 'discuss profile'}

            header_containers = soup.find_all('header')
            name = header_containers[1].find('h1', class_="h2-style").text

            user_details_section = soup.find('section', class_='user-details')
            user_details_list = user_details_section.find_all('li')

            user_details_response = {'name': name, 'username': user_details_list[0].text.split('★')[-1].rstrip('\n')}
            for user_details in user_details_list:
                attribute, value = user_details.text.split(':')[:2]
                attribute = attribute.strip().lower()
                value = value.strip()

                if attribute not in user_details_attribute_exclusion_list:
                    user_details_response[attribute] = value

            return user_details_response

        details = {'status': 'Success', 'rating': int(rating), 'stars': stars, 'highest_rating': int(highest_rating),
                   'global_rank': global_rank, 'country_rank': country_rank,
                   'user_details': user_details_get()}

        return details
    

    def __github(self):
        url = 'https://www.github.com/{}'.format(self.__username)
        r=requests.get(url)
        soup=BeautifulSoup(r.content,'html5lib')
        # namediv=soup.find("h1" ,class_="vcard-names pl-2 pl-md-0")
        # name=namediv.find_all('span')[0].getText()
        # u_name=namediv.find_all('span')[1].getText()
        statstab=soup.find(class_="flex-order-1 flex-md-order-none mt-2 mt-md-0")
        elements=statstab.find(class_="mb-3")
        # followers=elements.find_all('a')[0].find('span').getText().strip(' ')
        # following=elements.find_all('a')[1].find('span').getText().strip(' ')
        # totstars=elements.find_all('a')[2].find('span').getText().strip(' ')
        # u_img=soup.find(class_="avatar avatar-user width-full border bg-white")['src']
        # repo_num=soup.find(class_="UnderlineNav-body").find('span',class_="Counter").getText()

    def __codeforces(self):
        urls = {
            "user_info": {"url": f'https://codeforces.com/api/user.info?handles={self.__username}'},
            #"user_contests": {"url": f'https://codeforces.com/contests/with/{self.__username}'}
        }

        reqs = [grequests.get(item["url"]) for item in urls.values() if item.get("url")]

        responses = grequests.map(reqs)

        details_api = {}
        contests = []
        for page in responses:
            if page.status_code != 200:
                raise UsernameError('User not Found')
            if page.request.url == urls["user_info"]["url"]:
                details_api = page.json()
            elif page.request.url == urls["user_contests"]["url"]:
                soup = BeautifulSoup(page.text, 'html.parser')
                table = soup.find('table', attrs={'class': 'user-contests-table'})
                table_body = table.find('tbody')

                rows = table_body.find_all('tr')
                for row in rows:
                    cols = row.find_all('td')
                    cols = [ele.text.strip() for ele in cols]
                    contests.append({
                        "Contest": cols[1],
                        "Rank": cols[3],
                        "Solved": cols[4],
                        "Rating Change": cols[5],
                        "New Rating": cols[6]
                    })

        if details_api.get('status') != 'OK':
            raise UsernameError('User not Found')

        details_api = details_api['result'][0]

        try:
            rating = details_api['rating']
            max_rating = details_api['maxRating']
            rank = details_api['rank']
            max_rank = details_api['maxRank']

        except KeyError:
            rating = 'Unrated'
            max_rating = 'Unrated'
            rank = 'Unrated'
            max_rank = 'Unrated'

        return {
            'status': 'Success',
            'username': self.__username,
            'platform': 'Codeforces',
            'rating': rating,
            'max rating': max_rating,
            'rank': rank,
            'max rank': max_rank,
            'contests': contests
        }
    def __leetcode_v2(self):

        def __parse_response(response):
            total_submissions_count = 0
            total_easy_submissions_count = 0
            total_medium_submissions_count = 0
            total_hard_submissions_count = 0

            ac_submissions_count = 0
            ac_easy_submissions_count = 0
            ac_medium_submissions_count = 0
            ac_hard_submissions_count = 0

            total_easy_questions = 0
            total_medium_questions = 0
            total_hard_questions = 0

            total_problems_solved = 0
            easy_questions_solved = 0
            medium_questions_solved = 0
            hard_questions_solved = 0

            acceptance_rate = 0
            easy_acceptance_rate = 0
            medium_acceptance_rate = 0
            hard_acceptance_rate = 0

            total_problems_submitted = 0
            easy_problems_submitted = 0
            medium_problems_submitted = 0
            hard_problems_submitted = 0

            ranking = get_safe_nested_key(['data', 'matchedUser', 'profile', 'ranking'], response)
            if ranking > 100000:
                ranking = '~100000'

            reputation = get_safe_nested_key(['data', 'matchedUser', 'profile', 'reputation'], response)

            total_questions_stats = get_safe_nested_key(['data', 'allQuestionsCount'], response)
            for item in total_questions_stats:
                if item['difficulty'] == "Easy":
                    total_easy_questions = item['count']
                if item['difficulty'] == "Medium":
                    total_medium_questions = item['count']
                if item['difficulty'] == "Hard":
                    total_hard_questions = item['count']

            ac_submissions = get_safe_nested_key(['data', 'matchedUser', 'submitStats', 'acSubmissionNum'], response)
            for submission in ac_submissions:
                if submission['difficulty'] == "All":
                    total_problems_solved = submission['count']
                    ac_submissions_count = submission['submissions']
                if submission['difficulty'] == "Easy":
                    easy_questions_solved = submission['count']
                    ac_easy_submissions_count = submission['submissions']
                if submission['difficulty'] == "Medium":
                    medium_questions_solved = submission['count']
                    ac_medium_submissions_count = submission['submissions']
                if submission['difficulty'] == "Hard":
                    hard_questions_solved = submission['count']
                    ac_hard_submissions_count = submission['submissions']

            total_submissions = get_safe_nested_key(['data', 'matchedUser', 'submitStats', 'totalSubmissionNum'],
                                                    response)
            for submission in total_submissions:
                if submission['difficulty'] == "All":
                    total_problems_submitted = submission['count']
                    total_submissions_count = submission['submissions']
                if submission['difficulty'] == "Easy":
                    easy_problems_submitted = submission['count']
                    total_easy_submissions_count = submission['submissions']
                if submission['difficulty'] == "Medium":
                    medium_problems_submitted = submission['count']
                    total_medium_submissions_count = submission['submissions']
                if submission['difficulty'] == "Hard":
                    hard_problems_submitted = submission['count']
                    total_hard_submissions_count = submission['submissions']

            if total_submissions_count > 0:
                acceptance_rate = round(ac_submissions_count * 100 / total_submissions_count, 2)
            if total_easy_submissions_count > 0:
                easy_acceptance_rate = round(ac_easy_submissions_count * 100 / total_easy_submissions_count, 2)
            if total_medium_submissions_count > 0:
                medium_acceptance_rate = round(ac_medium_submissions_count * 100 / total_medium_submissions_count, 2)
            if total_hard_submissions_count > 0:
                hard_acceptance_rate = round(ac_hard_submissions_count * 100 / total_hard_submissions_count, 2)

            contribution_points = get_safe_nested_key(['data', 'matchedUser', 'contributions', 'points'],
                                                      response)
            contribution_problems = get_safe_nested_key(['data', 'matchedUser', 'contributions', 'questionCount'],
                                                        response)
            contribution_testcases = get_safe_nested_key(['data', 'matchedUser', 'contributions', 'testcaseCount'],
                                                         response)

            return {
                'status': 'Success',
                'ranking': str(ranking),
                'total_problems_submitted': str(total_problems_submitted),
                'total_problems_solved': str(total_problems_solved),
                'acceptance_rate': f"{acceptance_rate}%",
                'easy_problems_submitted': str(easy_problems_submitted),
                'easy_questions_solved': str(easy_questions_solved),
                'easy_acceptance_rate': f"{easy_acceptance_rate}%",
                'total_easy_questions': str(total_easy_questions),
                'medium_problems_submitted': str(medium_problems_submitted),
                'medium_questions_solved': str(medium_questions_solved),
                'medium_acceptance_rate': f"{medium_acceptance_rate}%",
                'total_medium_questions': str(total_medium_questions),
                'hard_problems_submitted': str(hard_problems_submitted),
                'hard_questions_solved': str(hard_questions_solved),
                'hard_acceptance_rate': f"{hard_acceptance_rate}%",
                'total_hard_questions': str(total_hard_questions),
                'contribution_points': str(contribution_points),
                'contribution_problems': str(contribution_problems),
                'contribution_testcases': str(contribution_testcases),
                'reputation': str(reputation)
            }

        url = f'https://leetcode.com/{self.__username}'
        if requests.get(url).status_code != 200:
            raise UsernameError('User not Found')
        payload = {
            "operationName": "getUserProfile",
            "variables": {
                "username": self.__username
            },
            "query": "query getUserProfile($username: String!) {  allQuestionsCount {    difficulty    count  }  matchedUser(username: $username) {    contributions {    points      questionCount      testcaseCount    }    profile {    reputation      ranking    }    submitStats {      acSubmissionNum {        difficulty        count        submissions      }      totalSubmissionNum {        difficulty        count        submissions      }    }  }}"
        }
        res = requests.post(url='https://leetcode.com/graphql',
                            json=payload,
                            headers={'referer': f'https://leetcode.com/{self.__username}/'})
        res.raise_for_status()
        res = res.json()
        return __parse_response(res)

    def get_details(self, platform):
        if platform == 'codechef':
            return self.__codechef()

        if platform == 'codeforces':
            return self.__codeforces()

        if platform == 'leetcode':
            return self.__leetcode_v2()
        
        if platform == 'github':
            return self.__github()

        raise PlatformError('Platform not Found')


if __name__ == '__main__':
    ud = UserData('uwi')
    ans = ud.get_details('leetcode')

    print(ans)


